import argparse

from pathlib import Path
from waitress import serve

from app import app, store, __version__
from app.scanner import Scanner
from app.util import get_scanner_paths

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
    
    args = parser.parse_args()
    scanner_paths = get_scanner_paths(args.config)

    db_path = args.db_path or (args.config.parent / "scanner.db")
    store.connect(db_path)

    scanner = Scanner(store, **scanner_paths)
    scanner.crawl()
    scanner.monitor()

    print(f"[main] Listening on {args.http_addr}:{args.http_port}")
    serve(app, host=args.http_addr, port=args.http_port)

if __name__ == "__main__": main()
