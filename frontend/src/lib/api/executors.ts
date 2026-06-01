// API для справочника исполнителей.
import { apiDelete, apiGet, apiPost, apiPut } from './client';
import type { Executor } from './types';

/** Получить всех исполнителей. */
export async function fetchExecutors(): Promise<Executor[]> {
  return apiGet<Executor[]>('/executors');
}

/** Создать исполнителя. */
export async function createExecutor(name: string, departmentId: number | null): Promise<Executor> {
  return apiPost<Executor>('/executors', { name, department_id: departmentId }, [409]);
}

/** Обновить исполнителя (имя и/или отдел). */
export async function updateExecutor(
  id: number,
  name: string,
  departmentId: number | null
): Promise<Executor> {
  return apiPut<Executor>(`/executors/${id}`, { name, department_id: departmentId }, [409]);
}

/** Удалить исполнителя. */
export async function deleteExecutor(id: number): Promise<void> {
  return apiDelete(`/executors/${id}`);
}
