// taken from: https://ponyfoo.com/articles/backgroundsync

// Connection Status
function isOnline() {
  const connectionStatus = document.getElementById('connectionStatus');

  if (navigator.onLine) {
    connectionStatus.innerHTML = 'You are currently online!';
  } else {
    connectionStatus.innerHTML = 'You are currently offline. Any requests made will be queued and synced as soon as you are connected again.';
  }
}

window.addEventListener('DOMContentLoaded', isOnline);
window.addEventListener('online', isOnline);
window.addEventListener('offline', isOnline);
