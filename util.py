from pathlib import Path

def get_name(path: Path, base_path: Path, extens):
    if path.suffix.lower() in extens:
        name = str(path.relative_to(base_path).with_suffix(""))
        return name.replace("\\", "/")
    else: return None
