<script lang="ts">
  // Универсальная кнопка с вариантами оформления.
  import type { Snippet } from 'svelte';

  type Variant = 'primary' | 'secondary' | 'danger' | 'ghost';
  type Size = 'sm' | 'md';

  let {
    variant = 'primary',
    size = 'md',
    type = 'button',
    disabled = false,
    title = '',
    ariaLabel = '',
    onclick,
    children
  }: {
    variant?: Variant;
    size?: Size;
    type?: 'button' | 'submit' | 'reset';
    disabled?: boolean;
    title?: string;
    ariaLabel?: string;
    onclick?: (e: MouseEvent) => void;
    children: Snippet;
  } = $props();

  const variantClasses: Record<Variant, string> = {
    primary: 'bg-[var(--accent)] text-white hover:bg-[var(--accent-light)]',
    secondary: 'bg-[var(--table-bg)] border border-[var(--border)] text-[var(--text-body)] hover:bg-[var(--table-hover)]',
    danger: 'bg-[var(--danger)] text-white hover:opacity-90',
    ghost: 'text-[var(--text-body)] hover:bg-[var(--table-hover)]'
  };
  const sizeClasses: Record<Size, string> = {
    sm: 'px-2.5 py-1 text-xs',
    md: 'px-4 py-2 text-sm'
  };
</script>

<button
  {type}
  {disabled}
  {title}
  aria-label={ariaLabel || undefined}
  class="inline-flex items-center justify-center gap-1.5 rounded-md font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-50 {variantClasses[variant]} {sizeClasses[size]}"
  {onclick}
>
  {@render children()}
</button>
