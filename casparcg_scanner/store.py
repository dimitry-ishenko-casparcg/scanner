import sqlite3
import threading

from pathlib import Path

schema = """
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
            try:
                self._db = sqlite3.connect(db_path, check_same_thread=False)
                self._db.executescript(schema)
            except sqlite3.Error as e: raise sqlite3.Error(f"{e} '{db_path}'")

    def add_media(self, name:str, path:str, size:int, time:float, cinf:str, tinf:str, media_info:str, thumbnail:bytes):
        with self._lock, self._db:
            sql = """
                INSERT OR REPLACE
                INTO media (name, path, size, time, cinf, tinf, media_info, thumbnail)
                VALUES (?,?,?,?,?,?,?,?)
            """
            self._db.execute(sql, (name, path, size, time, cinf, tinf, media_info, thumbnail))

    def remove_media(self, name: str):
        with self._lock, self._db:
            self._db.execute("DELETE FROM media WHERE name = ?", (name,))

    def get_media(self, *field, name: str = None):
        with self._lock:
            field = ",".join(field)
            if name is None:
                sql = f"SELECT {field} FROM media ORDER BY name ASC"
                return self._db.execute(sql).fetchall()
            else:
                sql = f"SELECT {field} FROM media WHERE name = ?"
                return self._db.execute(sql, (name,)).fetchone()
