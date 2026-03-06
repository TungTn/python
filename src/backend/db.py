from pathlib import Path
import sqlite3

DEFAULT_DB_PATH = Path("data/app.db")

def get_conn(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
  db_path.parent.mkdir(parents=True, exist_ok=True)
  conn = sqlite3.connect(db_path)
  conn.row_factory = sqlite3.Row
  return conn
