<script lang="ts">
  // Страница совещаний: CRUD + просмотр задач совещания.
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { Plus, Pencil, Trash2, Users, ListTodo, CalendarDays } from 'lucide-svelte';
  import type { Meeting } from '$lib/api/types';
  import { meetingsStore } from '$lib/stores/meetings.svelte';
  import { refsStore } from '$lib/stores/refs.svelte';
  import { confirmStore } from '$lib/stores/confirm.svelte';
  import { fmtDate } from '$lib/utils/date';
  import Modal from '$lib/components/ui/Modal.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import ExecutorMultiSelect from '$lib/components/items/ExecutorMultiSelect.svelte';

  let showModal = $state(false);
  let editingId = $state<number | null>(null);

  // Поля формы
  let title = $state('');
  let meetingDate = $state('');
  let description = $state('');
  let participants = $state<Set<number>>(new Set());
  let saving = $state(false);
  let formError = $state('');

  onMount(async () => {
    await Promise.all([meetingsStore.load(), refsStore.executors.length ? Promise.resolve() : refsStore.load()]);
  });

  const meetings = $derived(meetingsStore.all);

  function openCreate() {
    editingId = null;
    title = '';
    meetingDate = '';
    description = '';
    participants = new Set();
    formError = '';
    showModal = true;
  }

  function openEdit(m: Meeting) {
    editingId = m.id;
    title = m.title;
    meetingDate = m.meeting_date ?? '';
    description = m.description ?? '';
    participants = new Set(m.participants.map((p) => p.id));
    formError = '';
    showModal = true;
  }

  function close() {
    showModal = false;
    formError = '';
  }

  async function submit(e: SubmitEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    saving = true;
    formError = '';
    const payload = {
      title: title.trim(),
      meeting_date: meetingDate || null,
      description: description.trim() || null,
      participant_ids: [...participants]
    };
    try {
      const ok = editingId !== null
        ? await meetingsStore.update(editingId, payload)
        : !!(await meetingsStore.create(payload));
      if (ok) close();
      else formError = 'Не удалось сохранить';
    } finally {
      saving = false;
    }
  }

  async function remove(m: Meeting) {
    const ok = await confirmStore.ask({
      title: 'Удалить совещание?',
      message: `Совещание «${m.title}» будет удалено. Задачи останутся, но потеряют привязку.`,
      confirmLabel: 'Удалить',
      danger: true
    });
    if (ok) await meetingsStore.remove(m.id);
  }

  function openTasks(m: Meeting) {
    goto(`/?meeting=${m.id}`);
  }
</script>

<svelte:head>
  <title>Совещания — Протокол совещаний</title>
</svelte:head>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <h1 class="text-xl font-semibold text-[var(--text-body)]">Совещания</h1>
    <Button variant="primary" onclick={openCreate}>
      <Plus size={16} /> Совещание
    </Button>
  </div>

  {#if meetingsStore.loading}
    <p class="py-16 text-center text-sm text-[var(--text-secondary)]">Загрузка…</p>
  {:else if meetings.length === 0}
    <div class="rounded-lg border border-[var(--border)] bg-[var(--table-bg)] py-16 text-center text-sm text-[var(--text-secondary)]">
      Совещаний пока нет. Создайте первое.
    </div>
  {:else}
    <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {#each meetings as m (m.id)}
        <div class="flex flex-col gap-3 rounded-lg border border-[var(--border)] bg-[var(--table-bg)] p-4">
          <div class="flex items-start justify-between gap-2">
            <h2 class="font-semibold text-[var(--text-body)]">{m.title}</h2>
            <div class="flex shrink-0 gap-1">
              <button
                class="rounded p-1 text-[var(--text-secondary)] hover:text-[var(--accent)]"
                aria-label="Редактировать совещание" title="Редактировать"
                onclick={() => openEdit(m)}
              >
                <Pencil size={15} />
              </button>
              <button
                class="rounded p-1 text-[var(--text-secondary)] hover:text-[var(--danger)]"
                aria-label="Удалить совещание" title="Удалить"
                onclick={() => remove(m)}
              >
                <Trash2 size={15} />
              </button>
            </div>
          </div>

          {#if m.meeting_date}
            <div class="flex items-center gap-1.5 text-xs text-[var(--text-secondary)]">
              <CalendarDays size={13} /> {fmtDate(m.meeting_date)}
            </div>
          {/if}

          {#if m.description}
            <p class="line-clamp-2 text-sm text-[var(--text-secondary)]">{m.description}</p>
          {/if}

          <div class="flex items-center gap-3 text-xs text-[var(--text-secondary)]">
            <span class="inline-flex items-center gap-1" title="Участников">
              <Users size={13} /> {m.participants.length}
            </span>
            <span class="inline-flex items-center gap-1" title="Задач">
              <ListTodo size={13} /> {m.item_count}
            </span>
          </div>

          <button
            class="mt-auto inline-flex items-center gap-1 self-start text-sm text-[var(--accent)] hover:underline"
            onclick={() => openTasks(m)}
          >
            <ListTodo size={14} /> Задачи совещания ({m.item_count})
          </button>
        </div>
      {/each}
    </div>
  {/if}
</div>

<!-- Модальное окно создания/редактирования -->
<Modal open={showModal} title={editingId !== null ? 'Редактировать совещание' : 'Новое совещание'} onClose={close}>
  <form onsubmit={submit} class="flex flex-col gap-4">
    <Input id="m-title" label="Тема *" bind:value={title} disabled={saving} />
    <div class="flex flex-col gap-1">
      <label for="m-date" class="text-xs font-medium text-[var(--text-secondary)]">Дата</label>
      <input
        id="m-date" type="date" bind:value={meetingDate} disabled={saving}
        class="rounded-md border border-[var(--border)] bg-[var(--table-bg)] px-3 py-2 text-sm text-[var(--text-body)] outline-none focus:border-[var(--accent)]"
      />
    </div>
    <div class="flex flex-col gap-1">
      <label for="m-desc" class="text-xs font-medium text-[var(--text-secondary)]">Заметки / протокол</label>
      <textarea
        id="m-desc" bind:value={description} rows="3" disabled={saving}
        class="resize-y rounded-md border border-[var(--border)] bg-[var(--table-bg)] px-3 py-2 text-sm text-[var(--text-body)] outline-none focus:border-[var(--accent)]"
      ></textarea>
    </div>

    <ExecutorMultiSelect bind:selected={participants} label="Участники" />

    {#if formError}
      <p class="rounded bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">{formError}</p>
    {/if}

    <div class="flex justify-end gap-2 pt-1">
      <Button variant="secondary" onclick={close} disabled={saving}>Отмена</Button>
      <Button type="submit" variant="primary" disabled={saving || !title.trim()}>
        {saving ? 'Сохранение…' : editingId !== null ? 'Сохранить' : 'Создать'}
      </Button>
    </div>
  </form>
</Modal>
