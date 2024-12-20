// indexeddb.js
async function storeInIndexedDB(data) {
  const dbName = "StreamlitDB";
  const storeName = "DataStore";

  // Open a connection to the database
  const request = indexedDB.open(dbName, 1);

  request.onupgradeneeded = function(event) {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(storeName)) {
          db.createObjectStore(storeName, { keyPath: "id", autoIncrement: true });
      }
  };

  request.onsuccess = function(event) {
      const db = event.target.result;

      const transaction = db.transaction(storeName, "readwrite");
      const store = transaction.objectStore(storeName);
      store.add({ id: Date.now(), value: data });

      transaction.oncomplete = function() {
          alert("Data successfully stored in IndexedDB!");
      };
  };

  request.onerror = function(event) {
      console.error("Error opening IndexedDB:", event.target.error);
  };
}

async function fetchFromIndexedDB() {
  const dbName = "StreamlitDB";
  const storeName = "DataStore";

  return new Promise((resolve, reject) => {
      const request = indexedDB.open(dbName, 1);

      request.onsuccess = function(event) {
          const db = event.target.result;

          const transaction = db.transaction(storeName, "readonly");
          const store = transaction.objectStore(storeName);
          const getAllRequest = store.getAll();

          getAllRequest.onsuccess = function() {
              resolve(getAllRequest.result);
          };

          getAllRequest.onerror = function(event) {
              reject(event.target.error);
          };
      };

      request.onerror = function(event) {
          reject(event.target.error);
      };
  });
}

async function sendDataToStreamlit() {
  const data = await fetchFromIndexedDB();
  // Communicate with Streamlit using custom events
  const streamlitDataEvent = new CustomEvent("indexeddbData", { detail: data });
  document.dispatchEvent(streamlitDataEvent);
}
