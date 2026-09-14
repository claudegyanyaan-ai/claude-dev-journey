// Minimal service worker -- its only real job is satisfying browsers'
// requirement that an installable PWA have a registered service worker
// with a fetch handler. It deliberately does NOT cache API responses
// (login, answers, uploads) offline -- this app's whole point is live,
// current data, so serving a stale cached answer would be actively
// misleading.
const CACHE_NAME = "network-docs-assistant-v1";

self.addEventListener("install", () => {
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", (event) => {
  event.respondWith(fetch(event.request));
});
