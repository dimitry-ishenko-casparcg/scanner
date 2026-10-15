__version__ = "0.4.1"

import base64, json, os

from flask import Flask, Response
from pathlib import Path
from .scanner import FontScanner, MediaScanner, TemplateScanner
from .store import Store

app = Flask(__name__)

# used for testing flask endpoints, eg:
# SCANNER_DB_PATH=/path/to/scanner.db flask --app casparcg_scanner shell
db_path = os.environ.get("SCANNER_DB_PATH")
store = Store(Path(db_path) if db_path else None)

font = FontScanner()
mdia = MediaScanner(store)
tmpl = TemplateScanner()

@app.route("/cinf/<path:name>")
def cinf_path(name):
    if cinf := mdia.cinf(name.upper()):
        body = f"201 CINF OK\r\n{cinf}\r\n"
        return Response(body, mimetype="text/plain")
    return Response(status=404)

@app.route("/cls")
def cls():
    rows = "\r\n".join(mdia.cinfs() + [""])
    body = f"200 CLS OK\r\n{rows}\r\n"
    return Response(body, mimetype="text/plain")

@app.route("/fls")
def fls():
    rows = "\r\n".join(font.names() + [""])
    body = f"200 FLS OK\r\n{rows}\r\n"
    return Response(body, mimetype="text/plain")

@app.route("/media")
def media():
    body = "[" + ",".join(mdia.infos()) + "]"
    return Response(body, mimetype="application/json")

@app.route("/media/info/<path:name>")
def media_info_path(name):
    if info := mdia.info(name.upper()):
        return Response(info, mimetype="application/json")
    return Response(status=404)

@app.route("/media/thumbnail/<path:name>")
def media_thumbnail_path(name):
    if image := mdia.thumbnail(name.upper()):
        return Response(image, mimetype="image/png")
    return Response(status=404)

@app.route("/templates")
def templates():
    body = json.dumps({ "templates": tmpl.templates() })
    return Response(body, mimetype="application/json")

@app.route("/thumbnail")
def thumbnail():
    rows = "\r\n".join(mdia.tinfs() + [""])
    body = f"200 THUMBNAIL LIST OK\r\n{rows}\r\n"
    return Response(body, mimetype="text/plain")

@app.route("/thumbnail/<path:name>")
def thumbnail_path(name):
    if image := mdia.thumbnail(name.upper()):
        image = base64.b64encode(image).decode("utf8")
        body = f"201 THUMBNAIL RETRIEVE OK\r\n{image}\r\n"
        return Response(body, mimetype="text/plain")
    return Response(status=404)

@app.route("/tls")
def tls():
    rows = "\r\n".join(tmpl.names() + [""])
    body = f"200 TLS OK\r\n{rows}\r\n"
    return Response(body, mimetype="text/plain")
