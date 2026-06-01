<script lang="ts">
  // Фильтры по отделу, исполнителю и приоритету.
  import { X } from 'lucide-svelte';
  import { filtersStore } from '$lib/stores/filters.svelte';
  import { refsStore } from '$lib/stores/refs.svelte';
  import { PRIORITY_CONFIG } from '$lib/utils/constants';

  function onChange() {
    filtersStore.currentPage = 1;
    filtersStore.persist();
  }

  function reset() {
    filtersStore.resetAdvanced();
  }

  const selectClass =
    'rounded-md border border-[var(--border)] bg-[var(--table-bg)] px-2.5 py-1.5 text-sm text-[var(--text-body)] outline-none focus:border-[var(--accent)]';
</script>

<div class="flex flex-wrap items-center gap-2">
  <select bind:value={filtersStore.filterDept} onchange={onChange} class={selectClass} aria-label="Отдел">
    <option value="">Все отделы</option>
    {#each refsStore.departments as dept (dept.id)}
      <option value={String(dept.id)}>{dept.name}</option>
    {/each}
  </select>

  <select
    bind:value={filtersStore.filterExec}
    onchange={onChange}
    class={selectClass}
    aria-label="Исполнитель"
  >
    <option value="">Все исполнители</option>
    {#each refsStore.executors as exec (exec.id)}
      <option value={String(exec.id)}>{exec.name}</option>
    {/each}
  </select>

  <select
    bind:value={filtersStore.filterPriority}
    onchange={onChange}
    class={selectClass}
    aria-label="Приоритет"
  >
    <option value="">Любой приоритет</option>
    {#each Object.entries(PRIORITY_CONFIG) as [key, cfg] (key)}
      <option value={key}>{cfg.label}</option>
    {/each}
  </select>

  {#if filtersStore.hasActiveFilters}
    <button
      class="inline-flex items-center gap-1 rounded-md border border-[var(--border)] px-2.5 py-1.5 text-sm text-[var(--text-secondary)] hover:border-[var(--danger)] hover:text-[var(--danger)]"
      onclick={reset}
    >
      <X size={14} /> Сбросить
    </button>
  {/if}
</div>
