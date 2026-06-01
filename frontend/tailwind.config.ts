import type { Config } from 'tailwindcss';

export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  // Тёмная тема через атрибут data-theme на <html> (совместимо с v1)
  darkMode: ['selector', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        // Привязка к CSS-переменным из app.css — единый источник цветов для тем
        accent: 'var(--accent)',
        'accent-light': 'var(--accent-light)',
        danger: 'var(--danger)',
        warning: 'var(--warning)',
        success: 'var(--success)',
        'body-bg': 'var(--bg-body)',
        'body-text': 'var(--text-body)',
        'table-bg': 'var(--table-bg)',
        'table-hover': 'var(--table-hover)',
        'border-c': 'var(--border)'
      }
    }
  },
  plugins: []
} satisfies Config;
