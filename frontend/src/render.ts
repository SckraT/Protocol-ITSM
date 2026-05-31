import { state, saveViewState } from './state';
import { applyFilters, applySort } from './filters';
import { fmtDate, esc, dueInfo, STATE_LABEL, STATE_BADGE, STATE_ORDER, PRIORITY_CONFIG } from './utils';
import type { Item, Executor, ItemState } from './types';

// Колбэки из bulk.ts регистрируются из main.ts, чтобы избежать циклического импорта
let _clearSelection: (() => void) | null = null;
let _updateSelectAllCheckbox: (() => void) | null = null;

export function registerBulkCallbacks(
  clearSel: () => void,
  updateSel: () => void,
): void {
  _clearSelection = clearSel;
  _updateSelectAllCheckbox = updateSel;
}

// ── DOM state (accordions + scroll position) ───────────────────────────────────

export function saveDOMState(): void {
  const tableWrap = document.querySelector<HTMLElement>('.table-wrap');
  state.scrollPos = tableWrap ? tableWrap.scrollLeft : 0;
  const tbody = document.getElementById('tableBody')!;
  state.openAccordions.clear();
  tbody.querySelectorAll<HTMLElement>('tr.item-row').forEach(tr => {
    if (tr.querySelector('.status-toggle.open')) {
      state.openAccordions.add(parseInt(tr.dataset['itemId']!));
    }
  });
}

export function restoreDOMState(): void {
  const tbody = document.getElementById('tableBody')!;
  tbody.querySelectorAll<HTMLElement>('tr.item-row').forEach(tr => {
    const itemId = parseInt(tr.dataset['itemId']!);
    if (state.openAccordions.has(itemId)) {
      const toggle = tr.querySelector<HTMLElement>('.status-toggle');
      const extra  = tr.querySelector<HTMLElement>('.status-extra');
      if (toggle) toggle.classList.add('open');
      if (extra)  extra.style.display = '';
    }
  });
  const tableWrap = document.querySelector<HTMLElement>('.table-wrap');
  if (tableWrap) tableWrap.scrollLeft = state.scrollPos;
}

// ── Dashboard counts ───────────────────────────────────────────────────────────

export function updateDashboardCounts(): void {
  const c = { in_progress: 0, postponed: 0, closed: 0 };
  state.allItems.forEach(i => c[i.state]++);
  document.getElementById('dash-all')!.textContent        = String(state.allItems.length);
  document.getElementById('dash-inprogress')!.textContent = String(c.in_progress);
  document.getElementById('dash-postponed')!.textContent  = String(c.postponed);
  document.getElementById('dash-closed')!.textContent     = String(c.closed);
}

// ── Row helpers ────────────────────────────────────────────────────────────────

export function findRowInTable(itemId: number): HTMLElement | null {
  return document.querySelector<HTMLElement>(`tr.item-row[data-item-id="${itemId}"]`);
}

export function removeRowFromTable(itemId: number): void {
  const row = findRowInTable(itemId);
  if (row) {
    const qsRow = document.getElementById(`qs-${itemId}`);
    row.style.transition = 'opacity 0.2s';
    row.style.opacity = '0';
    setTimeout(() => { row.remove(); qsRow?.remove(); }, 200);
  }
}

/** Точечно обновляет цвет селекта состояния и ячейку срока без перерендера. */
export function updateRowStateVisuals(item: Item): void {
  const row = document.querySelector<HTMLElement>(`tr[data-item-id="${item.id}"]`);
  if (!row) return;
  const sel = row.querySelector<HTMLSelectElement>('.state-select');
  if (sel) {
    sel.value     = item.state;
    sel.className = `state-select ${STATE_BADGE[item.state]}`;
  }
  const dueCell = row.querySelector<HTMLElement>('td.due');
  if (dueCell) {
    const due = dueInfo(item.due_date, item.state);
    dueCell.className = `due ${due.cls}`.trim();
    dueCell.innerHTML = `${item.due_date ? fmtDate(item.due_date) : '—'}${due.rel ? `<br><span class="due-rel">${due.rel}</span>` : ''}`;
  }
}

// ── Executor select (used in modals) ──────────────────────────────────────────

