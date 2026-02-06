from pathlib import Path
import sqlite3
from fastapi import Depends

DEFAULT_DB_PATH = Path("data/app.db")

def get_conn(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
  db_path.parent.mkdir(parents=True, exist_ok=True)
  conn = sqlite3.connect(db_path)
  conn.row_factory = sqlite3.Row
  return conn

def init_db(conn: sqlite3.Connection) -> None:
  conn.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
                                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                                         name TEXT NOT NULL,
                                         age INTEGER NOT NULL CHECK(age >= 0),
        is_dev INTEGER NOT NULL DEFAULT 0,
        email TEXT NOT NULL UNIQUE
        );
    """
  )
  conn.commit()

def get_db():
  conn = get_conn()
  try:
    yield conn
  finally:
    conn.close()