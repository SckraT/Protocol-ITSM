// Стор авторизации — хранит пользователя и токены.
// Токены синхронизируются с localStorage для сохранения сессии после перезагрузки.
import { goto } from '$app/navigation';
import { browser } from '$app/environment';
import { apiLogin, type Role } from '$lib/api/auth';
import { LS_ACCESS, LS_REFRESH, LS_USER } from '$lib/api/client';

interface AuthUser {
  username: string;
  role: Role;
}

function createAuthStore() {
  // Состояние
  let user = $state<AuthUser | null>(null);
  let accessToken = $state<string | null>(null);

  // Восстановить сессию из localStorage
  function restore(): void {
    if (!browser) return;
    const storedUser = localStorage.getItem(LS_USER);
    const storedToken = localStorage.getItem(LS_ACCESS);
    if (storedUser && storedToken) {
      try {
        user = JSON.parse(storedUser) as AuthUser;
        accessToken = storedToken;
      } catch {
        _clear();
      }
    }
  }

  function _clear(): void {
    user = null;
    accessToken = null;
    if (browser) {
      localStorage.removeItem(LS_ACCESS);
      localStorage.removeItem(LS_REFRESH);
      localStorage.removeItem(LS_USER);
    }
  }

  function _save(data: { username: string; role: Role; access_token: string; refresh_token: string }): void {
    user = { username: data.username, role: data.role };
    accessToken = data.access_token;
    if (browser) {
      localStorage.setItem(LS_ACCESS, data.access_token);
      localStorage.setItem(LS_REFRESH, data.refresh_token);
      localStorage.setItem(LS_USER, JSON.stringify(user));
    }
  }

  /** Войти: аутентифицироваться на сервере, сохранить токены. */
  async function login(username: string, password: string): Promise<void> {
    const result = await apiLogin(username, password);
    _save(result);
  }

  /** Выйти: очистить токены и перейти на /login. */
  function logout(): void {
    _clear();
    goto('/login');
  }

  // Восстанавливаем сессию при инициализации модуля
  restore();

  return {
    get user() { return user; },
    get accessToken() { return accessToken; },
    get isAuthenticated() { return !!accessToken && !!user; },
    get isAdmin() { return user?.role === 'admin'; },
    get isEditor() { return user?.role === 'editor' || user?.role === 'admin'; },
    login,
    logout,
    restore,
  };
}

export const authStore = createAuthStore();
