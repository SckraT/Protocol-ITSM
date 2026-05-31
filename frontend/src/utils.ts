import type { ItemState, Priority } from './types';

export const STATE_LABEL: Record<ItemState, string> = {
  in_progress: 'В работе',
  postponed:   'Отложено',
  closed:      'Закрыто',
};

export const STATE_BADGE: Record<ItemState, string> = {
  in_progress: 'badge-in_progress',
  postponed:   'badge-postponed',
  closed:      'badge-closed',
};

export const STATE_ORDER: ItemState[] = ['in_progress', 'postponed', 'closed'];

export const PRIORITY_CONFIG: Record<Priority, { cls: string; label: string; letter: string }> = {
  high:   { cls: 'prio-high',   label: 'Высокий', letter: 'В' },
  medium: { cls: 'prio-medium', label: 'Средний', letter: 'С' },
  low:    { cls: 'prio-low',    label: 'Низкий',  letter: 'Н' },
};

export const PRIORITY_SORT_ORDER: Record<string, number> = {
  high: 0, medium: 1, low: 2, '': 3,
};

export function fmtDate(d: string | null | undefined): string {
  if (!d) return '';
  const [y, m, day] = d.split('-');
  return `${day}.${m}.${y}`;
}

export function esc(s: unknown): string {
  return String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

export function today(): string {
  return new Date().toISOString().slice(0, 10);
}

/** Склонение: plural(3, ['день','дня','дней']) */
export function plural(n: number, forms: [string, string, string]): string {
  const a = Math.abs(n) % 100, b = a % 10;
  if (a > 10 && a < 20) return forms[2];
  if (b > 1 && b < 5)   return forms[1];
  if (b === 1)           return forms[0];
  return forms[2];
}

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

export function dueInfo(dueDate: string | null, state: ItemState): { cls: string; rel: string } {
  if (!dueDate || state === 'closed') return { cls: '', rel: '' };
  const t = new Date(); t.setHours(0, 0, 0, 0);
  const [y, m, d] = dueDate.split('-').map(Number);
  const due  = new Date(y, m - 1, d);
  const diff = Math.round((due.getTime() - t.getTime()) / 86400000);

  if (diff < 0) {
    const cal = -diff;
    const yesterday = new Date(t.getTime() - 86400000);
    const wd = countWorkdays(due, yesterday);
    const wdNote = (cal >= 3 && wd !== cal)
      ? ` (${wd} ${plural(wd, ['рабочий', 'рабочих', 'рабочих'])})`
      : '';
    return { cls: 'overdue', rel: `просрочено на ${cal} ${plural(cal, ['день', 'дня', 'дней'])}${wdNote}` };
  }
  if (diff === 0) return { cls: 'soon', rel: 'сегодня' };
  if (diff === 1) return { cls: 'soon', rel: 'завтра' };
  if (diff <= 7)  return { cls: 'soon', rel: `через ${diff} ${plural(diff, ['день', 'дня', 'дней'])}` };
  if (diff <= 30) {
    const weeks = Math.round(diff / 7);
    return { cls: '', rel: `через ${weeks} ${plural(weeks, ['нед.', 'нед.', 'нед.'])}` };
  }
  const months = Math.round(diff / 30);
  return { cls: '', rel: `через ${months} ${plural(months, ['мес.', 'мес.', 'мес.'])}` };
}
