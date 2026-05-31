import type { Item } from './types';
import { state } from './state';
import { updateItem, deleteItemApi } from './api';
import { render, removeRowFromTable, updateDashboardCounts } from './render';
import { applyFilters, applySort } from './filters';
import { loadAll } from './loader';
import { toast } from './toast';
import { STATE_LABEL, plural } from './utils';
import { confirmDialog } from './confirm';

export function toggleRowSelect(id: number, checked: boolean): void {
  if (checked) state.selectedItems.add(id); else state.selectedItems.delete(id);
  const row = document.querySelector<HTMLElement>(`tr.item-row[data-item-id="${id}"]`);
  if (row) row.classList.toggle('selected', checked);
  updateBulkBar();
  updateSelectAllCheckbox();
}

export function updateBulkBar(): void {
  const bar   = document.getElementById('bulkBar')!;
  const count = document.getElementById('bulkCount')!;
  const n = state.selectedItems.size;
  bar.classList.toggle('visible', n > 0);
  count.textContent = String(n);
}

export function updateSelectAllCheckbox(): void {
  const cb = document.getElementById('selectAllCb') as HTMLInputElement | null;
  if (!cb) return;
  const all = applySort(applyFilters(state.allItems));
  const ps  = state.pageSize > 0 ? state.pageSize : all.length;
  const pageItems = all.slice((state.currentPage - 1) * ps, state.currentPage * ps);
  if (!pageItems.length) { cb.checked = false; cb.indeterminate = false; return; }
  const selCount = pageItems.filter(i => state.selectedItems.has(i.id)).length;
  cb.indeterminate = selCount > 0 && selCount < pageItems.length;
  cb.checked = selCount === pageItems.length;
}

export function clearSelection(): void {
  state.selectedItems.clear();
  document.querySelectorAll('tr.item-row.selected').forEach(r => r.classList.remove('selected'));
  document.querySelectorAll<HTMLInputElement>('.row-checkbox').forEach(cb => { cb.checked = false; });
  updateBulkBar();
  const allCb = document.getElementById('selectAllCb') as HTMLInputElement | null;
  if (allCb) { allCb.checked = false; allCb.indeterminate = false; }
}

export function initBulkEvents(): void {
  (document.getElementById('selectAllCb') as HTMLInputElement).addEventListener('change', function (this: HTMLInputElement) {
    const all = applySort(applyFilters(state.allItems));
    const ps  = state.pageSize > 0 ? state.pageSize : all.length;
    const pageItems = all.slice((state.currentPage - 1) * ps, state.currentPage * ps);
    pageItems.forEach(i => {
      if (this.checked) state.selectedItems.add(i.id); else state.selectedItems.delete(i.id);
    });
    render();
  });

  document.getElementById('btnBulkClear')!.addEventListener('click', () => clearSelection());

  document.getElementById('btnBulkState')!.addEventListener('click', async () => {
    const stateVal = (document.getElementById('bulkStateSelect') as HTMLSelectElement).value as Item['state'];
    if (!stateVal || !state.selectedItems.size) return;
    const ids = [...state.selectedItems];
    const label = STATE_LABEL[stateVal] || stateVal;

    ids.forEach(id => {
      const item = state.allItems.find(i => i.id === id);
      if (item) item.state = stateVal;
    });
    updateDashboardCounts();
    render();
    clearSelection();
    (document.getElementById('bulkStateSelect') as HTMLSelectElement).value = '';

    try {
      await Promise.all(ids.map(id => updateItem(id, { state: stateVal })));
      toast(`${ids.length} задач переведено в «${label}»`, 'success');
    } catch {
      await loadAll();
      toast('Не удалось обновить часть задач', 'error');
    }
  });

  document.getElementById('btnBulkDelete')!.addEventListener('click', async () => {
    const n = state.selectedItems.size;
    if (!n) return;
    const suffix = n === 1 ? 'у' : n < 5 ? 'и' : '';
    if (!await confirmDialog(`Удалить ${n} задач${suffix}?`)) return;
    const ids = [...state.selectedItems];

    ids.forEach(id => {
      removeRowFromTable(id);
      const idx = state.allItems.findIndex(i => i.id === id);
      if (idx !== -1) state.allItems.splice(idx, 1);
    });
    state.selectedItems.clear();
    updateDashboardCounts();
    updateBulkBar();

    try {
      await Promise.all(ids.map(id => deleteItemApi(id)));
      toast(`${n} ${plural(n, ['задача удалена', 'задачи удалено', 'задач удалено'])}`, 'success');
    } catch {
      await loadAll();
      toast('Не удалось удалить часть задач', 'error');
    }
  });
}
