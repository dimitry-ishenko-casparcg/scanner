from pathlib import Path
from store import Store
from watchdog.events import FileSystemEventHandler

class TemplateHandler(FileSystemEventHandler):
    def __init__(self, watch_path: Path, store: Store):
        self.watch_path = watch_path
        self.store = store
        super().__init__()

    def crawl(self):
        print("[templates] Scanning", self.watch_path)
        for file_path in self.watch_path.rglob("*"):
            if file_path.is_file():
                pass

    def on_created(self, event):
        if not event.is_directory:
            pass

    def on_modified(self, event):
        if not event.is_directory:
            pass

    def on_deleted(self, event):
        if not event.is_directory:
            pass


