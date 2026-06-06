<script lang="ts">
  // Таблица задач: сортируемые колонки, выбор строк, пагинация.
  import { ChevronDown, ChevronUp } from 'lucide-svelte';
  import type { ItemState } from '$lib/api/types';
  import ItemRow from './ItemRow.svelte';
  import Pagination from '$lib/components/common/Pagination.svelte';
  import Loader from '$lib/components/ui/Loader.svelte';
  import { itemsStore } from '$lib/stores/items.svelte';
  import { filtersStore } from '$lib/stores/filters.svelte';
  import { selectionStore } from '$lib/stores/selection.svelte';

  let { onOpen }: { onOpen: (id: number) => void } = $props();

  // Пагинация поверх отфильтрованного списка
  const paged = $derived.by(() => {
    const start = (filtersStore.currentPage - 1) * filtersStore.pageSize;
    return itemsStore.filtered.slice(start, start + filtersStore.pageSize);
  });

  // Видимые id на текущей странице — для «выбрать все»
  const pageIds = $derived(paged.map((i) => i.id));
  const allSelected = $derived(pageIds.length > 0 && pageIds.every((id) => selectionStore.has(id)));

  const columns: { key: string; label: string; sortable: boolean }[] = [
    { key: 'topic', label: 'Тема', sortable: true },
    { key: 'ticket', label: 'Тикет', sortable: false },
    { key: 'priority', label: 'Приоритет', sortable: true },
    { key: 'state', label: 'Состояние', sortable: true },
    { key: 'due_date', label: 'Срок', sortable: true },
    { key: 'executors', label: 'Исполнители', sortable: false },
    { key: 'status', label: 'Последний статус', sortable: false }
  ];

  function toggleSelectAll() {
    selectionStore.setAll(pageIds, !allSelected);
  }

  function handleStateChange(id: number, state: ItemState) {
    itemsStore.changeState(id, state);
  }
</script>

{#if itemsStore.loading}
  <Loader />
{:else if itemsStore.error}
  <div class="rounded-md bg-[var(--red-light)] p-4 text-[var(--danger)]">
    Ошибка: {itemsStore.error}
  </div>
{:else if itemsStore.filtered.length === 0}
  <div class="p-8 text-center text-[var(--text-secondary)]">Нет задач</div>
{:else}
  <div class="table-wrap overflow-x-auto rounded-lg border border-[var(--border)]">
    <!-- table-fixed + colgroup: ширины столбцов фиксированы и не зависят от
         содержимого, поэтому не «прыгают» при смене фильтра. Сумма ≈ 100%. -->
    <table class="w-full table-fixed text-sm">
      <colgroup>
        <col class="w-[3%]" />
        <!-- № -->
        <col class="w-[4%]" />
        <!-- Тема -->
        <col class="w-[20%]" />
        <!-- Тикет -->
        <col class="w-[9%]" />
        <!-- Приоритет -->
        <col class="w-[9%]" />
        <!-- Состояние -->
        <col class="w-[11%]" />
        <!-- Срок -->
        <col class="w-[10%]" />
        <!-- Исполнители -->
        <col class="w-[17%]" />
        <!-- Последний статус -->
        <col class="w-[17%]" />
      </colgroup>
      <thead class="bg-[var(--table-hover)] text-left text-xs text-[var(--text-secondary)]">
        <tr>
          <th class="px-3 py-2">
            <input
              type="checkbox"
              checked={allSelected}
              onchange={toggleSelectAll}
              aria-label="Выбрать все на странице"
            />
          </th>
          <th class="px-3 py-2">№</th>
          {#each columns as col (col.key)}
            <th class="px-3 py-2">
              {#if col.sortable}
                <button
                  class="inline-flex items-center gap-1 hover:text-[var(--text-body)]"
                  onclick={() => filtersStore.toggleSort(col.key)}
                >
                  {col.label}
                  {#if filtersStore.sortCol === col.key}
                    {#if filtersStore.sortDir === 'asc'}
                      <ChevronUp size={12} />
                    {:else}
                      <ChevronDown size={12} />
                    {/if}
                  {/if}
                </button>
              {:else}
                {col.label}
              {/if}
            </th>
          {/each}
        </tr>
      </thead>
      <tbody>
        {#each paged as item (item.id)}
          <ItemRow
            {item}
            selected={selectionStore.has(item.id)}
            onToggleSelect={(id) => selectionStore.toggle(id)}
            {onOpen}
            onStateChange={handleStateChange}
          />
        {/each}
      </tbody>
    </table>
  </div>

  <Pagination
    page={filtersStore.currentPage}
    pageSize={filtersStore.pageSize}
    total={itemsStore.filtered.length}
    onPage={(p) => (filtersStore.currentPage = p)}
    onPageSize={(s) => {
      filtersStore.pageSize = s;
      filtersStore.currentPage = 1;
      filtersStore.persist();
    }}
  />
{/if}
