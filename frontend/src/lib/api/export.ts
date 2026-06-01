// API для экспорта и импорта данных.
import { apiPostForm, apiUrl } from './client';

/** Скачать CSV — прямая навигация для загрузки файла. */
export function exportCsv(): void {
  window.location.href = apiUrl('/export/csv');
}

/** Скачать XLSX. */
export function exportXlsx(): void {
  window.location.href = apiUrl('/export/xlsx');
}

/** Импортировать задачи из CSV-файла. */
export async function importCsv(file: File): Promise<{ imported: number }> {
  const fd = new FormData();
  fd.append('file', file);
  return apiPostForm<{ imported: number }>('/import/csv', fd);
}
