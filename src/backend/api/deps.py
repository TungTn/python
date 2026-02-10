from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import sqlite3
from uuid import UUID
from backend.auth import SECRET_KEY, ALGORITHM
from backend.db import get_db

security = HTTPBearer()

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    conn: sqlite3.Connection = Depends(get_db),
):
  token = creds.credentials
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get("sub")
    if not user_id:
      raise HTTPException(status_code=401, detail="Invalid token")
  except JWTError:
    raise HTTPException(status_code=401, detail="Invalid token")

  row = conn.execute(
    """
    SELECT id, name, email, is_dev
    FROM users
    WHERE id = ? AND deleted_at IS NULL
    """,
    (user_id,),
  ).fetchone()

  if not row:
    raise HTTPException(status_code=404, detail="User not found")

  return {
    "id": row["id"],
    "name": row["name"],
    "email": row["email"],
    "is_dev": bool(row["is_dev"]),
  }