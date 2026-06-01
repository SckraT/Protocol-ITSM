// Главный стор задач: загрузка, фильтрация, сортировка, оптимистичные обновления.
// Svelte 5 Runes.
import {
  createItem as apiCreate,
  deleteItem as apiDelete,
  fetchItems,
  updateItem as apiUpdate
} from '$lib/api/items';
import type { Item, ItemCreatePayload, ItemState, ItemUpdatePayload } from '$lib/api/types';
import { isOverdue } from '$lib/utils/date';
import { PRIORITY_SORT_ORDER, STATE_ORDER } from '$lib/utils/constants';
import { filtersStore } from './filters.svelte';
import { refsStore } from './refs.svelte';
import { toastStore } from './toast.svelte';

class ItemsStore {
  all = $state<Item[]>([]);
  loading = $state(false);
  error = $state<string | null>(null);

  /** Количество просроченных задач — для счётчика в заголовке вкладки. */
  overdueCount = $derived(
    this.all.filter((i) => isOverdue(i.due_date, i.state)).length
  );

  /** Счётчики по состояниям для дашборда. */
  counts = $derived.by(() => {
    const c = { all: this.all.length, in_progress: 0, postponed: 0, closed: 0 };
    for (const i of this.all) c[i.state]++;
    return c;
  });

  /** Отфильтрованный и отсортированный список задач. */
  filtered = $derived.by(() => {
    let result = this.all;
    const f = filtersStore;

    // Фильтр по состоянию (вкладки дашборда)
    if (f.currentFilter) {
      result = result.filter((i) => i.state === f.currentFilter);
    }

    // Поиск по теме, тикету, исполнителям
    if (f.searchQuery) {
      const q = f.searchQuery.toLowerCase();
      result = result.filter(
        (i) =>
          i.topic.toLowerCase().includes(q) ||
          (i.ticket ?? '').toLowerCase().includes(q) ||
          i.executors.some((e) => e.name.toLowerCase().includes(q))
      );
    }

    // Фильтр по отделу: резолвим department_id → имя через справочник,
    // т.к. ItemResponse содержит только department_name исполнителя.
    if (f.filterDept) {
      const deptName = refsStore.departmentName(Number(f.filterDept));
      if (deptName) {
        result = result.filter((i) => i.executors.some((e) => e.department_name === deptName));
      }
    }

    // Фильтр по исполнителю
    if (f.filterExec) {
      const execId = Number(f.filterExec);
      result = result.filter((i) => i.executors.some((e) => e.id === execId));
    }

    // Фильтр по приоритету
    if (f.filterPriority) {
      result = result.filter((i) => (i.priority ?? '') === f.filterPriority);
    }

    // Сортировка
    if (f.sortCol) {
      result = [...result].sort((a, b) => this.compare(a, b, f.sortCol!, f.sortDir));
    }

    return result;
  });

  private compare(a: Item, b: Item, col: string, dir: 'asc' | 'desc'): number {
    let cmp = 0;
    switch (col) {
      case 'topic':
        cmp = a.topic.localeCompare(b.topic, 'ru');
        break;
      case 'priority':
        cmp = PRIORITY_SORT_ORDER[a.priority ?? ''] - PRIORITY_SORT_ORDER[b.priority ?? ''];
        break;
      case 'state':
        cmp = STATE_ORDER.indexOf(a.state) - STATE_ORDER.indexOf(b.state);
        break;
      case 'due_date':
        cmp = (a.due_date ?? '9999').localeCompare(b.due_date ?? '9999');
        break;
      default:
        cmp = a.id - b.id;
    }
    return dir === 'asc' ? cmp : -cmp;
  }

  /** Загрузить все задачи с бэкенда. */
  async load(): Promise<void> {
    this.loading = true;
    this.error = null;
    try {
      const response = await fetchItems({ page_size: 1000 });
      this.all = response.items;
    } catch (e) {
      this.error = e instanceof Error ? e.message : 'Ошибка загрузки';
      toastStore.error(this.error);
    } finally {
      this.loading = false;
    }
  }

  /** Найти задачу по ID. */
  getById(id: number): Item | undefined {
    return this.all.find((i) => i.id === id);
  }

  /** Создать задачу. */
  async create(data: ItemCreatePayload): Promise<Item | null> {
    try {
      const created = await apiCreate(data);
      this.all = [...this.all, created];
      toastStore.success('Задача создана');
      return created;
    } catch (e) {
      toastStore.error(e instanceof Error ? e.message : 'Ошибка создания');
      return null;
    }
  }

  /** Обновить задачу с оптимистичным UI и откатом при ошибке. */
  async update(id: number, data: ItemUpdatePayload): Promise<boolean> {
    const snapshot = this.all;
    // Оптимистичное обновление
    this.all = this.all.map((i) => (i.id === id ? { ...i, ...data } : i));
    try {
      const updated = await apiUpdate(id, data);
      // Синхронизация с ответом сервера (полные связи)
      this.all = this.all.map((i) => (i.id === id ? updated : i));
      return true;
    } catch (e) {
      this.all = snapshot; // откат
      toastStore.error(e instanceof Error ? e.message : 'Ошибка обновления');
      return false;
    }
  }

  /** Изменить состояние задачи (для inline-селекта и bulk). */
  async changeState(id: number, state: ItemState): Promise<boolean> {
    return this.update(id, { state });
  }

  /** Удалить задачу. */
  async remove(id: number): Promise<boolean> {
    const snapshot = this.all;
    this.all = this.all.filter((i) => i.id !== id);
    try {
      await apiDelete(id);
      toastStore.success('Задача удалена');
      return true;
    } catch (e) {
      this.all = snapshot;
      toastStore.error(e instanceof Error ? e.message : 'Ошибка удаления');
      return false;
    }
  }

  /** Обновить одну задачу в сторе (после изменений статусов/исполнителей). */
  replace(item: Item): void {
    this.all = this.all.map((i) => (i.id === item.id ? item : i));
  }
}

export const itemsStore = new ItemsStore();
