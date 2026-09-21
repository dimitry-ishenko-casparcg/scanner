import threading
import time

from pathlib import Path
from store import Store
from watchdog.events import FileSystemEventHandler

class EventHandler(FileSystemEventHandler):
    def __init__(self, watch_path: Path, store: Store):
        super().__init__()
        self.watch_path = watch_path.resolve()
        self.store = store

        self._pending = {}
        self._lock = threading.Lock()
        threading.Thread(target=self._loop, daemon=True).start()

    def crawl(self): pass
    def add(self, path: Path): pass
    def remove(self, path: Path): pass

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
