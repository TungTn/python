from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
  username: str = Field(min_length=1)
  email: EmailStr
  first_name: str | None = None
  last_name: str | None = None
  password: str = Field(min_length=1)


class KeycloakConfigResponse(BaseModel):
  realm: str
  client_id: str
