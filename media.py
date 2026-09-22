from handler import EventHandler
from pathlib import Path
from store import Store
from util import generate_thumbnail, get_cinf, get_info, get_media_info, get_name_type

class MediaHandler(EventHandler):

    def crawl(self):
        print(f"[media] Scanning {self.watch_path}")
        found = set()
        for path in self.watch_path.rglob("*"):
            if not path.is_file(): continue
            name, _ = get_name_type(path, self.watch_path)
            if name: found.add(path.resolve())
        stored = set(map(Path, self.store.get_media_paths()))

        for path in stored - found: self.remove(path)
        for path in found - stored: self.add(path)

    def add(self, path: Path):
        name, _ = get_name_type(path, self.watch_path)
        if not name: return

        fullpath = str(path.resolve())
        stat = path.stat()
        size, time = stat.st_size, stat.st_mtime

        if found := self.store.get_media_size_time(name):
            prev_size, prev_time = found
            if size == prev_size and time == prev_time: return

        print(f"[media] Adding {name} => {fullpath}")
        info = cinf = media_info = None
        try:
            info = get_info(path)
            cinf = get_cinf(name, size, time, info)
            media_info = get_media_info(name, path, size, time, info)
        except Exception as e: print(f"[media] Error: {e}")

        tinf = thumbnail = None
        try: tinf, thumbnail = generate_thumbnail(name, path)
        except Exception as e: print(f"[media] Error: {e}")

        self.store.add_media(name, fullpath, size, time, cinf, tinf, media_info, thumbnail)

    def remove(self, path: Path):
        name, _ = get_name_type(path, self.watch_path)
        if not name: return

        print(f"[media] Removing {name}")
        self.store.remove_media(name)
