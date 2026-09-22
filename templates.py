from handler import EventHandler
from pathlib import Path
from store import Store
from util import get_gdd, get_name_type

types = {"html", "htm", "ft", "wt", "ct", "swf"}

class TemplateHandler(EventHandler):

    def crawl(self):
        print(f"[templates] Scanning {self.watch_path}")
        found = set()
        for path in self.watch_path.rglob("*"):
            if not path.is_file(): continue
            name, _ = get_name_type(path, self.watch_path, types)
            if name: found.add(path.resolve())
        stored = set(map(Path, self.store.get_template_paths()))

        for path in stored - found: self.remove(path)
        for path in found - stored: self.add(path)

    def add(self, path: Path):
        name, type_ = get_name_type(path, self.watch_path, types)
        if not name: return

        fullpath = str(path.resolve())
        print(f"[templates] Adding {name} => {fullpath}")

        gdd = None
        try: gdd = get_gdd(path)
        except Exception as e: print(f"[templates] Error: {e}")
        self.store.add_template(name, fullpath, type_, gdd)

    def remove(self, path: Path):
        name, _ = get_name_type(path, self.watch_path, types)
        if not name: return

        print(f"[templates] Removing {name}")
        self.store.remove_template(name)
