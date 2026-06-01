// Стор справочников: отделы и исполнители. Svelte 5 Runes.
import {
  createDepartment as apiCreateDept,
  deleteDepartment as apiDeleteDept,
  fetchDepartments,
  updateDepartment as apiUpdateDept
} from '$lib/api/departments';
import {
  createExecutor as apiCreateExec,
  deleteExecutor as apiDeleteExec,
  fetchExecutors,
  updateExecutor as apiUpdateExec
} from '$lib/api/executors';
import type { Department, Executor } from '$lib/api/types';
import { toastStore } from './toast.svelte';

class RefsStore {
  departments = $state<Department[]>([]);
  executors = $state<Executor[]>([]);
  loading = $state(false);

  /** Отдел по ID. */
  departmentById(id: number): Department | undefined {
    return this.departments.find((d) => d.id === id);
  }

  /** Имя отдела по ID (для фильтрации задач). */
  departmentName(id: number): string | null {
    return this.departmentById(id)?.name ?? null;
  }

  /** Исполнители, сгруппированные по отделу (для UI справочников). */
  executorsByDepartment = $derived.by(() => {
    const groups = new Map<string, Executor[]>();
    for (const e of this.executors) {
      const key = e.department_name ?? '— Без отдела —';
      const list = groups.get(key) ?? [];
      list.push(e);
      groups.set(key, list);
    }
    return groups;
  });

  /** Загрузить отделы и исполнителей. */
  async load(): Promise<void> {
    this.loading = true;
    try {
      const [depts, execs] = await Promise.all([fetchDepartments(), fetchExecutors()]);
      this.departments = depts;
      this.executors = execs;
    } catch (e) {
      toastStore.error(e instanceof Error ? e.message : 'Ошибка загрузки справочников');
    } finally {
      this.loading = false;
    }
  }

  // ── Отделы ──────────────────────────────────────────────────────────────────

  async createDepartment(name: string): Promise<boolean> {
    try {
      const created = await apiCreateDept(name);
      this.departments = [...this.departments, created].sort((a, b) => a.name.localeCompare(b.name, 'ru'));
      toastStore.success('Отдел добавлен');
      return true;
    } catch (e) {
      toastStore.error(e instanceof Error ? e.message : 'Ошибка');
      return false;
    }
  }

  async updateDepartment(id: number, name: string): Promise<boolean> {
    try {
      const updated = await apiUpdateDept(id, name);
      this.departments = this.departments.map((d) => (d.id === id ? updated : d));
      // Обновляем имя отдела у исполнителей
      this.executors = this.executors.map((e) =>
        e.department_id === id ? { ...e, department_name: name } : e
      );
      return true;
    } catch (e) {
      toastStore.error(e instanceof Error ? e.message : 'Ошибка');
      return false;
    }
  }

  async deleteDepartment(id: number): Promise<boolean> {
    try {
      await apiDeleteDept(id);
      this.departments = this.departments.filter((d) => d.id !== id);
      // У исполнителей этого отдела сбрасываем привязку
      this.executors = this.executors.map((e) =>
        e.department_id === id ? { ...e, department_id: null, department_name: null } : e
      );
      toastStore.success('Отдел удалён');
      return true;
    } catch (e) {
      toastStore.error(e instanceof Error ? e.message : 'Ошибка');
      return false;
    }
  }

  // ── Исполнители ─────────────────────────────────────────────────────────────

  async createExecutor(name: string, departmentId: number | null): Promise<boolean> {
    try {
      const created = await apiCreateExec(name, departmentId);
      this.executors = [...this.executors, created];
      toastStore.success('Исполнитель добавлен');
      return true;
    } catch (e) {
      toastStore.error(e instanceof Error ? e.message : 'Ошибка');
      return false;
    }
  }

  async updateExecutor(id: number, name: string, departmentId: number | null): Promise<boolean> {
    try {
      const updated = await apiUpdateExec(id, name, departmentId);
      this.executors = this.executors.map((e) => (e.id === id ? updated : e));
      return true;
    } catch (e) {
      toastStore.error(e instanceof Error ? e.message : 'Ошибка');
      return false;
    }
  }

  async deleteExecutor(id: number): Promise<boolean> {
    try {
      await apiDeleteExec(id);
      this.executors = this.executors.filter((e) => e.id !== id);
      toastStore.success('Исполнитель удалён');
      return true;
    } catch (e) {
      toastStore.error(e instanceof Error ? e.message : 'Ошибка');
      return false;
    }
  }
}

export const refsStore = new RefsStore();
