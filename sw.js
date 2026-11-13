const VERSION = 'v4';
const STATIC_CACHE = `afs-static-${VERSION}`;

const PRECACHE_URLS = [
  '/offline/',
  '/static/css/common.css',
  '/static/js/theme.js'
  // boshqa CSS fayllaringiz
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => Promise.all(
        PRECACHE_URLS.map((u) => cache.add(u).catch((err) => console.warn('Keshlanmadi:', u, err)))
      ))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((names) => Promise.all(names.filter((n) => n !== STATIC_CACHE).map((n) => caches.delete(n))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const { request } = e;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== location.origin) return;

  // Sahifalar: doim tarmoqdan, offline bo'lsa /offline/
  if (request.mode === 'navigate') {
    e.respondWith(fetch(request).catch(() => caches.match('/offline/')));
    return;
  }

  // Static fayllar: keshdan bersin, orqada yangilasin
  if (url.pathname.startsWith('/static/')) {
    e.respondWith(
      caches.open(STATIC_CACHE).then(async (cache) => {
        const cached = await cache.match(request);
        const fresh = fetch(request).then((res) => {
          if (res.ok) cache.put(request, res.clone());
          return res;
        }).catch(() => cached);
        return cached || fresh;
      })
    );
  }
});
