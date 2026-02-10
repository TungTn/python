import re
from pydantic import BaseModel, EmailStr, Field, field_validator

class RegisterRequest(BaseModel):
  email: EmailStr
  password: str
  name: str = Field(min_length=1)
  age: int = Field(ge=0)

  @field_validator("password")
  @classmethod
  def validate_password(cls, value: str) -> str:
    if len(value) >= 20:
      raise ValueError("Password must be shorter than 20 characters")
    if sum(1 for ch in value if ch.islower()) < 4:
      raise ValueError("Password must include at least 4 lowercase letters")
    if not any(ch.isupper() for ch in value):
      raise ValueError("Password must include at least 1 uppercase letter")
    if not re.search(r"[^A-Za-z0-9]", value):
      raise ValueError("Password must include at least 1 special character")
    return value

class LoginRequest(BaseModel):
  email: EmailStr
  password: str

class TokenResponse(BaseModel):
  access_token: str
  token_type: str = "bearer"
