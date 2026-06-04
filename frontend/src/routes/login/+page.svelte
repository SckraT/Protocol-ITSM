<script lang="ts">
  // Страница входа в систему.
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { authStore } from '$lib/stores/auth.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  let identifier = $state('');
  let password = $state('');
  let error = $state('');
  let loading = $state(false);

  // Если уже авторизован — сразу на главную
  onMount(() => {
    if (authStore.isAuthenticated) goto('/');
  });

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    error = '';
    loading = true;
    try {
      await authStore.login(identifier, password);
      goto('/');
    } catch (err: unknown) {
      error = err instanceof Error ? err.message : 'Ошибка входа';
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>Вход — Протокол совещаний</title>
</svelte:head>

<div class="flex min-h-screen items-center justify-center bg-[var(--bg-body)]">
  <div class="w-full max-w-sm">
    <!-- Заголовок -->
    <div class="mb-8 text-center">
      <h1 class="text-2xl font-semibold text-[var(--text-body)]">Протокол совещаний</h1>
      <p class="mt-1 text-sm text-[var(--text-secondary)]">Войдите, чтобы продолжить</p>
    </div>

    <!-- Форма -->
    <form
      onsubmit={handleSubmit}
      class="rounded-lg border border-[var(--border)] bg-[var(--bg-primary)] p-6 shadow-sm"
    >
      <div class="flex flex-col gap-4">
        <Input
          id="identifier"
          label="Логин, email или телефон"
          placeholder="admin / user@mail.ru / +7…"
          bind:value={identifier}
          disabled={loading}
        />
        <Input
          id="password"
          type="password"
          label="Пароль"
          placeholder="••••••••"
          bind:value={password}
          disabled={loading}
        />

        {#if error}
          <p class="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">
            {error}
          </p>
        {/if}

        <Button type="submit" variant="primary" disabled={loading || !identifier || !password}>
          {#if loading}
            Вход…
          {:else}
            Войти
          {/if}
        </Button>
      </div>
    </form>
  </div>
</div>
