import { describe, expect, it } from 'vitest';
import type { Item } from '$lib/api/types';
import { filterAndSortItems } from './itemFilter';

/** Минимальная фабрика задачи для тестов. */
function makeItem(over: Partial<Item> & { id: number }): Item {
  return {
    id: over.id,
    topic: over.topic ?? `Задача ${over.id}`,
    ticket: over.ticket ?? null,
    priority: over.priority ?? null,
    state: over.state ?? 'in_progress',
    due_date: over.due_date ?? null,
    meeting_id: over.meeting_id ?? null,
    meeting_title: over.meeting_title ?? null,
    created_at: over.created_at ?? '2026-01-01T00:00:00',
    executors: over.executors ?? [],
    recent_statuses: over.recent_statuses ?? [],
    status_count: over.status_count ?? 0
  };
}

const items: Item[] = [
  makeItem({ id: 1, topic: 'Отчёт', state: 'in_progress', priority: 'high', due_date: '2026-06-10', meeting_id: 5,
    executors: [{ id: 10, name: 'Иванов', department_name: 'ИТ' }] }),
  makeItem({ id: 2, topic: 'Закупка', ticket: 'JIRA-42', state: 'postponed', priority: 'low', due_date: '2026-06-01', meeting_id: null,
    executors: [{ id: 11, name: 'Петров', department_name: 'Финансы' }] }),
  makeItem({ id: 3, topic: 'Аудит', state: 'closed', priority: 'medium', due_date: null, meeting_id: 5,
    executors: [{ id: 10, name: 'Иванов', department_name: 'ИТ' }] })
];

describe('filterAndSortItems — фильтры', () => {
  it('без критериев возвращает все', () => {
    expect(filterAndSortItems(items, {}).map((i) => i.id)).toEqual([1, 2, 3]);
  });

  it('фильтр по состоянию', () => {
    expect(filterAndSortItems(items, { state: 'closed' }).map((i) => i.id)).toEqual([3]);
  });

  it('поиск по теме (регистронезависимо)', () => {
    expect(filterAndSortItems(items, { search: 'отчёт' }).map((i) => i.id)).toEqual([1]);
  });

  it('поиск по тикету', () => {
    expect(filterAndSortItems(items, { search: 'jira-42' }).map((i) => i.id)).toEqual([2]);
  });

  it('поиск по имени исполнителя', () => {
    expect(filterAndSortItems(items, { search: 'петров' }).map((i) => i.id)).toEqual([2]);
  });

  it('фильтр по отделу (имя)', () => {
    expect(filterAndSortItems(items, { departmentName: 'ИТ' }).map((i) => i.id)).toEqual([1, 3]);
  });

  it('фильтр по исполнителю', () => {
    expect(filterAndSortItems(items, { executorId: 11 }).map((i) => i.id)).toEqual([2]);
  });

  it('фильтр по приоритету', () => {
    expect(filterAndSortItems(items, { priority: 'high' }).map((i) => i.id)).toEqual([1]);
  });

  it('фильтр по совещанию', () => {
    expect(filterAndSortItems(items, { meetingId: 5 }).map((i) => i.id)).toEqual([1, 3]);
  });

  it('meetingId=0 ищет ровно meeting_id===0, не null', () => {
    expect(filterAndSortItems(items, { meetingId: 0 })).toEqual([]);
  });

  it('комбинация фильтров', () => {
    const r = filterAndSortItems(items, { departmentName: 'ИТ', state: 'in_progress' });
    expect(r.map((i) => i.id)).toEqual([1]);
  });
});

describe('filterAndSortItems — сортировка', () => {
  it('по теме (ru), asc и desc', () => {
    expect(filterAndSortItems(items, { sortCol: 'topic', sortDir: 'asc' }).map((i) => i.topic)).toEqual([
      'Аудит', 'Закупка', 'Отчёт'
    ]);
    expect(filterAndSortItems(items, { sortCol: 'topic', sortDir: 'desc' }).map((i) => i.topic)).toEqual([
      'Отчёт', 'Закупка', 'Аудит'
    ]);
  });

  it('по приоритету (high<medium<low)', () => {
    expect(filterAndSortItems(items, { sortCol: 'priority', sortDir: 'asc' }).map((i) => i.id)).toEqual([1, 3, 2]);
  });

  it('по сроку (null уходит в конец)', () => {
    expect(filterAndSortItems(items, { sortCol: 'due_date', sortDir: 'asc' }).map((i) => i.id)).toEqual([2, 1, 3]);
  });

  it('не мутирует исходный массив', () => {
    const before = items.map((i) => i.id);
    filterAndSortItems(items, { sortCol: 'topic', sortDir: 'desc' });
    expect(items.map((i) => i.id)).toEqual(before);
  });
});
