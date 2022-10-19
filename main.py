import sqlite3
from flask import Flask
from pathlib import Path


app = Flask.
def init_db(file_path: Path):
  con = sqlite3.connect(file_path.__str__())
  return con.cursor()
