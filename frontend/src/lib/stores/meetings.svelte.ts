// Стор совещаний. Svelte 5 Runes.
import {
  createMeeting as apiCreate,
  deleteMeeting as apiDelete,
  fetchMeetings,
  updateMeeting as apiUpdate
} from '$lib/api/meetings';
import type { Meeting, MeetingCreatePayload, MeetingUpdatePayload } from '$lib/api/types';
import { toastStore } from './toast.svelte';

class MeetingsStore {
  all = $state<Meeting[]>([]);
  loading = $state(false);

  /** Совещание по ID. */
  byId(id: number): Meeting | undefined {
    return this.all.find((m) => m.id === id);
  }

  /** Название совещания по ID. */
  titleById(id: number | null): string | null {
    if (id === null) return null;
    return this.byId(id)?.title ?? null;
  }

  /** Загрузить все совещания. */
  async load(): Promise<void> {
    this.loading = true;
    try {
      const res = await fetchMeetings();
      this.all = res.items;
    } catch (e) {
      toastStore.error(e instanceof Error ? e.message : 'Ошибка загрузки совещаний');
    } finally {
      this.loading = false;
    }
  }

  async create(data: MeetingCreatePayload): Promise<Meeting | null> {
    try {
      const created = await apiCreate(data);
      this.all = [created, ...this.all];
      toastStore.success('Совещание создано');
      return created;
    } catch (e) {
      toastStore.error(e instanceof Error ? e.message : 'Ошибка');
      return null;
    }
  }

  async update(id: number, data: MeetingUpdatePayload): Promise<boolean> {
    try {
      const updated = await apiUpdate(id, data);
      this.all = this.all.map((m) => (m.id === id ? updated : m));
      toastStore.success('Сохранено');
      return true;
    } catch (e) {
      toastStore.error(e instanceof Error ? e.message : 'Ошибка');
      return false;
    }
  }

  async remove(id: number): Promise<boolean> {
    try {
      await apiDelete(id);
      this.all = this.all.filter((m) => m.id !== id);
      toastStore.success('Совещание удалено');
      return true;
    } catch (e) {
      toastStore.error(e instanceof Error ? e.message : 'Ошибка');
      return false;
    }
  }
}

export const meetingsStore = new MeetingsStore();
