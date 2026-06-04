<script lang="ts">
  // Список исполнителей с группировкой по отделам, добавлением и редактированием.
  import { onMount } from 'svelte';
  import { Check, Pencil, Trash2, X } from 'lucide-svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { refsStore } from '$lib/stores/refs.svelte';
  import { confirmStore } from '$lib/stores/confirm.svelte';

  let newName = $state('');
  let newDept = $state<string>('');
  let newUser = $state<string>('');
  let editingId = $state<number | null>(null);
  let editName = $state('');
  let editDept = $state<string>('');
  let editUser = $state<string>('');

  onMount(() => {
    refsStore.loadUserOptions();
  });

  async function add() {
    if (!newName.trim()) return;
    const ok = await refsStore.createExecutor(
      newName.trim(),
      newDept ? Number(newDept) : null,
      newUser ? Number(newUser) : null
    );
    if (ok) {
      newName = '';
      newDept = '';
      newUser = '';
    }
  }

  function startEdit(id: number, name: string, deptId: number | null, userId: number | null) {
    editingId = id;
    editName = name;
    editDept = deptId ? String(deptId) : '';
    editUser = userId ? String(userId) : '';
  }

  async function saveEdit() {
    if (editingId === null || !editName.trim()) return;
    const ok = await refsStore.updateExecutor(
      editingId,
      editName.trim(),
      editDept ? Number(editDept) : null,
      editUser ? Number(editUser) : null
    );
    if (ok) editingId = null;
  }

  async function remove(id: number, name: string) {
    const ok = await confirmStore.ask({
      title: 'Удалить исполнителя?',
      message: `Исполнитель «${name}» будет удалён из справочника.`,
      confirmLabel: 'Удалить',
      danger: true
    });
    if (ok) await refsStore.deleteExecutor(id);
  }

  const grouped = $derived(refsStore.executorsByDepartment);

  const inputClass =
    'rounded border border-[var(--border)] bg-[var(--table-bg)] px-2 py-1 text-sm outline-none focus:border-[var(--accent)]';
</script>

<section class="rounded-lg border border-[var(--border)] bg-[var(--table-bg)] p-4">
  <h2 class="mb-3 font-semibold">Исполнители ({refsStore.executors.length})</h2>

  <!-- Форма добавления -->
  <form
    class="mb-3 flex gap-2"
    onsubmit={(e) => {
      e.preventDefault();
      add();
    }}
  >
    <input bind:value={newName} placeholder="Имя исполнителя…" class="{inputClass} flex-1" />
    <select bind:value={newDept} class={inputClass} aria-label="Отдел">
      <option value="">Без отдела</option>
      {#each refsStore.departments as dept (dept.id)}
        <option value={String(dept.id)}>{dept.name}</option>
      {/each}
    </select>
    {#if refsStore.userOptions.length > 0}
      <select bind:value={newUser} class={inputClass} aria-label="Учётная запись">
        <option value="">Без УЗ</option>
        {#each refsStore.userOptions as u (u.id)}
          <option value={String(u.id)}>{u.username}</option>
        {/each}
      </select>
    {/if}
    <Button type="submit" size="sm">Добавить</Button>
  </form>

  <div class="flex flex-col gap-3">
    {#each [...grouped.entries()] as [deptName, execs] (deptName)}
      <div>
        <div class="mb-1 border-b border-[var(--border)] pb-1 text-xs font-semibold text-[var(--text-secondary)]">
          {deptName}
        </div>
        <ul class="flex flex-col gap-1">
          {#each execs as exec (exec.id)}
            <li class="flex items-center gap-2 rounded px-2 py-1.5 hover:bg-[var(--table-hover)]">
              {#if editingId === exec.id}
                <input bind:value={editName} class="{inputClass} flex-1" />
                <select bind:value={editDept} class={inputClass} aria-label="Отдел">
                  <option value="">Без отдела</option>
                  {#each refsStore.departments as dept (dept.id)}
                    <option value={String(dept.id)}>{dept.name}</option>
                  {/each}
                </select>
                {#if refsStore.userOptions.length > 0}
                  <select bind:value={editUser} class={inputClass} aria-label="Учётная запись">
                    <option value="">Без УЗ</option>
                    {#each refsStore.userOptions as u (u.id)}
                      <option value={String(u.id)}>{u.username}</option>
                    {/each}
                  </select>
                {/if}
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
                <span class="flex-1">{exec.name}</span>
                {#if exec.user}
                  <span class="rounded bg-[var(--accent)]/10 px-1.5 py-0.5 text-xs text-[var(--accent)]" title="Учётная запись">
                    @{exec.user.username}
                  </span>
                {/if}
                <button
                  class="text-[var(--text-secondary)] hover:text-[var(--accent)]"
                  aria-label="Редактировать"
                  onclick={() => startEdit(exec.id, exec.name, exec.department_id, exec.user_id)}
                >
                  <Pencil size={14} />
                </button>
                <button
                  class="text-[var(--text-secondary)] hover:text-[var(--danger)]"
                  aria-label="Удалить"
                  onclick={() => remove(exec.id, exec.name)}
                >
                  <Trash2 size={14} />
                </button>
              {/if}
            </li>
          {/each}
        </ul>
      </div>
    {:else}
      <p class="text-sm text-[var(--text-secondary)]">Нет исполнителей</p>
    {/each}
  </div>
</section>
