<script lang="ts">
  // Контейнер уведомлений. Подписывается на toastStore.
  import { toastStore } from '$lib/stores/toast.svelte';
  import { fade, fly } from 'svelte/transition';
  import { X } from 'lucide-svelte';
</script>

<div
  class="pointer-events-none fixed bottom-4 right-4 z-[100] flex flex-col gap-2"
  role="status"
  aria-live="polite"
>
  {#each toastStore.toasts as toast (toast.id)}
    <div
      class="pointer-events-auto flex items-center gap-3 rounded-lg px-4 py-3 text-sm shadow-lg"
      class:bg-green-600={toast.type === 'success'}
      class:bg-red-600={toast.type === 'error'}
      class:bg-slate-700={toast.type === 'info'}
      class:text-white={true}
      in:fly={{ y: 20, duration: 200 }}
      out:fade={{ duration: 150 }}
    >
      <span>{toast.message}</span>
      <button
        class="opacity-70 hover:opacity-100"
        aria-label="Закрыть уведомление"
        onclick={() => toastStore.dismiss(toast.id)}
      >
        <X size={16} />
      </button>
    </div>
  {/each}
</div>
