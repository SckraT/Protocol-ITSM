import type { Item, Executor, Department, Status } from './types';

async function apiFetch(url: string, options: RequestInit = {}, allow: number[] = []): Promise<Response> {
  let res: Response;
  try {
    res = await fetch(url, options);
  } catch {
    throw new Error('network');
  }
  if (!res.ok && !allow.includes(res.status)) {
    throw new Error('HTTP ' + res.status);
  }
  return res;
}

const JSON_HEADERS = { 'Content-Type': 'application/json' };

// ── Items ──────────────────────────────────────────────────────────────────────

export async function fetchItems(): Promise<Item[]> {
  return (await apiFetch('/api/items')).json();
}

export async function createItem(data: object): Promise<Item> {
  return (await apiFetch('/api/items', { method: 'POST', headers: JSON_HEADERS, body: JSON.stringify(data) })).json();
}

export async function updateItem(id: number, data: object): Promise<void> {
  await apiFetch(`/api/items/${id}`, { method: 'PUT', headers: JSON_HEADERS, body: JSON.stringify(data) });
}

export async function deleteItemApi(id: number): Promise<void> {
  await apiFetch(`/api/items/${id}`, { method: 'DELETE' });
}

// ── Statuses ───────────────────────────────────────────────────────────────────

export async function fetchStatuses(itemId: number): Promise<Status[]> {
  return (await apiFetch(`/api/items/${itemId}/statuses`)).json();
}

export async function addStatus(itemId: number, data: { status_date: string | null; status_note: string | null }): Promise<Status> {
  return (await apiFetch(`/api/items/${itemId}/statuses`, { method: 'POST', headers: JSON_HEADERS, body: JSON.stringify(data) })).json();
}

export async function deleteStatusApi(statusId: number): Promise<void> {
  await apiFetch(`/api/statuses/${statusId}`, { method: 'DELETE' });
}

// ── Departments ────────────────────────────────────────────────────────────────

export async function fetchDepartments(): Promise<Department[]> {
  return (await apiFetch('/api/departments')).json();
}

export async function createDepartment(name: string): Promise<Response> {
  return apiFetch('/api/departments', { method: 'POST', headers: JSON_HEADERS, body: JSON.stringify({ name }) }, [409]);
}

export async function updateDepartment(id: number, name: string): Promise<Response> {
  return apiFetch(`/api/departments/${id}`, { method: 'PUT', headers: JSON_HEADERS, body: JSON.stringify({ name }) }, [409]);
}

export async function deleteDepartmentApi(id: number): Promise<void> {
  await apiFetch(`/api/departments/${id}`, { method: 'DELETE' });
}

// ── Executors ──────────────────────────────────────────────────────────────────

export async function fetchExecutors(): Promise<Executor[]> {
  return (await apiFetch('/api/executors')).json();
}

export async function createExecutor(name: string, department_id: number | null): Promise<Response> {
  return apiFetch('/api/executors', { method: 'POST', headers: JSON_HEADERS, body: JSON.stringify({ name, department_id }) }, [409]);
}

export async function updateExecutor(id: number, name: string, department_id: number | null): Promise<Response> {
  return apiFetch(`/api/executors/${id}`, { method: 'PUT', headers: JSON_HEADERS, body: JSON.stringify({ name, department_id }) }, [409]);
}

export async function deleteExecutorApi(id: number): Promise<void> {
  await apiFetch(`/api/executors/${id}`, { method: 'DELETE' });
}

// ── Export / Import ────────────────────────────────────────────────────────────

export function exportCsv(): void {
  window.location.href = '/api/export/csv';
}

export async function importCsv(file: File): Promise<{ imported: number }> {
  const fd = new FormData();
  fd.append('file', file);
  return (await apiFetch('/api/import/csv', { method: 'POST', body: fd })).json();
}
