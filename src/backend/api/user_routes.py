import sqlite3
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from backend.api.schemas import UserCreate, UserOut, Page, CursorPage
from backend.user.mappers import to_out
from backend.user.models import User
from backend.user.service_api import (
  create_user_service,
  create_users_batch_service,
  soft_delete_user_service,
)
from backend.user.repository_sqlite import SqliteUserRepository
from backend.db import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/batch", response_model=list[UserOut])
def create_batch(payload: list[UserCreate], conn: sqlite3.Connection = Depends(get_db)):
  users = [User(name=p.name, age=p.age, is_dev=p.is_dev, email=str(p.email)) for p in payload]
  try:
    ids = create_users_batch_service(conn, users)
    return [UserOut(id=ids[i], **payload[i].model_dump()) for i in range(len(ids))]
  except sqlite3.IntegrityError:
    raise HTTPException(status_code=409, detail="Duplicate email in batch")

@router.post("", response_model=UserOut)
def create(payload: UserCreate, conn: sqlite3.Connection = Depends(get_db)):
  try:
    user = User(
      name=payload.name,
      age=payload.age,
      is_dev=payload.is_dev,
      email=payload.email,
    )
    user_id = create_user_service(conn, user)
    return {"id": user_id, **payload.model_dump()}
  except sqlite3.IntegrityError:
    raise HTTPException(status_code=409, detail="Email already exists")

@router.get("", response_model=Page[UserOut])
def list_all(
    q: str | None = None,
    is_dev: bool | None = None,
    min_age: int | None = None,
    max_age: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort: str = "id",
    order: str = "desc",
    conn: sqlite3.Connection = Depends(get_db),
):
  repo = SqliteUserRepository(conn)
  total = repo.count(q=q, is_dev=is_dev, min_age=min_age, max_age=max_age)
  rows = repo.list_page(q=q, is_dev=is_dev, min_age=min_age, max_age=max_age, page=page, page_size=page_size, sort=sort, order=order)
  items = [to_out(uid, u) for uid, u in rows]
  return Page[UserOut](total=total, page=page, page_size=page_size, items=items)

@router.get("/cursor", response_model=CursorPage[UserOut])
def list_cursor(
    conn: sqlite3.Connection = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    after: UUID | None = None,
    q: str | None = None,
    is_dev: bool | None = None,
    min_age: int | None = None,
    max_age: int | None = None,
):
  repo = SqliteUserRepository(conn)
  rows = repo.list_cursor(limit=limit, after=after, q=q, is_dev=is_dev, min_age=min_age, max_age=max_age)
  items = [to_out(uid, u) for uid, u in rows]
  next_after = rows[-1][0] if rows else None
  return {"items": items, "limit": limit, "next_after": next_after}

@router.get("/{user_id}", response_model=UserOut)
def get_one(user_id: UUID, conn: sqlite3.Connection = Depends(get_db)):
  repo = SqliteUserRepository(conn)
  result = repo.get(user_id)
  if result is None:
    raise HTTPException(status_code=404, detail="User not found")
  uid, u = result
  return {"id": uid, "name": u.name, "age": u.age, "is_dev": u.is_dev, "email": u.email}


@router.put("/{user_id}", response_model=UserOut)
def update_one(user_id: UUID, payload: UserCreate, conn: sqlite3.Connection = Depends(get_db)):
  user = User(name=payload.name, age=payload.age, is_dev=payload.is_dev, email=payload.email)
  repo = SqliteUserRepository(conn)
  ok = repo.update(user_id, user)
  conn.commit()
  if not ok:
    raise HTTPException(status_code=404, detail="User not found")
  return {"id": user_id, **payload.model_dump()}


@router.delete("/{user_id}")
def delete_one(user_id: UUID, conn: sqlite3.Connection = Depends(get_db)):
  ok = soft_delete_user_service(conn, user_id)
  if not ok:
    raise HTTPException(status_code=404, detail="User not found (or already deleted)")
  return {"deleted": True, "id": user_id}