export function buildExecutorSelect(selectedId: number | '' = '', selectedExec: Executor | null = null): HTMLSelectElement {
  const sel = document.createElement('select');

  const blank = document.createElement('option');
  blank.value = '';
  blank.textContent = '— не выбран —';
  sel.appendChild(blank);

  const inDirectory = selectedId !== '' && state.allExecutors.some(e => e.id === selectedId);
  if (selectedId !== '' && selectedExec && !inDirectory) {
    const og = document.createElement('optgroup');
    og.label = 'Удалён из справочника';
    const opt = document.createElement('option');
    opt.value = String(selectedExec.id);
    opt.textContent = selectedExec.department_name
      ? `${selectedExec.department_name} — ${selectedExec.name}`
      : selectedExec.name;
    og.appendChild(opt);
    sel.appendChild(og);
  }

  const byDept: Record<string, Executor[]> = {};
  const noDept: Executor[] = [];
  state.allExecutors.forEach(e => {
    if (e.department_name) {
      if (!byDept[e.department_name]) byDept[e.department_name] = [];
      byDept[e.department_name].push(e);
    } else {
      noDept.push(e);
    }
  });

  Object.keys(byDept).sort((a, b) => a.localeCompare(b, 'ru')).forEach(dname => {
    const og = document.createElement('optgroup');
    og.label = dname;
    byDept[dname]!.forEach(e => {
      const opt = document.createElement('option');
      opt.value = String(e.id);
      opt.textContent = e.name;
      og.appendChild(opt);
    });
    sel.appendChild(og);
  });

  if (noDept.length) {
    const og = document.createElement('optgroup');
    og.label = 'Без отдела';
    noDept.forEach(e => {
      const opt = document.createElement('option');
      opt.value = String(e.id);
      opt.textContent = e.name;
      og.appendChild(opt);
    });
    sel.appendChild(og);
  }

  if (selectedId !== '') sel.value = String(selectedId);
  return sel;
}

// ── Pagination ─────────────────────────────────────────────────────────────────

