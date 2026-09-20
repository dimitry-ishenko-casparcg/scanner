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
        print("[templates] Scanning", self.watch_path)
        disk_templates = {}
        for path in self.watch_path.rglob("*"):
            if path.is_file():
                name, type_ = get_name_type(path, self.watch_path, types)
                fullpath = str(path.resolve())
                if name: disk_templates[name] = (fullpath, type_)

        store_names = { name for name, *_ in self.store.get_templates() }
        disk_names = set(disk_templates.keys())

        remove_names = store_names - disk_names
        if remove_names:
            print(f"[templates] Removing {len(remove_names)} templates")
            self.store.remove_templates(remove_names)

        add_names = disk_names - store_names
        if add_names:
            print(f"[templates] Adding {len(add_names)} templates")
            self.store.add_templates([ (name,) + disk_templates[name] + (None,) for name in add_names ])

    def _add(self, path: str):
        path = Path(path)
        name, type_ = get_name_type(path, self.watch_path, types)
        if name:
            fullpath = str(path.resolve())
            print(f"[templates] Adding {name} => {fullpath}")
            gdd = None
            try: gdd = get_gdd(path)
            except Exception as e: print(f"[templates] GDD error: {e}")
            self.store.add_templates([(name, fullpath, type_, gdd)])

    def _remove(self, path: str):
        name, _ = get_name_type(Path(path), self.watch_path, types)
        if name:
            print(f"[templates] Removing {name}")
            self.store.remove_templates([name])

    def on_created(self, event):
        if not event.is_directory: self._add(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory: self._remove(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._remove(event.src_path)
            self._add(event.dest_path)
