from pathlib import Path
import sqlite3

MIGRATIONS_DIR = Path(__file__).parent / "migrations"

def ensure_migrations_table(conn: sqlite3.Connection) -> None:
  conn.execute("""
               CREATE TABLE IF NOT EXISTS schema_migrations (
                                                                version TEXT PRIMARY KEY
               )
               """)
  conn.commit()

def applied_versions(conn: sqlite3.Connection) -> set[str]:
  ensure_migrations_table(conn)
  rows = conn.execute("SELECT version FROM schema_migrations").fetchall()
  return {r[0] for r in rows}

def _has_column(conn: sqlite3.Connection, table: str, col: str) -> bool:
  rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
  return any(r[1] == col for r in rows)

def apply_migrations(conn: sqlite3.Connection) -> None:
  done = applied_versions(conn)

  files = sorted(MIGRATIONS_DIR.glob("*.sql"))
  for f in files:
    version = f.name.split("_")[0]
    if version in done:
      continue
    if version == "0002" and _has_column(conn, "users", "deleted_at"):
      conn.execute("INSERT INTO schema_migrations(version) VALUES(?)", (version,))
      conn.commit()
      continue
    sql = f.read_text(encoding="utf-8")
    if sql.strip():
      if "deleted_at" in sql and not _has_column(conn, "users", "deleted_at"):
        conn.execute("ALTER TABLE users ADD COLUMN deleted_at TEXT NULL")
      conn.executescript(sql)
    conn.execute("INSERT INTO schema_migrations(version) VALUES(?)", (version,))
    conn.commit()

  # migration đặc biệt cho SQLite: thêm deleted_at nếu chưa có
  if not _has_column(conn, "users", "deleted_at"):
    conn.execute("ALTER TABLE users ADD COLUMN deleted_at TEXT NULL")
    conn.commit()
