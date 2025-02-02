document.getElementById("extractButton").addEventListener("click", async () => {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      if (!tab?.id) {
        alert("No active tab found");
        return;
      }
  
      // Verify content script connection
      const response = await chrome.tabs.sendMessage(tab.id, { action: "extractData" });
      
      if (response?.success) {
        chrome.runtime.sendMessage({
          action: "sendToStreamlit",
          data: response.data
        });
        alert("Data sent successfully!");
      } else {
        alert("Extraction failed: " + (response?.error || "Unknown error"));
      }
    } catch (error) {
      console.error("Popup error:", error);
      alert(`Connection failed: ${error.message}\n\nMake sure you're on the test website!`);
    }
  });