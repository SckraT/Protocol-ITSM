<script lang="ts">
  // Форма задачи: поля + мультивыбор исполнителей, сгруппированных по отделам.
  import { untrack } from 'svelte';
  import type { Item, ItemState, Priority } from '$lib/api/types';
  import Button from '$lib/components/ui/Button.svelte';
  import { refsStore } from '$lib/stores/refs.svelte';
  import { STATE_LABEL, STATE_ORDER, PRIORITY_CONFIG } from '$lib/utils/constants';

  let {
    item = null,
    onSave,
    onDelete
  }: {
    item?: Item | null;
    onSave: (data: {
      topic: string;
      ticket: string | null;
      priority: Priority | null;
      state: ItemState;
      due_date: string | null;
      executor_ids: number[];
    }) => Promise<void>;
    onDelete?: () => void;
  } = $props();

  // Начальные значения формы. Захватываем единожды через untrack — форма
  // пересоздаётся родителем через {#key itemId} при смене задачи.
  const init = untrack(() => ({
    topic: item?.topic ?? '',
    ticket: item?.ticket ?? '',
    priority: (item?.priority ?? '') as string,
    state: (item?.state ?? 'in_progress') as ItemState,
    dueDate: item?.due_date ?? '',
    executorIds: new Set(item?.executors.map((e) => e.id) ?? [])
  }));

  let topic = $state(init.topic);
  let ticket = $state(init.ticket);
  let priority = $state<string>(init.priority);
  let stateVal = $state<ItemState>(init.state);
  let dueDate = $state(init.dueDate);
  let selectedExecutors = $state<Set<number>>(init.executorIds);
  let saving = $state(false);

  // Исполнители, сгруппированные по отделам
  const grouped = $derived(refsStore.executorsByDepartment);

  function toggleExecutor(id: number) {
    const next = new Set(selectedExecutors);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    selectedExecutors = next;
  }

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

  <!-- Исполнители -->
  <div class="flex flex-col gap-1">
    <span class={labelClass}>Исполнители</span>
    <div class="max-h-48 overflow-y-auto rounded-md border border-[var(--border)] p-2">
      {#each [...grouped.entries()] as [deptName, execs] (deptName)}
        <div class="mb-2">
          <div class="mb-1 text-xs font-semibold text-[var(--text-secondary)]">{deptName}</div>
          <div class="flex flex-wrap gap-2">
            {#each execs as exec (exec.id)}
              <label
                class="inline-flex cursor-pointer items-center gap-1 rounded border border-[var(--border)] px-2 py-1 text-sm hover:bg-[var(--table-hover)]"
              >
                <input
                  type="checkbox"
                  checked={selectedExecutors.has(exec.id)}
                  onchange={() => toggleExecutor(exec.id)}
                />
                {exec.name}
              </label>
            {/each}
          </div>
        </div>
      {:else}
        <p class="text-sm text-[var(--text-secondary)]">Нет исполнителей в справочнике</p>
      {/each}
    </div>
  </div>

  <!-- Кнопки -->
  <div class="flex items-center justify-between">
    {#if onDelete}
      <Button variant="danger" size="sm" onclick={onDelete}>Удалить</Button>
    {:else}
      <span></span>
    {/if}
    <Button type="submit" disabled={saving}>{item ? 'Сохранить' : 'Создать'}</Button>
  </div>
</form>
