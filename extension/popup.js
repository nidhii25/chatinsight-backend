document.getElementById("start").addEventListener("click", () => {
  const meetingId = document.getElementById("meeting_id").value || crypto.randomUUID();

  chrome.storage.local.set({ meeting_id: meetingId });

  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.tabs.sendMessage(tabs[0].id, { action: "start" });
  });

  document.getElementById("status").innerText = "Capturing captions...";
});

document.getElementById("stop").addEventListener("click", () => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.tabs.sendMessage(tabs[0].id, { action: "stop" });
  });

  document.getElementById("status").innerText = "Stopped.";
});
