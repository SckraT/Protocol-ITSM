<script lang="ts">
  // Поисковый мультиселект исполнителей — удобен при большом числе инженеров и отделов.
  // Возможности: поиск по имени/отделу, выбранные показаны чипами, выпадающий список
  // с группировкой по отделам, сворачивание групп, выбор/снятие всего отдела.
  import { tick } from 'svelte';
  import { ChevronDown, ChevronRight, Search, X, Check } from 'lucide-svelte';
  import { refsStore } from '$lib/stores/refs.svelte';

  let {
    selected = $bindable(new Set<number>()),
    label = 'Исполнители'
  }: {
    selected?: Set<number>;
    label?: string;
  } = $props();

  const NO_DEPT = '— Без отдела —';

  let open = $state(false);
  let query = $state('');
  let collapsed = $state<Set<string>>(new Set()); // свёрнутые отделы
  let container: HTMLDivElement;
  let searchInput = $state<HTMLInputElement | null>(null);

  // Все исполнители (для чипов — быстрый доступ по id)
  const byId = $derived(new Map(refsStore.executors.map((e) => [e.id, e])));

  // Выбранные исполнители (в порядке справочника)
  const selectedList = $derived(refsStore.executors.filter((e) => selected.has(e.id)));

  // Отфильтрованные и сгруппированные по отделу исполнители для выпадающего списка
  const groups = $derived.by(() => {
    const q = query.trim().toLowerCase();
    const map = new Map<string, typeof refsStore.executors>();
    for (const e of refsStore.executors) {
      const dept = e.department_name ?? NO_DEPT;
      if (q && !e.name.toLowerCase().includes(q) && !dept.toLowerCase().includes(q)) continue;
      const list = map.get(dept) ?? [];
      list.push(e);
      map.set(dept, list);
    }
    // Сортируем отделы и людей по алфавиту
    return [...map.entries()]
      .sort((a, b) => a[0].localeCompare(b[0], 'ru'))
      .map(([dept, execs]) => ({
        dept,
        execs: [...execs].sort((a, b) => a.name.localeCompare(b.name, 'ru'))
      }));
  });

  const hasQuery = $derived(query.trim().length > 0);

  function toggle(id: number) {
    const next = new Set(selected);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    selected = next;
  }

  function remove(id: number) {
    const next = new Set(selected);
    next.delete(id);
    selected = next;
  }

  function clearAll() {
    selected = new Set();
  }

  function isDeptCollapsed(dept: string): boolean {
    // При активном поиске показываем все группы развёрнутыми
    return !hasQuery && collapsed.has(dept);
  }

  function toggleDept(dept: string) {
    const next = new Set(collapsed);
    if (next.has(dept)) next.delete(dept);
    else next.add(dept);
    collapsed = next;
  }

  // Сколько из отдела выбрано
  function deptSelectedCount(execs: { id: number }[]): number {
    return execs.reduce((n, e) => n + (selected.has(e.id) ? 1 : 0), 0);
  }

  // Выбрать/снять весь отдел (по видимым в текущем фильтре)
  function toggleDeptAll(execs: { id: number }[]) {
    const allSelected = execs.every((e) => selected.has(e.id));
    const next = new Set(selected);
    for (const e of execs) {
      if (allSelected) next.delete(e.id);
      else next.add(e.id);
    }
    selected = next;
  }

  async function openDropdown() {
    open = true;
    await tick();
    searchInput?.focus();
  }

  function closeDropdown() {
    open = false;
    query = '';
  }

  function onWindowClick(e: MouseEvent) {
    // composedPath фиксируется в момент клика — устойчиво к тому, что кликнутый
    // узел был удалён/заменён при ре-рендере (напр. переключение иконки сворачивания).
    if (open && container && !e.composedPath().includes(container)) closeDropdown();
  }

  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape' && open) {
      e.stopPropagation();
      closeDropdown();
    }
  }
</script>

<svelte:window onclick={onWindowClick} onkeydown={onKeydown} />

