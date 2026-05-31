import type { Item, Executor, Department, SortDir } from './types';

export const state = {
  allItems:        [] as Item[],
  allExecutors:    [] as Executor[],
  allDepartments:  [] as Department[],
  currentFilter:   '',
  searchQuery:     '',
  filterDept:      '',
  filterExec:      '',
  filterPriority:  '',
  historyItemId:   null as number | null,
  sortState:       { col: null as string | null, dir: 'asc' as SortDir },
  currentPage:     1,
  pageSize:        20,
  openQsId:        null as number | null,
  editingDeptId:   null as number | null,
  editingExecId:   null as number | null,
  execSearchQuery: '',
  selectedItems:   new Set<number>(),
  scrollPos:       0,
  openAccordions:  new Set<number>(),
};

const VIEW_KEY = 'protocol_view_v1';

export function saveViewState(): void {
  try {
    localStorage.setItem(VIEW_KEY, JSON.stringify({
      currentFilter:  state.currentFilter,
      searchQuery:    state.searchQuery,
      sortState:      state.sortState,
      filterDept:     state.filterDept,
      filterExec:     state.filterExec,
      filterPriority: state.filterPriority,
      pageSize:       state.pageSize,
    }));
  } catch { /* ignore */ }
}

export function loadViewState(): void {
  try {
    const raw = localStorage.getItem(VIEW_KEY);
    if (!raw) return;
    const s = JSON.parse(raw) as Partial<typeof state>;
    if (s.currentFilter  !== undefined) state.currentFilter  = s.currentFilter  as string;
    if (s.searchQuery    !== undefined) state.searchQuery    = s.searchQuery    as string;
    if (s.sortState      !== undefined) state.sortState      = s.sortState      as typeof state.sortState;
    if (s.filterDept     !== undefined) state.filterDept     = s.filterDept     as string;
    if (s.filterExec     !== undefined) state.filterExec     = s.filterExec     as string;
    if (s.filterPriority !== undefined) state.filterPriority = s.filterPriority as string;
    if (s.pageSize       !== undefined) state.pageSize       = s.pageSize       as number;
  } catch { /* ignore */ }
}
