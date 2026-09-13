/**
 * Stores and reads the JWT issued by the backend's /login route.
 *
 * Kept in localStorage (not a cookie) since this is a client-rendered
 * SPA-style app talking to a separate FastAPI backend -- there's no
 * server-side session on the Next.js side to keep in sync.
 */

const TOKEN_KEY = "auth_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null; // guards server-side rendering
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export function isLoggedIn(): boolean {
  return getToken() !== null;
}