export function goToPage(n: number): void {
  state.currentPage = n;
  _clearSelection?.();
  render();
  document.querySelector('.table-wrap')?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

export function setPageSize(n: number): void {
  state.pageSize = n;
  state.currentPage = 1;
  _clearSelection?.();
  saveViewState();
  render();
}

function renderPagination(total: number, totalPages: number): void {
  const bar   = document.getElementById('paginationBar')!;
  const info  = document.getElementById('paginationInfo')!;
  const pages = document.getElementById('paginationPages')!;
  const ps = state.pageSize > 0 ? state.pageSize : total;
  bar.style.display = (total === 0 || (state.pageSize > 0 && total <= state.pageSize)) ? 'none' : 'flex';
  if (bar.style.display === 'none') return;

  const start = (state.currentPage - 1) * ps + 1;
  const end   = Math.min(state.currentPage * ps, total);
  info.textContent = `${start}–${end} из ${total}`;

  const btns: string[] = [];
  const addBtn = (label: string | number, page: number | null, extra = '') => {
    btns.push(`<button class="page-btn${extra}" ${page === null ? 'disabled' : `onclick="goToPage(${page})"`}>${label}</button>`);
  };
  const addDots = () => btns.push('<span class="page-btn page-dots">…</span>');

  addBtn('‹', state.currentPage > 1 ? state.currentPage - 1 : null);
  if (totalPages <= 7) {
    for (let i = 1; i <= totalPages; i++) addBtn(i, i, i === state.currentPage ? ' active' : '');
  } else {
    addBtn(1, 1, state.currentPage === 1 ? ' active' : '');
    if (state.currentPage > 3) addDots();
    const lo = Math.max(2, state.currentPage - 1);
    const hi = Math.min(totalPages - 1, state.currentPage + 1);
    for (let i = lo; i <= hi; i++) addBtn(i, i, i === state.currentPage ? ' active' : '');
    if (state.currentPage < totalPages - 2) addDots();
    addBtn(totalPages, totalPages, state.currentPage === totalPages ? ' active' : '');
  }
  addBtn('›', state.currentPage < totalPages ? state.currentPage + 1 : null);
  pages.innerHTML = btns.join('');
}

// ── Status options ─────────────────────────────────────────────────────────────

export function stateOptions(current: ItemState): string {
  return STATE_ORDER.map(s =>
    `<option value="${s}" ${s === current ? 'selected' : ''}>${STATE_LABEL[s]}</option>`
  ).join('');
}

// ── Accordion ─────────────────────────────────────────────────────────────────

export function toggleStatusExtra(id: number): void {
  const extra = document.getElementById(`status-extra-${id}`);
  const btn   = document.getElementById(`status-toggle-${id}`);
  if (!extra) return;
  const open = extra.style.display === 'none';
  extra.style.display = open ? '' : 'none';
  if (btn) { btn.classList.toggle('open', open); btn.setAttribute('aria-expanded', String(open)); }
}

// ── Row builder ────────────────────────────────────────────────────────────────

function renderAccordion(item: Item): string {
  const recent = item.recent_statuses || [];
  const latest = recent[0];
  const extra  = recent.slice(1);
  const hidden = (item.status_count ?? recent.length) - recent.length;

  if (!latest) return '<div class="status-empty">Нет статусов</div>';

  return `<div class="status-line">
    <span class="s-date">${latest.status_date ? fmtDate(latest.status_date) : '—'}</span>
    <span class="s-note" title="${esc(latest.status_note || '')}">${esc(latest.status_note || '')}</span>
    ${extra.length ? `<button class="status-toggle" id="status-toggle-${item.id}" onclick="toggleStatusExtra(${item.id})" aria-expanded="false" title="История статусов">▾</button>` : ''}
  </div>${extra.length ? `
  <div class="status-extra" id="status-extra-${item.id}" style="display:none">
    ${extra.map(s => `
      <div class="status-line status-line--sub">
        <span class="s-date">${s.status_date ? fmtDate(s.status_date) : '—'}</span>
        <span class="s-note" title="${esc(s.status_note || '')}">${esc(s.status_note || '')}</span>
      </div>`).join('')}
    ${hidden > 0 ? `<span class="status-link" role="button" tabindex="0" onclick="openHistory(${item.id})">…и ещё ${hidden} — вся история</span>` : ''}
  </div>` : ''}`;
}

function renderRow(item: Item, globalIdx: number): string {
  const due  = dueInfo(item.due_date, item.state);
  const pcfg = item.priority ? PRIORITY_CONFIG[item.priority] : null;
  const execChips = (item.executors || []).map(e => {
    const dept = e.department_name ? `<span class="dept">${esc(e.department_name)} —</span> ` : '';
    return `<span class="exec-chip">${dept}${esc(e.name)}</span>`;
  }).join('') || '—';
  const isSelected = state.selectedItems.has(item.id);

  return `
    <tr class="item-row${isSelected ? ' selected' : ''}" data-item-id="${item.id}">
      <td class="sel"><input type="checkbox" class="row-checkbox" data-id="${item.id}" ${isSelected ? 'checked' : ''} onchange="toggleRowSelect(${item.id}, this.checked)"></td>
      <td class="num">${globalIdx + 1}</td>
      <td class="prio">${pcfg ? `<span class="prio-badge ${pcfg.cls}" title="Приоритет: ${pcfg.label}" aria-label="Приоритет: ${pcfg.label}">${pcfg.letter}</span>` : ''}</td>
      <td class="ticket">${item.ticket ? esc(item.ticket) : '—'}</td>
      <td class="topic">${esc(item.topic)}</td>
      <td class="status">
        ${renderAccordion(item)}
        <span class="status-link" role="button" tabindex="0" onclick="openHistory(${item.id})">+ добавить</span>
      </td>
      <td>
        <select class="state-select ${STATE_BADGE[item.state]}" onchange="changeState(${item.id}, this.value)" title="Сменить состояние">
          ${stateOptions(item.state)}
        </select>
      </td>
      <td class="due ${due.cls}">${item.due_date ? fmtDate(item.due_date) : '—'}${due.rel ? `<br><span class="due-rel">${due.rel}</span>` : ''}</td>
      <td class="executor">${execChips}</td>
      <td class="actions">
        <button class="icon-btn qs-toggle" title="Быстрый статус" onclick="toggleQs(${item.id})">+</button>
        <button class="icon-btn" title="Редактировать" onclick="openEdit(${item.id})">✏️</button>
        <button class="icon-btn del" title="Удалить" onclick="deleteItem(${item.id})">🗑️</button>
      </td>
    </tr>
    <tr class="qs-row" id="qs-${item.id}" style="display:none">
      <td colspan="10">
        <div class="qs-form">
          <input type="date" id="qs-date-${item.id}">
          <input type="text" id="qs-note-${item.id}" placeholder="Описание статуса…" onkeydown="qsKeydown(event,${item.id})">
          <button class="btn-qs-save" onclick="saveQs(${item.id})">Сохранить</button>
          <button class="btn-qs-cancel" onclick="closeQs()">×</button>
        </div>
      </td>
    </tr>`;
}

// ── Main render ────────────────────────────────────────────────────────────────

export function render(): void {
  saveDOMState();

  document.querySelectorAll<HTMLElement>('thead th.sortable').forEach(th => {
    th.classList.remove('sort-asc', 'sort-desc');
    if (th.dataset['col'] === state.sortState.col)
      th.classList.add(state.sortState.dir === 'asc' ? 'sort-asc' : 'sort-desc');
  });

  const allFiltered = applySort(applyFilters(state.allItems));
  const total = allFiltered.length;
  const ps = state.pageSize > 0 ? state.pageSize : total;
  const totalPages = ps > 0 ? Math.max(1, Math.ceil(total / ps)) : 1;
  if (state.currentPage > totalPages) state.currentPage = totalPages;
  const start = (state.currentPage - 1) * ps;
  const items = ps > 0 ? allFiltered.slice(start, start + ps) : allFiltered;

  renderPagination(total, totalPages);

  const tbody = document.getElementById('tableBody')!;
  if (!items.length) {
    tbody.innerHTML = '<tr><td colspan="10" class="empty">Нет пунктов</td></tr>';
    state.openAccordions.clear();
    return;
  }

  tbody.innerHTML = items.map((item, idx) => renderRow(item, start + idx)).join('');

  restoreDOMState();
  _updateSelectAllCheckbox?.();
}
