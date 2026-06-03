// Базовый HTTP-клиент для общения с API бэкенда.
// Автоматически добавляет Authorization: Bearer из localStorage.
// При 401 пытается обновить токен через refresh; при неудаче — разлогинивает.

// В dev-режиме через Vite-прокси работает относительный путь /api.
// Можно переопределить через VITE_API_BASE_URL (напр. для standalone-режима).
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api';

// Ключи localStorage для хранения токенов
export const LS_ACCESS = 'pm_access';
export const LS_REFRESH = 'pm_refresh';
export const LS_USER = 'pm_user';

/** Ошибка API с HTTP-статусом для обработки в UI. */
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/** Попытаться обновить access-токен. Возвращает новый токен или null. */
async function tryRefresh(): Promise<string | null> {
  const refreshToken = localStorage.getItem(LS_REFRESH);
  if (!refreshToken) return null;

  try {
    const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken })
    });
    if (!res.ok) return null;
    const data = await res.json();
    localStorage.setItem(LS_ACCESS, data.access_token);
    localStorage.setItem(LS_REFRESH, data.refresh_token);
    return data.access_token;
  } catch {
    return null;
  }
}

/** Разлогинить пользователя — чистим localStorage и сообщаем layout. */
function forceLogout(): void {
  localStorage.removeItem(LS_ACCESS);
  localStorage.removeItem(LS_REFRESH);
  localStorage.removeItem(LS_USER);
  // Layout слушает этот событие для редиректа на /login
  window.dispatchEvent(new Event('auth:logout'));
}

/**
 * Низкоуровневая обёртка над fetch с поддержкой авторизации.
 * @param allow — список статусов, которые не считаются ошибкой (напр. [409]).
 * @param isRetry — флаг повторного запроса после refresh (предотвращает петлю).
 */
async function apiFetch(
  path: string,
  options: RequestInit = {},
  allow: number[] = [],
  isRetry = false
): Promise<Response> {
  // Добавляем Bearer-токен если есть
  const token = localStorage.getItem(LS_ACCESS);
  const headers = new Headers(options.headers);
  if (token) headers.set('Authorization', `Bearer ${token}`);

  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  } catch {
    throw new ApiError(0, 'Ошибка сети');
  }

  // 401 — пробуем refresh, но только один раз
  if (res.status === 401 && !isRetry) {
    const newToken = await tryRefresh();
    if (newToken) {
      // Повторяем запрос с новым токеном
      headers.set('Authorization', `Bearer ${newToken}`);
      return apiFetch(path, options, allow, true);
    } else {
      forceLogout();
      throw new ApiError(401, 'Сессия истекла. Войдите снова.');
    }
  }

  if (!res.ok && !allow.includes(res.status)) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* тело не JSON — оставляем статус */
    }
    throw new ApiError(res.status, detail);
  }
  return res;
}

/** GET-запрос с разбором JSON. */
export async function apiGet<T>(path: string): Promise<T> {
  const res = await apiFetch(path);
  return res.json() as Promise<T>;
}

const JSON_HEADERS = { 'Content-Type': 'application/json' };

/** POST-запрос с JSON-телом. */
export async function apiPost<T>(path: string, body: unknown, allow: number[] = []): Promise<T> {
  const res = await apiFetch(path, { method: 'POST', headers: JSON_HEADERS, body: JSON.stringify(body) }, allow);
  return res.json() as Promise<T>;
}

/** PATCH-запрос с JSON-телом. */
export async function apiPatch<T>(path: string, body: unknown, allow: number[] = []): Promise<T> {
  const res = await apiFetch(path, { method: 'PATCH', headers: JSON_HEADERS, body: JSON.stringify(body) }, allow);
  return res.json() as Promise<T>;
}

/** PUT-запрос с JSON-телом. */
export async function apiPut<T>(path: string, body: unknown, allow: number[] = []): Promise<T> {
  const res = await apiFetch(path, { method: 'PUT', headers: JSON_HEADERS, body: JSON.stringify(body) }, allow);
  return res.json() as Promise<T>;
}

/** DELETE-запрос (без тела ответа). */
export async function apiDelete(path: string): Promise<void> {
  await apiFetch(path, { method: 'DELETE' });
}

/** POST с FormData (для загрузки файлов). */
export async function apiPostForm<T>(path: string, formData: FormData): Promise<T> {
  const res = await apiFetch(path, { method: 'POST', body: formData });
  return res.json() as Promise<T>;
}

/** Абсолютный URL для прямых ссылок (экспорт файлов). */
export function apiUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}
