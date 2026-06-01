// Стор подтверждений: promise-based диалог. Svelte 5 Runes.
interface ConfirmOptions {
  title: string;
  message: string;
  confirmLabel?: string;
  danger?: boolean;
}

class ConfirmStore {
  open = $state(false);
  title = $state('');
  message = $state('');
  confirmLabel = $state('Подтвердить');
  danger = $state(false);

  private resolver: ((value: boolean) => void) | null = null;

  /** Показать диалог подтверждения. Возвращает Promise<boolean>. */
  ask(options: ConfirmOptions): Promise<boolean> {
    this.title = options.title;
    this.message = options.message;
    this.confirmLabel = options.confirmLabel ?? 'Подтвердить';
    this.danger = options.danger ?? false;
    this.open = true;
    return new Promise<boolean>((resolve) => {
      this.resolver = resolve;
    });
  }

  confirm(): void {
    this.open = false;
    this.resolver?.(true);
    this.resolver = null;
  }

  cancel(): void {
    this.open = false;
    this.resolver?.(false);
    this.resolver = null;
  }
}

export const confirmStore = new ConfirmStore();
