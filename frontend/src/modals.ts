import type { Item } from './types';
import { state } from './state';
import {
  updateItem, createItem, deleteItemApi,
  fetchStatuses, addStatus, deleteStatusApi,
} from './api';
import { render, updateDashboardCounts, updateRowStateVisuals, removeRowFromTable, buildExecutorSelect, saveDOMState } from './render';
import { updateBulkBar } from './bulk';
import { loadAll } from './loader';
import { toast } from './toast';
import { confirmDialog } from './confirm';
import { fmtDate, esc, today } from './utils';
import type { Executor } from './types';

// ── Quick status form ──────────────────────────────────────────────────────────

export function toggleQs(id: number): void {
  const row = document.getElementById(`qs-${id}`);
  const isOpen = row?.style.display !== 'none';
  closeQs();
  if (!isOpen && row) {
    row.style.display = '';
    state.openQsId = id;
    const d = document.getElementById(`qs-date-${id}`) as HTMLInputElement | null;
    if (d) d.value = today();
    const n = document.getElementById(`qs-note-${id}`) as HTMLInputElement | null;
    if (n) n.focus();
  }
}

export function closeQs(): void {
  if (state.openQsId !== null) {
    const row = document.getElementById(`qs-${state.openQsId}`);
    if (row) row.style.display = 'none';
    state.openQsId = null;
  }
}

export function qsKeydown(e: KeyboardEvent, id: number): void {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); saveQs(id); }
  if (e.key === 'Escape') closeQs();
}

export async function saveQs(id: number): Promise<void> {
  const date = (document.getElementById(`qs-date-${id}`) as HTMLInputElement | null)?.value || null;
  const note = (document.getElementById(`qs-note-${id}`) as HTMLInputElement | null)?.value.trim() || null;
  if (!note) { closeQs(); return; }

  const item = state.allItems.find(i => i.id === id);
  if (!item) return;

  const newStatus = { status_date: date, status_note: note };
  const oldRecent = item.recent_statuses ? [...item.recent_statuses] : [];

  item.recent_statuses = [newStatus as Item['recent_statuses'][0], ...oldRecent].slice(0, 3);
  item.status_count = (item.status_count ?? 0) + 1;

  closeQs();
  render();

  try {
    await addStatus(id, { status_date: date, status_note: note });
    toast('Статус добавлен', 'success');
  } catch {
    item.recent_statuses = oldRecent;
    item.status_count = (item.status_count ?? 0) - 1;
    render();
    toast('Не удалось сохранить статус', 'error');
  }
}

// ── State change (inline select) ──────────────────────────────────────────────

export async function changeState(id: number, value: Item['state']): Promise<void> {
  const item = state.allItems.find(i => i.id === id);
  if (!item) return;
  const oldState = item.state;
  item.state = value;
  updateRowStateVisuals(item);
  updateDashboardCounts();

  try {
    await updateItem(id, { state: value });
  } catch {
    item.state = oldState;
    updateRowStateVisuals(item);
    updateDashboardCounts();
    render();
    toast('Не удалось сменить состояние', 'error');
  }
}

// ── Delete item ────────────────────────────────────────────────────────────────

export async function deleteItem(id: number): Promise<void> {
  const item = state.allItems.find(i => i.id === id);
  if (!await confirmDialog(`Удалить задачу?\n\n${item?.topic || ''}`)) return;

  saveDOMState();
  const itemIndex = state.allItems.findIndex(i => i.id === id);
  const deletedItem = state.allItems[itemIndex]!;

  removeRowFromTable(id);
  state.allItems.splice(itemIndex, 1);
  state.selectedItems.delete(id);

  updateDashboardCounts();
  updateBulkBar();

  try {
    await deleteItemApi(id);
    toast('Задача удалена', 'success');
  } catch {
    state.allItems.splice(itemIndex, 0, deletedItem);
    render();
    toast('Не удалось удалить задачу. Повтор…', 'error');
  }
}

// ── Executor form helpers ──────────────────────────────────────────────────────

