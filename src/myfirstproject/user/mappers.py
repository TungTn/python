from myfirstproject.user.models import User
from myfirstproject.api.schemas import UserCreate, UserOut

def to_domain(payload: UserCreate) -> User:
  return User(name=payload.name, age=payload.age, is_dev=payload.is_dev, email=str(payload.email))

def to_out(user_id: int, user: User) -> UserOut:
  return UserOut(id=user_id, name=user.name, age=user.age, is_dev=user.is_dev, email=user.email)