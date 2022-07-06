/*
This serviceworker.js file is in part built upon the instructions in the book 'Building Progressive Web Apps' by Tal Alter.
The code examples provided in the book can be found in this github repository: https://github.com/TalAter/gotham_imperial_hotel/
*/

import { getRequests, deleteFromObjectStore } from "/static/js/backgroundSync.js";

const staticCacheName = "django-pwa-static" + Date.now();

// static files to cache on install
const filesToCacheInstall = [
  "/offline/",
  "/static/css/general.css",
  "/static/css/index.css",
  "/static/css/bootstrap.min.css",
  "/static/css/bootstrap.css",
  "/static/images/aries.png",
  "/static/js/bootstrap.bundle.min.js",
  "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.0/font/bootstrap-icons.css",
  "manifest.json",
  "serviceworker.js",
  "/static/js/backgroundSync.js"
];

// listen to "install" event
self.addEventListener("install", (event) => {
  // forces waiting service worker to progress into the activating state
  self.skipWaiting();
  // keeps service worker in installing phase until following task is complete
  event.waitUntil(
    // open the cache with the earlier defined staticCacheName
    caches.open(staticCacheName)
      .then((cache) => {
        // add all files mentioned in filesToCacheInstall into the static cache
        return cache.addAll(filesToCacheInstall);
      })
  );
});


// Clear cache on activate event of the serviceworker
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          // only caches that start with django-pwa are left
          .filter((cacheName) => (cacheName.startsWith("django-pwa-")))
          // only caches that are not the static cache are left
          .filter((cacheName) => (cacheName !== staticCacheName))
          // these are deleted
          .map((cacheName) => caches.delete(cacheName))
      );
    })
  );
});

// dynamic cache for non-static files
const dynamicCacheName = "django-pwa-dynamic" + Date.now();

self.addEventListener("fetch", function (event) {
  // serviceworkers can natively only deal with GET requests
  if (event.request.method === "GET") {
    // get the requests URL
    const requestURL = new URL(event.request.url);
    // check if the requests URL/file can be found in the static cache
    if (
      filesToCacheInstall.includes(requestURL.href) ||
      filesToCacheInstall.includes(requestURL.pathname)
    ) {
      // if so respond with the cached file
      event.respondWith(
        caches.open(staticCacheName).then(function (cache) {
          return cache.match(event.request).then(function (response) {
            return response || fetch(event.request);
          });
        })
      );
    } else {
      // else try to load the file through network first
      event.respondWith(
        caches.open(dynamicCacheName).then(function (cache) {
          return fetch(event.request).then(function (networkResponse) {
            cache.put(event.request, networkResponse.clone());
            return networkResponse;
          }).catch(function () {
            // if that does not work due to a lack of network connection
            // try to find an older version of the file in the cache
            return caches.match(event.request)
              .then(function (cacheResponse) {
                // if there is no older version return the standard offline page
                if (cacheResponse === undefined) {
                  return caches.match("/offline/").then(function (offlinePage) {
                    return offlinePage;
                  });
                }
                return cacheResponse;
              });
          });
        })
      );
    }
  }
});

function alertResponse(type, message) {
  self.registration.showNotification(type, { body: message });
}

function syncInvitation() {
  // get all requests with type 'receive_invitation' from IndexedDB
  return getRequests("idx_type", "receive_invitation").then(function (requests) {
    return Promise.all(
      // post the data of every found object to the matching Django URL
      requests.map(function (request) {
        const formData = new FormData();
        formData.append("invitation_url", JSON.stringify(request.params.invitation_url));
        return fetch("receive_invitation", {
          method: "POST",
          body: formData,
          headers: { "X-CSRFToken": request.params.csrftoken },
          mode: "same-origin"
        }).then(function (response) {
          response.json().then((object) => {
            // alert the user that sync has been executed
            alertResponse("Queued connection invitation", object.content.message);
          });
        }).then(function () {
          // delete object from DB
          return deleteFromObjectStore(
            "post_queue",
            request.id
          );
        });
      })
    );
  });
}

function syncAcceptConnection() {
  // get all requests with type 'accept_connection' from IndexedDB
  return getRequests("idx_type", "accept_connection").then(function (requests) {
    return Promise.all(
      // post the data of every found object to the matching Django URL
      requests.map(function (request) {
        return fetch("accept_connection/" + request.params.connection_id)
          .then(function (response) {
            response.json().then((object) => {
              // alert the user that sync has been executed
              alertResponse("Queued connection acceptance", object.content.message);
            });
          }).then(function () {
            // delete object from DB
            return deleteFromObjectStore(
              "post_queue",
              request.id
            );
          });
      })
    );
  });
}

function syncProblemReport() {
  // get all requests with type 'problem_report' from IndexedDB
  return getRequests("idx_type", "problem_report").then(function (requests) {
    return Promise.all(
      // post the data of every found object to the matching Django URL
      requests.map(function (request) {
        const formData = new FormData();
        formData.append("description", JSON.stringify(request.params.description));
        return fetch("/problem_report/" + request.params.cred_ex_id, {
          method: "POST",
          body: formData,
          headers: { "X-CSRFToken": request.params.csrftoken },
          mode: "same-origin"
        }).then(function (response) {
          response.json().then((object) => {
            // alert the user that sync has been executed
            alertResponse("Queued problelm report", object.content.message);
          });
        }).then(function () {
          // delete object from DB
          return deleteFromObjectStore(
            "post_queue",
            request.id
          );
        });
      })
    );
  });
}

function syncRequestCredential() {
  // get all requests with type 'request_credential' from IndexedDB
  return getRequests("idx_type", "request_credential").then(function (requests) {
    return Promise.all(
      // post the data of every found object to the matching Django URL
      requests.map(function (request) {
        return fetch("request_credential/" + request.params.cred_ex_id)
          .then(function (response) {
            response.json().then((object) => {
              // alert the user that sync has been executed
              alertResponse("Queued credential request", object.content.message);
            });
          }).then(function () {
            // delete object from DB
            return deleteFromObjectStore(
              "post_queue",
              request.id
            );
          });
      })
    );
  });
}

function syncPresentProof() {
  // get all requests with type 'present_proof' from IndexedDB
  return getRequests("idx_type", "present_proof").then(function (requests) {
    return Promise.all(
      // post the data of every found object to the matching Django URL
      requests.map(function (request) {
        const formData = new FormData();
        formData.append("credential", request.params.credential_id);
        return fetch("/present_proof/" + request.params.pres_ex_id, {
          method: "POST",
          body: formData,
          headers: { "X-CSRFToken": request.params.csrftoken },
          mode: "same-origin"
        }).then(function (response) {
          response.json().then((object) => {
            // alert the user that sync has been executed
            alertResponse("Queued proof presentation", object.content.message);
          });
        }).then(function () {
          // delete object from DB
          return deleteFromObjectStore(
            "post_queue",
            request.id
          );
        });
      })
    );
  });
}

// listen to sync events and match tags to matching sync function
self.addEventListener("sync", function (event) {
  const eventTag = event.tag;
  if (eventTag.includes("receive_invitation")) {
    event.waitUntil(syncInvitation());

  } else if (eventTag.includes("accept_connection")) {
    event.waitUntil(syncAcceptConnection());

  } else if (eventTag.includes("present_proof")) {
    event.waitUntil(syncPresentProof());

  } else if (eventTag.includes("request_credential")) {
    event.waitUntil(syncRequestCredential());

  } else if (eventTag.includes("problem_report")) {
    event.waitUntil(syncProblemReport());
  }
});
