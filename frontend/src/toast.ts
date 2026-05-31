import { esc } from './utils';

export type ToastType = 'success' | 'error' | 'info';

export function toast(message: string, type: ToastType = 'info'): void {
  const wrap = document.getElementById('toastWrap')!;
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ';
  el.innerHTML = `<span class="toast-icon">${icon}</span><span>${esc(message)}</span>`;
  wrap.appendChild(el);
  setTimeout(() => {
    el.classList.add('hide');
    el.addEventListener('transitionend', () => el.remove(), { once: true });
  }, 3200);
}
