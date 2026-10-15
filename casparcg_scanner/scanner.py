import json

from pathlib import Path
from .util import get_gdd, get_name_type

class Scanner:
    _path = None
    _types = None

    def set_path(self, path: Path):
        self._path = path.resolve()

    def _crawl(self):
        for path in self._path.rglob("*"):
            if path.is_file():
                name, type_ = get_name_type(path, self._path, self._types)
                if name: yield name, type_, path.resolve()


class FontScanner(Scanner):
    _types = {"ttf", "otf", "woff", "woff2"}

    def names(self):
        print(f"[fonts] Scanning names {self._path}")
        return sorted({ name for name, *_ in self._crawl() })


class TemplateScanner(Scanner):
    _types = {"html", "htm", "ft", "wt", "ct", "swf"}

    def names(self):
        print(f"[templates] Scanning names {self._path}")
        return sorted({ name for name, *_ in self._crawl() })

    def templates(self):
        def make(name, type_, path):
            gdd = None
            try: gdd = get_gdd(path)
            except Exception as e: print(f"[templates] Error in {path}: {e}")

            tmpl = {"id": name, "path": str(path), "type": type_}
            if gdd: tmpl["gdd"] = json.loads(gdd)
            return tmpl

        print(f"[templates] Scanning names {self._path}")
        return [ make(*args) for args in sorted(self._crawl()) ]
