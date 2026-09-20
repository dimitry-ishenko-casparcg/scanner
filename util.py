import json

from lxml import html
from pathlib import Path

def get_name_type(path: Path, base_path: Path, types = None):
    type_ = path.suffix.lower()[1:]
    if types is not None and type_ not in types: return None, None
    if type_ == "htm": type_ = "html"

    name = str(path.relative_to(base_path).with_suffix("")).upper().replace("\\", "/")
    return name, type_

def get_gdd(path: Path):
    text = path.read_text(encoding="utf8", errors="ignore")
    tree = html.fromstring(text)

    scripts = tree.xpath("//script[@name='graphics-data-definition']")
    if not scripts: return None

    src = scripts[0].get("src")
    if not src: gdd = scripts[0].text
    else: gdd = (path.parent / src).read_text(encoding="utf8")

    json.loads(gdd) # test gdd
    return gdd.strip()
