import argparse
import shutil
import sys

from . import app, font, mdia, store, tmpl, __version__
from lxml import etree
from pathlib import Path
from waitress import serve

def main():
    parser = argparse.ArgumentParser(description="CasparCG Media Scanner")

    parser.add_argument("config", nargs="?", type=Path, default=Path("casparcg.config"),
        help="path to the casparcg.config file (default: casparcg.config)")
    parser.add_argument("--db-path", type=Path, metavar="path",
        help="override database location (default: scanner.db in the config directory)")
    parser.add_argument("--http-addr", type=str, default="0.0.0.0", metavar="addr",
        help="host address to bind the server to (default: 0.0.0.0)")
    parser.add_argument("--http-port", type=int, default=8000, metavar="port",
        help="port to bind the server to (default: 8000)")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s v{__version__}")
    parser.add_argument("--debug", action="store_true", help="show full stack trace on errors")

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"): stream.reconfigure(encoding="utf8", errors="replace")

    args = parser.parse_args()
    try:
        for tool in ("ffprobe", "ffmpeg"):
            if not shutil.which(tool): raise FileNotFoundError(f"{tool} not found in PATH")

        db_path = args.db_path or (args.config.parent / "scanner.db")
        store.connect(db_path)

        root = etree.parse(args.config).getroot()
        if root.tag != "configuration":
            raise ValueError(f"invalid root tag <{root.tag}>")

        def get_path(xpath, fallback):
            val = root.findtext(xpath, default="").strip()
            # If 'Path(...)' is absolute, 'config_path' will be ignored.
            path = args.config.parent / Path(val or fallback)
            if not path.is_dir(): raise ValueError(f"directory {path} not found")
            return path

        font.set_path(get_path("paths/font-path", "font"))
        mdia.set_path(get_path("paths/media-path", "media"))
        tmpl.set_path(get_path("paths/template-path", "template"))

        mdia.monitor()

        print(f"[main] Listening on {args.http_addr}:{args.http_port}")
        serve(app, host=args.http_addr, port=args.http_port)

    except KeyboardInterrupt:
        print("\n[main] Shutting down...")
        sys.exit(0)

    except Exception as e:
        if not args.debug:
            print(str(e), file=sys.stderr)
            sys.exit(1)
        else: raise

if __name__ == "__main__": main()
