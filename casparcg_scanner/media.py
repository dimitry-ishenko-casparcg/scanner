import threading
import time

from pathlib import Path
from queue import Queue
from .store import Store
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

class MediaHandler(FileSystemEventHandler):
    def __init__(self, store: Store, path: Path):
        self._store = store
        self._path = path
        self._tasks = Queue()

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
            except Exception as e: print(f"[media] {e}")

    def _enqueue(self, func, path: str): self._tasks.put((func, Path(path)))
    def _dequeue(self): return self._tasks.get()

    def _rescan(self, path: Path):
        pass

    def _update(self, path: Path):
        pass
