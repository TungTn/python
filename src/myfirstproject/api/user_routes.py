import sqlite3
from fastapi import APIRouter, HTTPException, Query
from myfirstproject.api.schemas import UserCreate, UserOut, Page
from myfirstproject.user.mappers import to_out
from myfirstproject.user.models import User
from myfirstproject.user import storage_sqlite as repo

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/batch", response_model=list[UserOut])
def create_batch(payload: list[UserCreate]):
  try:
    created: list[UserOut] = []
    for p in payload:
      user = User(name=p.name, age=p.age, is_dev=p.is_dev, email=str(p.email))
      new_id = repo.create_user(user)
      created.append(UserOut(id=new_id, **p.model_dump()))
    return created
  except sqlite3.IntegrityError:
    raise HTTPException(status_code=409, detail="Email already exists")

@router.post("", response_model=UserOut)
def create(payload: UserCreate):
  try:
    user = User(name=payload.name, age=payload.age, is_dev=payload.is_dev, email=payload.email)
    new_id = repo.create_user(user)
    return {"id": new_id, **payload.model_dump()}
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
):
  total = repo.count_users(q=q, is_dev=is_dev, min_age=min_age, max_age=max_age)
  rows = repo.list_users(q=q, is_dev=is_dev, min_age=min_age, max_age=max_age, page=page, page_size=page_size, sort=sort, order=order)
  items = [to_out(uid, u) for uid, u in rows]
  return Page[UserOut](total=total, page=page, page_size=page_size, items=items)

@router.get("/{user_id}", response_model=UserOut)
def get_one(user_id: int):
  result = repo.get_user(user_id)
  if result is None:
    raise HTTPException(status_code=404, detail="User not found")
  uid, u = result
  return {"id": uid, "name": u.name, "age": u.age, "is_dev": u.is_dev, "email": u.email}


@router.put("/{user_id}", response_model=UserOut)
def update_one(user_id: int, payload: UserCreate):
  user = User(name=payload.name, age=payload.age, is_dev=payload.is_dev, email=payload.email)
  ok = repo.update_user(user_id, user)
  if not ok:
    raise HTTPException(status_code=404, detail="User not found")
  return {"id": user_id, **payload.model_dump()}


@router.delete("/{user_id}")
def delete_one(user_id: int):
  ok = repo.delete_user(user_id)
  if not ok:
    raise HTTPException(status_code=404, detail="User not found")
  return {"deleted": True, "id": user_id}
