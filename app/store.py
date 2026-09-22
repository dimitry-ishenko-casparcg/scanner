import sqlite3
import threading

from pathlib import Path

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
    def __init__(self, db_path: Path = None):
        self._lock = threading.Lock()
        self.connect(db_path)

    def connect(self, db_path: Path):
        if getattr(self, "_db", None):
            self._db.close()
            del self._db
        if db_path:
            self._db = sqlite3.connect(db_path, check_same_thread=False)
            self._db.executescript(schema)

    def _add(self, table: str, fields: tuple, item: tuple):
        with self._lock, self._db:
            places = ",".join(["?"] * len(fields))
            fields = ",".join(fields)
            sql = f"INSERT OR REPLACE INTO {table} ({fields}) VALUES ({places})"
            self._db.execute(sql, item)

    def _remove(self, table: str, name: str):
        with self._lock, self._db:
            sql = f"DELETE FROM {table} WHERE name = ?"
            self._db.execute(sql, (name,))

    def _get(self, table: str, fields: tuple, **match):
        with self._lock:
            fields = ",".join(fields)
            cond, params = "", []
            if match:
                cond = "WHERE " + (" AND ".join(f"{name} = ?" for name in match.keys()))
                params = list(match.values())
            sql = f"SELECT {fields} FROM {table} {cond} ORDER BY name ASC"
            return self._db.execute(sql, params).fetchall()

    ####################
    def add_font(self, name: str, path: str): self._add("font", ("name", "path"), (name, path))
    def remove_font(self, name: str): self._remove("font", name)
    def get_font_names(self): return [ name for name, in self._get("font", ("name",)) ]
    def get_font_paths(self): return [ path for path, in self._get("font", ("path",)) ]

    ####################
    def add_media(self, name: str, path: str, size: int, time: float,
        cinf: str, tinf: str, media_info: str, thumbnail: bytes):
        self._add("media", ("name", "path", "size", "time", "cinf", "tinf", "media_info", "thumbnail"),
            (name, path, size, time, cinf, tinf, media_info, thumbnail)
        )
    def remove_media(self, name: str): self._remove("media", name)

    def get_media_size_time(self, name: str):
        rows = self._get("media", ("size", "time"), name=name)
        return rows[0] if rows else None
    def get_media_paths(self): return [ path for path, in self._get("media", ("path",)) ]

    def get_media_cinf(self, name: strNone):
        rows = self._get("media", ("cinf",), name=name)
        return rows[0][0] if rows else None
    def get_media_cinfs(self): return [ cinf for cinf, in self._get("media", ("cinf",)) if cinf ]

    def get_media_info(self, name: strNone):
        rows = self._get("media", ("media_info",), name=name)
        return rows[0][0] if rows else None
    def get_media_infos(self): return [ info for info, in self._get("media", ("media_info",)) if info ]

    def get_media_tinfs(self): return [ tinf for tinf, in self._get("media", ("tinf",)) if tinf ]
    def get_media_thumbnail(self, name: str):
        rows = self._get("media", ("thumbnail",), name=name)
        return rows[0][0] if rows else None

    ####################
    def add_template(self, name: str, path: str, type_: str, gdd: str):
        self._add("template", ("name", "path", "type", "gdd"), (name, path, type_, gdd))
    def remove_template(self, name: str): self._remove("template", name)
    def get_templates(self): return self._get("template", ("name", "path", "type", "gdd"))

    def get_template_names(self): return [ name for name, in self._get("template", ("name",)) ]
    def get_template_paths(self): return [ path for path, in self._get("template", ("path",)) ]
