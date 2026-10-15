import json

from lxml import html
from pathlib import Path

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

    def names(self):
        print(f"[fonts] Scanning names {self._path}")
        return sorted({ name for _, name, _ in self._crawl() })


class TemplateScanner(Scanner):
    _types = {"html", "htm", "ft", "wt", "ct", "swf"}

    def names(self):
        print(f"[templates] Scanning names {self._path}")
        return sorted({ name for _, name, _ in self._crawl() })

    def templates(self):
        def make_tmpl(path, name, type):
            tmpl = {"id": name, "path": str(path), "type": type}
            try:
                tree = html.parse(path)
                if scripts := tree.xpath("//script[@name='graphics-data-definition']"):
                    src = scripts[0].get("src")

                    if src: gdd = (path.parent / src).read_text(encoding="utf8")
                    else: gdd = scripts[0].text

                    tmpl["gdd"] = json.loads(gdd)
            except Exception as e: print(f"[templates] Error in {path}: {e}")
            return tmpl

        print(f"[templates] Scanning names {self._path}")
        return [ make_tmpl(*args) for args in sorted(self._crawl()) ]
