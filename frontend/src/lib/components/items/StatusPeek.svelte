<script lang="ts">
  // Быстрый просмотр истории статусов задачи во всплывающем окне,
  // без открытия боковой панели. Полная история подгружается по клику.
  import { History } from 'lucide-svelte';
  import { fade } from 'svelte/transition';
  import type { Status } from '$lib/api/types';
  import { fetchStatuses } from '$lib/api/statuses';
  import { fmtDate } from '$lib/utils/date';

  let { itemId, statusCount }: { itemId: number; statusCount: number } = $props();

  const WIDTH = 300;

  let open = $state(false);
  let loading = $state(false);
  let statuses = $state<Status[]>([]);
  let btnEl = $state<HTMLButtonElement | null>(null);
  let posStyle = $state('');

  // Пересчитывает позицию окна относительно кнопки (мягкая привязка к строке).
  function updatePosition() {
    if (!btnEl) return;
    const r = btnEl.getBoundingClientRect();
    let left = Math.min(r.right - WIDTH, window.innerWidth - WIDTH - 8);
    left = Math.max(8, left);
    // По умолчанию окно снизу; если внизу мало места — показываем сверху
    const below = r.bottom + 6;
    const wantAbove = below + 200 > window.innerHeight && r.top - 6 > 200;
    const top = wantAbove ? r.top - 6 : below;
    const transform = wantAbove ? 'translateY(-100%)' : '';
    posStyle = `top:${top}px; left:${left}px; width:${WIDTH}px; transform:${transform};`;
  }

  async function toggle() {
    if (open) {
      open = false;
      return;
    }
    updatePosition();
    open = true;
    loading = true;
    try {
      statuses = await fetchStatuses(itemId);
    } catch {
      statuses = [];
    } finally {
      loading = false;
    }
  }

  function close() {
    open = false;
  }

  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') close();
  }

  // Пока окно открыто — следим за прокруткой и ресайзом, чтобы оно следовало
  // за строкой. capture:true ловит скролл вложенных контейнеров (обёртка таблицы).
  $effect(() => {
    if (!open) return;
    const handler = () => updatePosition();
    window.addEventListener('scroll', handler, true);
    window.addEventListener('resize', handler);
    return () => {
      window.removeEventListener('scroll', handler, true);
      window.removeEventListener('resize', handler);
    };
  });
</script>

<svelte:window onkeydown={open ? onKeydown : undefined} />

<button
  bind:this={btnEl}
  class="inline-flex items-center gap-0.5 rounded px-1 text-[var(--text-secondary)] hover:bg-[var(--table-hover)] hover:text-[var(--accent)]"
  aria-label="Показать историю статусов"
  title="История статусов"
  onclick={toggle}
>
  <History size={14} />
  {#if statusCount > 0}<span class="text-xs">{statusCount}</span>{/if}
</button>

{#if open}
  <!-- Невидимый слой для закрытия по клику вне окна -->
  <button
    class="fixed inset-0 z-40 cursor-default"
    aria-label="Закрыть"
    tabindex="-1"
    onclick={close}
  ></button>

  <div
    class="fixed z-50 max-h-80 overflow-y-auto rounded-lg border border-[var(--border)] bg-[var(--table-bg)] p-3 shadow-xl"
    style={posStyle}
    role="dialog"
    aria-label="История статусов"
    transition:fade={{ duration: 120 }}
  >
    <div class="mb-2 text-xs font-semibold text-[var(--text-secondary)]">История статусов</div>
    {#if loading}
      <div class="py-2 text-sm text-[var(--text-secondary)]">Загрузка…</div>
    {:else if statuses.length === 0}
      <div class="py-2 text-sm text-[var(--text-secondary)]">Статусов нет</div>
    {:else}
      <ul class="flex flex-col gap-2">
        {#each statuses as status, idx (status.id)}
          <li
            class="rounded border-l-2 pl-2 {idx === 0
              ? 'border-[var(--accent)]'
              : 'border-[var(--border)]'}"
          >
            {#if status.status_date}
              <div class="text-xs font-medium text-[var(--accent)]">
                {fmtDate(status.status_date)}
              </div>
            {/if}
            <div class="text-sm text-[var(--text-body)]">{status.status_note || '—'}</div>
          </li>
        {/each}
      </ul>
    {/if}
  </div>
{/if}
