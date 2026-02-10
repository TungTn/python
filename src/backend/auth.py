from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "CHANGE_ME_TO_ENV_LATER"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def hash_password(password: str) -> str:
  return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
  return pwd_context.verify(password, password_hash)

def create_access_token(subject: str) -> str:
  expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  payload = {"sub": subject, "exp": expire}
  return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)