// Константы интерфейса.
import type { ItemState, Priority } from '$lib/api/types';

export const STATE_LABEL: Record<ItemState, string> = {
  in_progress: 'В работе',
  postponed: 'Отложено',
  closed: 'Закрыто'
};

export const STATE_BADGE: Record<ItemState, string> = {
  in_progress: 'badge-in_progress',
  postponed: 'badge-postponed',
  closed: 'badge-closed'
};

export const STATE_ORDER: ItemState[] = ['in_progress', 'postponed', 'closed'];

export const PRIORITY_CONFIG: Record<Priority, { cls: string; label: string; letter: string }> = {
  high: { cls: 'prio-high', label: 'Высокий', letter: 'В' },
  medium: { cls: 'prio-medium', label: 'Средний', letter: 'С' },
  low: { cls: 'prio-low', label: 'Низкий', letter: 'Н' }
};

export const PRIORITY_SORT_ORDER: Record<string, number> = {
  high: 0,
  medium: 1,
  low: 2,
  '': 3
};
