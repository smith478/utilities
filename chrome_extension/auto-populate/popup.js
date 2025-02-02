document.getElementById("extractButton").addEventListener("click", () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (!tabs[0]?.id) {
        alert("No active tab found");
        return;
      }
  
      chrome.tabs.sendMessage(
        tabs[0].id,
        { action: "extractData" },
        (response) => {
          // Handle connection errors
          if (chrome.runtime.lastError) {
            console.error("Connection error:", chrome.runtime.lastError);
            alert(`Error: ${chrome.runtime.lastError.message}`);
            return;
          }
  
          // Handle content script response
          if (response?.success) {
            chrome.runtime.sendMessage({
              action: "sendToStreamlit",
              data: response.data
            });
          } else {
            alert("Failed to extract data: " + (response?.error || "Unknown error"));
          }
        }
      );
    });
  });