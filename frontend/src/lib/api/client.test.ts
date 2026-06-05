import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { apiGet, LS_ACCESS, LS_REFRESH } from './client';

/** Сконструировать JSON-ответ (глобальный Response доступен в Node 20). */
function json(status: number, body?: unknown): Response {
  return new Response(body === undefined ? null : JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json' }
  });
}

describe('apiFetch — обновление токена', () => {
  beforeEach(() => {
    localStorage.clear();
    localStorage.setItem(LS_ACCESS, 'a1');
    localStorage.setItem(LS_REFRESH, 'r1');
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('параллельные 401 запускают /auth/refresh ровно один раз', async () => {
    let refreshCalls = 0;
    const fetchMock = vi.fn(async (url: unknown, opts: { headers?: Headers } = {}) => {
      const u = String(url);
      if (u.includes('/auth/refresh')) {
        refreshCalls++;
        return json(200, { access_token: 'a2', refresh_token: 'r2' });
      }
      // Старый токен — просрочен; обновлённый — валиден.
      if (opts.headers?.get?.('Authorization') === 'Bearer a1') return json(401, { detail: 'expired' });
      return json(200, { ok: true });
    });
    vi.stubGlobal('fetch', fetchMock);

    const [r1, r2] = await Promise.all([
      apiGet<{ ok: boolean }>('/items'),
      apiGet<{ ok: boolean }>('/users')
    ]);

    expect(refreshCalls).toBe(1);
    expect(r1.ok).toBe(true);
    expect(r2.ok).toBe(true);
    expect(localStorage.getItem(LS_ACCESS)).toBe('a2');
  });

  it('401 без refresh-токена → ошибка (разлогин)', async () => {
    localStorage.removeItem(LS_REFRESH);
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => json(401, { detail: 'expired' }))
    );
    await expect(apiGet('/items')).rejects.toThrow();
  });
});