export function addExecutorField(executor: Executor | null = null): void {
  const wrap = document.getElementById('executorsWrap')!;
  const selectedId = executor ? executor.id : 0;

  if (!state.allExecutors.length && !selectedId) {
    if (!document.querySelector('.no-executors-hint')) {
      const hint = document.createElement('p');
      hint.className = 'no-executors-hint';
      hint.textContent = 'Справочник пуст — сначала добавьте исполнителей во вкладке «Справочники».';
      wrap.parentNode!.insertBefore(hint, wrap);
    }
    return;
  }

  const row = document.createElement('div');
  row.className = 'executor-row';
  const sel = buildExecutorSelect(selectedId || '', executor);
  const btn = document.createElement('button');
  btn.type      = 'button';
  btn.className = 'btn-exec-remove';
  btn.title     = 'Убрать';
  btn.textContent = '−';
  btn.addEventListener('click', () => {
    const rows = wrap.querySelectorAll('.executor-row');
    if (rows.length === 1) { sel.value = ''; } else { row.remove(); }
  });
  row.appendChild(sel);
  row.appendChild(btn);
  wrap.appendChild(row);
}

export function getExecutorsFromForm(): number[] {
  return [...document.querySelectorAll<HTMLSelectElement>('#executorsWrap .executor-row select')]
    .map(s => parseInt(s.value))
    .filter(v => !isNaN(v) && v > 0);
}

export function setExecutorsInForm(executors: Executor[]): void {
  document.querySelector('.no-executors-hint')?.remove();
  const wrap = document.getElementById('executorsWrap')!;
  wrap.innerHTML = '';
  if (executors.length) {
    executors.forEach(e => addExecutorField(e));
  } else {
    addExecutorField();
  }
}

// ── Item modal ─────────────────────────────────────────────────────────────────

const itemOverlay = () => document.getElementById('itemOverlay')!;

export function openAdd(): void {
  document.getElementById('modalTitle')!.textContent         = 'Новый пункт';
  document.getElementById('statusSectionLabel')!.textContent = 'Первый статус';
  (document.getElementById('itemForm') as HTMLFormElement).reset();
  (document.getElementById('fieldId') as HTMLInputElement).value = '';
  (document.getElementById('fieldStatusDate') as HTMLInputElement).value = today();
  setExecutorsInForm([]);
  itemOverlay().classList.add('open');
  (document.getElementById('fieldTopic') as HTMLTextAreaElement).focus();
}

export function openEdit(id: number): void {
  const item = state.allItems.find(i => i.id === id);
  if (!item) return;
  document.getElementById('modalTitle')!.textContent         = 'Редактировать задачу';
  document.getElementById('statusSectionLabel')!.textContent = 'Добавить статус';
  (document.getElementById('fieldId')       as HTMLInputElement).value = String(id);
  (document.getElementById('fieldTopic')    as HTMLTextAreaElement).value = item.topic;
  (document.getElementById('fieldTicket')   as HTMLInputElement).value   = item.ticket   || '';
  (document.getElementById('fieldPriority') as HTMLSelectElement).value  = item.priority || '';
  (document.getElementById('fieldState')    as HTMLSelectElement).value  = item.state;
  (document.getElementById('fieldDueDate')  as HTMLInputElement).value   = item.due_date || '';
  (document.getElementById('fieldStatusDate') as HTMLInputElement).value = today();
  (document.getElementById('fieldStatusNote') as HTMLTextAreaElement).value = '';
  setExecutorsInForm(item.executors || []);
  itemOverlay().classList.add('open');
}

export function closeItemModal(): void {
  itemOverlay().classList.remove('open');
}

export function initItemModalEvents(): void {
  document.getElementById('btnAdd')!.addEventListener('click', openAdd);
  document.getElementById('btnItemCancel')!.addEventListener('click', closeItemModal);
  itemOverlay().addEventListener('click', e => { if (e.target === itemOverlay()) closeItemModal(); });
  document.getElementById('btnAddExecutorField')!.addEventListener('click', () => addExecutorField());

  (document.getElementById('itemForm') as HTMLFormElement).addEventListener('submit', async e => {
    e.preventDefault();
    const id         = (document.getElementById('fieldId') as HTMLInputElement).value;
    const statusDate = (document.getElementById('fieldStatusDate') as HTMLInputElement).value || null;
    const statusNote = (document.getElementById('fieldStatusNote') as HTMLTextAreaElement).value.trim() || null;

    const payload = {
      topic:     (document.getElementById('fieldTopic')    as HTMLTextAreaElement).value.trim(),
      ticket:    (document.getElementById('fieldTicket')   as HTMLInputElement).value.trim()  || null,
      priority:  (document.getElementById('fieldPriority') as HTMLSelectElement).value       || null,
      state:     (document.getElementById('fieldState')    as HTMLSelectElement).value,
      due_date:  (document.getElementById('fieldDueDate')  as HTMLInputElement).value        || null,
      executors: getExecutorsFromForm(),
    };

    try {
      if (id) {
        await updateItem(parseInt(id), payload);
        if (statusNote) {
          await addStatus(parseInt(id), { status_date: statusDate, status_note: statusNote });
        }
        const item = state.allItems.find(i => i.id === parseInt(id));
        if (item) {
          item.topic    = payload.topic;
          item.ticket   = payload.ticket;
          item.priority = payload.priority as Item['priority'];
          item.state    = payload.state as Item['state'];
          item.due_date = payload.due_date;
          item.executors = payload.executors
            .map(eid => state.allExecutors.find(e => e.id === eid))
            .filter((e): e is Executor => !!e);
          if (statusNote) {
            const ns = { status_date: statusDate, status_note: statusNote } as Item['recent_statuses'][0];
            item.recent_statuses = [ns, ...(item.recent_statuses || [])].slice(0, 3);
            item.status_count = (item.status_count ?? 0) + 1;
          }
        }
        closeItemModal();
        updateDashboardCounts();
        render();
        toast('Задача обновлена', 'success');
      } else {
        await createItem({ ...payload, status_date: statusDate, status_note: statusNote });
        closeItemModal();
        await loadAll();
        toast('Задача добавлена', 'success');
      }
    } catch {
      toast('Не удалось сохранить задачу', 'error');
    }
  });
}

