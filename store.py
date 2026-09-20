import sqlite3
import threading

from collections.abc import Iterable
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

    def _add(self, table: str, fields: tuple[str, ...], items: Iterable[tuple[Any, ...]]):
        with self._lock, self._db:
            places = ",".join(["?"] * len(fields))
            fields = ",".join(fields)
            sql = f"INSERT OR REPLACE INTO {table} ({fields}) VALUES ({places})"
            self._db.executemany(sql, items)

    def _remove(self, table: str, names: Iterable[str]):
        with self._lock, self._db:
            sql = f"DELETE FROM {table} WHERE name = ?"
            self._db.executemany(sql, [(name,) for name in names])

    def _get(self, table: str, fields: tuple[str, ...], **match):
        with self._lock:
            fields = ",".join(fields)
            cond, params = "", []
            if match:
                cond = "WHERE " + (" AND ".join(f"{name} = ?" for name in match.keys()))
                params = list(match.values())
            sql = f"SELECT {fields} FROM {table} {cond} ORDER BY name ASC"
            return self._db.execute(sql, params).fetchall()

    def add_fonts(self, items: Iterable[tuple[Any, ...]]): self._add("font", ("name", "path"), items)
    def remove_fonts(self, names: Iterable[str]): self._remove("font", names)
    def get_fonts(self): return self._get("font", ("name", "path"))

    def add_media(self, items: Iterable[tuple[Any, ...]]):
        self._add("media", ("name", "path", "size", "time", "cinf", "tinf", "media_info", "thumbnail"), items)
    def remove_media(self, names: Iterable[str]): self._remove("media", names)
    def get_media(self): return self._get("media", ("name", "path", "size", "time"))

    def get_media_cinf(self, name: str = None):
        if name:
            rows = self._get("media", ("cinf",), name=name)
            return rows[0][0] if rows else None
        return self._get("media", ("cinf",))

    def add_templates(self, items: Iterable[tuple[Any, ...]]):
        self._add("template", ("name", "path", "type", "gdd"), items)
    def remove_templates(self, names: Iterable[str]): self._remove("template", names)
    def get_templates(self): return self._get("template", ("name", "path", "type", "gdd"))
