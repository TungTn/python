import time
from typing import Any

import httpx
from jose import jwt, JWTError
from backend.apiBaseUrl import (
  KEYCLOAK_AUDIENCE,
  KEYCLOAK_BASE_URL,
  KEYCLOAK_CLIENT_ID,
  KEYCLOAK_CLIENT_SECRET,
  KEYCLOAK_JWKS_CACHE_SEC,
  KEYCLOAK_REALM,
  KEYCLOAK_VERIFY_SSL,
)

_jwks_cache: dict[str, Any] | None = None
_jwks_cache_time: float = 0.0

def _realm_url(path: str) -> str:
  base = KEYCLOAK_BASE_URL.rstrip("/")
  realm = KEYCLOAK_REALM.strip("/")
  return f"{base}/realms/{realm}/{path.lstrip('/')}"

def _token_endpoint() -> str:
  return _realm_url("protocol/openid-connect/token")

def _certs_endpoint() -> str:
  return _realm_url("protocol/openid-connect/certs")

def _token_request(data: dict[str, str]) -> dict[str, Any]:
  payload = {
    "client_id": KEYCLOAK_CLIENT_ID,
    **data,
  }
  if KEYCLOAK_CLIENT_SECRET:
    payload["client_secret"] = KEYCLOAK_CLIENT_SECRET
  try:
    with httpx.Client(timeout=10.0, verify=KEYCLOAK_VERIFY_SSL) as client:
      resp = client.post(_token_endpoint(), data=payload)
      resp.raise_for_status()
      return resp.json()
  except httpx.HTTPStatusError as exc:
    detail = exc.response.text or "Keycloak token request failed"
    raise ValueError(detail) from exc
  except httpx.RequestError as exc:
    raise ValueError("Keycloak is unavailable") from exc

def login_with_password(username: str, password: str) -> dict[str, Any]:
  return _token_request({
    "grant_type": "password",
    "username": username,
    "password": password,
  })

def refresh_with_token(refresh_token: str) -> dict[str, Any]:
  return _token_request({
    "grant_type": "refresh_token",
    "refresh_token": refresh_token,
  })

def _load_jwks() -> dict[str, Any]:
  global _jwks_cache, _jwks_cache_time
  now = time.time()
  if _jwks_cache and (now - _jwks_cache_time) < KEYCLOAK_JWKS_CACHE_SEC:
    return _jwks_cache
  try:
    with httpx.Client(timeout=10.0, verify=KEYCLOAK_VERIFY_SSL) as client:
      resp = client.get(_certs_endpoint())
      resp.raise_for_status()
      _jwks_cache = resp.json()
      _jwks_cache_time = now
      return _jwks_cache
  except httpx.RequestError as exc:
    raise ValueError("Keycloak JWKS endpoint unavailable") from exc

def _find_jwk(kid: str) -> dict[str, Any]:
  jwks = _load_jwks()
  keys = jwks.get("keys", [])
  for key in keys:
    if key.get("kid") == kid:
      return key
  raise ValueError("Signing key not found")

def decode_token(token: str) -> dict[str, Any]:
  try:
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    if not kid:
      raise ValueError("Missing token header")
    key = _find_jwk(kid)
    options = {"verify_aud": bool(KEYCLOAK_AUDIENCE)}
    return jwt.decode(
      token,
      key,
      algorithms=[header.get("alg", "RS256")],
      audience=KEYCLOAK_AUDIENCE,
      options=options,
    )
  except (JWTError, ValueError) as exc:
    raise ValueError("Invalid token") from exc

def extract_roles(payload: dict[str, Any]) -> list[str]:
  roles: set[str] = set()
  realm_access = payload.get("realm_access") or {}
  roles.update(realm_access.get("roles") or [])
  resource_access = payload.get("resource_access") or {}
  client_roles = resource_access.get(KEYCLOAK_CLIENT_ID) or {}
  roles.update(client_roles.get("roles") or [])
  if "roles" in payload and isinstance(payload["roles"], list):
    roles.update(payload["roles"])
  return sorted(roles)
