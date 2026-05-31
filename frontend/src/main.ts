import './styles/theme.css';
import './styles/base.css';
import './styles/components.css';
import './styles/table.css';
import './styles/print.css';

import { initTheme, toggleTheme } from './theme';
import { loadAll } from './loader';
import { loadViewState, saveViewState } from './state';
import { initFilterEvents } from './filters';
import { render, goToPage, setPageSize, toggleStatusExtra, registerBulkCallbacks, initInlineEdit } from './render';
import { initBulkEvents, toggleRowSelect, clearSelection, updateSelectAllCheckbox } from './bulk';
import { initConfirmEvents, closeConfirm } from './confirm';
import {
  initItemModalEvents, initHistoryModalEvents,
  openEdit, deleteItem,
  openHistory, closeHistoryModal, deleteStatus,
  changeState, toggleQs, closeQs, saveQs, qsKeydown,
} from './modals';
import {
  loadRefs, initRefsEvents,
  startEditDept, cancelEditDept, saveEditDept, deleteDept,
  startEditExec, cancelEditExec, saveEditExec, deleteExecutor,
  refEditKeydown,
} from './refs';
import { exportCsv, importCsv } from './api';
import { toast } from './toast';
import { closeItemModal } from './modals';
import { state } from './state';

// ── Expose to window (для inline onclick в шаблонах рендера) ──────────────────
// Используется в HTML-строках, которые генерирует render.ts
Object.assign(window, {
  // pagination
  goToPage,
  setPageSize,
  saveViewState,
  // bulk
  toggleRowSelect,
  clearSelection,
  updateSelectAllCheckbox,
  // table actions
  changeState,
  openEdit,
  deleteItem,
  openHistory,
  toggleQs,
  closeQs,
  saveQs,
  qsKeydown,
  toggleStatusExtra,
  deleteStatus,
  // refs
  startEditDept,
  cancelEditDept,
  saveEditDept,
  deleteDept,
  startEditExec,
  cancelEditExec,
  saveEditExec,
  deleteExecutor,
  refEditKeydown,
  // reload (используется в кнопке "Повторить")
  loadAll,
});

// ── Init ───────────────────────────────────────────────────────────────────────

// Регистрируем колбэки bulk в render, чтобы избежать циклического импорта
registerBulkCallbacks(clearSelection, updateSelectAllCheckbox);
initInlineEdit();

initTheme();
document.getElementById('themeToggle')!.addEventListener('click', toggleTheme);

initConfirmEvents();
initItemModalEvents();
initHistoryModalEvents();
initBulkEvents();
initFilterEvents(render);
initRefsEvents();

// Вкладки
document.querySelectorAll<HTMLElement>('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const tab = btn.dataset['tab']!;
    document.getElementById('tab-protocol')!.style.display = tab === 'protocol' ? '' : 'none';
    document.getElementById('tab-refs')!.style.display     = tab === 'refs'     ? '' : 'none';
    if (tab === 'refs') loadRefs();
  });
});

// Экспорт / Импорт
document.getElementById('btnExport')!.addEventListener('click', () => exportCsv());
document.getElementById('btnImport')!.addEventListener('click', () => {
  (document.getElementById('importFile') as HTMLInputElement).click();
});
(document.getElementById('importFile') as HTMLInputElement).addEventListener('change', async e => {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (!file) return;
  try {
    const data = await importCsv(file);
    (e.target as HTMLInputElement).value = '';
    await loadAll();
    toast(`Импортировано задач: ${data.imported}`, 'success');
  } catch {
    (e.target as HTMLInputElement).value = '';
    toast('Не удалось импортировать файл', 'error');
  }
});

// Глобальные клавиши
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    const confirmOverlay  = document.getElementById('confirmOverlay')!;
    const historyOverlay  = document.getElementById('historyOverlay')!;
    const itemOverlay     = document.getElementById('itemOverlay')!;
    if (confirmOverlay.classList.contains('open')) { closeConfirm(false);    return; }
    if (historyOverlay.classList.contains('open')) { closeHistoryModal();    return; }
    if (itemOverlay.classList.contains('open'))    { closeItemModal();      return; }
    if (state.selectedItems.size)                  { clearSelection();       return; }
  }
  if ((e.key === 'Enter' || e.key === ' ') && (e.target as Element).matches?.('[role="button"]')) {
    e.preventDefault();
    (e.target as HTMLElement).click();
  }
});

// Печать
window.addEventListener('beforeprint', () => {
  const filterLabels: Record<string, string> = { in_progress: 'В работе', postponed: 'Отложено', closed: 'Закрыто' };
  const filterLabel = state.currentFilter ? (filterLabels[state.currentFilter] || state.currentFilter) : 'Все задачи';
  const now = new Date().toLocaleDateString('ru', { day: '2-digit', month: 'long', year: 'numeric' });
  document.getElementById('printMeta')!.textContent = `${filterLabel} · ${now}`;
});

// Старт
loadViewState();
loadAll();
