// Minimal service worker -- enables PWA installability.
// Caches the core app shell so it loads instantly on repeat visits.
const CACHE_NAME = 'alpha-cache-v1';
const urlsToCache = [
    '/',
    '/static/style.css',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => response || fetch(event.request))
    );
});