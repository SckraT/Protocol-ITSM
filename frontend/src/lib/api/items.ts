// API для работы с задачами.
import { apiDelete, apiGet, apiPatch, apiPost } from './client';
import type { Item, ItemCreatePayload, ItemUpdatePayload, PaginatedResponse } from './types';

/** Параметры фильтрации списка задач. */
export interface ItemQuery {
  state?: string;
  search?: string;
  executor_id?: number;
  department_id?: number;
  priority?: string;
  page?: number;
  page_size?: number;
}

function buildQuery(params: ItemQuery): string {
  const qs = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      qs.set(key, String(value));
    }
  }
  const s = qs.toString();
  return s ? `?${s}` : '';
}

/** Получить список задач. По умолчанию грузим все (page_size большой) — фильтрация на клиенте. */
export async function fetchItems(query: ItemQuery = {}): Promise<PaginatedResponse<Item>> {
  const params = { page_size: 1000, ...query };
  return apiGet<PaginatedResponse<Item>>(`/items${buildQuery(params)}`);
}

/** Получить одну задачу по ID. */
export async function fetchItem(id: number): Promise<Item> {
  return apiGet<Item>(`/items/${id}`);
}

/** Создать задачу. */
export async function createItem(data: ItemCreatePayload): Promise<Item> {
  return apiPost<Item>('/items', data);
}

/** Частично обновить задачу. */
export async function updateItem(id: number, data: ItemUpdatePayload): Promise<Item> {
  return apiPatch<Item>(`/items/${id}`, data);
}

/** Удалить задачу. */
export async function deleteItem(id: number): Promise<void> {
  return apiDelete(`/items/${id}`);
}
