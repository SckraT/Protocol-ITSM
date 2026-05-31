import { state } from './state';
import {
  fetchExecutors, fetchDepartments,
  createDepartment, updateDepartment, deleteDepartmentApi,
  createExecutor, updateExecutor, deleteExecutorApi,
} from './api';
import { toast } from './toast';
import { confirmDialog } from './confirm';
import { esc, plural } from './utils';

async function loadRefs(): Promise<void> {
  try {
    const [executors, departments] = await Promise.all([fetchExecutors(), fetchDepartments()]);
    state.allExecutors   = executors;
    state.allDepartments = departments;
    renderDeptList();
    renderExecList();
    renderExecDeptSelect();
  } catch {
    toast('Не удалось загрузить справочники', 'error');
  }
}

// ── Departments ────────────────────────────────────────────────────────────────

export function renderDeptList(): void {
  const list = document.getElementById('deptList')!;
  if (!state.allDepartments.length) {
    list.innerHTML = '<div class="ref-empty">Список пуст</div>';
    return;
  }

  const execPerDept = new Map<number, number>();
  state.allExecutors.forEach(e => {
    if (e.department_id) execPerDept.set(e.department_id, (execPerDept.get(e.department_id) || 0) + 1);
  });

  list.innerHTML = state.allDepartments.map(d => {
    if (state.editingDeptId === d.id) {
      return `
        <div class="ref-item">
          <div class="ref-edit-form">
            <input type="text" id="edit-dept-name-${d.id}" value="${esc(d.name)}" maxlength="100"
                   onkeydown="refEditKeydown(event, () => saveEditDept(${d.id}), cancelEditDept)">
            <button class="btn-ref-save" onclick="saveEditDept(${d.id})">Сохранить</button>
            <button class="btn-ref-cancel" onclick="cancelEditDept()" title="Отмена">×</button>
          </div>
        </div>`;
    }
    const cnt = execPerDept.get(d.id) || 0;
    const badgeCls = cnt > 0 ? 'ref-count-badge ref-count-badge--active' : 'ref-count-badge ref-count-badge--zero';
    const badgeTxt = cnt > 0 ? `${cnt} ${plural(cnt, ['исполнитель', 'исполнителя', 'исполнителей'])}` : 'нет исполнителей';
    return `
      <div class="ref-item">
        <span class="ref-name">${esc(d.name)}</span>
        <span class="${badgeCls}">${badgeTxt}</span>
        <button class="ref-edit" onclick="startEditDept(${d.id})" title="Редактировать">✏️</button>
        <button class="ref-del" onclick="deleteDept(${d.id})" title="Удалить">×</button>
      </div>`;
  }).join('');

  if (state.editingDeptId != null) {
    const inp = document.getElementById(`edit-dept-name-${state.editingDeptId}`) as HTMLInputElement | null;
    if (inp) { inp.focus(); inp.select(); }
  }
}

export function startEditDept(id: number): void { state.editingExecId = null; state.editingDeptId = id; renderDeptList(); renderExecList(); }
export function cancelEditDept(): void          { state.editingDeptId = null; renderDeptList(); }

export async function saveEditDept(id: number): Promise<void> {
  const name = (document.getElementById(`edit-dept-name-${id}`) as HTMLInputElement | null)?.value.trim();
  if (!name) return;
  try {
    const res = await updateDepartment(id, name);
    if (res.status === 409) { toast('Такой отдел уже существует', 'error'); return; }
    state.editingDeptId = null;
    await loadRefs();
    toast('Отдел обновлён', 'success');
  } catch {
    toast('Не удалось сохранить отдел', 'error');
  }
}

async function addDept(): Promise<void> {
  const input = document.getElementById('deptNameInput') as HTMLInputElement;
  const name  = input.value.trim();
  if (!name) return;
  try {
    const res = await createDepartment(name);
    if (res.status === 409) { toast('Такой отдел уже существует', 'error'); return; }
    input.value = '';
    await loadRefs();
    toast('Отдел добавлен', 'success');
  } catch {
    toast('Не удалось добавить отдел', 'error');
  }
}

