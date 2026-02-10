from pydantic import BaseModel, Field, EmailStr
from typing import Generic, TypeVar
from uuid import UUID

class UserCreate(BaseModel):
  name: str = Field(min_length=1)
  age: int = Field(ge=0)
  is_dev: bool = False
  email: EmailStr

class UserOut(BaseModel):
  id: UUID
  name: str
  age: int
  is_dev: bool
  email: EmailStr | None = None

T = TypeVar("T")

class Page(BaseModel, Generic[T]):
  total: int
  page: int
  page_size: int
  items: list[T]

class CursorPage(BaseModel, Generic[T]):
  items: list[T]
  limit: int
  next_after: UUID | None = None