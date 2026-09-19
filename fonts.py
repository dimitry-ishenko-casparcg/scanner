from pathlib import Path
from store import Store
from util import get_name
from watchdog.events import FileSystemEventHandler

extens = {".ttf", ".otf", ".woff", ".woff2"}

class FontHandler(FileSystemEventHandler):
    def __init__(self, watch_path: Path, store: Store):
        self.watch_path = watch_path
        self.store = store
        super().__init__()

    def crawl(self):
        print("[fonts] Scanning", self.watch_path)
        disk_fonts = {}
        for path in self.watch_path.rglob("*"):
            if path.is_file():
                name = get_name(path, self.watch_path, extens)
                if name: disk_fonts[name] = str(path)

        store_names = { name for name, _ in self.store.get_fonts() }
        disk_names = set(disk_fonts.keys())

        remove_names = store_names - disk_names
        if remove_names:
            print(f"[fonts] Removing {len(remove_names)} fonts")
            self.store.remove_fonts(remove_names)

        add_names = disk_names - store_names
        if add_names:
            print(f"[fonts] Adding {len(add_names)} fonts")
            self.store.add_fonts([ (name, disk_fonts[name]) for name in add_names ])

    def _add(self, path: str):
        if name := get_name(Path(path), self.watch_path, extens):
            print(f"[fonts] Adding {name} => {path}")
            self.store.add_fonts([(name, path)])

    def _remove(self, path: str):
        if name := get_name(Path(path), self.watch_path, extens):
            print(f"[fonts] Removing {name} => {path}")
            self.store.remove_fonts([name])

    def on_created(self, event):
        if not event.is_directory: self._add(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory: self._remove(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._remove(event.src_path)
            self._add(event.dest_path)
