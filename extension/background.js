chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "caption_chunk") {
    fetch("http://localhost:8000/api/meetings/live", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${message.token}`
      },
      body: JSON.stringify({
        meeting_id: message.meeting_id,
        text: message.text,
        sender: message.sender,
        timestamp: new Date().toISOString()
      })
    })
    .then(res => res.json())
    .then(data => console.log("📩 Sent:", data))
    .catch(err => console.error("❌ Backend error:", err));
  }
});
