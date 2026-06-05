<script lang="ts">
  // Плавающая панель групповых операций. Появляется при выделении задач.
  import { X } from 'lucide-svelte';
  import { fly } from 'svelte/transition';
  import type { ItemState } from '$lib/api/types';
  import Button from '$lib/components/ui/Button.svelte';
  import { itemsStore } from '$lib/stores/items.svelte';
  import { selectionStore } from '$lib/stores/selection.svelte';
  import { confirmStore } from '$lib/stores/confirm.svelte';
  import { toastStore } from '$lib/stores/toast.svelte';
  import { STATE_LABEL, STATE_ORDER } from '$lib/utils/constants';
  import { plural } from '$lib/utils/format';

  let bulkState = $state<ItemState | ''>('');

  async function applyState() {
    if (!bulkState) return;
    const ids = selectionStore.ids();
    const { ok, failed } = await itemsStore.bulkChangeState(ids, bulkState);
    if (failed === 0) toastStore.success(`Обновлено: ${ok}`);
    else toastStore.error(`Обновлено: ${ok} из ${ids.length}, ошибок: ${failed}`);
    bulkState = '';
    selectionStore.clear();
  }

  async function deleteSelected() {
    const ids = selectionStore.ids();
    const ok = await confirmStore.ask({
      title: 'Удалить выбранные задачи?',
      message: `Будет удалено задач: ${ids.length}. Действие необратимо.`,
      confirmLabel: 'Удалить',
      danger: true
    });
    if (!ok) return;
    const { ok: removed, failed } = await itemsStore.bulkRemove(ids);
    if (failed === 0) toastStore.success(`Удалено: ${removed}`);
    else toastStore.error(`Удалено: ${removed} из ${ids.length}, ошибок: ${failed}`);
    selectionStore.clear();
  }

  const countLabel = $derived(
    `${selectionStore.count} ${plural(selectionStore.count, ['задача', 'задачи', 'задач'])}`
  );
</script>

{#if selectionStore.count > 0}
  <div
    class="fixed inset-x-0 bottom-0 z-30 flex justify-center p-4"
    transition:fly={{ y: 80, duration: 200 }}
  >
    <div
      class="flex items-center gap-3 rounded-lg border border-[var(--border)] bg-[var(--table-bg)] px-4 py-3 shadow-xl"
    >
      <span class="text-sm font-medium">Выбрано: {countLabel}</span>

      <select
        bind:value={bulkState}
        onchange={applyState}
        class="rounded border border-[var(--border)] bg-[var(--table-bg)] px-2 py-1 text-sm"
        aria-label="Изменить состояние выбранных"
      >
        <option value="">Изменить состояние…</option>
        {#each STATE_ORDER as st (st)}
          <option value={st}>{STATE_LABEL[st]}</option>
        {/each}
      </select>

      <Button variant="danger" size="sm" onclick={deleteSelected}>Удалить</Button>

      <button
        class="text-[var(--text-secondary)] hover:text-[var(--text-body)]"
        aria-label="Снять выделение"
        onclick={() => selectionStore.clear()}
      >
        <X size={18} />
      </button>
    </div>
  </div>
{/if}
