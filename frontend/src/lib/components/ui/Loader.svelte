<script lang="ts">
  // Индикатор загрузки (спиннер).
  let { size = 24, label = 'Загрузка…' }: { size?: number; label?: string } = $props();
</script>

<div class="flex items-center justify-center gap-3 p-6 text-[var(--text-secondary)]">
  <span
    class="inline-block animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--accent)]"
    style="width: {size}px; height: {size}px;"
    aria-hidden="true"
  ></span>
  {#if label}<span class="text-sm">{label}</span>{/if}
</div>
