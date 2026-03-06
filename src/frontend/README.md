# Frontend

Keycloak auth uses password grant for login and a backend proxy to create users via the Keycloak Admin API.

Required env vars (Vite):
- `VITE_KEYCLOAK_URL` (default `/keycloak` - uses Vite dev proxy to avoid CORS)

Keycloak `realm` and `client_id` are loaded from backend endpoint `GET /auth/config`.

Flow:
1) FE sends username/password to Keycloak token endpoint
2) FE stores access token and calls backend `/auth/me`
3) Register submits user info to backend `/auth/register`, which creates user in Keycloak, then logs in

Dev CORS note:
- If you see CORS errors, keep `VITE_KEYCLOAK_URL=/keycloak` and run Vite dev server.
