export const KEYCLOAK_BASE_URL = import.meta.env.VITE_KEYCLOAK_URL ?? "/keycloak";
export const KEYCLOAK_LOGIN_REDIRECT =
  import.meta.env.VITE_KEYCLOAK_LOGIN_REDIRECT ?? `${window.location.origin}/login`;
export const KEYCLOAK_REGISTER_REDIRECT =
  import.meta.env.VITE_KEYCLOAK_REGISTER_REDIRECT ?? `${window.location.origin}/register`;
