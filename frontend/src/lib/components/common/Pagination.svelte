<script lang="ts">
  // Постраничная навигация.
  let {
    page = 1,
    pageSize = 20,
    total = 0,
    onPage,
    onPageSize
  }: {
    page?: number;
    pageSize?: number;
    total?: number;
    onPage: (p: number) => void;
    onPageSize: (s: number) => void;
  } = $props();

  const totalPages = $derived(Math.max(1, Math.ceil(total / pageSize)));

  // Формирует список номеров страниц с многоточиями
  const pages = $derived.by(() => {
    const result: (number | '...')[] = [];
    const tp = totalPages;
    if (tp <= 7) {
      for (let i = 1; i <= tp; i++) result.push(i);
    } else {
      result.push(1);
      if (page > 3) result.push('...');
      for (let i = Math.max(2, page - 1); i <= Math.min(tp - 1, page + 1); i++) result.push(i);
      if (page < tp - 2) result.push('...');
      result.push(tp);
    }
    return result;
  });

  const sizeOptions = [10, 20, 50, 100];
</script>

{#if total > 0}
  <div class="no-print mt-4 flex flex-wrap items-center justify-between gap-3">
    <div class="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
      <span>На странице:</span>
      <select
        value={String(pageSize)}
        onchange={(e) => onPageSize(Number((e.target as HTMLSelectElement).value))}
        class="rounded border border-[var(--border)] bg-[var(--table-bg)] px-2 py-1 text-sm"
        aria-label="Размер страницы"
      >
        {#each sizeOptions as opt (opt)}
          <option value={String(opt)}>{opt}</option>
        {/each}
      </select>
      <span>Всего: {total}</span>
    </div>

    {#if totalPages > 1}
      <div class="flex items-center gap-1">
        <button
          class="rounded border border-[var(--border)] px-2.5 py-1 text-sm disabled:opacity-40"
          disabled={page <= 1}
          onclick={() => onPage(page - 1)}
          aria-label="Предыдущая страница"
        >
          ‹
        </button>
        {#each pages as p (p)}
          {#if p === '...'}
            <span class="px-1.5 text-[var(--text-secondary)]">…</span>
          {:else}
            <button
              class="min-w-[32px] rounded border px-2.5 py-1 text-sm {p === page
                ? 'border-[var(--accent)] bg-[var(--accent)] text-white'
                : 'border-[var(--border)] hover:bg-[var(--table-hover)]'}"
              onclick={() => onPage(p)}
            >
              {p}
            </button>
          {/if}
        {/each}
        <button
          class="rounded border border-[var(--border)] px-2.5 py-1 text-sm disabled:opacity-40"
          disabled={page >= totalPages}
          onclick={() => onPage(page + 1)}
          aria-label="Следующая страница"
        >
          ›
        </button>
      </div>
    {/if}
  </div>
{/if}
