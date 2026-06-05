import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { Item } from '$lib/api/types';

// Мокаем API-модуль до импорта стора (стор берёт из него updateItem/deleteItem).
vi.mock('$lib/api/items', () => ({
  fetchItems: vi.fn(),
  createItem: vi.fn(),
  updateItem: vi.fn(),
  deleteItem: vi.fn()
}));

import { deleteItem, updateItem } from '$lib/api/items';
import { itemsStore } from './items.svelte';

function makeItem(over: Partial<Item> & { id: number }): Item {
  return {
    id: over.id,
    topic: over.topic ?? `Задача ${over.id}`,
    ticket: null,
    priority: null,
    state: over.state ?? 'in_progress',
    due_date: null,
    meeting_id: null,
    meeting_title: null,
    created_at: '2026-01-01T00:00:00',
    executors: [],
    recent_statuses: [],
    status_count: 0
  };
}

describe('itemsStore — bulk-операции', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    itemsStore.all = [makeItem({ id: 1 }), makeItem({ id: 2 }), makeItem({ id: 3 })];
  });

  it('bulkChangeState: все успешно → ok=N, failed=0', async () => {
    vi.mocked(updateItem).mockImplementation(async (id, data) => makeItem({ id, ...data }));
    const r = await itemsStore.bulkChangeState([1, 2, 3], 'closed');
    expect(r).toEqual({ ok: 3, failed: 0 });
    expect(updateItem).toHaveBeenCalledTimes(3);
  });

  it('bulkChangeState: частичный сбой → точные счётчики', async () => {
    vi.mocked(updateItem).mockImplementation(async (id) => {
      if (id === 2) throw new Error('boom');
      return makeItem({ id });
    });
    const r = await itemsStore.bulkChangeState([1, 2, 3], 'postponed');
    expect(r).toEqual({ ok: 2, failed: 1 });
  });

  it('bulkRemove: частичный сбой → точные счётчики', async () => {
    vi.mocked(deleteItem).mockImplementation(async (id) => {
      if (id === 3) throw new Error('boom');
    });
    const r = await itemsStore.bulkRemove([1, 2, 3]);
    expect(r).toEqual({ ok: 2, failed: 1 });
    expect(deleteItem).toHaveBeenCalledTimes(3);
  });
});
