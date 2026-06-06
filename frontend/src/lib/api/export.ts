// API для экспорта и импорта данных.
import { apiDownload, apiPostForm } from './client';

/** Скачать CSV (авторизованный запрос + blob). */
export function exportCsv(): Promise<void> {
  return apiDownload('/export/csv', 'protocol.csv');
}

/** Скачать XLSX (авторизованный запрос + blob). */
export function exportXlsx(): Promise<void> {
  return apiDownload('/export/xlsx', 'protocol.xlsx');
}

/** Импортировать задачи из CSV-файла. */
export async function importCsv(file: File): Promise<{ imported: number }> {
  const fd = new FormData();
  fd.append('file', file);
  return apiPostForm<{ imported: number }>('/import/csv', fd);
}
