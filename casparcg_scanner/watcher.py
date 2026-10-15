from .media import MediaHandler
from pathlib import Path
from .store import Store
from watchdog.observers import Observer

class Watcher:
    def __init__(self, store: Store, media_path: Path):
        self.observer = Observer()
        self.handlers = [ MediaHandler(store, media_path) ]

    def crawl(self):
        for handler in self.handlers: handler.crawl()

    def monitor(self):
        for handler in self.handlers:
            self.observer.schedule(handler, handler.watch_path, recursive=True)

        print("[watcher] Starting monitor")
        self.observer.start()
