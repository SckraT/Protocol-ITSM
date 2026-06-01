// Базовый HTTP-клиент для общения с API бэкенда.

// В dev-режиме через Vite-прокси работает относительный путь /api.
// Можно переопределить через VITE_API_BASE_URL (напр. для standalone-режима).
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api';

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

const JSON_HEADERS = { 'Content-Type': 'application/json' };

/**
 * Низкоуровневая обёртка над fetch.
 * @param allow — список статусов, которые не считаются ошибкой (напр. [409]).
 */
async function apiFetch(path: string, options: RequestInit = {}, allow: number[] = []): Promise<Response> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}${path}`, options);
  } catch {
    throw new ApiError(0, 'Ошибка сети');
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
