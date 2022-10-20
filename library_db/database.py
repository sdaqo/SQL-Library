import sqlite3
from pathlib import Path


def get_db_connection():
    db_path = Path(__file__).parent / "library.db"
    print(__file__)
    print(db_path)
    return sqlite3.connect(db_path.__str__(), check_same_thread=False)
