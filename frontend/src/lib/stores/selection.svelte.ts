// Стор выделения задач для bulk-операций. Svelte 5 Runes.
class SelectionStore {
  // SvelteSet недоступен напрямую — используем обычный Set, пересоздаём для реактивности
  selected = $state<Set<number>>(new Set());

  count = $derived(this.selected.size);

  has(id: number): boolean {
    return this.selected.has(id);
  }

  toggle(id: number): void {
    const next = new Set(this.selected);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    this.selected = next;
  }

  set(id: number, value: boolean): void {
    const next = new Set(this.selected);
    if (value) next.add(id);
    else next.delete(id);
    this.selected = next;
  }

  /** Выделить/снять выделение со всех переданных id. */
  setAll(ids: number[], value: boolean): void {
    const next = new Set(this.selected);
    for (const id of ids) {
      if (value) next.add(id);
      else next.delete(id);
    }
    this.selected = next;
  }

  clear(): void {
    this.selected = new Set();
  }

  ids(): number[] {
    return [...this.selected];
  }
}

export const selectionStore = new SelectionStore();
