// SPA-режим: отключаем SSR и пререндеринг — приложение работает только на клиенте,
// раздаётся как статика с fallback на index.html.
export const ssr = false;
export const prerender = false;
