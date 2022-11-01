import sqlite3
from pathlib import Path


def get_db_path() -> Path:
    return Path(__file__).parent / "library.db"


def get_db_connection():
    return sqlite3.connect(get_db_path().__str__(), check_same_thread=False)
