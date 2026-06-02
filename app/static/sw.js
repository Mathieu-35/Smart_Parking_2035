// =============================================================
//  sw.js  -  Le "service worker" de Smart Parking 2035
// =============================================================
//
//  Un service worker est un petit programme qui tourne en
//  arriere-plan dans le navigateur, MEME quand on ferme l'onglet.
//
//  Son role ici :
//    1) Au moment de l'installation, il met de cote (en cache)
//       quelques fichiers de base de l'application.
//    2) Ensuite, a chaque demande de page (fetch) :
//         - s'il y a du reseau -> on prend la version du reseau ;
//         - s'il n'y a PAS de reseau -> on montre une page
//           "hors-ligne" propre, au lieu de l'erreur du navigateur.
//
//  C'est ce fichier qui transforme le site en "vraie app"
//  installable et utilisable hors-ligne.
//
// =============================================================

// On donne un nom + un numero de version a notre cache.
// Si on change les fichiers, on augmente le numero (v2, v3...)
// pour que le navigateur remplace l'ancien cache.
var NOM_CACHE = "smart-parking-v6";

// La liste des fichiers a garder pour le hors-ligne.
var FICHIERS_A_GARDER = [
  "/static/css/style.css",
  "/static/css/mobile.css",
  "/static/offline.html",
  "/static/icons/icon-192.png",
  "/static/icons/icon-512.png"
];

// --- 1) INSTALLATION : on remplit le cache une 1ere fois ---
self.addEventListener("install", function (evenement) {
  evenement.waitUntil(
    caches.open(NOM_CACHE).then(function (cache) {
      return cache.addAll(FICHIERS_A_GARDER);
    })
  );
  // On active tout de suite la nouvelle version.
  self.skipWaiting();
});

// --- 2) ACTIVATION : on efface les vieux caches (autres versions) ---
self.addEventListener("activate", function (evenement) {
  evenement.waitUntil(
    caches.keys().then(function (noms) {
      return Promise.all(
        noms.map(function (nom) {
          if (nom !== NOM_CACHE) {
            return caches.delete(nom);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// --- 3) A chaque demande de fichier (fetch) ---
self.addEventListener("fetch", function (evenement) {
  var requete = evenement.request;

  // On ne s'occupe que des pages (navigation) et du GET.
  // Pour le reste (API en POST, etc.) on laisse passer normalement.
  if (requete.method !== "GET") {
    return;
  }

  evenement.respondWith(
    // On essaie d'abord le reseau...
    fetch(requete)
      .then(function (reponse) {
        return reponse;
      })
      .catch(function () {
        // ...si le reseau echoue (hors-ligne) :
        // pour une page, on montre la page hors-ligne ;
        // sinon on tente de retrouver le fichier dans le cache.
        if (requete.mode === "navigate") {
          return caches.match("/static/offline.html");
        }
        return caches.match(requete);
      })
  );
});
