// API для работы с историей статусов задачи.
import { apiDelete, apiGet, apiPost } from './client';
import type { Status } from './types';

/** Получить все статусы задачи. */
export async function fetchStatuses(itemId: number): Promise<Status[]> {
  return apiGet<Status[]>(`/items/${itemId}/statuses`);
}

/** Добавить статус к задаче. */
export async function addStatus(
  itemId: number,
  data: { status_date: string | null; status_note: string | null }
): Promise<Status> {
  return apiPost<Status>(`/items/${itemId}/statuses`, data);
}

/** Удалить запись статуса. */
export async function deleteStatus(statusId: number): Promise<void> {
  return apiDelete(`/statuses/${statusId}`);
}
