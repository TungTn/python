import sqlite3
from myfirstproject.user.models import User
from myfirstproject.user import storage_sqlite as repo

def create(conn: sqlite3.Connection, user: User) -> int:
  # chỗ này về sau bạn thêm business rules (check age range, normalize email...)
  return repo.create_user(conn, user)

def get(conn: sqlite3.Connection, user_id: int):
  return repo.get_user(conn, user_id)

def update(conn: sqlite3.Connection, user_id: int, user: User) -> bool:
  return repo.update_user(conn, user_id, user)

def delete(conn: sqlite3.Connection, user_id: int) -> bool:
  return repo.delete_user(conn, user_id)

def list_and_count(conn: sqlite3.Connection, **kwargs):
  total = repo.count_users(conn, q=kwargs.get("q"), is_dev=kwargs.get("is_dev"),
                           min_age=kwargs.get("min_age"), max_age=kwargs.get("max_age"))
  items = repo.list_users(conn, **kwargs)
  return total, items