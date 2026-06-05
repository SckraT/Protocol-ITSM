import { describe, expect, it } from 'vitest';
import { plural } from './format';

describe('plural', () => {
  const days: [string, string, string] = ['день', 'дня', 'дней'];

  it('форма 1 — для чисел, оканчивающихся на 1 (кроме 11)', () => {
    expect(plural(1, days)).toBe('день');
    expect(plural(21, days)).toBe('день');
    expect(plural(101, days)).toBe('день');
  });

  it('форма 2 — для 2..4 (кроме 12..14)', () => {
    expect(plural(2, days)).toBe('дня');
    expect(plural(3, days)).toBe('дня');
    expect(plural(24, days)).toBe('дня');
  });

  it('форма 3 — для 0, 5..20, 11..14', () => {
    expect(plural(0, days)).toBe('дней');
    expect(plural(5, days)).toBe('дней');
    expect(plural(11, days)).toBe('дней');
    expect(plural(12, days)).toBe('дней');
    expect(plural(14, days)).toBe('дней');
  });
});
