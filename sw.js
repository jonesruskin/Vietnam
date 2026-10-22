/* Offline support for the guides.
   Pages: network first, so an online visit always gets the latest version; the saved
   copy is used when there's no signal or the network takes too long.
   Photos and fonts: saved copy first; they never change under the same name.
   Bump CACHE when photos are re-imported under existing names. */
var CACHE = "vietnam-v1";
var SLOW_MS = 3500;

self.addEventListener("install", function () { self.skipWaiting(); });

self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k.indexOf("vietnam-") === 0 && k !== CACHE; })
      .map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

function fromCache(req) {
  return caches.open(CACHE).then(function (c) {
    return c.match(req, { ignoreSearch: req.mode === "navigate", ignoreVary: true });
  });
}

function store(req, res) {
  if (res && (res.ok || res.type === "opaque")) {
    var copy = res.clone();
    caches.open(CACHE).then(function (c) { return c.put(req, copy); });
  }
  return res;
}

function networkFirst(req) {
  return new Promise(function (resolve, reject) {
    var settled = false;
    function done(r) { if (!settled && r) { settled = true; resolve(r); } }
    var net = fetch(req).then(function (r) { return store(req, r); });
    var timer = setTimeout(function () { fromCache(req).then(done); }, SLOW_MS);
    net.then(function (r) { clearTimeout(timer); done(r); }, function () {
      clearTimeout(timer);
      fromCache(req).then(function (r) { if (r) done(r); else if (!settled) reject(new Error("offline")); });
    });
  });
}

function cacheFirst(req) {
  return fromCache(req).then(function (hit) {
    return hit || fetch(req).then(function (r) { return store(req, r); });
  });
}

self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET") return;
  var url = new URL(req.url);
  var font = url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com";
  if (url.origin !== self.location.origin && !font) return;
  if (font || /\.(webp|png|svg)$/.test(url.pathname)) e.respondWith(cacheFirst(req));
  else e.respondWith(networkFirst(req));
});
