from pydantic import BaseModel, Field, EmailStr
from typing import Generic, TypeVar

class UserCreate(BaseModel):
  name: str = Field(min_length=1)
  age: int = Field(ge=0)
  is_dev: bool = False
  email: EmailStr

class UserOut(UserCreate):
  id: int

T = TypeVar("T")

class Page(BaseModel, Generic[T]):
  total: int
  page: int
  page_size: int
  items: list[T]