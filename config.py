from lxml import etree
from pathlib import Path

class Config:
    def __init__(self, config_path: Path):
        self.db_path = config_path.parent / "scanner.db"
        self.http_addr = "0.0.0.0"
        self.http_port = 8000

        root = etree.parse(config_path).getroot()
        if root.tag != "configuration":
            raise ValueError(f"Invalid root tag <{root.tag}>")

        def get_path(tag, fallback):
            val = root.findtext(f"paths/{tag}", default="").strip()
            # If 'Path(...)' is absolute, 'config_path' will be ignored.
            return config_path.parent / Path(val or fallback)

        self.font_path = get_path("font-path", "./font")
        self.media_path = get_path("media-path", "./media")
        self.template_path = get_path("template-path", "./template")
