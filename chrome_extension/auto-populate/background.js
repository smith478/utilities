chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "sendToStreamlit") {
      const rawData = JSON.stringify(request.data);
      const timestamp = Date.now();
      const streamlitUrl = `http://localhost:8501/?data=${encodeURIComponent(rawData)}&_=${timestamp}`;
  
      chrome.tabs.query({ url: "http://localhost:8501/*" }, (tabs) => {
        if (tabs?.[0]?.id) {
          // Force new navigation with cache busting
          chrome.tabs.update(tabs[0].id, { 
            url: streamlitUrl,
            active: true 
          }, (tab) => {
            console.log("Updated tab:", tab.id);
          });
        } else {
          chrome.tabs.create({ url: streamlitUrl }, (tab) => {
            console.log("Created new tab:", tab.id);
          });
        }
        sendResponse({ success: true });
      });
      return true;
    }
  });