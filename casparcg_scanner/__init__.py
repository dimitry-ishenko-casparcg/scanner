__version__ = "0.2"

import base64, json, os

from flask import Flask, Response
from pathlib import Path
from .store import Store

app = Flask(__name__)

db_path = os.environ.get("SCANNER_DB_PATH")
store = Store(Path(db_path) if db_path else None)

@app.route("/cinf/<path:name>")
def cinf_path(name):
    if cinf := store.get_media_cinf(name.upper()):
        body = f"201 CINF OK\r\n{cinf}\r\n"
        return Response(body, mimetype="text/plain")
    return Response(status=404)

@app.route("/cls")
def cls():
    rows = "\r\n".join(store.get_media_cinfs() + [""])
    body = f"200 CLS OK\r\n{rows}\r\n"
    return Response(body, mimetype="text/plain")

@app.route("/fls")
def fls():
    rows = "\r\n".join(store.get_font_names() + [""])
    body = f"200 FLS OK\r\n{rows}\r\n"
    return Response(body, mimetype="text/plain")

@app.route("/media")
def media():
    body = "[" + ",".join(store.get_media_infos()) + "]"
    return Response(body, mimetype="application/json")

@app.route("/media/info/<path:name>")
def media_info_path(name):
    if info := store.get_media_info(name.upper()):
        return Response(info, mimetype="application/json")
    return Response(status=404)

@app.route("/media/thumbnail/<path:name>")
def media_thumbnail_path(name):
    if image := store.get_media_thumbnail(name.upper()):
        return Response(image, mimetype="image/png")
    return Response(status=404)

@app.route("/templates")
def templates():
    def make(name, path, type_, gdd):
        tmpl = { "id": name, "path": path, "type": type_ }
        if gdd: tmpl["gdd"] = json.loads(gdd)
        return tmpl
    templates = [ make(*tmpl) for tmpl in store.get_templates() ]

    body = json.dumps({ "templates": templates })
    return Response(body, mimetype="application/json")

@app.route("/thumbnail")
def thumbnail():
    rows = "\r\n".join(store.get_media_tinfs() + [""])
    body = f"200 THUMBNAIL LIST OK\r\n{rows}\r\n"
    return Response(body, mimetype="text/plain")

@app.route("/thumbnail/<path:name>")
def thumbnail_path(name):
    if image := store.get_media_thumbnail(name.upper()):
        image = base64.b64encode(image).decode("utf8")
        body = f"201 THUMBNAIL RETRIEVE OK\r\n{image}\r\n"
        return Response(body, mimetype="text/plain")
    return Response(status=404)

@app.route("/tls")
def tls():
    rows = "\r\n".join(store.get_template_names() + [""])
    body = f"200 TLS OK\r\n{rows}\r\n"
    return Response(body, mimetype="text/plain")
