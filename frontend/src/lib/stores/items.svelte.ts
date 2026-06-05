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
import { filterAndSortItems } from '$lib/utils/itemFilter';
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

  /**
   * Отфильтрованный и отсортированный список задач.
   * Клиент — источник истины для отображаемого списка: грузим все задачи один раз
   * (load → page_size:1000) и фильтруем/сортируем в памяти. Бэкенд-фильтры
   * (item_repository.list_with_filters) оставлены для API/экспорта, в UI не используются.
   * Сама логика — в чистом utils/itemFilter.ts (тестируется изолированно).
   */
  filtered = $derived.by(() => {
    const f = filtersStore;
    // Отдел: резолвим id → имя через справочник (ItemResponse хранит только имя отдела).
    const departmentName = f.filterDept ? refsStore.departmentName(Number(f.filterDept)) : null;
    return filterAndSortItems(this.all, {
      state: f.currentFilter,
      search: f.searchQuery,
      departmentName,
      executorId: f.filterExec ? Number(f.filterExec) : null,
      priority: f.filterPriority,
      meetingId: f.filterMeeting ? Number(f.filterMeeting) : null,
      sortCol: f.sortCol,
      sortDir: f.sortDir
    });
  });

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

  /** Обновить задачу с оптимистичным UI и откатом при ошибке.
   * silent — не показывать тост ошибки (для bulk, где тост агрегируется вызывающим). */
  async update(id: number, data: ItemUpdatePayload, silent = false): Promise<boolean> {
    const snapshot = this.all;
    // Оптимистичное обновление: применяем только поля Item.
    // executor_ids — поле payload, а не Item (в Item исполнители лежат в executors),
    // исключаем, чтобы не класть лишний ключ в объект задачи.
    const { executor_ids, ...itemFields } = data;
    void executor_ids;
    this.all = this.all.map((i) => (i.id === id ? { ...i, ...itemFields } : i));
    try {
      const updated = await apiUpdate(id, data);
      // Синхронизация с ответом сервера (полные связи)
      this.all = this.all.map((i) => (i.id === id ? updated : i));
      return true;
    } catch (e) {
      this.all = snapshot; // откат
      if (!silent) toastStore.error(e instanceof Error ? e.message : 'Ошибка обновления');
      return false;
    }
  }

  /** Изменить состояние задачи (для inline-селекта и bulk). */
  async changeState(id: number, state: ItemState): Promise<boolean> {
    return this.update(id, { state });
  }

  /** Удалить задачу.
   * silent — не показывать тосты (для bulk, где результат агрегируется вызывающим). */
  async remove(id: number, silent = false): Promise<boolean> {
    const snapshot = this.all;
    this.all = this.all.filter((i) => i.id !== id);
    try {
      await apiDelete(id);
      if (!silent) toastStore.success('Задача удалена');
      return true;
    } catch (e) {
      this.all = snapshot;
      if (!silent) toastStore.error(e instanceof Error ? e.message : 'Ошибка удаления');
      return false;
    }
  }

  /**
   * Массовая смена состояния. Индивидуальные тосты подавлены — возвращает счётчики,
   * чтобы вызывающий показал один агрегированный тост.
   * Последовательно (не Promise.all): параллель ломала бы оптимистичные snapshot/откат.
   */
  async bulkChangeState(ids: number[], state: ItemState): Promise<{ ok: number; failed: number }> {
    let ok = 0;
    for (const id of ids) {
      if (await this.update(id, { state }, true)) ok++;
    }
    return { ok, failed: ids.length - ok };
  }

  /** Массовое удаление. Тосты подавлены — возвращает счётчики (см. bulkChangeState). */
  async bulkRemove(ids: number[]): Promise<{ ok: number; failed: number }> {
    let ok = 0;
    for (const id of ids) {
      if (await this.remove(id, true)) ok++;
    }
    return { ok, failed: ids.length - ok };
  }

  /** Обновить одну задачу в сторе (после изменений статусов/исполнителей). */
  replace(item: Item): void {
    this.all = this.all.map((i) => (i.id === item.id ? item : i));
  }
}

export const itemsStore = new ItemsStore();
