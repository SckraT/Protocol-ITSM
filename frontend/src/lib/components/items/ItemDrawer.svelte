<script lang="ts">
  // Боковая панель задачи: форма редактирования + история статусов.
  import { ExternalLink } from 'lucide-svelte';
  import type { Item, ItemState, Priority, Status } from '$lib/api/types';
  import { fetchItem } from '$lib/api/items';
  import { addStatus, deleteStatus, fetchStatuses } from '$lib/api/statuses';
  import Drawer from '$lib/components/ui/Drawer.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Loader from '$lib/components/ui/Loader.svelte';
  import ItemForm from './ItemForm.svelte';
  import Timeline from './Timeline.svelte';
  import { itemsStore } from '$lib/stores/items.svelte';
  import { confirmStore } from '$lib/stores/confirm.svelte';
  import { toastStore } from '$lib/stores/toast.svelte';

  let {
    itemId = null,
    open = false,
    onClose
  }: {
    itemId?: number | null;
    open?: boolean;
    onClose: () => void;
  } = $props();

  // Текущая задача из стора (для режима редактирования)
  const item = $derived(itemId !== null ? (itemsStore.getById(itemId) ?? null) : null);
  const isEdit = $derived(itemId !== null);

  let statuses = $state<Status[]>([]);
  // Состояние сохранения формы (биндится из ItemForm для блокировки кнопки)
  let saving = $state(false);

  // Загружаем статусы при открытии существующей задачи
  $effect(() => {
    if (open && itemId !== null) {
      loadStatuses(itemId);
    } else {
      statuses = [];
    }
  });

  async function loadStatuses(id: number) {
    try {
      statuses = await fetchStatuses(id);
    } catch {
      statuses = [];
    }
  }

  // Сохранение задачи (создание или обновление)
  async function handleSave(data: {
    topic: string;
    ticket: string | null;
    priority: Priority | null;
    state: ItemState;
    due_date: string | null;
    meeting_id: number | null;
    executor_ids: number[];
  }) {
    if (isEdit && itemId !== null) {
      const ok = await itemsStore.update(itemId, data);
      if (ok) {
        toastStore.success('Сохранено');
        onClose();
      }
    } else {
      const created = await itemsStore.create(data);
      if (created) onClose();
    }
  }

  async function handleDelete() {
    if (itemId === null) return;
    const ok = await confirmStore.ask({
      title: 'Удалить задачу?',
      message: 'Задача и вся история статусов будут удалены безвозвратно.',
      confirmLabel: 'Удалить',
      danger: true
    });
    if (ok) {
      await itemsStore.remove(itemId);
      onClose();
    }
  }

  // Добавление статуса
  async function handleAddStatus(date: string | null, note: string) {
    if (itemId === null) return;
    try {
      await addStatus(itemId, { status_date: date, status_note: note });
      await refresh(itemId);
      toastStore.success('Статус добавлен');
    } catch (e) {
      toastStore.error(e instanceof Error ? e.message : 'Ошибка');
    }
  }

  // Удаление статуса
  async function handleDeleteStatus(statusId: number) {
    if (itemId === null) return;
    try {
      await deleteStatus(statusId);
      await refresh(itemId);
    } catch (e) {
      toastStore.error(e instanceof Error ? e.message : 'Ошибка');
    }
  }

  // Обновляет статусы и саму задачу в сторе (для счётчиков в таблице)
  async function refresh(id: number) {
    statuses = await fetchStatuses(id);
    try {
      const fresh: Item = await fetchItem(id);
      itemsStore.replace(fresh);
    } catch {
      /* ignore */
    }
  }

  function openInNewTab() {
    if (itemId !== null) window.open(`/?task=${itemId}`, '_blank');
  }

  const title = $derived(isEdit ? `Задача #${itemId}` : 'Новая задача');
</script>

<Drawer {open} {title} {onClose}>
  {#if isEdit}
    <div class="mb-3 flex justify-end">
      <button
        class="inline-flex items-center gap-1 text-xs text-[var(--accent)] hover:underline"
        onclick={openInNewTab}
      >
        <ExternalLink size={14} /> Открыть в новой вкладке
      </button>
    </div>
  {/if}

  {#if isEdit && item === null}
    <!-- Открытие по ссылке / F5: задача ещё грузится в стор. Форму не создаём
         раньше данных — иначе её начальные значения (захват через untrack)
         останутся пустыми (см. ItemForm). После загрузки item появится и
         сработает {#key itemId} с заполненными полями. -->
    {#if itemsStore.loaded}
      <p class="py-10 text-center text-[var(--text-secondary)]">Задача не найдена</p>
    {:else}
      <Loader />
    {/if}
  {:else}
    {#key itemId}
      <ItemForm {item} onSave={handleSave} bind:saving />
    {/key}

    {#if isEdit}
      <hr class="my-5 border-[var(--border)]" />
      <Timeline {statuses} onAdd={handleAddStatus} onDelete={handleDeleteStatus} />
    {/if}

    <!-- Кнопки действий — после блока статусов -->
    <div class="mt-5 flex items-center justify-between border-t border-[var(--border)] pt-4">
      {#if isEdit}
        <Button variant="danger" onclick={handleDelete}>Удалить</Button>
      {:else}
        <span></span>
      {/if}
      <Button type="submit" form="item-edit-form" disabled={saving}>
        {isEdit ? 'Сохранить' : 'Создать'}
      </Button>
    </div>
  {/if}
</Drawer>