<div class="flex flex-col gap-1" bind:this={container}>
  <span class="text-xs font-medium text-[var(--text-secondary)]">
    {label}
    {#if selected.size > 0}
      <span class="text-[var(--accent)]">· выбрано {selected.size}</span>
    {/if}
  </span>

  <!-- Поле-триггер с чипами выбранных -->
  <div
    class="relative flex min-h-[2.5rem] flex-wrap items-center gap-1.5 rounded-md border border-[var(--border)] bg-[var(--table-bg)] p-1.5"
  >
    {#each selectedList as exec (exec.id)}
      <span class="exec-chip gap-1" title={exec.department_name ?? ''}>
        {exec.name}
        <button
          type="button"
          class="rounded-full hover:text-[var(--danger)]"
          aria-label="Убрать {exec.name}"
          onclick={() => remove(exec.id)}
        >
          <X size={12} />
        </button>
      </span>
    {/each}

    <button
      type="button"
      class="ml-auto inline-flex items-center gap-1 rounded px-2 py-1 text-sm text-[var(--text-secondary)] hover:bg-[var(--table-hover)] hover:text-[var(--text-body)]"
      onclick={() => (open ? closeDropdown() : openDropdown())}
    >
      {selected.size === 0 ? 'Выбрать исполнителей' : 'Изменить'}
      <ChevronDown size={14} class={open ? 'rotate-180 transition-transform' : 'transition-transform'} />
    </button>
  </div>

  <!-- Выпадающая панель -->
  {#if open}
    <div
      class="z-20 mt-1 overflow-hidden rounded-md border border-[var(--border)] bg-[var(--bg-primary)] shadow-lg"
    >
      <!-- Поиск -->
      <div class="flex items-center gap-2 border-b border-[var(--border)] px-2.5 py-2">
        <Search size={14} class="shrink-0 text-[var(--text-secondary)]" />
        <input
          bind:this={searchInput}
          bind:value={query}
          placeholder="Поиск по имени или отделу…"
          class="w-full bg-transparent text-sm text-[var(--text-body)] outline-none"
        />
        {#if query}
          <button
            type="button"
            class="shrink-0 text-[var(--text-secondary)] hover:text-[var(--text-body)]"
            aria-label="Очистить поиск"
            onclick={() => (query = '')}
          >
            <X size={14} />
          </button>
        {/if}
      </div>

      <!-- Список групп -->
      <div class="max-h-72 overflow-y-auto py-1">
        {#each groups as group (group.dept)}
          {@const selCount = deptSelectedCount(group.execs)}
          {@const allSel = selCount === group.execs.length}
          <div>
            <!-- Заголовок отдела -->
            <div
              class="flex items-center gap-1 px-2 py-1.5 text-xs font-semibold text-[var(--text-secondary)]"
            >
              <button
                type="button"
                class="inline-flex items-center gap-1 hover:text-[var(--text-body)]"
                onclick={() => toggleDept(group.dept)}
              >
                {#if isDeptCollapsed(group.dept)}
                  <ChevronRight size={13} />
                {:else}
                  <ChevronDown size={13} />
                {/if}
                {group.dept}
              </button>
              <span class="text-[var(--text-secondary)]">({selCount}/{group.execs.length})</span>
              <button
                type="button"
                class="ml-auto rounded px-1.5 py-0.5 text-[11px] font-normal text-[var(--accent)] hover:bg-[var(--table-hover)]"
                onclick={() => toggleDeptAll(group.execs)}
              >
                {allSel ? 'Снять все' : 'Выбрать все'}
              </button>
            </div>

            <!-- Исполнители отдела -->
            {#if !isDeptCollapsed(group.dept)}
              {#each group.execs as exec (exec.id)}
                {@const checked = selected.has(exec.id)}
                <button
                  type="button"
                  class="flex w-full items-center gap-2 px-3 py-1.5 text-left text-sm hover:bg-[var(--table-hover)] {checked
                    ? 'text-[var(--text-body)]'
                    : 'text-[var(--text-secondary)]'}"
                  onclick={() => toggle(exec.id)}
                >
                  <span
                    class="flex h-4 w-4 shrink-0 items-center justify-center rounded border {checked
                      ? 'border-[var(--accent)] bg-[var(--accent)] text-white'
                      : 'border-[var(--border)]'}"
                  >
                    {#if checked}<Check size={12} />{/if}
                  </span>
                  {exec.name}
                </button>
              {/each}
            {/if}
          </div>
        {:else}
          <p class="px-3 py-4 text-center text-sm text-[var(--text-secondary)]">
            {hasQuery ? 'Ничего не найдено' : 'Нет исполнителей в справочнике'}
          </p>
        {/each}
      </div>

      <!-- Подвал -->
      {#if selected.size > 0}
        <div class="flex items-center justify-between border-t border-[var(--border)] px-3 py-2">
          <span class="text-xs text-[var(--text-secondary)]">Выбрано: {selected.size}</span>
          <button
            type="button"
            class="text-xs text-[var(--danger)] hover:underline"
            onclick={clearAll}
          >
            Очистить всё
          </button>
        </div>
      {/if}
    </div>
  {/if}
</div>
