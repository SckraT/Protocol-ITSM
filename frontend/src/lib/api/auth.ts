// API-вызовы для аутентификации (без зависимости от store).

export type Role = 'viewer' | 'editor' | 'admin';

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  username: string;
  role: Role;
}

export interface UserResponse {
  id: number;
  username: string;
  role: Role;
  is_active: boolean;
  created_at: string;
}

export interface UserCreate {
  username: string;
  password: string;
  role: Role;
}

export interface UserUpdate {
  role?: Role;
  is_active?: boolean;
  password?: string;
}

const BASE = (import.meta.env.VITE_API_BASE_URL ?? '/api') as string;

async function post<T>(path: string, body: unknown, token?: string): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${BASE}${path}`, { method: 'POST', headers, body: JSON.stringify(body) });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.detail ?? `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

/** Войти по логину и паролю. */
export async function apiLogin(username: string, password: string): Promise<TokenResponse> {
  return post('/auth/login', { username, password });
}

/** Обновить access-токен по refresh-токену. */
export async function apiRefresh(refreshToken: string): Promise<TokenResponse> {
  return post('/auth/refresh', { refresh_token: refreshToken });
}
