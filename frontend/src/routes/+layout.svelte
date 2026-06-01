<script lang="ts">
  // Корневой layout: шапка с навигацией, переключатель темы, контейнер уведомлений.
  import '../app.css';
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { Moon, Sun } from 'lucide-svelte';
  import Toast from '$lib/components/ui/Toast.svelte';
  import ConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';
  import { themeStore } from '$lib/stores/theme.svelte';
  import { itemsStore } from '$lib/stores/items.svelte';
  import { refsStore } from '$lib/stores/refs.svelte';

  let { children } = $props();

  // Загружаем данные при старте приложения
  onMount(async () => {
    await Promise.all([refsStore.load(), itemsStore.load()]);
  });

  // Счётчик просроченных задач в заголовке вкладки
  $effect(() => {
    const overdue = itemsStore.overdueCount;
    document.title = overdue > 0 ? `(${overdue}) Протокол совещаний` : 'Протокол совещаний';
  });

  const navItems = [
    { href: '/', label: 'Задачи' },
    { href: '/refs', label: 'Справочники' }
  ];
</script>

<div class="min-h-screen bg-[var(--bg-body)] text-[var(--text-body)]">
  <header
    class="no-print border-b border-[var(--border)] bg-[var(--bg-primary)] text-[var(--text-primary)]"
  >
    <div class="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
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
        </nav>
      </div>
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
    </div>
  </header>

  <main class="mx-auto max-w-7xl px-4 py-6">
    {@render children()}
  </main>
</div>

<Toast />
<ConfirmDialog />
