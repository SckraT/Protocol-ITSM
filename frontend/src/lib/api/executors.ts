// API для справочника исполнителей.
import { apiDelete, apiGet, apiPost, apiPut } from './client';
import type { Executor, UserOption } from './types';

/** Получить всех исполнителей. */
export async function fetchExecutors(): Promise<Executor[]> {
  return apiGet<Executor[]>('/executors');
}

/** Получить список УЗ (id + username) для привязки исполнителя. */
export async function fetchUserOptions(): Promise<UserOption[]> {
  return apiGet<UserOption[]>('/executors/user-options');
}

/** Создать исполнителя. */
export async function createExecutor(
  name: string,
  departmentId: number | null,
  userId: number | null = null
): Promise<Executor> {
  return apiPost<Executor>('/executors', { name, department_id: departmentId, user_id: userId }, [409]);
}

/** Обновить исполнителя (имя, отдел и/или привязку к УЗ). */
export async function updateExecutor(
  id: number,
  name: string,
  departmentId: number | null,
  userId: number | null = null
): Promise<Executor> {
  return apiPut<Executor>(
    `/executors/${id}`,
    { name, department_id: departmentId, user_id: userId },
    [409]
  );
}

/** Удалить исполнителя. */
export async function deleteExecutor(id: number): Promise<void> {
  return apiDelete(`/executors/${id}`);
}
