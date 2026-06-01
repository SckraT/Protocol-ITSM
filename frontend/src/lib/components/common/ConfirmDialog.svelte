<script lang="ts">
  // Диалог подтверждения — подключается к confirmStore.
  import Modal from '$lib/components/ui/Modal.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { confirmStore } from '$lib/stores/confirm.svelte';
</script>

<Modal open={confirmStore.open} title={confirmStore.title} onClose={() => confirmStore.cancel()}>
  <p class="mb-5 text-sm text-[var(--text-body)]">{confirmStore.message}</p>
  <div class="flex justify-end gap-2">
    <Button variant="secondary" onclick={() => confirmStore.cancel()}>Отмена</Button>
    <Button
      variant={confirmStore.danger ? 'danger' : 'primary'}
      onclick={() => confirmStore.confirm()}
    >
      {confirmStore.confirmLabel}
    </Button>
  </div>
</Modal>
