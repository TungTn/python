from pathlib import Path
import sqlite3
from uuid import UUID
from uuid6 import uuid7
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
    CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, 
                                      name TEXT NOT NULL, 
                                      age INTEGER NOT NULL CHECK(age >= 0), 
                                      is_dev INTEGER NOT NULL DEFAULT 0, 
                                      email TEXT NOT NULL UNIQUE);
    """
  )
  _migrate_legacy_user_ids(conn)
  conn.commit()

def _needs_uuid(value) -> bool:
  try:
    UUID(str(value))
  except (ValueError, TypeError):
    return True
  return False

def _migrate_legacy_user_ids(conn: sqlite3.Connection) -> None:
  columns = conn.execute("PRAGMA table_info(users)").fetchall()
  id_type = None
  for col in columns:
    if col[1] == "id":
      id_type = (col[2] or "").upper()
      break

  # If the table was created with INTEGER PRIMARY KEY, rebuild it as TEXT id.
  if id_type == "INTEGER":
    conn.execute(
      """
      CREATE TABLE users_new (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER NOT NULL CHECK(age >= 0),
        is_dev INTEGER NOT NULL DEFAULT 0,
        email TEXT NOT NULL UNIQUE
      )
      """
    )
    rows = conn.execute("SELECT id, name, age, is_dev, email FROM users").fetchall()
    for row in rows:
      new_id = uuid7()
      conn.execute(
        "INSERT INTO users_new (id, name, age, is_dev, email) VALUES (?, ?, ?, ?, ?)",
        (str(new_id), row[1], row[2], row[3], row[4]),
      )
    conn.execute("DROP TABLE users")
    conn.execute("ALTER TABLE users_new RENAME TO users")
    return

  rows = conn.execute("SELECT id FROM users").fetchall()
  for (user_id,) in rows:
    if _needs_uuid(user_id):
      new_id = uuid7()
      conn.execute("UPDATE users SET id = ? WHERE id = ?", (str(new_id), str(user_id)))

def get_db():
  conn = get_conn()
  try:
    yield conn
  finally:
    conn.close()
