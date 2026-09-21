import json
import sys

from config import Config
from flask import Flask, Response
from pathlib import Path
from scanner import Scanner
from store import Store
from waitress import serve

app = Flask(__name__)

config_path = Path(sys.argv[1] if len(sys.argv) > 1 else "./casparcg.config")
config = Config(config_path)

store = Store(config)

@app.route("/cinf/<path:name>")
def cinf_path(name):
    cinf = store.get_media_cinf(name.upper())
    if not cinf: return "", 404
    body = f"201 CINF OK\r\n{cinf}\r\n"
    return Response(body, mimetype="text/plain")

@app.route("/cls")
def cls():
    cinfs = [ cinf for cinf, in store.get_media_cinf() ] + [""]
    rows = "\r\n".join(cinfs)
    body = f"200 CLS OK\r\n{rows}\r\n"
    return Response(body, mimetype="text/plain")

@app.route("/fls")
def fls():
    names = [ name for name, _ in store.get_fonts() ] + [""]
    rows = "\r\n".join(names)
    body = f"200 FLS OK\r\n{rows}\r\n"
    return Response(body, mimetype="text/plain")

@app.route("/media")
def media():
    infos = [ info for info, in store.get_media_info() if info ]
    body = f"[{','.join(infos)}]"
    return Response(body, mimetype="application/json")

@app.route("/media/info/<path:name>")
def media_info_path(name):
    info = store.get_media_info(name.upper())
    body = info or "{}"
    return Response(body, mimetype="application/json")

@app.route("/media/thumbnail/<path:name>")
def media_thumbnail_path(name):
    pass

@app.route("/templates")
def templates():
    templates = []
    for name, path, type_, gdd in store.get_templates():
        info = { "id": name, "path": path, "type": type_ }
        if gdd:
            try: info["gdd"] = json.loads(gdd)
            except json.JSONDecodeError: pass
        templates.append(info)

    body = json.dumps({"templates": templates})
    return Response(body, mimetype="application/json")

@app.route("/thumbnail")
def thumbnail():
    pass

@app.route("/thumbnail/<path:name>")
def thumbnail_path(name):
    pass

@app.route("/tls")
def tls():
    names = [ name for name, *_ in store.get_templates() ] + [""]
    rows = "\r\n".join(names)
    body = f"200 TLS OK\r\n{rows}\r\n"
    return Response(body, mimetype="text/plain")

if __name__ == "__main__":
    scanner = Scanner(config, store)
    scanner.crawl()
    scanner.monitor()

    print(f"[main] Listening on {config.http_addr}:{config.http_port}")
    serve(app, host=config.http_addr, port=config.http_port)
