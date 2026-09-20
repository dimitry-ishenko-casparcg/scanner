from pathlib import Path
from store import Store
from watchdog.events import FileSystemEventHandler

class EventHandler(FileSystemEventHandler):
    def __init__(self, watch_path: Path, store: Store):
        self.watch_path = watch_path
        self.store = store
        super().__init__()

    def crawl(self): pass
    def add(self, path: Path): pass
    def remove(self, path: Path): pass

    def on_created(self, event):
        if not event.is_directory: self.add(Path(event.src_path))

    def on_modified(self, event):
        if not event.is_directory: self.add(Path(event.src_path))

    def on_deleted(self, event):
        if not event.is_directory: self.remove(Path(event.src_path))
        else: self.crawl()

    def on_moved(self, event):
        if not event.is_directory:
            self.remove(Path(event.src_path))
            self.add(Path(event.dest_path))
        else: self.crawl()
