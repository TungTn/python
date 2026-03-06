from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.keycloak import decode_token, extract_roles

security = HTTPBearer()

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
):
  token = creds.credentials
  try:
    payload = decode_token(token)
  except ValueError:
    raise HTTPException(status_code=401, detail="Invalid token")

  subject = payload.get("sub")
  if not subject:
    raise HTTPException(status_code=401, detail="Invalid token")

  roles = extract_roles(payload)
  return {
    "sub": subject,
    "email": payload.get("email"),
    "roles": roles,
    "name": payload.get("name"),
  }

def require_roles(required: set[str]):
  def _checker(user = Depends(get_current_user)):
    roles = set(user.get("roles") or [])
    if not roles.intersection(required):
      raise HTTPException(status_code=403, detail="Insufficient role")
    return user
  return _checker
