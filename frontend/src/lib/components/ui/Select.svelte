<script lang="ts">
  // Выпадающий список с двусторонней привязкой.
  interface Option {
    value: string;
    label: string;
  }

  let {
    value = $bindable(''),
    options = [],
    label = '',
    id = '',
    placeholder = '',
    disabled = false,
    onchange
  }: {
    value?: string;
    options?: Option[];
    label?: string;
    id?: string;
    placeholder?: string;
    disabled?: boolean;
    onchange?: (e: Event) => void;
  } = $props();
</script>

<div class="flex flex-col gap-1">
  {#if label}
    <label for={id} class="text-xs font-medium text-[var(--text-secondary)]">{label}</label>
  {/if}
  <select
    {id}
    {disabled}
    bind:value
    {onchange}
    class="rounded-md border border-[var(--border)] bg-[var(--table-bg)] px-3 py-2 text-sm text-[var(--text-body)] outline-none focus:border-[var(--accent)]"
  >
    {#if placeholder}
      <option value="">{placeholder}</option>
    {/if}
    {#each options as opt (opt.value)}
      <option value={opt.value}>{opt.label}</option>
    {/each}
  </select>
</div>
