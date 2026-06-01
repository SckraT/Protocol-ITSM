<script lang="ts">
  // Список отделов с добавлением, inline-редактированием и удалением.
  import { Check, Pencil, Trash2, X } from 'lucide-svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { refsStore } from '$lib/stores/refs.svelte';
  import { confirmStore } from '$lib/stores/confirm.svelte';

  let newName = $state('');
  let editingId = $state<number | null>(null);
  let editName = $state('');

  // Количество исполнителей в отделе
  function execCount(deptId: number): number {
    return refsStore.executors.filter((e) => e.department_id === deptId).length;
  }

  async function add() {
    if (!newName.trim()) return;
    const ok = await refsStore.createDepartment(newName.trim());
    if (ok) newName = '';
  }

  function startEdit(id: number, name: string) {
    editingId = id;
    editName = name;
  }

  async function saveEdit() {
    if (editingId === null || !editName.trim()) return;
    const ok = await refsStore.updateDepartment(editingId, editName.trim());
    if (ok) editingId = null;
  }

  async function remove(id: number, name: string) {
    const ok = await confirmStore.ask({
      title: 'Удалить отдел?',
      message: `Отдел «${name}» будет удалён. У исполнителей отдела привязка сбросится.`,
      confirmLabel: 'Удалить',
      danger: true
    });
    if (ok) await refsStore.deleteDepartment(id);
  }

  const inputClass =
    'flex-1 rounded border border-[var(--border)] bg-[var(--table-bg)] px-2 py-1 text-sm outline-none focus:border-[var(--accent)]';
</script>

<section class="rounded-lg border border-[var(--border)] bg-[var(--table-bg)] p-4">
  <h2 class="mb-3 font-semibold">Отделы ({refsStore.departments.length})</h2>

  <!-- Форма добавления -->
  <form
    class="mb-3 flex gap-2"
    onsubmit={(e) => {
      e.preventDefault();
      add();
    }}
  >
    <input bind:value={newName} placeholder="Новый отдел…" class={inputClass} />
    <Button type="submit" size="sm">Добавить</Button>
  </form>

  <ul class="flex flex-col gap-1">
    {#each refsStore.departments as dept (dept.id)}
      <li class="flex items-center gap-2 rounded px-2 py-1.5 hover:bg-[var(--table-hover)]">
        {#if editingId === dept.id}
          <input bind:value={editName} class={inputClass} />
          <button class="text-[var(--success)]" aria-label="Сохранить" onclick={saveEdit}>
            <Check size={16} />
          </button>
          <button
            class="text-[var(--text-secondary)]"
            aria-label="Отмена"
            onclick={() => (editingId = null)}
          >
            <X size={16} />
          </button>
        {:else}
          <span class="flex-1">{dept.name}</span>
          <span class="rounded bg-[var(--blue-light)] px-1.5 text-xs text-[var(--accent)]">
            {execCount(dept.id)}
          </span>
          <button
            class="text-[var(--text-secondary)] hover:text-[var(--accent)]"
            aria-label="Редактировать"
            onclick={() => startEdit(dept.id, dept.name)}
          >
            <Pencil size={14} />
          </button>
          <button
            class="text-[var(--text-secondary)] hover:text-[var(--danger)]"
            aria-label="Удалить"
            onclick={() => remove(dept.id, dept.name)}
          >
            <Trash2 size={14} />
          </button>
        {/if}
      </li>
    {:else}
      <li class="text-sm text-[var(--text-secondary)]">Нет отделов</li>
    {/each}
  </ul>
</section>
