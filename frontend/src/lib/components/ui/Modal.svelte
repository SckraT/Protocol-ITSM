<script lang="ts">
  // Модальное окно по центру экрана.
  import type { Snippet } from 'svelte';
  import { fade, scale } from 'svelte/transition';
  import { X } from 'lucide-svelte';

  let {
    open = false,
    title = '',
    onClose,
    children
  }: {
    open?: boolean;
    title?: string;
    onClose: () => void;
    children: Snippet;
  } = $props();

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') onClose();
  }
</script>

<svelte:window onkeydown={open ? handleKeydown : undefined} />

{#if open}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
    transition:fade={{ duration: 150 }}
    onclick={(e) => {
      if (e.target === e.currentTarget) onClose();
    }}
    role="presentation"
  >
    <div
      class="w-full max-w-lg rounded-lg bg-[var(--table-bg)] shadow-2xl"
      transition:scale={{ duration: 150, start: 0.95 }}
      role="dialog"
      aria-modal="true"
      aria-label={title || 'Окно'}
      tabindex="-1"
    >
      <header class="flex items-center justify-between border-b border-[var(--border)] px-5 py-3">
        <h2 class="text-base font-semibold text-[var(--text-body)]">{title}</h2>
        <button
          class="rounded p-1 text-[var(--text-secondary)] hover:bg-[var(--table-hover)]"
          aria-label="Закрыть окно"
          onclick={onClose}
        >
          <X size={20} />
        </button>
      </header>
      <div class="p-5">
        {@render children()}
      </div>
    </div>
  </div>
{/if}
