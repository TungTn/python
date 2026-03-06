import logging
from typing import Any

import httpx
from backend.apiBaseUrl import (
  KEYCLOAK_ADMIN_CLIENT_ID,
  KEYCLOAK_ADMIN_CLIENT_SECRET,
  KEYCLOAK_ADMIN_PASSWORD,
  KEYCLOAK_ADMIN_REALM,
  KEYCLOAK_ADMIN_USERNAME,
  KEYCLOAK_BASE_URL,
  KEYCLOAK_REALM,
  KEYCLOAK_VERIFY_SSL,
)
logger = logging.getLogger("backend.keycloak_admin")

def _admin_token() -> str:
  if KEYCLOAK_ADMIN_USERNAME and KEYCLOAK_ADMIN_PASSWORD:
    logger.info(
      "Keycloak admin token: password grant for client '%s' in realm '%s'",
      KEYCLOAK_ADMIN_CLIENT_ID,
      KEYCLOAK_ADMIN_REALM,
    )
    data = {
      "grant_type": "password",
      "client_id": KEYCLOAK_ADMIN_CLIENT_ID,
      "username": KEYCLOAK_ADMIN_USERNAME,
      "password": KEYCLOAK_ADMIN_PASSWORD,
    }
  else:
    logger.warning(
      "Keycloak admin token: client_credentials grant for client '%s' in realm '%s'",
      KEYCLOAK_ADMIN_CLIENT_ID,
      KEYCLOAK_ADMIN_REALM,
    )
    data = {
      "grant_type": "client_credentials",
      "client_id": KEYCLOAK_ADMIN_CLIENT_ID,
    }
    if KEYCLOAK_ADMIN_CLIENT_SECRET:
      data["client_secret"] = KEYCLOAK_ADMIN_CLIENT_SECRET
  token_url = f"{KEYCLOAK_BASE_URL.rstrip('/')}/realms/{KEYCLOAK_ADMIN_REALM}/protocol/openid-connect/token"
  with httpx.Client(timeout=10.0, verify=KEYCLOAK_VERIFY_SSL) as client:
    resp = client.post(token_url, data=data)
    resp.raise_for_status()
    return resp.json()["access_token"]

def create_user(payload: dict[str, Any]) -> str:
  token = _admin_token()
  url = f"{KEYCLOAK_BASE_URL.rstrip('/')}/admin/realms/{KEYCLOAK_REALM}/users"
  headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
  with httpx.Client(timeout=10.0, verify=KEYCLOAK_VERIFY_SSL) as client:
    resp = client.post(url, json=payload, headers=headers)
    if resp.status_code == 409:
      raise ValueError("User already exists")
    resp.raise_for_status()
    location = resp.headers.get("Location", "")
    return location.rsplit("/", 1)[-1] if location else ""
