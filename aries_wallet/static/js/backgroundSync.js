/*
This file is in part built upon the instructions in the book 'Building Progressive Web Apps' by Tal Alter.
The code examples provided in the book can be found in this github repository: https://github.com/TalAter/gotham_imperial_hotel/
*/
import v4 from "https://unpkg.com/uuid@8.3.2/dist/esm-browser/v4.js";

const DB_VERSION = 4;
const DB_NAME = "acapy_requests";

const openDatabase = function() {
  return new Promise(function(resolve, reject) {
    // check if IndexedDB is supported in browser
    if (!self.indexedDB) {
      reject("IndexedDB not supported");
    }
    // open IndexedDB
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onerror = function(event) {
      reject("Database error: " + event.target.error);
    };

    // add object store to database
    request.onupgradeneeded = function(event) {
      const db = event.target.result;
      const upgradeTransaction = event.target.transaction;
      let requestStore;
      if (!db.objectStoreNames.contains("post_queue")) {
        requestStore = db.createObjectStore("post_queue",
          { keyPath: "id" }
        );
      } else {
        requestStore = upgradeTransaction.objectStore("post_queue");
      }

      // create index object store with index type (idx_type being type)
      if (!requestStore.indexNames.contains("idx_type")) {
        requestStore.createIndex("idx_type", "type", { unique: false });
      }
    };

    request.onsuccess = function(event) {
      resolve(event.target.result);
    };
  });
};

// open a object store to add/delete objects
const openObjectStore = function(db, storeName, transactionMode) {
  return db
    .transaction(storeName, transactionMode)
    .objectStore(storeName);
};

// open object store and add object to it
const addToObjectStore = function(storeName, object) {
  return new Promise(function(resolve, reject) {
    openDatabase().then(function(db) {
      openObjectStore(db, storeName, "readwrite")
        .add(object).onsuccess = resolve;
    }).catch(function(errorMessage) {
      reject(errorMessage);
    });
  });
};

// open object store to delete object from it
const deleteFromObjectStore = function(storeName, id) {
  return new Promise(function(resolve, reject) {
    openDatabase().then(function(db) {
      openObjectStore(db, storeName, "readwrite")
        .openCursor().onsuccess = function(event) {
          const cursor = event.target.result;
          // check if object is in object store
          if (!cursor) {
            reject("Request not found in object store");
          }
          // if id matches, delete object
          if (cursor.value.id === id) {
            cursor.delete().onsuccess = resolve;
            return;
          }
          cursor.continue();
        };
    }).catch(function(errorMessage) {
      reject(errorMessage);
    });
  });
};

// get requests from object store 'post_queue'
const getRequests = function (indexName, indexValue) {
  return new Promise(function (resolve) {
      openDatabase().then(function (db) {
          // open object store
          const objectStore = openObjectStore(db, "post_queue");
          const requests = [];
          let cursor;
          // check for object with matching indexValue
          if (indexName && indexValue) {
              cursor = objectStore.index(indexName).openCursor(indexValue);
          } else {
              cursor = objectStore.openCursor();
          }

          // when object was found add it to requests list
          cursor.onsuccess = function (event) {
              cursor = event.target.result;
              if (cursor) {
                  requests.push(cursor.value);
                  cursor.continue();
              } else {
                  if (requests.length > 0) {
                      resolve(requests);
                  }
              }

          };
      }).catch(function(err) {
          console.log(err);
        });
  });
};

// add objects to IndexedDB and register sync event
function add_to_db_and_sync(type, params) {
    // generate uuid
    let uuid = v4();

    // set up object that should be saved in the db
    const object = {
        id: uuid,
        timestamp: Date.now(),
        type: type,
        params: params
    };

    // add object to indexeddb object store
    addToObjectStore("post_queue", object);

    // register a sync event with the matching tag if serviceWorker is activated
    if ("serviceWorker" in navigator && "SyncManager" in window) {
        navigator.serviceWorker.ready.then(function (registration) {
            registration.sync.register(type + uuid);
        });
    }
};


export { deleteFromObjectStore, getRequests, addToObjectStore, add_to_db_and_sync };