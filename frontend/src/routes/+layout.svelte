<script lang="ts">
  // Корневой layout: шапка с навигацией, переключатель темы, контейнер уведомлений.
  // Для неавторизованных — редирект на /login.
  import '../app.css';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { Moon, Sun, LogOut, Users } from 'lucide-svelte';
  import Toast from '$lib/components/ui/Toast.svelte';
  import ConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';
  import { themeStore } from '$lib/stores/theme.svelte';
  import { itemsStore } from '$lib/stores/items.svelte';
  import { refsStore } from '$lib/stores/refs.svelte';
  import { meetingsStore } from '$lib/stores/meetings.svelte';
  import { authStore } from '$lib/stores/auth.svelte';
  import { ROLE_LABEL } from '$lib/api/auth';

  let { children } = $props();

  // Определяем, находимся ли мы на странице /login
  const isLoginPage = $derived($page.url.pathname === '/login');
  const isChangePwPage = $derived($page.url.pathname === '/change-password');

  onMount(async () => {
    // Auth guard: перенаправляем неавторизованных на /login
    if (!authStore.isAuthenticated && !isLoginPage) {
      goto('/login');
      return;
    }

    // Слушаем событие принудительного logout (из api/client.ts при 401)
    window.addEventListener('auth:logout', () => {
      authStore.logout();
    });

    // Загружаем данные только для авторизованных пользователей
    if (authStore.isAuthenticated) {
      await Promise.all([refsStore.load(), itemsStore.load(), meetingsStore.load()]);
    }
  });

  // Guard: пока требуется смена пароля — держим пользователя на /change-password
  $effect(() => {
    if (authStore.isAuthenticated && authStore.mustChangePassword && !isChangePwPage) {
      goto('/change-password');
    }
  });

  // Счётчик просроченных задач в заголовке вкладки
  $effect(() => {
    if (isLoginPage) return;
    const overdue = itemsStore.overdueCount;
    document.title = overdue > 0 ? `(${overdue}) Протокол совещаний` : 'Протокол совещаний';
  });

  const navItems = [
    { href: '/', label: 'Задачи' },
    { href: '/meetings', label: 'Совещания' },
    { href: '/refs', label: 'Справочники' }
  ];
</script>

{#if isLoginPage || isChangePwPage}
  <!-- Вход / обязательная смена пароля — без шапки и навигации -->
  {@render children()}
{:else}
  <div class="min-h-screen bg-[var(--bg-body)] text-[var(--text-body)]">
    <header
      class="no-print border-b border-[var(--border)] bg-[var(--bg-primary)] text-[var(--text-primary)]"
    >
      <div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
        <!-- Левая часть: логотип + навигация -->
        <div class="flex items-center gap-6">
          <span class="text-lg font-semibold">Протокол совещаний</span>
          <nav class="flex gap-1">
            {#each navItems as item (item.href)}
              {@const active = $page.url.pathname === item.href}
              <a
                href={item.href}
                class="rounded px-3 py-1.5 text-sm transition-colors {active
                  ? 'bg-[var(--accent)] text-white'
                  : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'}"
              >
                {item.label}
              </a>
            {/each}
            {#if authStore.isAdmin}
              {@const active = $page.url.pathname === '/admin'}
              <a
                href="/admin"
                class="rounded px-3 py-1.5 text-sm transition-colors {active
                  ? 'bg-[var(--accent)] text-white'
                  : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'}"
              >
                Пользователи
              </a>
            {/if}
          </nav>
        </div>

        <!-- Правая часть: пользователь + тема + выход -->
        <div class="flex items-center gap-3">
          {#if authStore.user}
            <div class="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
              <Users size={14} />
              <span class="font-medium text-[var(--text-primary)]">{authStore.user.displayName || authStore.user.username}</span>
              <span class="rounded bg-[var(--table-hover)] px-1.5 py-0.5 text-xs">
                {ROLE_LABEL[authStore.user.role] ?? authStore.user.role}
              </span>
            </div>
          {/if}

          <!-- Переключатель темы -->
          <button
            class="rounded p-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
            aria-label="Переключить тему"
            onclick={() => themeStore.toggle()}
          >
            {#if themeStore.current === 'dark'}
              <Sun size={18} />
            {:else}
              <Moon size={18} />
            {/if}
          </button>

          <!-- Выход -->
          <button
            class="rounded p-2 text-[var(--text-secondary)] hover:text-red-500"
            aria-label="Выйти из системы"
            title="Выйти"
            onclick={() => authStore.logout()}
          >
            <LogOut size={18} />
          </button>
        </div>
      </div>
    </header>

    <main class="mx-auto max-w-7xl px-4 py-6">
      {@render children()}
    </main>
  </div>

  <Toast />
  <ConfirmDialog />
{/if}
