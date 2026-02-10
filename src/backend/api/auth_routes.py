from fastapi import APIRouter, Depends, HTTPException
import sqlite3
from datetime import datetime, timezone
from backend.api.deps import get_current_user
from backend.db import get_db
from backend.api.auth_schemas import RegisterRequest, LoginRequest, TokenResponse
from backend.auth import hash_password, verify_password, create_access_token
from backend.user.models import User
from backend.user.repository_sqlite import SqliteUserRepository  # nếu bạn dùng repo class

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/me")
def me(current_user = Depends(get_current_user)):
  return current_user

@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, conn: sqlite3.Connection = Depends(get_db)):
  # check email exists
  existing = conn.execute("SELECT 1 FROM users WHERE email = ?", (str(payload.email),)).fetchone()
  if existing:
    raise HTTPException(status_code=409, detail="Email already exists")

  repo = SqliteUserRepository(conn)
  user = User(name=payload.name, age=payload.age, is_dev=False, email=str(payload.email))
  uid = repo.create(user)

  # set password_hash + created_at
  conn.execute(
    "UPDATE users SET password_hash = ?, created_at = ? WHERE id = ?",
    (hash_password(payload.password), datetime.now(timezone.utc).isoformat(), str(uid)),
  )
  conn.commit()

  token = create_access_token(str(uid))
  return TokenResponse(access_token=token)

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, conn: sqlite3.Connection = Depends(get_db)):
  row = conn.execute(
    "SELECT id, password_hash FROM users WHERE email = ? AND deleted_at IS NULL",
    (str(payload.email),),
  ).fetchone()

  if not row or not row["password_hash"]:
    raise HTTPException(status_code=401, detail="Invalid credentials")

  if not verify_password(payload.password, row["password_hash"]):
    raise HTTPException(status_code=401, detail="Invalid credentials")

  token = create_access_token(row["id"])
  return TokenResponse(access_token=token)