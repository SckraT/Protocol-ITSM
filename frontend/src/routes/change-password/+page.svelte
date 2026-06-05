<script lang="ts">
  // Страница обязательной/добровольной смены пароля.
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { authStore } from '$lib/stores/auth.svelte';
  import { apiChangePassword } from '$lib/api/auth';
  import Input from '$lib/components/ui/Input.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  let oldPassword = $state('');
  let newPassword = $state('');
  let confirm = $state('');
  let error = $state('');
  let loading = $state(false);

  onMount(() => {
    if (!authStore.isAuthenticated) goto('/login');
  });

  const forced = $derived(authStore.mustChangePassword);

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    error = '';
    if (newPassword.length < 8) {
      error = 'Новый пароль должен содержать минимум 8 символов';
      return;
    }
    if (newPassword !== confirm) {
      error = 'Пароли не совпадают';
      return;
    }
    loading = true;
    try {
      await apiChangePassword(authStore.accessToken ?? '', oldPassword, newPassword);
      authStore.clearPasswordChangeFlag();
      goto('/');
    } catch (err: unknown) {
      error = err instanceof Error ? err.message : 'Ошибка смены пароля';
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>Смена пароля — Протокол совещаний</title>
</svelte:head>

<div class="flex min-h-screen items-center justify-center bg-[var(--bg-body)]">
  <div class="w-full max-w-sm">
    <div class="mb-8 text-center">
      <h1 class="text-2xl font-semibold text-[var(--text-body)]">Смена пароля</h1>
      <p class="mt-1 text-sm text-[var(--text-secondary)]">
        {#if forced}
          Для продолжения необходимо сменить пароль
        {:else}
          Введите текущий и новый пароль
        {/if}
      </p>
    </div>

    <form
      onsubmit={handleSubmit}
      class="rounded-lg border border-[var(--border)] bg-[var(--bg-primary)] p-6 shadow-sm"
    >
      <div class="flex flex-col gap-4">
        <Input id="old-password" type="password" label="Текущий пароль" bind:value={oldPassword} disabled={loading} />
        <Input id="new-password" type="password" label="Новый пароль (мин. 8 символов)" bind:value={newPassword} disabled={loading} />
        <Input id="confirm-password" type="password" label="Повторите новый пароль" bind:value={confirm} disabled={loading} />

        {#if error}
          <p class="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
            {error}
          </p>
        {/if}

        <Button type="submit" variant="primary" disabled={loading || !oldPassword || !newPassword || !confirm}>
          {loading ? 'Сохранение…' : 'Сменить пароль'}
        </Button>
        {#if !forced}
          <Button variant="secondary" onclick={() => goto('/')} disabled={loading}>Отмена</Button>
        {/if}
      </div>
    </form>
  </div>
</div>
