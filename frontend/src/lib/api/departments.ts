// API для справочника отделов.
import { apiDelete, apiGet, apiPost, apiPut } from './client';
import type { Department } from './types';

/** Получить все отделы. */
export async function fetchDepartments(): Promise<Department[]> {
  return apiGet<Department[]>('/departments');
}

/** Создать отдел. allow [409] — конфликт имени обрабатывается вызывающим кодом. */
export async function createDepartment(name: string): Promise<Department> {
  return apiPost<Department>('/departments', { name }, [409]);
}

/** Переименовать отдел. */
export async function updateDepartment(id: number, name: string): Promise<Department> {
  return apiPut<Department>(`/departments/${id}`, { name }, [409]);
}

/** Удалить отдел. */
export async function deleteDepartment(id: number): Promise<void> {
  return apiDelete(`/departments/${id}`);
}
