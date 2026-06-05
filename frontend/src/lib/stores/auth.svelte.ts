// Стор авторизации — хранит пользователя и токены.
// Токены синхронизируются с localStorage для сохранения сессии после перезагрузки.
import { goto } from '$app/navigation';
import { browser } from '$app/environment';
import { apiLogin, type Role } from '$lib/api/auth';
import { LS_ACCESS, LS_REFRESH, LS_USER } from '$lib/api/client';

interface AuthUser {
  username: string;
  role: Role;
  displayName: string;
  mustChangePassword: boolean;
}

function createAuthStore() {
  // Состояние
  let user = $state<AuthUser | null>(null);
  let accessToken = $state<string | null>(null);

  // Проверка, что распарсенный объект действительно похож на пользователя
  function isAuthUser(v: unknown): v is AuthUser {
    return (
      typeof v === 'object' &&
      v !== null &&
      typeof (v as AuthUser).username === 'string' &&
      typeof (v as AuthUser).role === 'string'
    );
  }

  // Нормализуем восстановленного пользователя: старый формат без новых полей → дефолты
  function _withDisplay(u: AuthUser): AuthUser {
    return { ...u, displayName: u.displayName || u.username, mustChangePassword: u.mustChangePassword ?? false };
  }

  // Восстановить сессию из localStorage
  function restore(): void {
    if (!browser) return;
    const storedUser = localStorage.getItem(LS_USER);
    const storedToken = localStorage.getItem(LS_ACCESS);
    if (!storedUser || !storedToken) return;
    try {
      const parsed = JSON.parse(storedUser);
      if (isAuthUser(parsed)) {
        user = _withDisplay(parsed);
        accessToken = storedToken;
      } else {
        _clear(); // валидный JSON, но не пользователь (повреждённые данные)
      }
    } catch {
      _clear();
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

  function _save(data: {
    username: string;
    role: Role;
    access_token: string;
    refresh_token: string;
    display_name: string;
    must_change_password?: boolean;
  }): void {
    user = {
      username: data.username,
      role: data.role,
      displayName: data.display_name || data.username,
      mustChangePassword: data.must_change_password ?? false
    };
    accessToken = data.access_token;
    if (browser) {
      localStorage.setItem(LS_ACCESS, data.access_token);
      localStorage.setItem(LS_REFRESH, data.refresh_token);
      localStorage.setItem(LS_USER, JSON.stringify(user));
    }
  }

  /** Войти: аутентифицироваться по идентификатору (логин/email/телефон), сохранить токены. */
  async function login(identifier: string, password: string): Promise<void> {
    const result = await apiLogin(identifier, password);
    _save(result);
  }

  /** Выйти: очистить токены и перейти на /login. */
  function logout(): void {
    _clear();
    goto('/login');
  }

  /** Снять флаг обязательной смены пароля (после успешной смены). */
  function clearPasswordChangeFlag(): void {
    if (!user) return;
    user = { ...user, mustChangePassword: false };
    if (browser) localStorage.setItem(LS_USER, JSON.stringify(user));
  }

  // Восстанавливаем сессию при инициализации модуля
  restore();

  // После «тихого» refresh токена (api/client.ts) перечитываем роль/имя из localStorage
  if (browser) {
    window.addEventListener('auth:refreshed', restore);
  }

  return {
    get user() { return user; },
    get accessToken() { return accessToken; },
    get isAuthenticated() { return !!accessToken && !!user; },
    get isAdmin() { return user?.role === 'admin'; },
    get isEditor() { return user?.role === 'editor' || user?.role === 'admin'; },
    get mustChangePassword() { return user?.mustChangePassword ?? false; },
    login,
    logout,
    restore,
    clearPasswordChangeFlag,
  };
}

export const authStore = createAuthStore();
