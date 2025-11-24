console.log("ChatInsight content script loaded");

let observer = null;
let capturing = false;

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.action === "start") startCapturing();
  if (msg.action === "stop") stopCapturing();
});

async function startCapturing() {
  if (capturing) return;
  capturing = true;

  const meetingId = await chrome.storage.local.get("meeting_id").then(x => x.meeting_id);
  const token = await chrome.storage.local.get("token").then(x => x.token);

  console.log("📡 Starting capture for Meeting:", meetingId);

  const captionContainer = waitForCaptionContainer();
  captionContainer.then(container => {
    observer = new MutationObserver((mutations) => {
      for (let m of mutations) {
        const el = m.addedNodes[0];
        if (el && el.innerText) {
          chrome.runtime.sendMessage({
            type: "caption_chunk",
            meeting_id: meetingId,
            text: el.innerText.trim(),
            sender: "Unknown",
            token: token
          });
        }
      }
    });

    observer.observe(container, { childList: true, subtree: true });
  });
}

function stopCapturing() {
  if (observer) observer.disconnect();
  capturing = false;
  console.log("🛑 Caption capturing stopped");
}

// Utility: wait until captions appear
function waitForCaptionContainer() {
  return new Promise(resolve => {
    const check = setInterval(() => {
      const el = document.querySelector('[aria-live="polite"]');
      if (el) {
        clearInterval(check);
        console.log("📡 Caption container found");
        resolve(el);
      }
    }, 700);
  });
}
