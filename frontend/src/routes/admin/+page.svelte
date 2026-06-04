<script lang="ts">
  // Admin-панель: управление пользователями системы.
  // Доступна только пользователям с ролью admin.
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { Pencil, Trash2, Plus, ShieldCheck, Eye, FilePen } from 'lucide-svelte';
  import { authStore } from '$lib/stores/auth.svelte';
  import { toastStore } from '$lib/stores/toast.svelte';
  import { confirmStore } from '$lib/stores/confirm.svelte';
  import { apiGet, apiPost, apiPatch, apiDelete } from '$lib/api/client';
  import { ROLE_LABEL, type UserResponse, type UserCreate, type UserUpdate, type Role } from '$lib/api/auth';
  import Modal from '$lib/components/ui/Modal.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Input from '$lib/components/ui/Input.svelte';
  import Select from '$lib/components/ui/Select.svelte';
  import { fmtIsoDate } from '$lib/utils/date';

  let users = $state<UserResponse[]>([]);
  let loading = $state(true);
  let showCreateModal = $state(false);
  let editingUser = $state<UserResponse | null>(null);

  // Форма создания
  let newUsername = $state('');
  let newPassword = $state('');
  let newRole = $state<Role>('viewer');
  let newEmail = $state('');
  let newPhone = $state('');
  let formError = $state('');
  let formLoading = $state(false);

  // Форма редактирования
  let editRole = $state<Role>('viewer');
  let editPassword = $state('');
  let editIsActive = $state(true);
  let editEmail = $state('');
  let editPhone = $state('');

  const roleOptions = (Object.keys(ROLE_LABEL) as Role[]).map((value) => ({ value, label: ROLE_LABEL[value] }));

  // В Svelte 5 Runes-режиме динамические компоненты рендерятся через переменную напрямую
  const ROLE_ICON: Record<Role, typeof Eye> = {
    viewer: Eye,
    editor: FilePen,
    admin: ShieldCheck
  };

  onMount(async () => {
    // Только admin имеет доступ
    if (!authStore.isAdmin) {
      goto('/');
      return;
    }
    await loadUsers();
  });

  async function loadUsers(): Promise<void> {
    loading = true;
    try {
      users = await apiGet<UserResponse[]>('/users');
    } catch (err: unknown) {
      toastStore.error(err instanceof Error ? err.message : 'Не удалось загрузить пользователей');
    } finally {
      loading = false;
    }
  }

  function openCreate(): void {
    newUsername = '';
    newPassword = '';
    newRole = 'viewer';
    newEmail = '';
    newPhone = '';
    formError = '';
    showCreateModal = true;
  }

  function openEdit(user: UserResponse): void {
    editingUser = user;
    editRole = user.role;
    editPassword = '';
    editIsActive = user.is_active;
    editEmail = user.email ?? '';
    editPhone = user.phone ?? '';
    formError = '';
  }

  function closeModals(): void {
    showCreateModal = false;
    editingUser = null;
    formError = '';
  }

  async function handleCreate(e: SubmitEvent): Promise<void> {
    e.preventDefault();
    formError = '';
    formLoading = true;
    try {
      const body: UserCreate = { username: newUsername.trim(), password: newPassword, role: newRole };
      if (newEmail.trim()) body.email = newEmail.trim();
      if (newPhone.trim()) body.phone = newPhone.trim();
      const created = await apiPost<UserResponse>('/users', body);
      users = [...users, created];
      toastStore.success(`Пользователь «${created.username}» создан`);
      closeModals();
    } catch (err: unknown) {
      formError = err instanceof Error ? err.message : 'Ошибка создания';
    } finally {
      formLoading = false;
    }
  }

  async function handleEdit(e: SubmitEvent): Promise<void> {
    e.preventDefault();
    if (!editingUser) return;
    formError = '';
    formLoading = true;
    try {
      const body: UserUpdate = { role: editRole, is_active: editIsActive };
      if (editPassword) body.password = editPassword;
      body.email = editEmail.trim() || null;
      body.phone = editPhone.trim() || null;
      const updated = await apiPatch<UserResponse>(`/users/${editingUser.id}`, body);
      users = users.map((u) => (u.id === updated.id ? updated : u));
      toastStore.success(`Пользователь «${updated.username}» обновлён`);
      closeModals();
    } catch (err: unknown) {
      formError = err instanceof Error ? err.message : 'Ошибка обновления';
    } finally {
      formLoading = false;
    }
  }

  async function handleDelete(user: UserResponse): Promise<void> {
    const ok = await confirmStore.ask({
      title: 'Удалить пользователя?',
      message: `Пользователь «${user.username}» будет удалён.`,
      confirmLabel: 'Удалить',
      danger: true
    });
    if (!ok) return;
    try {
      await apiDelete(`/users/${user.id}`);
      users = users.filter((u) => u.id !== user.id);
      toastStore.success(`Пользователь «${user.username}» удалён`);
    } catch (err: unknown) {
      toastStore.error(err instanceof Error ? err.message : 'Ошибка удаления');
    }
  }

</script>

<svelte:head>
  <title>Пользователи — Протокол совещаний</title>
</svelte:head>

