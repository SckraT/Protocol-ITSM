import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

// Конфиг тестов. Плагин sveltekit() резолвит $lib/$app и компилирует .svelte.ts (Runes).
// Окружение jsdom — для localStorage и прочих браузерных API в сторах.
export default defineConfig({
  plugins: [sveltekit()],
  test: {
    environment: 'jsdom',
    include: ['src/**/*.{test,spec}.{js,ts}']
  }
});
