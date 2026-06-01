<script lang="ts">
  // Строка таблицы задач.
  import type { Item, ItemState } from '$lib/api/types';
  import Badge from '$lib/components/ui/Badge.svelte';
  import StatusPeek from './StatusPeek.svelte';
  import { STATE_LABEL, STATE_ORDER } from '$lib/utils/constants';
  import { fmtDate, dueInfo } from '$lib/utils/date';

  let {
    item,
    selected = false,
    onToggleSelect,
    onOpen,
    onStateChange
  }: {
    item: Item;
    selected?: boolean;
    onToggleSelect: (id: number) => void;
    onOpen: (id: number) => void;
    onStateChange: (id: number, state: ItemState) => void;
  } = $props();

  const due = $derived(dueInfo(item.due_date, item.state));
  const lastStatus = $derived(item.recent_statuses[0] ?? null);

  function handleStateChange(e: Event) {
    const value = (e.target as HTMLSelectElement).value as ItemState;
    onStateChange(item.id, value);
  }
</script>

<tr
  class="border-t border-[var(--border)] transition-colors hover:bg-[var(--table-hover)] {selected
    ? 'bg-[var(--blue-light)]/30'
    : ''}"
>
  <!-- Чекбокс -->
  <td class="px-3 py-2">
    <input
      type="checkbox"
      checked={selected}
      onchange={() => onToggleSelect(item.id)}
      aria-label="Выбрать задачу {item.id}"
    />
  </td>

  <!-- № -->
  <td class="px-3 py-2 text-[var(--text-secondary)]">{item.id}</td>

  <!-- Тема (клик открывает Drawer) -->
  <td class="px-3 py-2">
    <button
      class="text-left font-medium text-[var(--text-body)] hover:text-[var(--accent)] hover:underline"
      onclick={() => onOpen(item.id)}
    >
      {item.topic}
    </button>
  </td>

  <!-- Тикет -->
  <td class="px-3 py-2 text-[var(--text-secondary)]">{item.ticket ?? ''}</td>

  <!-- Приоритет -->
  <td class="px-3 py-2">
    {#if item.priority}<Badge priority={item.priority} />{/if}
  </td>

  <!-- Состояние (inline-селект) -->
  <td class="px-3 py-2">
    <select
      value={item.state}
      onchange={handleStateChange}
      class="rounded border border-[var(--border)] bg-[var(--table-bg)] px-2 py-1 text-xs"
      aria-label="Состояние задачи {item.id}"
    >
      {#each STATE_ORDER as st (st)}
        <option value={st}>{STATE_LABEL[st]}</option>
      {/each}
    </select>
  </td>

  <!-- Срок -->
  <td class="px-3 py-2 whitespace-nowrap">
    {#if item.due_date}
      <span
        class={due.cls === 'overdue'
          ? 'text-[var(--danger)]'
          : due.cls === 'soon'
            ? 'text-[var(--warning)]'
            : ''}
      >
        {fmtDate(item.due_date)}
      </span>
      {#if due.rel}
        <div class="text-xs text-[var(--text-secondary)]">{due.rel}</div>
      {/if}
    {/if}
  </td>

  <!-- Исполнители -->
  <td class="px-3 py-2">
    <div class="flex flex-wrap gap-1">
      {#each item.executors as exec (exec.id)}
        <span class="exec-chip" title={exec.department_name ?? ''}>
          {exec.name}
        </span>
      {/each}
    </div>
  </td>

  <!-- Последний статус -->
  <td class="px-3 py-2 text-sm">
    {#if lastStatus}
      <div class="text-[var(--text-body)]">{lastStatus.status_note ?? ''}</div>
      <div class="flex items-center gap-2 text-xs text-[var(--text-secondary)]">
        {#if lastStatus.status_date}<span>{fmtDate(lastStatus.status_date)}</span>{/if}
        {#if item.status_count > 0}
          <StatusPeek itemId={item.id} statusCount={item.status_count} />
        {/if}
      </div>
    {/if}
  </td>
</tr>
