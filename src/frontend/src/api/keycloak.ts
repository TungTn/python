import {
  KEYCLOAK_BASE_URL,
  KEYCLOAK_LOGIN_REDIRECT,
  KEYCLOAK_REGISTER_REDIRECT,
} from "./apiBaseUrl";
import { API_BASE_URL } from "./api";

const STATE_KEY = "kc_auth_state";
const VERIFIER_KEY = "kc_pkce_verifier";

type KeycloakConfig = {
  realm: string;
  client_id: string;
};

let keycloakConfigCache: KeycloakConfig | null = null;

async function getKeycloakConfig(): Promise<KeycloakConfig> {
  if (keycloakConfigCache) {
    return keycloakConfigCache;
  }

  const response = await fetch(`${API_BASE_URL}/auth/config`);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "Failed to load auth config");
  }

  keycloakConfigCache = (await response.json()) as KeycloakConfig;
  return keycloakConfigCache;
}

function base64UrlEncode(data: ArrayBuffer) {
  const bytes = new Uint8Array(data);
  let binary = "";
  for (const b of bytes) {
    binary += String.fromCharCode(b);
  }
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function randomString(length = 64) {
  const bytes = new Uint8Array(length);
  crypto.getRandomValues(bytes);
  return base64UrlEncode(bytes.buffer);
}

async function sha256(value: string) {
  const encoder = new TextEncoder();
  const data = encoder.encode(value);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return base64UrlEncode(digest);
}

async function authEndpoint() {
  const config = await getKeycloakConfig();
  return `${KEYCLOAK_BASE_URL.replace(/\/$/, "")}/realms/${config.realm}/protocol/openid-connect/auth`;
}

async function tokenEndpoint() {
  const config = await getKeycloakConfig();
  return `${KEYCLOAK_BASE_URL.replace(/\/$/, "")}/realms/${config.realm}/protocol/openid-connect/token`;
}

export function getLoginRedirectUri() {
  return KEYCLOAK_LOGIN_REDIRECT;
}

export function getRegisterRedirectUri() {
  return KEYCLOAK_REGISTER_REDIRECT;
}

async function startAuthFlow(redirectUri: string, action?: "register") {
  const config = await getKeycloakConfig();
  const state = randomString(24);
  const verifier = randomString(64);
  const challenge = await sha256(verifier);

  sessionStorage.setItem(STATE_KEY, state);
  sessionStorage.setItem(VERIFIER_KEY, verifier);

  const params = new URLSearchParams({
    client_id: config.client_id,
    redirect_uri: redirectUri,
    response_type: "code",
    scope: "openid profile email",
    state,
    code_challenge: challenge,
    code_challenge_method: "S256",
  });

  if (action === "register") {
    params.set("kc_action", "register");
  }

  const endpoint = await authEndpoint();
  window.location.href = `${endpoint}?${params.toString()}`;
}

export async function startLogin() {
  await startAuthFlow(getLoginRedirectUri());
}

export async function startRegister() {
  await startAuthFlow(getRegisterRedirectUri(), "register");
}

export type KeycloakTokenResponse = {
  access_token: string;
  refresh_token?: string;
  id_token?: string;
  token_type: string;
  expires_in?: number;
};

export async function loginWithPassword(username: string, password: string) {
  const config = await getKeycloakConfig();
  const body = new URLSearchParams({
    grant_type: "password",
    client_id: config.client_id,
    username,
    password,
    scope: "openid profile email",
  });

  const endpoint = await tokenEndpoint();
  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "Keycloak login failed");
  }

  return (await response.json()) as KeycloakTokenResponse;
}

export async function handleKeycloakCallback(search: string, redirectUri: string) {
  const config = await getKeycloakConfig();
  const params = new URLSearchParams(search);
  const code = params.get("code");
  const state = params.get("state");
  const error = params.get("error");
  const errorDescription = params.get("error_description");

  if (error) {
    throw new Error(errorDescription ?? error);
  }

  if (!code) {
    return null;
  }

  const expectedState = sessionStorage.getItem(STATE_KEY);
  const verifier = sessionStorage.getItem(VERIFIER_KEY);
  sessionStorage.removeItem(STATE_KEY);
  sessionStorage.removeItem(VERIFIER_KEY);

  if (!state || !expectedState || state !== expectedState) {
    throw new Error("Invalid login state");
  }

  if (!verifier) {
    throw new Error("Missing PKCE verifier");
  }

  const body = new URLSearchParams({
    grant_type: "authorization_code",
    client_id: config.client_id,
    code,
    redirect_uri: redirectUri,
    code_verifier: verifier,
  });

  const endpoint = await tokenEndpoint();
  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "Keycloak token exchange failed");
  }

  return (await response.json()) as KeycloakTokenResponse;
}
