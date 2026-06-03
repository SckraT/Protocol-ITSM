<script lang="ts">
  // Форма задачи: поля + мультивыбор исполнителей, сгруппированных по отделам.
  // Кнопки «Сохранить»/«Удалить» вынесены в ItemDrawer (после блока статусов)
  // и связаны с этой формой через атрибут form="item-edit-form".
  import { untrack } from 'svelte';
  import type { Item, ItemState, Priority } from '$lib/api/types';
  import { STATE_LABEL, STATE_ORDER, PRIORITY_CONFIG } from '$lib/utils/constants';
  import { meetingsStore } from '$lib/stores/meetings.svelte';
  import ExecutorMultiSelect from './ExecutorMultiSelect.svelte';

  let {
    item = null,
    onSave,
    saving = $bindable(false)
  }: {
    item?: Item | null;
    onSave: (data: {
      topic: string;
      ticket: string | null;
      priority: Priority | null;
      state: ItemState;
      due_date: string | null;
      meeting_id: number | null;
      executor_ids: number[];
    }) => Promise<void>;
    saving?: boolean;
  } = $props();

  // Начальные значения формы. Захватываем единожды через untrack — форма
  // пересоздаётся родителем через {#key itemId} при смене задачи.
  const init = untrack(() => ({
    topic: item?.topic ?? '',
    ticket: item?.ticket ?? '',
    priority: (item?.priority ?? '') as string,
    state: (item?.state ?? 'in_progress') as ItemState,
    dueDate: item?.due_date ?? '',
    meeting: item?.meeting_id != null ? String(item.meeting_id) : '',
    executorIds: new Set(item?.executors.map((e) => e.id) ?? [])
  }));

  let topic = $state(init.topic);
  let ticket = $state(init.ticket);
  let priority = $state<string>(init.priority);
  let stateVal = $state<ItemState>(init.state);
  let dueDate = $state(init.dueDate);
  let meetingVal = $state<string>(init.meeting);
  let selectedExecutors = $state<Set<number>>(init.executorIds);

  const meetings = $derived(meetingsStore.all);

  async function submit() {
    if (!topic.trim()) return;
    saving = true;
    try {
      await onSave({
        topic: topic.trim(),
        ticket: ticket.trim() || null,
        priority: (priority || null) as Priority | null,
        state: stateVal,
        due_date: dueDate || null,
        meeting_id: meetingVal ? Number(meetingVal) : null,
        executor_ids: [...selectedExecutors]
      });
    } finally {
      saving = false;
    }
  }

  const fieldClass =
    'rounded-md border border-[var(--border)] bg-[var(--table-bg)] px-3 py-2 text-sm text-[var(--text-body)] outline-none focus:border-[var(--accent)]';
  const labelClass = 'text-xs font-medium text-[var(--text-secondary)]';
</script>

<form
  id="item-edit-form"
  class="flex flex-col gap-4"
  onsubmit={(e) => {
    e.preventDefault();
    submit();
  }}
>
  <!-- Тема -->
  <div class="flex flex-col gap-1">
    <label for="f-topic" class={labelClass}>Тема *</label>
    <textarea id="f-topic" bind:value={topic} rows="2" class="{fieldClass} resize-y" required
    ></textarea>
  </div>

  <div class="grid grid-cols-2 gap-3">
    <!-- Тикет -->
    <div class="flex flex-col gap-1">
      <label for="f-ticket" class={labelClass}>Тикет</label>
      <input id="f-ticket" bind:value={ticket} class={fieldClass} />
    </div>
    <!-- Срок -->
    <div class="flex flex-col gap-1">
      <label for="f-due" class={labelClass}>Срок</label>
      <input id="f-due" type="date" bind:value={dueDate} class={fieldClass} />
    </div>
    <!-- Приоритет -->
    <div class="flex flex-col gap-1">
      <label for="f-prio" class={labelClass}>Приоритет</label>
      <select id="f-prio" bind:value={priority} class={fieldClass}>
        <option value="">—</option>
        {#each Object.entries(PRIORITY_CONFIG) as [key, cfg] (key)}
          <option value={key}>{cfg.label}</option>
        {/each}
      </select>
    </div>
    <!-- Состояние -->
    <div class="flex flex-col gap-1">
      <label for="f-state" class={labelClass}>Состояние</label>
      <select id="f-state" bind:value={stateVal} class={fieldClass}>
        {#each STATE_ORDER as st (st)}
          <option value={st}>{STATE_LABEL[st]}</option>
        {/each}
      </select>
    </div>
  </div>

  <!-- Совещание -->
  <div class="flex flex-col gap-1">
    <label for="f-meeting" class={labelClass}>Совещание</label>
    <select id="f-meeting" bind:value={meetingVal} class={fieldClass}>
      <option value="">— Без совещания —</option>
      {#each meetings as m (m.id)}
        <option value={String(m.id)}>{m.title}</option>
      {/each}
    </select>
  </div>

  <!-- Исполнители — поисковый мультиселект -->
  <ExecutorMultiSelect bind:selected={selectedExecutors} />
</form>
