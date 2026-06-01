// Типы данных API — соответствуют Pydantic-схемам бэкенда v2.0.
// При наличии запущенного бэкенда можно перегенерировать из OpenAPI:
//   npm run generate-types

export type ItemState = 'in_progress' | 'postponed' | 'closed';
export type Priority = 'high' | 'medium' | 'low';
export type Theme = 'light' | 'dark';
export type SortDir = 'asc' | 'desc';

export interface Department {
  id: number;
  name: string;
}

export interface Executor {
  id: number;
  name: string;
  department_id: number | null;
  department_name: string | null;
}

/** Исполнитель в составе задачи (краткая форма из ItemResponse). */
export interface ExecutorInItem {
  id: number;
  name: string;
  department_name: string | null;
}

export interface Status {
  id: number;
  item_id: number;
  status_date: string | null;
  status_note: string | null;
}

/** Запись статуса в составе задачи. */
export interface StatusInItem {
  id: number;
  status_date: string | null;
  status_note: string | null;
}

export interface Item {
  id: number;
  topic: string;
  ticket: string | null;
  priority: Priority | null;
  state: ItemState;
  due_date: string | null;
  created_at: string;
  executors: ExecutorInItem[];
  recent_statuses: StatusInItem[];
  status_count: number;
}

/** Постраничный ответ для списка задач. */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

/** Данные для создания задачи. */
export interface ItemCreatePayload {
  topic: string;
  ticket?: string | null;
  priority?: Priority | null;
  state?: ItemState;
  due_date?: string | null;
  executor_ids?: number[];
  status_date?: string | null;
  status_note?: string | null;
}

/** Данные для частичного обновления задачи (PATCH). */
export interface ItemUpdatePayload {
  topic?: string;
  ticket?: string | null;
  priority?: Priority | null;
  state?: ItemState;
  due_date?: string | null;
  executor_ids?: number[];
}
