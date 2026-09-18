import sqlite3
import threading

from config import Config

schema = """
CREATE TABLE IF NOT EXISTS font (
    name TEXT PRIMARY KEY,
    path TEXT NOT NULL
);
"""

class Store:
    def __init__(self, config):
        self._lock = threading.Lock()
        self._db = sqlite3.connect(config.db_path, check_same_thread=False)
        self._db.executescript(schema)

    def _add_fonts(self, fonts):
        self._db.executemany("INSERT OR REPLACE INTO font (name, path) VALUES (?, ?)", fonts)

    def _remove_fonts(self, names):
        self._db.executemany("DELETE FROM font WHERE name = ?", [(name,) for name in names])

    def add_fonts(self, fonts):
        with self._lock:
            with self._db:
                self._add_fonts(fonts)

    def remove_fonts(self, names):
        with self._lock:
            with self._db:
                self._remove_fonts(names)

    def add_remove_fonts(self, add_fonts, remove_names):
        with self._lock:
            with self._db:
                self._add_fonts(add_fonts)
                self._remove_fonts(remove_names)

    def get_fonts(self):
        with self._lock:
            return self._db.execute("SELECT name, path FROM font ORDER BY name ASC").fetchall()
