from pathlib import Path
from store import Store
from util import get_name_type
from watchdog.events import FileSystemEventHandler

types = {"ttf", "otf", "woff", "woff2"}

class FontHandler(FileSystemEventHandler):
    def __init__(self, watch_path: Path, store: Store):
        self.watch_path = watch_path
        self.store = store
        super().__init__()

    def crawl(self):
        print(f"[fonts] Scanning {self.watch_path}")
        on_disk = {}
        for path in self.watch_path.rglob("*"):
            if not path.is_file(): continue

            name, _ = get_name_type(path, self.watch_path, types)
            fullpath = str(path.resolve())
            if name: on_disk[name] = fullpath

        store_names = { name for name, _ in self.store.get_fonts() }
        disk_names = set(on_disk.keys())

        remove_names = store_names - disk_names
        if remove_names:
            print(f"[fonts] Removing {len(remove_names)} fonts")
            self.store.remove_fonts(remove_names)

        add_names = disk_names - store_names
        if add_names:
            print(f"[fonts] Adding {len(add_names)} fonts")
            self.store.add_fonts([ (name, on_disk[name]) for name in add_names ])

    def _add(self, path: Path):
        name, _ = get_name_type(path, self.watch_path, types)
        if not name: return

        fullpath = str(path.resolve())
        print(f"[fonts] Adding {name} => {fullpath}")
        self.store.add_fonts([ (name, fullpath) ])

    def _remove(self, path: Path):
        name, _ = get_name_type(path, self.watch_path, types)
        if not name: return

        print(f"[fonts] Removing {name}")
        self.store.remove_fonts([ name ])

    def on_created(self, event):
        if not event.is_directory: self._add(Path(event.src_path))

    def on_modified(self, event):
        if not event.is_directory: self._add(Path(event.src_path))

    def on_deleted(self, event):
        if not event.is_directory: self._remove(Path(event.src_path))
        else: self.crawl()

    def on_moved(self, event):
        if not event.is_directory:
            self._remove(Path(event.src_path))
            self._add(Path(event.dest_path))
        else: self.crawl()
