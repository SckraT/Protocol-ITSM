import { state } from './state';
import { fetchItems, fetchExecutors, fetchDepartments } from './api';
import { populateAdvFilters, applyViewStateToDOM } from './filters';
import { updateDashboardCounts, render } from './render';

export async function loadAll(): Promise<void> {
  const tbody = document.getElementById('tableBody')!;
  tbody.innerHTML = '<tr class="state-row"><td colspan="9"><div class="spinner"></div></td></tr>';
  try {
    const [items, executors, departments] = await Promise.all([
      fetchItems(),
      fetchExecutors(),
      fetchDepartments(),
    ]);
    state.allItems       = items;
    state.allExecutors   = executors;
    state.allDepartments = departments;
    populateAdvFilters();
    applyViewStateToDOM();
    updateDashboardCounts();
    render();
  } catch {
    tbody.innerHTML = '<tr class="state-row"><td colspan="9">Не удалось загрузить данные.'
      + '<br><button class="btn-secondary retry" onclick="loadAll()">Повторить</button></td></tr>';
  }
}
