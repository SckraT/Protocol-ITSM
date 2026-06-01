<script lang="ts">
  // Страница справочников: отделы и исполнители с CRUD и inline-редактированием.
  import Loader from '$lib/components/ui/Loader.svelte';
  import DepartmentsList from '$lib/components/refs/DepartmentsList.svelte';
  import ExecutorsList from '$lib/components/refs/ExecutorsList.svelte';
  import { refsStore } from '$lib/stores/refs.svelte';
</script>

<h1 class="mb-6 text-xl font-semibold">Справочники</h1>

{#if refsStore.loading}
  <Loader />
{:else}
  <div class="grid gap-6 md:grid-cols-2">
    <DepartmentsList />
    <ExecutorsList />
  </div>
{/if}
