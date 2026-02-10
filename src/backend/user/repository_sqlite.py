import sqlite3
from uuid import UUID
from uuid6 import uuid7
from datetime import datetime, timezone
from backend.user.models import User

class SqliteUserRepository:
  def __init__(self, conn: sqlite3.Connection):
    self.conn = conn

  def create(self, user: User) -> UUID:
    uid = uuid7()
    self.conn.execute(
      "INSERT INTO users (id, name, age, is_dev, email, deleted_at) VALUES (?, ?, ?, ?, ?, NULL)",
      (str(uid), user.name, user.age, 1 if user.is_dev else 0, user.email),
    )
    return uid

  def get(self, user_id: UUID, include_deleted: bool = False):
    where = "" if include_deleted else "AND deleted_at IS NULL"
    row = self.conn.execute(
      f"SELECT id, name, age, is_dev, email FROM users WHERE id = ? {where}",
      (str(user_id),),
    ).fetchone()
    if not row:
      return None
    return (
      UUID(row["id"]),
      User(name=row["name"], age=int(row["age"]), is_dev=bool(row["is_dev"]), email=row["email"]),
    )

  def soft_delete(self, user_id: UUID) -> bool:
    now = datetime.now(timezone.utc).isoformat()
    cur = self.conn.execute(
      "UPDATE users SET deleted_at=? WHERE id=? AND deleted_at IS NULL",
      (now, str(user_id)),
    )
    return cur.rowcount > 0

  def update(self, user_id: UUID, user: User) -> bool:
    cur = self.conn.execute(
      """
      UPDATE users
      SET name = ?, age = ?, is_dev = ?, email = ?
      WHERE id = ? AND deleted_at IS NULL
      """,
      (user.name, user.age, 1 if user.is_dev else 0, user.email, str(user_id)),
    )
    return cur.rowcount > 0

  def count(self, *, q=None, is_dev=None, min_age=None, max_age=None) -> int:
    where = ["deleted_at IS NULL"]
    params: list[object] = []

    if q:
      where.append("(name LIKE ? OR email LIKE ?)")
      like = f"%{q}%"
      params += [like, like]
    if is_dev is not None:
      where.append("is_dev = ?")
      params.append(1 if is_dev else 0)
    if min_age is not None:
      where.append("age >= ?")
      params.append(min_age)
    if max_age is not None:
      where.append("age <= ?")
      params.append(max_age)

    where_sql = "WHERE " + " AND ".join(where)
    row = self.conn.execute(f"SELECT COUNT(*) AS c FROM users {where_sql}", params).fetchone()
    return int(row["c"])

  def list_page(self, *, q=None, is_dev=None, min_age=None, max_age=None,
                page=1, page_size=10, sort="id", order="desc"):
    allowed_sort = {"id", "age", "name", "email"}
    if sort not in allowed_sort:
      sort = "id"
    order = "asc" if str(order).lower() == "asc" else "desc"

    where = ["deleted_at IS NULL"]
    params: list[object] = []

    if q:
      where.append("(name LIKE ? OR email LIKE ?)")
      like = f"%{q}%"
      params += [like, like]
    if is_dev is not None:
      where.append("is_dev = ?")
      params.append(1 if is_dev else 0)
    if min_age is not None:
      where.append("age >= ?")
      params.append(min_age)
    if max_age is not None:
      where.append("age <= ?")
      params.append(max_age)

    where_sql = "WHERE " + " AND ".join(where)
    limit = page_size
    offset = (page - 1) * page_size

    rows = self.conn.execute(
      f"""
            SELECT id, name, age, is_dev, email
            FROM users
            {where_sql}
            ORDER BY {sort} {order}
            LIMIT ? OFFSET ?
            """,
      params + [limit, offset],
      ).fetchall()

    return [
      (UUID(r["id"]), User(name=r["name"], age=int(r["age"]), is_dev=bool(r["is_dev"]), email=r["email"]))
      for r in rows
    ]

  # Cursor pagination (UUIDv7)
  def list_cursor(self, *, limit=20, after: UUID | None = None,
                  q=None, is_dev=None, min_age=None, max_age=None):
    where = ["deleted_at IS NULL"]
    params: list[object] = []

    if after:
      where.append("id > ?")
      params.append(str(after))

    if q:
      where.append("(name LIKE ? OR email LIKE ?)")
      like = f"%{q}%"
      params += [like, like]
    if is_dev is not None:
      where.append("is_dev = ?")
      params.append(1 if is_dev else 0)
    if min_age is not None:
      where.append("age >= ?")
      params.append(min_age)
    if max_age is not None:
      where.append("age <= ?")
      params.append(max_age)

    where_sql = "WHERE " + " AND ".join(where)

    rows = self.conn.execute(
      f"""
            SELECT id, name, age, is_dev, email
            FROM users
            {where_sql}
            ORDER BY id ASC
            LIMIT ?
            """,
      params + [limit],
      ).fetchall()

    return [
      (UUID(r["id"]), User(name=r["name"], age=int(r["age"]), is_dev=bool(r["is_dev"]), email=r["email"]))
      for r in rows
    ]

  def find_by_email(conn: sqlite3.Connection, email: str):
    row = conn.execute(
      "SELECT id, name, age, is_dev, email, password_hash FROM users WHERE email = ? AND deleted_at IS NULL",
      (email,),
    ).fetchone()
    return row

  def set_password_hash(conn: sqlite3.Connection, user_id: str, password_hash: str):
    conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))