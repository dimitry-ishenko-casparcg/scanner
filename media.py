from handler import EventHandler
from pathlib import Path
from store import Store
from util import get_cinf, get_info, get_name_type

class MediaHandler(EventHandler):

    def crawl(self):
        print(f"[media] Scanning {self.watch_path}")
        found = set()
        for path in self.watch_path.rglob("*"):
            if not path.is_file(): continue
            name, _ = get_name_type(path, self.watch_path)
            if name: found.add(path.resolve())
        stored = { Path(path) for _, path, *_ in self.store.get_media() }

        for path in stored - found: self.remove(path)
        for path in found - stored: self.add(path)

    def add(self, path: Path):
        name, _ = get_name_type(path, self.watch_path)
        if not name: return

        fullpath = str(path.resolve())
        stat = path.stat()
        size, time = stat.st_size, stat.st_mtime
        print(f"[media] Adding {name} => {fullpath}")

        info = None
        try: info = get_info(path)
        except Exception as e: print(f"[media] Error: {e}")
        if not info: return

        cinf = get_cinf(name, size, time, info)
        info = json.dumps(info)
        self.store.add_media([ (name, fullpath, size, time, cinf, None, info, None) ])

    def remove(self, path: Path):
        name, _ = get_name_type(path, self.watch_path)
        if not name: return

        print(f"[media] Removing {name}")
        self.store.remove_templates([ name ])
