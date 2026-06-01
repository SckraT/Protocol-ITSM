<script lang="ts">
  // Форма добавления статуса: дата + примечание.
  import Button from '$lib/components/ui/Button.svelte';
  import { today } from '$lib/utils/date';

  let { onAdd }: { onAdd: (date: string | null, note: string) => Promise<void> } = $props();

  let date = $state(today());
  let note = $state('');
  let saving = $state(false);

  async function submit() {
    if (!note.trim() && !date) return;
    saving = true;
    try {
      await onAdd(date || null, note.trim());
      note = '';
      date = today();
    } finally {
      saving = false;
    }
  }
</script>

<form
  class="flex flex-col gap-2 rounded-md border border-[var(--border)] bg-[var(--table-hover)] p-3"
  onsubmit={(e) => {
    e.preventDefault();
    submit();
  }}
>
  <div class="flex items-center gap-2">
    <input
      type="date"
      bind:value={date}
      class="rounded border border-[var(--border)] bg-[var(--table-bg)] px-2 py-1 text-sm"
      aria-label="Дата статуса"
    />
    <span class="text-xs text-[var(--text-secondary)]">Новый статус</span>
  </div>
  <textarea
    bind:value={note}
    placeholder="Комментарий к статусу…"
    rows="2"
    class="resize-y rounded border border-[var(--border)] bg-[var(--table-bg)] px-2 py-1 text-sm outline-none focus:border-[var(--accent)]"
  ></textarea>
  <div class="flex justify-end">
    <Button type="submit" size="sm" disabled={saving}>Добавить</Button>
  </div>
</form>
