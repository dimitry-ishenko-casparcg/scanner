from pathlib import Path
from store import Store
from util import get_gdd, get_name_type
from watchdog.events import FileSystemEventHandler

types = {"html", "htm", "ft", "wt", "ct", "swf"}

class TemplateHandler(FileSystemEventHandler):
    def __init__(self, watch_path: Path, store: Store):
        self.watch_path = watch_path
        self.store = store
        super().__init__()

    def crawl(self):
        print(f"[templates] Scanning {self.watch_path}")
        on_disk = {}
        for path in self.watch_path.rglob("*"):
            if not path.is_file(): continue

            name, type_ = get_name_type(path, self.watch_path, types)
            fullpath = str(path.resolve())
            if name: on_disk[name] = (fullpath, type_)

        store_names = { name for name, *_ in self.store.get_templates() }
        disk_names = set(on_disk.keys())

        remove_names = store_names - disk_names
        if remove_names:
            print(f"[templates] Removing {len(remove_names)} templates")
            self.store.remove_templates(remove_names)

        add_names = disk_names - store_names
        if add_names:
            print(f"[templates] Adding {len(add_names)} templates")
            self.store.add_templates([ (name,) + on_disk[name] + (None,) for name in add_names ])

    def _add(self, path: Path):
        name, type_ = get_name_type(path, self.watch_path, types)
        if not name: return

        fullpath = str(path.resolve())
        print(f"[templates] Adding {name} => {fullpath}")

        gdd = None
        try: gdd = get_gdd(path)
        except Exception as e: print(f"[templates] Error: {e}")
        self.store.add_templates([ (name, fullpath, type_, gdd) ])

    def _remove(self, path: Path):
        name, _ = get_name_type(path, self.watch_path, types)
        if not name: return

        print(f"[templates] Removing {name}")
        self.store.remove_templates([ name ])

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