// ── History modal ──────────────────────────────────────────────────────────────

const historyOverlay = () => document.getElementById('historyOverlay')!;

function syncItemStatuses(id: number, statuses: Item['recent_statuses']): void {
  const item = state.allItems.find(i => i.id === id);
  if (!item) return;
  item.recent_statuses = statuses.slice(0, 3);
  item.status_count = statuses.length;
}

async function renderHistory(): Promise<void> {
  const list = document.getElementById('historyList')!;
  try {
    const statuses = await fetchStatuses(state.historyItemId!);
    syncItemStatuses(state.historyItemId!, statuses as Item['recent_statuses']);
    render();

    if (!statuses.length) { list.innerHTML = '<div class="history-empty">Статусов ещё нет</div>'; return; }
    list.innerHTML = statuses.map((s, idx) => `
      <div class="history-item ${idx === 0 ? 'latest' : ''}">
        <div class="history-dot"></div>
        <div class="history-body">
          <div class="history-date">${s.status_date ? fmtDate(s.status_date) : 'Дата не указана'}</div>
          ${s.status_note ? `<div class="history-note">${esc(s.status_note)}</div>` : `<div class="history-note-empty">Описание не указано</div>`}
        </div>
        <button class="history-del" onclick="deleteStatus(${s.id})">×</button>
      </div>`).join('');
  } catch {
    list.innerHTML = '<div class="history-empty">Не удалось загрузить историю</div>';
  }
}

export async function openHistory(id: number): Promise<void> {
  state.historyItemId = id;
  document.getElementById('historyTopic')!.textContent = state.allItems.find(i => i.id === id)?.topic || '';
  (document.getElementById('newStatusDate') as HTMLInputElement).value = today();
  (document.getElementById('newStatusNote') as HTMLTextAreaElement).value = '';
  await renderHistory();
  historyOverlay().classList.add('open');
}

export async function deleteStatus(statusId: number): Promise<void> {
  if (!await confirmDialog('Удалить этот статус?')) return;
  try {
    await deleteStatusApi(statusId);
    await renderHistory();
    toast('Статус удалён', 'success');
  } catch {
    toast('Не удалось удалить статус', 'error');
  }
}

export function closeHistoryModal(): void {
  historyOverlay().classList.remove('open');
  state.historyItemId = null;
}

export function initHistoryModalEvents(): void {
  historyOverlay().addEventListener('click', e => {
    if (e.target === historyOverlay()) closeHistoryModal();
  });
  document.getElementById('btnHistoryClose')!.addEventListener('click', closeHistoryModal);

  document.getElementById('btnAddStatus')!.addEventListener('click', async () => {
    const date = (document.getElementById('newStatusDate') as HTMLInputElement).value || null;
    const note = (document.getElementById('newStatusNote') as HTMLTextAreaElement).value.trim() || null;
    if (!note) return;
    try {
      await addStatus(state.historyItemId!, { status_date: date, status_note: note });
      (document.getElementById('newStatusNote') as HTMLTextAreaElement).value = '';
      (document.getElementById('newStatusDate') as HTMLInputElement).value = today();
      await renderHistory();
      toast('Статус добавлен', 'success');
    } catch {
      toast('Не удалось добавить статус', 'error');
    }
  });
}
