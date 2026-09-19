from pathlib import Path

def get_name_type(path: Path, base_path: Path, types):
    type_ = path.suffix.lower()[1:]
    if not type_ in types: return None, None

    name = str(path.relative_to(base_path).with_suffix(""))
    name = name.upper().replace("\\", "/")

    return name, "html" if type_ == "htm" else type_
