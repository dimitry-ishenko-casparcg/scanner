from pathlib import Path

def get_name_type(path: Path, base_path: Path, types):
    type_ = path.suffix.lower()[1:]
    if not type_ in types: return None, None
    if type_ == "htm": type_ = "html"

    name = str(path.relative_to(base_path).with_suffix("")).upper().replace("\\", "/")
    return name, type_
