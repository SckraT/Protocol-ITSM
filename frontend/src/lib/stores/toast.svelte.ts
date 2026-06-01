// Стор уведомлений (toast). Svelte 5 Runes.
export type ToastType = 'success' | 'error' | 'info';

export interface Toast {
  id: number;
  message: string;
  type: ToastType;
}

class ToastStore {
  toasts = $state<Toast[]>([]);
  private nextId = 1;

  /** Показать уведомление. Автоскрытие через timeout мс. */
  show(message: string, type: ToastType = 'info', timeout = 3000): void {
    const id = this.nextId++;
    this.toasts = [...this.toasts, { id, message, type }];
    if (timeout > 0) {
      setTimeout(() => this.dismiss(id), timeout);
    }
  }

  success(message: string): void {
    this.show(message, 'success');
  }

  error(message: string): void {
    this.show(message, 'error', 5000);
  }

  dismiss(id: number): void {
    this.toasts = this.toasts.filter((t) => t.id !== id);
  }
}

export const toastStore = new ToastStore();
