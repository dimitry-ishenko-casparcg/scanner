from handler import EventHandler
from pathlib import Path
from store import Store

class MediaHandler(EventHandler):

    def crawl(self):
        print(f"[media] Scanning {self.watch_path}")
        for file_path in self.watch_path.rglob("*"):
            if file_path.is_file():
                pass
