from pathlib import Path
import xml.etree.ElementTree as et

class Config:
    def __init__(self, config_path: Path):
        self.db_path = Path("./scanner.db")
        self.http_addr = "0.0.0.0"
        self.http_port = 8000

        def get_path(config_path: Path, parent, tag, fallback):
            node = parent.find(tag) if parent else None
            path = node.text.strip() if node is not None and node.text else fallback

            # Compute 'path' relative to 'config_path'.
            # If 'path' is absolute, 'config_path' will be ignored.
            return config_path.parent / Path(path)

        root = et.parse(config_path).getroot()
        if root.tag != "configuration":
            raise ValueError(f"Invalid root tag <{root.tag}>.")
        paths = root.find("paths")

        self.font_path = get_path(config_path, paths, "font-path", "./font")
        self.media_path = get_path(config_path, paths, "media-path", "./media")
        self.template_path = get_path(config_path, paths, "template-path", "./template")
