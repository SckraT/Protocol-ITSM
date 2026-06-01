<script lang="ts">
  // Главная страница: дашборд, фильтры, таблица задач, drawer, групповые операции.
  import { Plus, Download, Upload } from 'lucide-svelte';
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import Dashboard from '$lib/components/common/Dashboard.svelte';
  import SearchBar from '$lib/components/common/SearchBar.svelte';
  import Filters from '$lib/components/items/Filters.svelte';
  import ItemsTable from '$lib/components/items/ItemsTable.svelte';
  import ItemDrawer from '$lib/components/items/ItemDrawer.svelte';
  import BulkActions from '$lib/components/items/BulkActions.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { exportCsv, exportXlsx, importCsv } from '$lib/api/export';
  import { itemsStore } from '$lib/stores/items.svelte';
  import { toastStore } from '$lib/stores/toast.svelte';

  // Состояние drawer'а
  let drawerOpen = $state(false);
  let drawerItemId = $state<number | null>(null);
  let fileInput: HTMLInputElement;

  function openItem(id: number) {
    drawerItemId = id;
    drawerOpen = true;
    goto(`/?task=${id}`, { replaceState: true, keepFocus: true, noScroll: true });
  }

  function openNew() {
    drawerItemId = null;
    drawerOpen = true;
  }

  function closeDrawer() {
    drawerOpen = false;
    drawerItemId = null;
    goto('/', { replaceState: true, keepFocus: true, noScroll: true });
  }

  // Открываем задачу по ?task=N из URL (при загрузке / прямой ссылке)
  onMount(() => {
    const taskParam = $page.url.searchParams.get('task');
    if (taskParam) {
      const id = Number(taskParam);
      if (!Number.isNaN(id)) {
        drawerItemId = id;
        drawerOpen = true;
      }
    }
  });

  async function handleImport(e: Event) {
    const input = e.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    try {
      const result = await importCsv(file);
      toastStore.success(`Импортировано: ${result.imported}`);
      await itemsStore.load();
    } catch (err) {
      toastStore.error(err instanceof Error ? err.message : 'Ошибка импорта');
    } finally {
      input.value = '';
    }
  }
</script>

<!-- Заголовок только для печати -->
<div class="print-only">
  <div class="print-title">Протокол совещаний</div>
  <div class="print-meta">Дата печати: {new Date().toLocaleDateString('ru-RU')}</div>
</div>

<div class="no-print">
  <Dashboard />
</div>

<!-- Панель инструментов -->
<div class="no-print mb-4 flex flex-wrap items-center justify-between gap-3">
  <div class="flex flex-wrap items-center gap-2">
    <SearchBar />
    <Filters />
  </div>
  <div class="flex items-center gap-2">
    <Button variant="secondary" size="sm" onclick={() => exportCsv()}>
      <Download size={14} /> CSV
    </Button>
    <Button variant="secondary" size="sm" onclick={() => exportXlsx()}>
      <Download size={14} /> Excel
    </Button>
    <Button variant="secondary" size="sm" onclick={() => fileInput.click()}>
      <Upload size={14} /> Импорт
    </Button>
    <Button onclick={openNew}>
      <Plus size={16} /> Задача
    </Button>
  </div>
</div>

<input
  bind:this={fileInput}
  type="file"
  accept=".csv"
  class="hidden"
  onchange={handleImport}
/>

<ItemsTable onOpen={openItem} />

<BulkActions />

<ItemDrawer itemId={drawerItemId} open={drawerOpen} onClose={closeDrawer} />
