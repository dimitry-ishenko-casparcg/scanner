from config import Config
from fonts import FontHandler
from media import MediaHandler
from store import Store
from templates import TemplateHandler
from watchdog.observers import Observer

class Scanner:
    def __init__(self, config: Config, store: Store):
        self.observer = Observer()
        self.handlers = [ FontHandler(config.font_path, store),
            MediaHandler(config.media_path, store),
            TemplateHandler(config.template_path, store),
        ]

    def crawl(self):
        for handler in self.handlers:
            handler.crawl()

    def monitor(self):
        for handler in self.handlers:
            self.observer.schedule(handler, handler.watch_path, recursive=True)

        print("[scanner] Starting monitor")
        self.observer.start()
