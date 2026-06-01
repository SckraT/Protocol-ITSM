<script lang="ts">
  // История статусов задачи: список + добавление/удаление.
  import { Trash2 } from 'lucide-svelte';
  import type { Status } from '$lib/api/types';
  import StatusForm from './StatusForm.svelte';
  import { fmtDate } from '$lib/utils/date';

  let {
    statuses = [],
    onAdd,
    onDelete
  }: {
    statuses: Status[];
    onAdd: (date: string | null, note: string) => Promise<void>;
    onDelete: (statusId: number) => Promise<void>;
  } = $props();
</script>

<div class="flex flex-col gap-3">
  <h3 class="text-sm font-semibold text-[var(--text-body)]">История статусов</h3>

  <StatusForm {onAdd} />

  {#if statuses.length === 0}
    <p class="text-sm text-[var(--text-secondary)]">Статусов пока нет</p>
  {:else}
    <ul class="flex flex-col gap-2">
      {#each statuses as status, idx (status.id)}
        <li
          class="rounded-md border p-3 {idx === 0
            ? 'border-[var(--accent)] bg-[var(--blue-light)]/20'
            : 'border-[var(--border)] bg-[var(--table-bg)]'}"
        >
          <div class="flex items-start justify-between gap-2">
            <div class="flex-1">
              {#if status.status_date}
                <div class="text-xs font-medium text-[var(--accent)]">
                  {fmtDate(status.status_date)}
                </div>
              {/if}
              <div class="text-sm text-[var(--text-body)]">
                {status.status_note || '—'}
              </div>
            </div>
            <button
              class="text-[var(--text-secondary)] hover:text-[var(--danger)]"
              aria-label="Удалить статус"
              onclick={() => onDelete(status.id)}
            >
              <Trash2 size={14} />
            </button>
          </div>
        </li>
      {/each}
    </ul>
  {/if}
</div>
