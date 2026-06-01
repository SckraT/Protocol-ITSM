// Стор фильтров и сортировки с персистентностью в localStorage. Svelte 5 Runes.
import { browser } from '$app/environment';
import type { SortDir } from '$lib/api/types';

const STORAGE_KEY = 'protocol_filters_v2';

interface PersistedFilters {
  currentFilter?: string;
  searchQuery?: string;
  filterDept?: string;
  filterExec?: string;
  filterPriority?: string;
  pageSize?: number;
  sortCol?: string | null;
  sortDir?: SortDir;
}

function load(): PersistedFilters {
  if (!browser) return {};
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as PersistedFilters) : {};
  } catch {
    return {};
  }
}

class FiltersStore {
  private saved = load();

  currentFilter = $state<string>(this.saved.currentFilter ?? '');
  searchQuery = $state<string>(this.saved.searchQuery ?? '');
  filterDept = $state<string>(this.saved.filterDept ?? '');
  filterExec = $state<string>(this.saved.filterExec ?? '');
  filterPriority = $state<string>(this.saved.filterPriority ?? '');
  pageSize = $state<number>(this.saved.pageSize ?? 20);
  currentPage = $state<number>(1);
  sortCol = $state<string | null>(this.saved.sortCol ?? null);
  sortDir = $state<SortDir>(this.saved.sortDir ?? 'asc');

  /** Активен ли хоть один фильтр (для показа кнопки «Сбросить»). */
  hasActiveFilters = $derived(
    !!this.searchQuery || !!this.filterDept || !!this.filterExec || !!this.filterPriority
  );

  /** Сохраняет текущее состояние фильтров в localStorage. */
  persist(): void {
    if (!browser) return;
    try {
      const data: PersistedFilters = {
        currentFilter: this.currentFilter,
        searchQuery: this.searchQuery,
        filterDept: this.filterDept,
        filterExec: this.filterExec,
        filterPriority: this.filterPriority,
        pageSize: this.pageSize,
        sortCol: this.sortCol,
        sortDir: this.sortDir
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch {
      /* ignore */
    }
  }

  /** Сбрасывает расширенные фильтры (отдел, исполнитель, приоритет, поиск). */
  resetAdvanced(): void {
    this.searchQuery = '';
    this.filterDept = '';
    this.filterExec = '';
    this.filterPriority = '';
    this.currentPage = 1;
    this.persist();
  }

  /** Переключает сортировку по колонке. */
  toggleSort(col: string): void {
    if (this.sortCol === col) {
      this.sortDir = this.sortDir === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortCol = col;
      this.sortDir = 'asc';
    }
    this.persist();
  }
}

export const filtersStore = new FiltersStore();
