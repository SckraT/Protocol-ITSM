<script lang="ts">
  // Текстовое поле ввода с двусторонней привязкой.
  let {
    value = $bindable(''),
    type = 'text',
    placeholder = '',
    label = '',
    id = '',
    disabled = false,
    oninput
  }: {
    value?: string;
    type?: string;
    placeholder?: string;
    label?: string;
    id?: string;
    disabled?: boolean;
    oninput?: (e: Event) => void;
  } = $props();
</script>

<div class="flex flex-col gap-1">
  {#if label}
    <label for={id} class="text-xs font-medium text-[var(--text-secondary)]">{label}</label>
  {/if}
  <input
    {id}
    {type}
    {placeholder}
    {disabled}
    bind:value
    {oninput}
    class="rounded-md border border-[var(--border)] bg-[var(--table-bg)] px-3 py-2 text-sm text-[var(--text-body)] outline-none focus:border-[var(--accent)]"
  />
</div>
