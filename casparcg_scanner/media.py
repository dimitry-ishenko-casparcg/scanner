import subprocess
import threading
import time

from pathlib import Path
from .store import Store
from .util import generate_thumbnail, get_cinf, get_info, get_media_info
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

class MediaHandler(FileSystemEventHandler):
    def __init__(self, store: Store, path: Path):
        self._store = store
        self._path = path

        self._pending = {}
        self._cond = threading.Condition()

    def start(self):
        print("[media] Starting monitor")
        observer = Observer()
        observer.schedule(self, self._path, recursive=True)
        observer.start()

        threading.Thread(target=self._worker, daemon=True).start()

        print("[media] Starting initial scan")
        self._enqueue(self._rescan, self._path)

    def on_created(self, event):
        if event.is_directory: self._enqueue(self._rescan, event.src_path)
        else: self._enqueue(self._update, event.src_path)

    def on_modified(self, event):
        if event.is_directory: pass # process individual files only
        else: self._enqueue(self._update, event.src_path)

    def on_deleted(self, event):
        if event.is_directory: self._enqueue(self._rescan, event.src_path)
        else: self._enqueue(self._update, event.src_path)

    def on_moved(self, event):
        if event.is_directory:
            self._enqueue(self._rescan, event.src_path)
            self._enqueue(self._rescan, event.dest_path)
        else:
            self._enqueue(self._update, event.src_path)
            self._enqueue(self._update, event.dest_path)

    def _worker(self):
        while True:
            func, path = self._dequeue()
            try: func(path)
            except Exception as e: print(f"[media] {e} in '{path}'")

    def _enqueue(self, func, path: str):
        task = (func, Path(path))
        with self._cond:
            self._pending.pop(task, None)
            self._pending[task] = time.monotonic() + 1
            self._cond.notify()

    def _dequeue(self):
        with self._cond:
            while True:
                if self._pending:
                    task, tick = next(iter(self._pending.items()))
                    if (wait := tick - time.monotonic()) <= 0:
                        del self._pending[task]
                        return task
                    self._cond.wait(wait)
                else: self._cond.wait()

    def _rescan(self, subdir: Path):
        stored = map(Path, (path for path, in self._store.get_media("path")))
        stored = { path for path in stored if path.is_relative_to(subdir) }

        found = { path for path in subdir.rglob("*") if path.is_file() }
        for path in stored | found: self._enqueue(self._update, path)

    def _update(self, path: Path):
        name = path.relative_to(self._path).with_suffix("")
        name = str(name).upper().replace("\\", "/")

        try: stat = path.stat()
        except FileNotFoundError:
            if self._store.get_media("name", name=name):
                print(f"[media] Removing {name}")
                self._store.remove_media(name)
            return

        size, mtime = stat.st_size, stat.st_mtime
        if row := self._store.get_media("size", "time", name=name):
            if row == (size, mtime): return

        print(f"[media] Adding {name} => {path}")
        info = cinf = media_info = tinf = image = None
        try:
            info = get_info(path)
            cinf = get_cinf(name, size, mtime, info)
            media_info = get_media_info(name, path, size, mtime, info)

            tinf, image = generate_thumbnail(name, path, info)

        except subprocess.CalledProcessError as e:
            lines = e.stderr.decode(errors="replace").splitlines()
            msg = lines[-1] if lines else f"exit status {e.returncode}"
            print(f"[media] {e.cmd[0]}: {msg}")

        except subprocess.TimeoutExpired as e:
            print(f"[media] {e.cmd[0]}: timeout expired")

        except Exception as e: print(f"[media] {e}")

        self._store.add_media(name, str(path), size, mtime, cinf, tinf, media_info, image)
