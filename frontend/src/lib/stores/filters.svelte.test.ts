import { beforeEach, describe, expect, it, vi } from 'vitest';

// В тестах считаем, что код выполняется в браузере — иначе persist()/load() — no-op.
vi.mock('$app/environment', () => ({ browser: true }));

import { filtersStore } from './filters.svelte';

const STORAGE_KEY = 'protocol_filters_v2';

describe('filtersStore', () => {
  beforeEach(() => {
    localStorage.clear();
    // Сбрасываем состояние синглтона к дефолтам между тестами.
    filtersStore.currentFilter = '';
    filtersStore.searchQuery = '';
    filtersStore.filterDept = '';
    filtersStore.filterExec = '';
    filtersStore.filterPriority = '';
    filtersStore.filterMeeting = '';
    filtersStore.sortCol = null;
    filtersStore.sortDir = 'asc';
    filtersStore.currentPage = 1;
  });

  it('hasActiveFilters реагирует на расширенные фильтры', () => {
    expect(filtersStore.hasActiveFilters).toBe(false);
    filtersStore.searchQuery = 'отчёт';
    expect(filtersStore.hasActiveFilters).toBe(true);
  });

  it('persist() сохраняет состояние в localStorage', () => {
    filtersStore.searchQuery = 'аудит';
    filtersStore.filterPriority = 'high';
    filtersStore.persist();

    const raw = localStorage.getItem(STORAGE_KEY);
    expect(raw).not.toBeNull();
    const data = JSON.parse(raw as string);
    expect(data.searchQuery).toBe('аудит');
    expect(data.filterPriority).toBe('high');
  });

  it('toggleSort переключает направление и сохраняется', () => {
    filtersStore.toggleSort('topic');
    expect(filtersStore.sortCol).toBe('topic');
    expect(filtersStore.sortDir).toBe('asc');

    filtersStore.toggleSort('topic');
    expect(filtersStore.sortDir).toBe('desc');

    filtersStore.toggleSort('due_date');
    expect(filtersStore.sortCol).toBe('due_date');
    expect(filtersStore.sortDir).toBe('asc'); // новая колонка → сброс на asc
  });

  it('resetAdvanced очищает фильтры и сбрасывает страницу', () => {
    filtersStore.searchQuery = 'x';
    filtersStore.filterDept = '3';
    filtersStore.currentPage = 5;
    filtersStore.resetAdvanced();

    expect(filtersStore.searchQuery).toBe('');
    expect(filtersStore.filterDept).toBe('');
    expect(filtersStore.currentPage).toBe(1);
    expect(filtersStore.hasActiveFilters).toBe(false);
  });
});
