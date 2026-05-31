import { state, saveViewState } from './state';
import type { Item } from './types';
import { PRIORITY_SORT_ORDER } from './utils';

export function applyFilters(items: Item[]): Item[] {
  let r = state.currentFilter ? items.filter(i => i.state === state.currentFilter) : items;

  if (state.searchQuery) {
    const q = state.searchQuery;
    r = r.filter(i =>
      (i.topic  || '').toLowerCase().includes(q) ||
      (i.ticket || '').toLowerCase().includes(q) ||
      (i.executors || []).some(e =>
        (e.name || '').toLowerCase().includes(q) ||
        (e.department_name || '').toLowerCase().includes(q)
      )
    );
  }
  if (state.filterDept) {
    r = r.filter(i => (i.executors || []).some(e => e.department_name === state.filterDept));
  }
  if (state.filterExec) {
    const execId = parseInt(state.filterExec);
    r = r.filter(i => (i.executors || []).some(e => e.id === execId));
  }
  if (state.filterPriority) {
    r = r.filter(i => i.priority === state.filterPriority);
  }
  return r;
}

export function applySort(items: Item[]): Item[] {
  if (!state.sortState.col) return items;
  return [...items].sort((a, b) => {
    const col = state.sortState.col as keyof Item;
    const va = String(a[col] ?? '');
    const vb = String(b[col] ?? '');
    if (col === 'priority') {
      const na = PRIORITY_SORT_ORDER[va] ?? 3;
      const nb = PRIORITY_SORT_ORDER[vb] ?? 3;
      return state.sortState.dir === 'asc' ? na - nb : nb - na;
    }
    if (va < vb) return state.sortState.dir === 'asc' ? -1 : 1;
    if (va > vb) return state.sortState.dir === 'asc' ?  1 : -1;
    return 0;
  });
}

export function populateAdvFilters(): void {
  const deptSel = document.getElementById('filterDeptSel') as HTMLSelectElement;
  const execSel = document.getElementById('filterExecSel') as HTMLSelectElement;
  const curDept = deptSel.value;
  const curExec = execSel.value;

  deptSel.innerHTML = '<option value="">Все отделы</option>';
  state.allDepartments.forEach(d => {
    const opt = document.createElement('option');
    opt.value = d.name;
    opt.textContent = d.name;
    deptSel.appendChild(opt);
  });
  deptSel.value = curDept;

  execSel.innerHTML = '<option value="">Все исполнители</option>';
  state.allExecutors.forEach(e => {
    const opt = document.createElement('option');
    opt.value = String(e.id);
    opt.textContent = e.department_name ? `${e.department_name} — ${e.name}` : e.name;
    execSel.appendChild(opt);
  });
  execSel.value = curExec;
}

export function updateResetBtn(): void {
  const active = state.filterDept || state.filterExec || state.filterPriority;
  const btn = document.getElementById('btnResetAdv')!;
  btn.style.display = active ? '' : 'none';
}

export function applyViewStateToDOM(): void {
  const searchInput = document.getElementById('searchInput') as HTMLInputElement;
  searchInput.value = state.searchQuery;

  const ps = document.getElementById('pageSizeSel') as HTMLSelectElement | null;
  if (ps) ps.value = String(state.pageSize);

  document.querySelectorAll<HTMLElement>('.dash-tile').forEach(t => {
    t.classList.toggle('active', t.dataset['filter'] === state.currentFilter);
  });

  const ids = ['filterDeptSel', 'filterExecSel', 'filterPrioSel'] as const;
  const vals = [state.filterDept, state.filterExec, state.filterPriority];
  ids.forEach((id, i) => {
    const el = document.getElementById(id) as HTMLSelectElement;
    el.value = vals[i]!;
    el.classList.toggle('filtered', !!el.value);
  });
  updateResetBtn();
}

export function initFilterEvents(renderFn: () => void): void {
  document.getElementById('dashboard')!.addEventListener('click', e => {
    const tile = (e.target as Element).closest<HTMLElement>('.dash-tile');
    if (!tile) return;
    document.querySelectorAll('.dash-tile').forEach(t => t.classList.remove('active'));
    tile.classList.add('active');
    state.currentFilter = tile.dataset['filter'] ?? '';
    state.currentPage = 1;
    saveViewState();
    renderFn();
  });

  const searchInput = document.getElementById('searchInput') as HTMLInputElement;
  searchInput.addEventListener('input', e => {
    state.searchQuery = (e.target as HTMLInputElement).value.toLowerCase().trim();
    state.currentPage = 1;
    saveViewState();
    renderFn();
  });

  document.getElementById('filterDeptSel')!.addEventListener('change', e => {
    state.filterDept = (e.target as HTMLSelectElement).value;
    (e.target as HTMLSelectElement).classList.toggle('filtered', !!state.filterDept);
    updateResetBtn(); state.currentPage = 1; saveViewState(); renderFn();
  });

  document.getElementById('filterExecSel')!.addEventListener('change', e => {
    state.filterExec = (e.target as HTMLSelectElement).value;
    (e.target as HTMLSelectElement).classList.toggle('filtered', !!state.filterExec);
    updateResetBtn(); state.currentPage = 1; saveViewState(); renderFn();
  });

  document.getElementById('filterPrioSel')!.addEventListener('change', e => {
    state.filterPriority = (e.target as HTMLSelectElement).value;
    (e.target as HTMLSelectElement).classList.toggle('filtered', !!state.filterPriority);
    updateResetBtn(); state.currentPage = 1; saveViewState(); renderFn();
  });

  document.getElementById('btnResetAdv')!.addEventListener('click', () => {
    state.filterDept = state.filterExec = state.filterPriority = '';
    ['filterDeptSel', 'filterExecSel', 'filterPrioSel'].forEach(id => {
      const el = document.getElementById(id) as HTMLSelectElement;
      el.value = '';
      el.classList.remove('filtered');
    });
    updateResetBtn(); state.currentPage = 1; saveViewState(); renderFn();
  });

  document.querySelectorAll<HTMLElement>('thead th.sortable').forEach(th => {
    th.addEventListener('click', () => {
      const col = th.dataset['col']!;
      state.sortState.dir = state.sortState.col === col
        ? (state.sortState.dir === 'asc' ? 'desc' : 'asc')
        : 'asc';
      state.sortState.col = col;
      state.currentPage = 1;
      saveViewState();
      renderFn();
    });
  });
}
