//
// Central API configuration — no URLs are hardcoded anywhere in the app.
//
// The backend origin is read from the environment:
//   - Vite dev / Vercel build:  frontend/.env  ->  VITE_API_BASE_URL
//   - Same-origin deployments:  leave VITE_API_BASE_URL empty and the app
//     will call the API on the same host it is served from.
//
// Trailing slashes are stripped so paths can never become '//patients'.
const rawBaseUrl = import.meta.env.VITE_API_BASE_URL ?? '';

export const API_BASE_URL = String(rawBaseUrl).trim().replace(/\/+$/, '');

/** Build an absolute endpoint URL from a backend path such as '/patients'. */
export function apiUrl(path) {
  const cleanPath = `/${String(path).replace(/^\/+/, '')}`;
  return `${API_BASE_URL}${cleanPath}`;
}
