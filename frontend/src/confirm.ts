let confirmResolve: ((v: boolean) => void) | null = null;

const confirmOverlay = () => document.getElementById('confirmOverlay')!;

export function confirmDialog(message: string, okLabel = 'Удалить'): Promise<boolean> {
  document.getElementById('confirmMsg')!.textContent = message;
  document.getElementById('confirmOk')!.textContent  = okLabel;
  confirmOverlay().classList.add('open');
  document.getElementById('confirmCancel')!.focus();
  return new Promise(resolve => { confirmResolve = resolve; });
}

export function closeConfirm(result: boolean): void {
  confirmOverlay().classList.remove('open');
  if (confirmResolve) { confirmResolve(result); confirmResolve = null; }
}

export function initConfirmEvents(): void {
  document.getElementById('confirmOk')!.addEventListener('click', () => closeConfirm(true));
  document.getElementById('confirmCancel')!.addEventListener('click', () => closeConfirm(false));
  confirmOverlay().addEventListener('click', e => {
    if (e.target === confirmOverlay()) closeConfirm(false);
  });
}
