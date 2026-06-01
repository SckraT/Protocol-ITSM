<script lang="ts">
  // Боковая панель (slide-over), выезжает справа.
  // Нативная реализация на Svelte-транзишенах с поддержкой Esc и клика по фону.
  import type { Snippet } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { X } from 'lucide-svelte';

  let {
    open = false,
    title = '',
    width = '640px',
    onClose,
    children
  }: {
    open?: boolean;
    title?: string;
    width?: string;
    onClose: () => void;
    children: Snippet;
  } = $props();

  let panel = $state<HTMLElement | null>(null);

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') onClose();
  }

  // Переносим фокус на панель при открытии (доступность)
  $effect(() => {
    if (open && panel) {
      panel.focus();
    }
  });
</script>

<svelte:window onkeydown={open ? handleKeydown : undefined} />

{#if open}
  <!-- Затемнение фона -->
  <div
    class="fixed inset-0 z-40 bg-black/40"
    transition:fade={{ duration: 150 }}
    onclick={onClose}
    role="presentation"
  ></div>

  <!-- Панель -->
  <div
    bind:this={panel}
    class="fixed right-0 top-0 z-50 flex h-full flex-col bg-[var(--table-bg)] shadow-xl outline-none"
    style="width: {width}; max-width: 100vw;"
    transition:fly={{ x: 400, duration: 200 }}
    role="dialog"
    aria-modal="true"
    aria-label={title || 'Панель'}
    tabindex="-1"
  >
    <header class="flex items-center justify-between border-b border-[var(--border)] px-5 py-3">
      <h2 class="text-base font-semibold text-[var(--text-body)]">{title}</h2>
      <button
        class="rounded p-1 text-[var(--text-secondary)] hover:bg-[var(--table-hover)]"
        aria-label="Закрыть панель"
        onclick={onClose}
      >
        <X size={20} />
      </button>
    </header>
    <div class="flex-1 overflow-y-auto p-5">
      {@render children()}
    </div>
  </div>
{/if}
