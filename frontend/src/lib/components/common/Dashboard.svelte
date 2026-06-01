<script lang="ts">
  // Дашборд: тайлы-счётчики по состояниям задач.
  import { itemsStore } from '$lib/stores/items.svelte';
  import { filtersStore } from '$lib/stores/filters.svelte';

  const tiles = [
    { key: '', label: 'Все' },
    { key: 'in_progress', label: 'В работе' },
    { key: 'postponed', label: 'Отложено' },
    { key: 'closed', label: 'Закрыто' }
  ] as const;

  function tileCount(key: string): number {
    if (key === '') return itemsStore.counts.all;
    return itemsStore.counts[key as 'in_progress' | 'postponed' | 'closed'];
  }

  function setFilter(key: string) {
    // Повторный клик по активному тайлу сбрасывает фильтр
    filtersStore.currentFilter = filtersStore.currentFilter === key ? '' : key;
    filtersStore.currentPage = 1;
    filtersStore.persist();
  }
</script>

<div class="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
  {#each tiles as tile (tile.key)}
    {@const active = filtersStore.currentFilter === tile.key}
    <button
      class="rounded-lg border bg-[var(--table-bg)] p-4 text-left transition-colors hover:bg-[var(--table-hover)] {active
        ? 'border-[var(--accent)] ring-1 ring-[var(--accent)]'
        : 'border-[var(--border)]'}"
      onclick={() => setFilter(tile.key)}
    >
      <div class="text-2xl font-bold">{tileCount(tile.key)}</div>
      <div class="text-sm text-[var(--text-secondary)]">{tile.label}</div>
    </button>
  {/each}
</div>
