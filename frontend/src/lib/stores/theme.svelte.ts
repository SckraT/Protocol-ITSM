// Стор темы (светлая/тёмная). Svelte 5 Runes.
import { browser } from '$app/environment';
import type { Theme } from '$lib/api/types';

const STORAGE_KEY = 'protocol_theme';

function initialTheme(): Theme {
  if (!browser) return 'light';
  const saved = localStorage.getItem(STORAGE_KEY) as Theme | null;
  if (saved === 'light' || saved === 'dark') return saved;
  // Системное предпочтение как fallback
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

class ThemeStore {
  current = $state<Theme>(initialTheme());

  /** Применяет тему к DOM и сохраняет в localStorage. */
  private apply(): void {
    if (!browser) return;
    document.documentElement.setAttribute('data-theme', this.current);
    localStorage.setItem(STORAGE_KEY, this.current);
  }

  toggle(): void {
    this.current = this.current === 'light' ? 'dark' : 'light';
    this.apply();
  }

  set(theme: Theme): void {
    this.current = theme;
    this.apply();
  }
}

export const themeStore = new ThemeStore();
