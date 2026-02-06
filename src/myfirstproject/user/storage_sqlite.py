from pathlib import Path
from typing import Optional
import sqlite3
from myfirstproject.user.models import User

DB_PATH = Path("data/app.db")

def get_conn(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: Path = DB_PATH) -> None:
    sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            is_dev INTEGER NOT NULL DEFAULT 0,
            email TEXT NOT NULL UNIQUE
        )
    """
    with get_conn(db_path) as conn:
        conn.execute(sql)

def build_where(q: str | None, is_dev: bool | None, min_age: int | None, max_age: int | None):
    where = []
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

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    return where_sql, params

def create_user(user: User, *, db_path: Path = DB_PATH) -> int:
    sql = """
        INSERT INTO users (name, age, is_dev, email)
        VALUES (?, ?, ?, ?)
    """
    params = (user.name, user.age, 1 if user.is_dev else 0, user.email)
    with get_conn(db_path) as conn:
        cur = conn.execute(sql, params)
        return int(cur.lastrowid)

def get_user(user_id: int, *, db_path: Path = DB_PATH) -> Optional[tuple[int, User]]:
    sql = "SELECT id, name, age, is_dev, email FROM users WHERE id = ?"
    with get_conn(db_path) as conn:
        row = conn.execute(sql, (user_id,)).fetchone()
    if row is None:
        return None
    user = User(name=row["name"], age=int(row["age"]), is_dev=bool(row["is_dev"]), email=row["email"])
    return int(row["id"]), user

def update_user(user_id: int, user: User, *, db_path: Path = DB_PATH) -> bool:
    sql = """
        UPDATE users
        SET name = ?, age = ?, is_dev = ?, email = ?
        WHERE id = ?
    """
    params = (user.name, user.age, 1 if user.is_dev else 0, user.email, user_id)
    with get_conn(db_path) as conn:
        cur = conn.execute(sql, params)
    return cur.rowcount > 0

def delete_user(user_id: int, *, db_path: Path = DB_PATH) -> bool:
    sql = "DELETE FROM users WHERE id = ?"
    with get_conn(db_path) as conn:
        cur = conn.execute(sql, (user_id,))
    return cur.rowcount > 0

def count_users(*, q=None, is_dev=None, min_age=None, max_age=None, db_path: Path = DB_PATH) -> int:
    where_sql, params = build_where(q, is_dev, min_age, max_age)
    sql = f"SELECT COUNT(*) AS c FROM users {where_sql}"
    with get_conn(db_path) as conn:
        row = conn.execute(sql, params).fetchone()
    return int(row["c"])

def list_users(
    *,
    q: str | None = None,
    is_dev: bool | None = None,
    min_age: int | None = None,
    max_age: int | None = None,
    page: int = 1,
    page_size: int = 10,
    sort: str = "id",
    order: str = "desc",
    db_path: Path = DB_PATH,
) -> list[tuple[int, User]]:
    allowed_sort = {"id", "age", "name", "email"}
    if sort not in allowed_sort:
        sort = "id"
    order = "asc" if order.lower() == "asc" else "desc"

    where_sql, params = build_where(q, is_dev, min_age, max_age)
    limit = page_size
    offset = (page - 1) * page_size

    sql = f"""
        SELECT id, name, age, is_dev, email
        FROM users
        {where_sql}
        ORDER BY {sort} {order}
        LIMIT ? OFFSET ?
    """
    params += [limit, offset]

    with get_conn(db_path) as conn:
        rows = conn.execute(sql, params).fetchall()

    return [
        (int(r["id"]), User(name=r["name"], age=int(r["age"]), is_dev=bool(r["is_dev"]), email=r["email"]))
        for r in rows
    ]