<div class="space-y-6">
  <!-- Заголовок -->
  <div class="flex items-center justify-between">
    <h1 class="text-xl font-semibold text-[var(--text-body)]">Пользователи</h1>
    <Button variant="primary" onclick={openCreate}>
      <Plus size={16} />
      Добавить
    </Button>
  </div>

  <!-- Таблица пользователей -->
  <div class="overflow-hidden rounded-lg border border-[var(--border)] bg-[var(--table-bg)]">
    {#if loading}
      <div class="py-16 text-center text-sm text-[var(--text-secondary)]">Загрузка…</div>
    {:else if users.length === 0}
      <div class="py-16 text-center text-sm text-[var(--text-secondary)]">Пользователей нет</div>
    {:else}
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-[var(--border)] bg-[var(--bg-primary)] text-left text-xs text-[var(--text-secondary)]">
            <th class="px-4 py-2 font-medium">Пользователь</th>
            <th class="px-4 py-2 font-medium">Роль</th>
            <th class="px-4 py-2 font-medium">Статус</th>
            <th class="px-4 py-2 font-medium">Создан</th>
            <th class="px-4 py-2 font-medium"></th>
          </tr>
        </thead>
        <tbody>
          {#each users as user (user.id)}
            {@const isSelf = user.username === authStore.user?.username}
            {@const RoleIcon = ROLE_ICON[user.role]}
            <tr class="border-b border-[var(--border)] last:border-0 hover:bg-[var(--table-hover)]">
              <td class="px-4 py-3 font-medium text-[var(--text-body)]">
                {user.username}
                {#if isSelf}
                  <span class="ml-1 text-xs text-[var(--text-secondary)]">(вы)</span>
                {/if}
              </td>
              <td class="px-4 py-3">
                <span class="inline-flex items-center gap-1.5 text-[var(--text-secondary)]">
                  <RoleIcon size={14} />
                  {ROLE_LABEL[user.role]}
                </span>
              </td>
              <td class="px-4 py-3">
                {#if user.is_active}
                  <span class="rounded-full bg-green-100 px-2 py-0.5 text-xs text-green-700 dark:bg-green-950 dark:text-green-300">
                    Активен
                  </span>
                {:else}
                  <span class="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500 dark:bg-gray-800">
                    Заблокирован
                  </span>
                {/if}
              </td>
              <td class="px-4 py-3 text-[var(--text-secondary)]">{fmtIsoDate(user.created_at)}</td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-1">
                  <button
                    class="rounded p-1 text-[var(--text-secondary)] hover:text-[var(--accent)]"
                    aria-label="Редактировать пользователя"
                    title="Редактировать"
                    onclick={() => openEdit(user)}
                  >
                    <Pencil size={15} />
                  </button>
                  {#if !isSelf}
                    <button
                      class="rounded p-1 text-[var(--text-secondary)] hover:text-[var(--danger)]"
                      aria-label="Удалить пользователя"
                      title="Удалить"
                      onclick={() => handleDelete(user)}
                    >
                      <Trash2 size={15} />
                    </button>
                  {/if}
                </div>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    {/if}
  </div>
</div>

<!-- Модальное окно: создание пользователя -->
<Modal open={showCreateModal} title="Новый пользователь" onClose={closeModals}>
  <form onsubmit={handleCreate} class="flex flex-col gap-4">
    <Input id="new-username" label="Имя пользователя" bind:value={newUsername} disabled={formLoading} />
    <Input id="new-password" type="password" label="Пароль" bind:value={newPassword} disabled={formLoading} />
    <Input id="new-email" type="email" label="Email (необязательно)" bind:value={newEmail} disabled={formLoading} />
    <Input id="new-phone" label="Телефон (необязательно)" placeholder="+7…" bind:value={newPhone} disabled={formLoading} />
    <Select
      id="new-role"
      label="Роль"
      options={roleOptions}
      bind:value={newRole as string}
      disabled={formLoading}
    />
    {#if formError}
      <p class="rounded bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">{formError}</p>
    {/if}
    <div class="flex justify-end gap-2 pt-1">
      <Button variant="secondary" onclick={closeModals} disabled={formLoading}>Отмена</Button>
      <Button type="submit" variant="primary" disabled={formLoading || !newUsername || !newPassword}>
        {formLoading ? 'Создание…' : 'Создать'}
      </Button>
    </div>
  </form>
</Modal>

<!-- Модальное окно: редактирование пользователя -->
<Modal open={!!editingUser} title="Редактировать пользователя" onClose={closeModals}>
  {#if editingUser}
    <form onsubmit={handleEdit} class="flex flex-col gap-4">
      <p class="text-sm text-[var(--text-secondary)]">
        Пользователь: <span class="font-medium text-[var(--text-body)]">{editingUser.username}</span>
      </p>
      <Select
        id="edit-role"
        label="Роль"
        options={roleOptions}
        bind:value={editRole as string}
        disabled={formLoading || editingUser.username === authStore.user?.username}
      />
      <div class="flex items-center gap-2">
        <input
          id="edit-active"
          type="checkbox"
          bind:checked={editIsActive}
          disabled={formLoading || editingUser.username === authStore.user?.username}
          class="h-4 w-4 accent-[var(--accent)]"
        />
        <label for="edit-active" class="text-sm text-[var(--text-body)]">Активен</label>
      </div>
      <Input
        id="edit-password"
        type="password"
        label="Новый пароль (оставьте пустым, чтобы не менять)"
        bind:value={editPassword}
        disabled={formLoading}
        placeholder="Оставьте пустым для сохранения текущего"
      />
      <Input id="edit-email" type="email" label="Email" bind:value={editEmail} disabled={formLoading} />
      <Input id="edit-phone" label="Телефон" placeholder="+7…" bind:value={editPhone} disabled={formLoading} />
      {#if formError}
        <p class="rounded bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950 dark:text-red-300">{formError}</p>
      {/if}
      <div class="flex justify-end gap-2 pt-1">
        <Button variant="secondary" onclick={closeModals} disabled={formLoading}>Отмена</Button>
        <Button type="submit" variant="primary" disabled={formLoading}>
          {formLoading ? 'Сохранение…' : 'Сохранить'}
        </Button>
      </div>
    </form>
  {/if}
</Modal>