export async function deleteDept(id: number): Promise<void> {
  const dept = state.allDepartments.find(d => d.id === id);
  if (!await confirmDialog(`Удалить отдел «${dept?.name}»?\n\nИсполнители этого отдела останутся, но потеряют привязку к отделу.`)) return;
  try {
    await deleteDepartmentApi(id);
    await loadRefs();
    toast('Отдел удалён', 'success');
  } catch {
    toast('Не удалось удалить отдел', 'error');
  }
}

// ── Executors ──────────────────────────────────────────────────────────────────

export function renderExecList(): void {
  const list = document.getElementById('execList')!;
  const q = state.execSearchQuery.toLowerCase();
  const visible = q
    ? state.allExecutors.filter(e =>
        e.name.toLowerCase().includes(q) || (e.department_name || '').toLowerCase().includes(q))
    : state.allExecutors;

  if (!visible.length) {
    list.innerHTML = `<div class="ref-empty">${q ? 'Не найдено' : 'Список пуст'}</div>`;
    return;
  }

  const taskCount = new Map<number, number>();
  state.allItems.forEach(item =>
    (item.executors || []).forEach(e => {
      if (e.id) taskCount.set(e.id, (taskCount.get(e.id) || 0) + 1);
    })
  );

  const renderExecRow = (e: (typeof state.allExecutors)[0]): string => {
    if (state.editingExecId === e.id) {
      const opts = ['<option value="">Без отдела</option>'].concat(
        state.allDepartments.map(d =>
          `<option value="${d.id}" ${d.id === e.department_id ? 'selected' : ''}>${esc(d.name)}</option>`)
      ).join('');
      return `
        <div class="ref-item">
          <div class="ref-edit-form">
            <input type="text" id="edit-exec-name-${e.id}" value="${esc(e.name)}" maxlength="120"
                   onkeydown="refEditKeydown(event, () => saveEditExec(${e.id}), cancelEditExec)">
            <select id="edit-exec-dept-${e.id}">${opts}</select>
            <button class="btn-ref-save" onclick="saveEditExec(${e.id})">Сохранить</button>
            <button class="btn-ref-cancel" onclick="cancelEditExec()" title="Отмена">×</button>
          </div>
        </div>`;
    }
    const cnt = taskCount.get(e.id) || 0;
    const badgeCls = cnt > 0 ? 'ref-count-badge ref-count-badge--active' : 'ref-count-badge ref-count-badge--zero';
    const badgeTxt = cnt > 0 ? `${cnt} ${plural(cnt, ['задача', 'задачи', 'задач'])}` : 'нет задач';
    return `
      <div class="ref-item">
        <span class="ref-name">${esc(e.name)}</span>
        <span class="${badgeCls}">${badgeTxt}</span>
        <button class="ref-edit" onclick="startEditExec(${e.id})" title="Редактировать">✏️</button>
        <button class="ref-del" onclick="deleteExecutor(${e.id})" title="Удалить">×</button>
      </div>`;
  };

  const byDept = new Map<string, typeof visible>();
  const noDept: typeof visible = [];
  visible.forEach(e => {
    if (e.department_name) {
      if (!byDept.has(e.department_name)) byDept.set(e.department_name, []);
      byDept.get(e.department_name)!.push(e);
    } else {
      noDept.push(e);
    }
  });

  let html = '';
  [...byDept.keys()].sort((a, b) => a.localeCompare(b, 'ru')).forEach(dept => {
    html += `<div class="ref-dept-header">${esc(dept)}</div>`;
    html += byDept.get(dept)!.map(renderExecRow).join('');
  });
  if (noDept.length) {
    if (byDept.size) html += `<div class="ref-dept-header">Без отдела</div>`;
    html += noDept.map(renderExecRow).join('');
  }
  list.innerHTML = html;

  if (state.editingExecId != null) {
    const inp = document.getElementById(`edit-exec-name-${state.editingExecId}`) as HTMLInputElement | null;
    if (inp) { inp.focus(); inp.select(); }
  }
}

