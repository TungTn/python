import sqlite3
from uuid import UUID
from backend.user.models import User
from backend.user.repository_sqlite import SqliteUserRepository

def create_user_service(conn: sqlite3.Connection, user: User) -> UUID:
  repo = SqliteUserRepository(conn)
  uid = repo.create(user)
  conn.commit()
  return uid

def create_users_batch_service(conn: sqlite3.Connection, users: list[User]) -> list[UUID]:
  repo = SqliteUserRepository(conn)
  try:
    conn.execute("BEGIN")
    ids = [repo.create(u) for u in users]
    conn.commit()
    return ids
  except sqlite3.IntegrityError:
    conn.rollback()
    raise

def soft_delete_user_service(conn: sqlite3.Connection, user_id: UUID) -> bool:
  repo = SqliteUserRepository(conn)
  ok = repo.soft_delete(user_id)
  conn.commit()
  return ok