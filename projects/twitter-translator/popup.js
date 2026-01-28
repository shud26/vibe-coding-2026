const enableToggle = document.getElementById("enableToggle");
const autoToggle = document.getElementById("autoToggle");

// Load saved settings
chrome.storage.sync.get({ enabled: true, autoMode: false }, (settings) => {
  enableToggle.checked = settings.enabled;
  autoToggle.checked = settings.autoMode;
});

enableToggle.addEventListener("change", () => {
  chrome.storage.sync.set({ enabled: enableToggle.checked });
});

autoToggle.addEventListener("change", () => {
  chrome.storage.sync.set({ autoMode: autoToggle.checked });
});
