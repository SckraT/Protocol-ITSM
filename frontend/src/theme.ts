import type { Theme } from './types';

export function initTheme(): void {
  const saved = localStorage.getItem('theme') || 'light';
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme: Theme = saved === 'auto' ? (prefersDark ? 'dark' : 'light') : (saved as Theme);
  setTheme(theme);
}

export function setTheme(theme: Theme): void {
  if (theme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
    document.querySelector<HTMLElement>('#themeToggle .theme-icon')!.textContent = '☀️';
  } else {
    document.documentElement.removeAttribute('data-theme');
    document.querySelector<HTMLElement>('#themeToggle .theme-icon')!.textContent = '🌙';
  }
  localStorage.setItem('theme', theme);
}

export function toggleTheme(): void {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  setTheme(isDark ? 'light' : 'dark');
}
