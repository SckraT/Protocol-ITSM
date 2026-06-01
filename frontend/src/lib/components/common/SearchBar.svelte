<script lang="ts">
  // Строка поиска с debounce.
  import { Search } from 'lucide-svelte';
  import { filtersStore } from '$lib/stores/filters.svelte';

  let value = $state(filtersStore.searchQuery);
  let timer: ReturnType<typeof setTimeout>;

  function onInput() {
    clearTimeout(timer);
    timer = setTimeout(() => {
      filtersStore.searchQuery = value;
      filtersStore.currentPage = 1;
      filtersStore.persist();
    }, 150);
  }
</script>

<div class="relative w-full max-w-md">
  <Search
    size={16}
    class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-secondary)]"
  />
  <input
    type="search"
    placeholder="Поиск по теме, тикету, исполнителю…"
    bind:value
    oninput={onInput}
    class="w-full rounded-md border border-[var(--border)] bg-[var(--table-bg)] py-2 pl-9 pr-3 text-sm outline-none focus:border-[var(--accent)]"
  />
</div>
