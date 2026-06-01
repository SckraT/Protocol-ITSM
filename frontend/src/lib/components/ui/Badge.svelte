<script lang="ts">
  // Бейдж состояния или приоритета задачи.
  import type { ItemState, Priority } from '$lib/api/types';
  import { PRIORITY_CONFIG, STATE_BADGE, STATE_LABEL } from '$lib/utils/constants';

  let {
    state,
    priority
  }: {
    state?: ItemState;
    priority?: Priority | null;
  } = $props();
</script>

{#if state}
  <span class="badge {STATE_BADGE[state]}">{STATE_LABEL[state]}</span>
{:else if priority}
  <span
    class="badge w-[72px] justify-center"
    class:bg-red-100={priority === 'high'}
    class:text-red-700={priority === 'high'}
    class:bg-yellow-100={priority === 'medium'}
    class:text-yellow-700={priority === 'medium'}
    class:bg-green-100={priority === 'low'}
    class:text-green-700={priority === 'low'}
    title={PRIORITY_CONFIG[priority].label}
  >
    {PRIORITY_CONFIG[priority].label}
  </span>
{/if}