export function startEditExec(id: number): void { state.editingDeptId = null; state.editingExecId = id; renderExecList(); renderDeptList(); }
export function cancelEditExec(): void          { state.editingExecId = null; renderExecList(); }

export async function saveEditExec(id: number): Promise<void> {
  const name = (document.getElementById(`edit-exec-name-${id}`) as HTMLInputElement | null)?.value.trim();
  if (!name) return;
  const deptVal = (document.getElementById(`edit-exec-dept-${id}`) as HTMLSelectElement | null)?.value;
  const deptId  = deptVal ? parseInt(deptVal) : null;
  try {
    const res = await updateExecutor(id, name, deptId);
    if (res.status === 409) { toast('Такой исполнитель уже есть в списке', 'error'); return; }
    state.editingExecId = null;
    await loadRefs();
    toast('Исполнитель обновлён', 'success');
  } catch {
    toast('Не удалось сохранить исполнителя', 'error');
  }
}

export function renderExecDeptSelect(): void {
  const sel = document.getElementById('execDeptSelect') as HTMLSelectElement;
  const cur = sel.value;
  sel.innerHTML = '<option value="">Без отдела</option>';
  state.allDepartments.forEach(d => {
    const opt = document.createElement('option');
    opt.value = String(d.id);
    opt.textContent = d.name;
    sel.appendChild(opt);
  });
  sel.value = cur;
}

async function addExecutorRef(): Promise<void> {
  const nameInput = document.getElementById('execNameInput') as HTMLInputElement;
  const deptSel   = document.getElementById('execDeptSelect') as HTMLSelectElement;
  const name = nameInput.value.trim();
  if (!name) return;
  const deptId = deptSel.value ? parseInt(deptSel.value) : null;
  try {
    const res = await createExecutor(name, deptId);
    if (res.status === 409) { toast('Такой исполнитель уже есть в списке', 'error'); return; }
    nameInput.value = '';
    await loadRefs();
    toast('Исполнитель добавлен', 'success');
  } catch {
    toast('Не удалось добавить исполнителя', 'error');
  }
}

export async function deleteExecutor(id: number): Promise<void> {
  const exec = state.allExecutors.find(e => e.id === id);
  if (!await confirmDialog(`Удалить «${exec?.name}» из справочника?\n\nЗадачи с этим исполнителем затронуты не будут.`)) return;
  try {
    await deleteExecutorApi(id);
    await loadRefs();
    toast('Исполнитель удалён', 'success');
  } catch {
    toast('Не удалось удалить исполнителя', 'error');
  }
}

export function refEditKeydown(e: KeyboardEvent, onSave: () => void, onCancel: () => void): void {
  if (e.key === 'Enter')  { e.preventDefault(); onSave(); }
  if (e.key === 'Escape') { e.preventDefault(); onCancel(); }
}

export function initRefsEvents(): void {
  document.getElementById('btnDeptAdd')!.addEventListener('click', () => addDept());
  (document.getElementById('deptNameInput') as HTMLInputElement).addEventListener('keydown', e => {
    if (e.key === 'Enter') addDept();
  });
  document.getElementById('btnExecAdd')!.addEventListener('click', () => addExecutorRef());
  (document.getElementById('execNameInput') as HTMLInputElement).addEventListener('keydown', e => {
    if (e.key === 'Enter') addExecutorRef();
  });
  (document.getElementById('execSearchInput') as HTMLInputElement).addEventListener('input', e => {
    state.execSearchQuery = (e.target as HTMLInputElement).value.toLowerCase().trim();
    renderExecList();
  });
}

export { loadRefs };
