// Работа с датами и расчёт сроков. Портировано из v1 без изменений логики.
import type { ItemState } from '$lib/api/types';
import { plural } from './format';

/** Форматирует ISO-дату (YYYY-MM-DD) в DD.MM.YYYY. */
export function fmtDate(d: string | null | undefined): string {
  if (!d) return '';
  const [y, m, day] = d.split('-');
  return `${day}.${m}.${y}`;
}

/** Форматирует ISO-таймстамп (created_at) в локальную дату DD.MM.YYYY. */
export function fmtIsoDate(iso: string | null | undefined): string {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString('ru-RU');
}

/** Сегодняшняя дата в формате YYYY-MM-DD. */
export function today(): string {
  return new Date().toISOString().slice(0, 10);
}

/** Считает количество рабочих дней (пн-пт) в интервале [from, to]. */
function countWorkdays(from: Date, to: Date): number {
  let count = 0;
  const cur = new Date(from);
  while (cur <= to) {
    const day = cur.getDay();
    if (day !== 0 && day !== 6) count++;
    cur.setDate(cur.getDate() + 1);
  }
  return count;
}

/**
 * Возвращает CSS-класс и относительный текст срока задачи.
 * Закрытые задачи и задачи без срока — пустой результат.
 */
export function dueInfo(dueDate: string | null, state: ItemState): { cls: string; rel: string } {
  if (!dueDate || state === 'closed') return { cls: '', rel: '' };
  const t = new Date();
  t.setHours(0, 0, 0, 0);
  const [y, m, d] = dueDate.split('-').map(Number);
  const due = new Date(y, m - 1, d);
  const diff = Math.round((due.getTime() - t.getTime()) / 86400000);

  if (diff < 0) {
    const cal = -diff;
    const yesterday = new Date(t.getTime() - 86400000);
    const wd = countWorkdays(due, yesterday);
    const wdNote =
      cal >= 3 && wd !== cal ? ` (${wd} ${plural(wd, ['рабочий', 'рабочих', 'рабочих'])})` : '';
    return {
      cls: 'overdue',
      rel: `просрочено на ${cal} ${plural(cal, ['день', 'дня', 'дней'])}${wdNote}`
    };
  }
  if (diff === 0) return { cls: 'soon', rel: 'сегодня' };
  if (diff === 1) return { cls: 'soon', rel: 'завтра' };
  if (diff <= 7) return { cls: 'soon', rel: `через ${diff} ${plural(diff, ['день', 'дня', 'дней'])}` };
  if (diff <= 30) {
    const weeks = Math.round(diff / 7);
    return { cls: '', rel: `через ${weeks} ${plural(weeks, ['нед.', 'нед.', 'нед.'])}` };
  }
  const months = Math.round(diff / 30);
  return { cls: '', rel: `через ${months} ${plural(months, ['мес.', 'мес.', 'мес.'])}` };
}

/** Проверяет, просрочена ли задача (для счётчика в заголовке вкладки). */
export function isOverdue(dueDate: string | null, state: ItemState): boolean {
  if (!dueDate || state === 'closed') return false;
  return dueDate < today();
}
