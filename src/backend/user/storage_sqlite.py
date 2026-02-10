from pathlib import Path
import sqlite3
from uuid import UUID
from uuid6 import uuid7
from backend.user.models import User

DB_PATH = Path("data/app.db")

def get_conn(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: Path = DB_PATH) -> None:
    sql = """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL CHECK(age >= 0),
            is_dev INTEGER NOT NULL DEFAULT 0,
            email TEXT NOT NULL UNIQUE
        )
    """
    with get_conn(db_path) as conn:
        conn.execute(sql)
        conn.commit()

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

def create_user(conn: sqlite3.Connection, user: User) -> UUID:
    user_id = uuid7()
    conn.execute(
        """
        INSERT INTO users (id, name, age, is_dev, email)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            str(user_id),
            user.name,
            user.age,
            int(user.is_dev),
            user.email,
        ),
    )
    conn.commit()
    return user_id

def get_user(conn: sqlite3.Connection, user_id: UUID):
    row = conn.execute(
        "SELECT id, name, age, is_dev, email FROM users WHERE id = ?",
        (str(user_id),),
    ).fetchone()

    if not row:
        return None

    return (
        UUID(row[0]),
        User(
            name=row[1],
            age=row[2],
            is_dev=bool(row[3]),
            email=row[4],
        ),
    )

def update_user(conn: sqlite3.Connection, user_id: UUID, user: User) -> bool:
    sql = """
        UPDATE users
        SET name = ?, age = ?, is_dev = ?, email = ?
        WHERE id = ?
    """
    params = (user.name, user.age, 1 if user.is_dev else 0, user.email, str(user_id))
    cur = conn.execute(sql, params)
    conn.commit()
    return cur.rowcount > 0

def delete_user(conn: sqlite3.Connection, user_id: UUID) -> bool:
    sql = "DELETE FROM users WHERE id = ?"
    cur = conn.execute(sql, (str(user_id),))
    conn.commit()
    return cur.rowcount > 0

def count_users(
    conn: sqlite3.Connection,
    *,
    q=None,
    is_dev=None,
    min_age=None,
    max_age=None,
) -> int:
    where_sql, params = build_where(q, is_dev, min_age, max_age)
    sql = f"SELECT COUNT(*) AS c FROM users {where_sql}"
    row = conn.execute(sql, params).fetchone()
    return int(row["c"])

def list_users(
    conn: sqlite3.Connection,
    *,
    q: str | None = None,
    is_dev: bool | None = None,
    min_age: int | None = None,
    max_age: int | None = None,
    page: int = 1,
    page_size: int = 10,
    sort: str = "id",
    order: str = "desc",
) -> list[tuple[UUID, User]]:
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

    rows = conn.execute(sql, params).fetchall()

    return [
        (UUID(r["id"]), User(name=r["name"], age=int(r["age"]), is_dev=bool(r["is_dev"]), email=r["email"]))
        for r in rows
    ]
