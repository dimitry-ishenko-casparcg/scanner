import threading
import time

from pathlib import Path
from .store import Store
from .util import generate_thumbnail, get_cinf, get_info, get_media_info, get_name_type
from watchdog.events import FileSystemEventHandler

class MediaHandler(FileSystemEventHandler):
    def __init__(self, store: Store, watch_path: Path):
        super().__init__()
        self.store = store
        self.watch_path = watch_path.resolve()

        self._pending = {}
        self._lock = threading.Lock()
        threading.Thread(target=self._loop, daemon=True).start()

    def _touch(self, path: Path):
        with self._lock: self._pending[path] = time.monotonic() + 1.

    def _remove(self, path: Path):
        with self._lock: self._pending.pop(path, None)
        self.remove(path)

    def _loop(self):
        while True:
            time.sleep(0.5)
            now = time.monotonic()

            with self._lock:
                ready = [ path for path, time in self._pending.items() if time <= now ]
                for path in ready: del self._pending[path]

            for path in ready:
                if path.exists(): self.add(path)

    def on_created(self, event):
        if not event.is_directory: self._touch(Path(event.src_path))

    def on_modified(self, event):
        if not event.is_directory: self._touch(Path(event.src_path))

    def on_deleted(self, event):
        if not event.is_directory: self._remove(Path(event.src_path))
        else: self.crawl()

    def on_moved(self, event):
        if not event.is_directory:
            self._remove(Path(event.src_path))
            self._touch(Path(event.dest_path))
        else: self.crawl()

    ####################
    def crawl(self):
        print(f"[media] Scanning {self.watch_path}")
        found = set()
        for path in self.watch_path.rglob("*"):
            if not path.is_file(): continue
            name, _ = get_name_type(path, self.watch_path)
            if name: found.add(path.resolve())
        stored = set(map(Path, self.store.get_media_paths()))

        for path in stored - found: self.remove(path)
        # call add() on every found file to detect changes,
        # while the scanner was offline
        for path in found: self.add(path)

    def add(self, path: Path):
        name, _ = get_name_type(path, self.watch_path)
        if not name: return

        fullpath = str(path.resolve())
        stat = path.stat()
        size, time = stat.st_size, stat.st_mtime

        if found := self.store.get_media_size_time(name):
            prev_size, prev_time = found
            if size == prev_size and time == prev_time: return

        print(f"[media] Adding {name} => {fullpath}")
        cinf = image = media_info = tinf = None
        try:
            info = get_info(path)
            cinf = get_cinf(name, size, time, info)
            media_info = get_media_info(name, path, size, time, info)

            tinf, image = generate_thumbnail(name, path, info)
        except Exception as e: print(f"[media] {e}")

        self.store.add_media(name, fullpath, size, time, cinf, tinf, media_info, image)

    def remove(self, path: Path):
        name, _ = get_name_type(path, self.watch_path)
        if not name: return

        print(f"[media] Removing {name}")
        self.store.remove_media(name)
