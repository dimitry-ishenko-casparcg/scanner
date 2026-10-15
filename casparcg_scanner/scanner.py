import json

from lxml import html
from pathlib import Path
from .store import Store

class Scanner:
    _path = None
    _types = None

    def set_path(self, path: Path):
        self._path = path.resolve()

    def _crawl(self):
        for path in self._path.rglob("*"):
            if not path.is_file(): continue

            type = path.suffix.lower()[1:]
            if self._types is not None and type not in self._types: continue

            name = path.relative_to(self._path).with_suffix("")
            name = str(name).upper().replace("\\", "/")

            yield path, name, type

class FontScanner(Scanner):
    _types = {"ttf", "otf", "woff", "woff2"}
    def names(self): return sorted({ name for _, name, _ in self._crawl() })


class MediaScanner(Scanner):
    def __init__(self, store: Store):
        self._store = store

    def monitor(self):
        pass

    def cinf(self, name: str):
        row = self._store.get_media("cinf", name=name)
        return row[0] if row else None

    def cinfs(self):
        return [ cinf for cinf, in self._store.get_media("cinf") if cinf ]

    def info(self, name: str):
        row = self._store.get_media("media_info", name=name)
        return row[0] if row else None

    def infos(self):
        return [ info for info, in self._store.get_media("media_info") if info ]

    def tinfs(self):
        return [ tinf for tinf, in self._store.get_media("tinf") if tinf ]

    def thumbnail(self, name: str):
        row = self._store.get_media("thumbnail", name=name)
        return row[0] if row else None


class TemplateScanner(Scanner):
    _types = {"html", "htm", "ft", "wt", "ct", "swf"}
    def names(self): return sorted({ name for _, name, _ in self._crawl() })

    def templates(self):
        def make_tmpl(path, name, type):
            if type == "htm": type = "html"
            tmpl = {"id": name, "path": str(path), "type": type}
            try:
                tree = html.parse(path)
                if scripts := tree.xpath("//script[@name='graphics-data-definition']"):
                    src = scripts[0].get("src")

                    if src: gdd = (path.parent / src).read_text(encoding="utf8")
                    else: gdd = scripts[0].text

                    tmpl["gdd"] = json.loads(gdd)
            except Exception as e: print(f"[templates] {e} in {path}")
            return tmpl

        return [ make_tmpl(*args) for args in sorted(self._crawl()) ]
