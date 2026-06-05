import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { dueInfo, fmtDate, isOverdue } from './date';

describe('fmtDate', () => {
  it('форматирует ISO-дату в DD.MM.YYYY', () => {
    expect(fmtDate('2026-06-05')).toBe('05.06.2026');
  });

  it('пустые значения → пустая строка', () => {
    expect(fmtDate(null)).toBe('');
    expect(fmtDate(undefined)).toBe('');
    expect(fmtDate('')).toBe('');
  });
});

describe('isOverdue', () => {
  it('прошедшая дата у незакрытой задачи — просрочена', () => {
    expect(isOverdue('2000-01-01', 'in_progress')).toBe(true);
  });

  it('будущая дата — не просрочена', () => {
    expect(isOverdue('2999-01-01', 'in_progress')).toBe(false);
  });

  it('закрытая задача никогда не просрочена', () => {
    expect(isOverdue('2000-01-01', 'closed')).toBe(false);
  });

  it('без срока — не просрочена', () => {
    expect(isOverdue(null, 'in_progress')).toBe(false);
  });
});

describe('dueInfo (с фиксированной «сегодня» = 2026-06-05)', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date(2026, 5, 5)); // 5 июня 2026, локальное время
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  it('закрытая или без срока — пустой результат', () => {
    expect(dueInfo(null, 'in_progress')).toEqual({ cls: '', rel: '' });
    expect(dueInfo('2026-06-10', 'closed')).toEqual({ cls: '', rel: '' });
  });

  it('срок сегодня → soon/«сегодня»', () => {
    expect(dueInfo('2026-06-05', 'in_progress')).toEqual({ cls: 'soon', rel: 'сегодня' });
  });

  it('срок завтра → soon/«завтра»', () => {
    expect(dueInfo('2026-06-06', 'in_progress')).toEqual({ cls: 'soon', rel: 'завтра' });
  });

  it('просрочка помечается классом overdue', () => {
    const r = dueInfo('2026-06-03', 'in_progress');
    expect(r.cls).toBe('overdue');
    expect(r.rel).toContain('просрочено на 2');
  });
});
