const CACHE_NAME = 'afs-v3';
const STATIC_CACHE = 'afs-static-v3';
const DYNAMIC_CACHE = 'afs-dynamic-v3';
const MAX_CACHE_SIZE = 50 * 1024 * 1024; // 50 MB

// Precache only the real Django app assets.
const PRECACHE_URLS = [
  '/',
  '/login/',
  '/static/manifest.json',
  '/static/css/common.css',
  '/static/css/azolar.css',
  '/static/css/davomat.css',
  '/static/css/tolov.css',
  '/static/css/dev-console.css',
  '/static/css/ota-ona.css',
  '/static/css/legal.css',
  '/static/js/theme.js'
];

// Cache management helpers
async function openCache(cacheName) {
  return await caches.open(cacheName);
}

async function addToCache(cacheName, request, response) {
  const cache = await openCache(cacheName);
  await cache.put(request, response);
}

async function getFromCache(cacheName, request) {
  const cache = await openCache(cacheName);
  return await cache.match(request);
}

async function cleanOldCaches() {
  const cacheNames = await caches.keys();
  const cachesToDelete = cacheNames.filter(
    (name) => name !== CACHE_NAME && name !== STATIC_CACHE && name !== DYNAMIC_CACHE
  );
  await Promise.all(cachesToDelete.map((name) => caches.delete(name)));
}

async function limitCacheSize(cacheName, maxSize) {
  const cache = await openCache(cacheName);
  const keys = await cache.keys();
  let totalSize = 0;

  for (const request of keys) {
    const response = await cache.match(request);
    if (response) {
      const size = response.headers.get('content-length') || 0;
      totalSize += parseInt(size, 10);
    }
  }

  if (totalSize > maxSize) {
    const keysToDelete = keys.slice(0, Math.ceil(keys.length / 4));
    await Promise.all(keysToDelete.map((key) => cache.delete(key)));
  }
}

// Install event - precache critical assets
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      return cache.addAll(PRECACHE_URLS).catch((err) => {
        console.error('Precache failed:', err);
        // Continue even if some assets fail
      });
    }).then(() => self.skipWaiting())
  );
});

// Activate event - clean old caches
self.addEventListener('activate', (e) => {
  e.waitUntil(
    cleanOldCaches().then(() => self.clients.claim())
  );
});

// Fetch event - different strategies for different resources
self.addEventListener('fetch', (e) => {
  const { request } = e;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') return;

  // Skip chrome-extension and other protocols
  if (!url.protocol.startsWith('http')) return;

  // Cache First strategy for static assets (CSS, JS, images)
  if (url.pathname.match(/\.(css|js|png|jpg|jpeg|webp|svg|woff|woff2)$/)) {
    e.respondWith(cacheFirst(request));
    return;
  }

  // Network First strategy for HTML pages
  if (url.pathname.match(/\.html$/) || url.pathname === '/') {
    e.respondWith(networkFirst(request));
    return;
  }

  // Network First for manifest.json
  if (url.pathname === '/manifest.json') {
    e.respondWith(networkFirst(request));
    return;
  }

  // Default: Network First with cache fallback
  e.respondWith(networkFirst(request));
});

// Cache First: serve from cache, fallback to network
async function cacheFirst(request) {
  try {
    const cached = await getFromCache(STATIC_CACHE, request);
    if (cached) {
      return cached;
    }

    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      await addToCache(STATIC_CACHE, request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.error('Cache First failed:', error);
    throw error;
  }
}

// Network First: try network, fallback to cache
async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      await addToCache(DYNAMIC_CACHE, request, networkResponse.clone());
      await limitCacheSize(DYNAMIC_CACHE, MAX_CACHE_SIZE);
    }
    return networkResponse;
  } catch (error) {
    const cached = await getFromCache(DYNAMIC_CACHE, request);
    if (cached) {
      return cached;
    }

    // Offline fallback for HTML pages: use the real Django login route.
    if (request.destination === 'document') {
      const offlineFallback = await getFromCache(STATIC_CACHE, new Request('/login/'));
      if (offlineFallback) {
        return offlineFallback;
      }
    }

    throw error;
  }
}

// Message handling for manual cache updates
self.addEventListener('message', (e) => {
  if (e.data === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  if (e.data === 'CLEAR_CACHE') {
    e.waitUntil(
      Promise.all([
        caches.delete(STATIC_CACHE),
        caches.delete(DYNAMIC_CACHE)
      ]).then(() => self.clients.claim())
    );
  }
});
