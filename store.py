import sqlite3
import threading

from config import Config
from typing import Any

schema = """
CREATE TABLE IF NOT EXISTS font (
    name TEXT PRIMARY KEY,
    path TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS media (
    name TEXT PRIMARY KEY,
    path TEXT NOT NULL,
    size INTEGER NOT NULL,
    time INTEGER NOT NULL,
    cinf TEXT,
    tinf TEXT,
    media_info TEXT,
    thumbnail BLOB
);

CREATE TABLE IF NOT EXISTS template (
    name TEXT PRIMARY KEY,
    path TEXT NOT NULL,
    type TEXT NOT NULL,
    gdd TEXT
);
"""

class Store:
    def __init__(self, config: Config):
        self._lock = threading.Lock()
        self._db = sqlite3.connect(config.db_path, check_same_thread=False)
        self._db.executescript(schema)

    def _add(self, table: str, fields: tuple[str, ...], item: tuple[Any, ...]):
        with self._lock, self._db:
            places = ",".join(["?"] * len(fields))
            fields = ",".join(fields)
            sql = f"INSERT OR REPLACE INTO {table} ({fields}) VALUES ({places})"
            self._db.execute(sql, item)

    def _remove(self, table: str, name: str):
        with self._lock, self._db:
            sql = f"DELETE FROM {table} WHERE name = ?"
            self._db.execute(sql, (name,))

    def _get(self, table: str, fields: tuple[str, ...], **match):
        with self._lock:
            fields = ",".join(fields)
            cond, params = "", []
            if match:
                cond = "WHERE " + (" AND ".join(f"{name} = ?" for name in match.keys()))
                params = list(match.values())
            sql = f"SELECT {fields} FROM {table} {cond} ORDER BY name ASC"
            return self._db.execute(sql, params).fetchall()

    def add_font(self, *args): self._add("font", ("name", "path"), args)
    def remove_font(self, name: str): self._remove("font", name)
    def get_fonts(self): return self._get("font", ("name", "path"))

    def add_media(self, *args):
        self._add("media", ("name", "path", "size", "time", "cinf", "tinf", "media_info", "thumbnail"), args)
    def remove_media(self, name: str): self._remove("media", name)

    def get_media_path(self): return self._get("media", ("path",))
    def get_media_stat(self, name: str): return self._get("media", ("size", "time"), name=name)

    def get_media_cinf(self, name: str = None):
        if name:
            rows = self._get("media", ("cinf",), name=name)
            return rows[0][0] if rows else None
        return self._get("media", ("cinf",))

    def get_media_info(self, name: str = None):
        if name:
            rows = self._get("media", ("media_info",), name=name)
            return rows[0][0] if rows else None
        return self._get("media", ("media_info",))

    def get_media_tinf(self): return self._get("media", ("tinf",))
    def get_media_thumbnail(self, name: str):
        rows = self._get("media", ("thumbnail",), name=name)
        return rows[0][0] if rows else None

    def add_template(self, *args):
        self._add("template", ("name", "path", "type", "gdd"), args)
    def remove_template(self, name: str): self._remove("template", name)
    def get_templates(self): return self._get("template", ("name", "path", "type", "gdd"))
