from pathlib import Path
import xml.etree.ElementTree as et

class Config:
    def __init__(self, config_path):
        self.db_path = Path("./scanner.db")
        self.http_addr = "0.0.0.0"
        self.http_port = 8000

        def get_path(config_path, parent_node, tag_name, fallback):
            node = parent_node.find(tag_name) if parent_node else None
            path = node.text.strip() if node is not None and node.text else fallback

            # Compute 'path' relative to 'config_path'.
            # If 'path' is absolute, 'config_path' will be ignored.
            return config_path.parent / Path(path)

        root_node = et.parse(config_path).getroot()
        if root_node.tag != "configuration":
            raise ValueError(f"Invalid root tag <{root_node.tag}>.")
        paths_node = root_node.find("paths")

        self.font_path = get_path(config_path, paths_node, "font-path", "./font")
        self.media_path = get_path(config_path, paths_node, "media-path", "./media")
        self.template_path = get_path(config_path, paths_node, "template-path", "./template")
