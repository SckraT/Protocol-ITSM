// API-вызовы для аутентификации (без зависимости от store).

export type Role = 'viewer' | 'editor' | 'admin';

/** Человекочитаемые названия ролей (RU). */
export const ROLE_LABEL: Record<Role, string> = {
  viewer: 'Просмотр',
  editor: 'Редактор',
  admin: 'Администратор'
};

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
  email: string | null;
  phone: string | null;
  executor_id: number | null;
}

export interface UserCreate {
  username: string;
  password: string;
  role: Role;
  email?: string | null;
  phone?: string | null;
}

export interface UserUpdate {
  role?: Role;
  is_active?: boolean;
  password?: string;
  email?: string | null;
  phone?: string | null;
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

/** Войти по идентификатору (логин/email/телефон) и паролю. */
export async function apiLogin(identifier: string, password: string): Promise<TokenResponse> {
  return post('/auth/login', { identifier, password });
}

/** Обновить access-токен по refresh-токену. */
export async function apiRefresh(refreshToken: string): Promise<TokenResponse> {
  return post('/auth/refresh', { refresh_token: refreshToken });
}
