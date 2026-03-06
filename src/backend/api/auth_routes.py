from fastapi import APIRouter, Depends, HTTPException
from backend.api.deps import get_current_user
from backend.api.auth_schemas import KeycloakConfigResponse, RegisterRequest
from backend.apiBaseUrl import KEYCLOAK_CLIENT_ID, KEYCLOAK_REALM
from backend.keycloak_admin import create_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/config", response_model=KeycloakConfigResponse)
def keycloak_config():
  return {
    "realm": KEYCLOAK_REALM,
    "client_id": KEYCLOAK_CLIENT_ID,
  }

@router.get("/me")
def me(current_user = Depends(get_current_user)):
  return current_user

@router.post("/register")
def register(payload: RegisterRequest):
  body = {
    "username": payload.username,
    "email": payload.email,
    "firstName": payload.first_name or "",
    "lastName": payload.last_name or "",
    "enabled": True,
    "credentials": [
      {
        "type": "password",
        "value": payload.password,
        "temporary": False,
      }
    ],
  }
  try:
    user_id = create_user(body)
  except ValueError as exc:
    raise HTTPException(status_code=409, detail=str(exc)) from exc
  return {"id": user_id or payload.username}
