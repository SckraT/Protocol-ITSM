// Чистая логика фильтрации и сортировки задач для UI.
// Клиент — источник истины для отображаемого списка (см. комментарий в items.svelte.ts).
// Логика вынесена из стора без изменений, чтобы её можно было тестировать изолированно.
import type { Item, SortDir } from '$lib/api/types';
import { PRIORITY_SORT_ORDER, STATE_ORDER } from './constants';

/** Критерии фильтрации/сортировки. null/пустая строка означает «фильтр не применяется». */
export interface ItemFilterCriteria {
  /** Состояние (вкладка дашборда). */
  state?: string;
  /** Поиск по теме, тикету, именам исполнителей. */
  search?: string;
  /** Имя отдела (резолвится вызывающим через справочник; null — не фильтровать). */
  departmentName?: string | null;
  /** ID исполнителя (null — не фильтровать). */
  executorId?: number | null;
  /** Приоритет. */
  priority?: string;
  /** ID совещания (null — не фильтровать; 0 — соответствует meeting_id === 0). */
  meetingId?: number | null;
  /** Колонка сортировки (null — без сортировки). */
  sortCol?: string | null;
  /** Направление сортировки. */
  sortDir?: SortDir;
}

/** Сравнение двух задач по колонке и направлению (стабильное по id). */
export function compareItems(a: Item, b: Item, col: string, dir: SortDir): number {
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

/** Применяет фильтры и сортировку к списку задач. Возвращает новый массив. */
export function filterAndSortItems(items: Item[], c: ItemFilterCriteria): Item[] {
  let result = items;

  // Фильтр по состоянию (вкладки дашборда)
  if (c.state) {
    result = result.filter((i) => i.state === c.state);
  }

  // Поиск по теме, тикету, исполнителям
  if (c.search) {
    const q = c.search.toLowerCase();
    result = result.filter(
      (i) =>
        i.topic.toLowerCase().includes(q) ||
        (i.ticket ?? '').toLowerCase().includes(q) ||
        i.executors.some((e) => e.name.toLowerCase().includes(q))
    );
  }

  // Фильтр по отделу: имя отдела резолвит вызывающий (ItemResponse содержит только
  // department_name исполнителя, не id).
  if (c.departmentName) {
    result = result.filter((i) => i.executors.some((e) => e.department_name === c.departmentName));
  }

  // Фильтр по исполнителю
  if (c.executorId != null) {
    result = result.filter((i) => i.executors.some((e) => e.id === c.executorId));
  }

  // Фильтр по приоритету
  if (c.priority) {
    result = result.filter((i) => (i.priority ?? '') === c.priority);
  }

  // Фильтр по совещанию
  if (c.meetingId != null) {
    result = result.filter((i) => i.meeting_id === c.meetingId);
  }

  // Сортировка
  if (c.sortCol) {
    const col = c.sortCol;
    const dir = c.sortDir ?? 'asc';
    result = [...result].sort((a, b) => compareItems(a, b, col, dir));
  }

  return result;
}
