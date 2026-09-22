from .handler import EventHandler
from pathlib import Path
from .store import Store
from .util import get_name_type

types = {"ttf", "otf", "woff", "woff2"}

class FontHandler(EventHandler):

    def crawl(self):
        print(f"[fonts] Scanning {self.watch_path}")
        found = set()
        for path in self.watch_path.rglob("*"):
            if not path.is_file(): continue
            name, _ = get_name_type(path, self.watch_path, types)
            if name: found.add(path.resolve())
        stored = set(map(Path, self.store.get_font_paths()))

        for path in stored - found: self.remove(path)
        for path in found - stored: self.add(path)

    def add(self, path: Path):
        name, _ = get_name_type(path, self.watch_path, types)
        if not name: return

        fullpath = str(path.resolve())
        print(f"[fonts] Adding {name} => {fullpath}")
        self.store.add_font(name, fullpath)

    def remove(self, path: Path):
        name, _ = get_name_type(path, self.watch_path, types)
        if not name: return

        print(f"[fonts] Removing {name}")
        self.store.remove_font(name)
