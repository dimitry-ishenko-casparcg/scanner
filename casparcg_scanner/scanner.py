from .fonts import FontHandler
from .media import MediaHandler
from .store import Store
from .templates import TemplateHandler
from watchdog.observers import Observer

class Scanner:
    def __init__(self, store: Store, font_path: Path, media_path: Path, template_path: Path):
        self.observer = Observer()
        self.handlers = [ FontHandler(store, font_path),
            MediaHandler(store, media_path),
            TemplateHandler(store, template_path)
        ]

    def crawl(self):
        for handler in self.handlers: handler.crawl()

    def monitor(self):
        for handler in self.handlers:
            self.observer.schedule(handler, handler.watch_path, recursive=True)

        print("[scanner] Starting monitor")
        self.observer.start()
