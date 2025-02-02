chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "sendToStreamlit") {
      // Wrap in Promise to handle async properly
      new Promise((resolve) => {
        const jsonData = encodeURIComponent(JSON.stringify(request.data));
        const streamlitUrl = `http://localhost:8501/?data=${jsonData}`;
  
        chrome.tabs.query({ url: "http://localhost:8501/*" }, (tabs) => {
          if (tabs && tabs.length > 0) {
            chrome.tabs.update(tabs[0].id, { url: streamlitUrl }, () => resolve());
          } else {
            chrome.tabs.create({ url: streamlitUrl }, () => resolve());
          }
        });
      }).then(() => sendResponse({ success: true }));
      
      return true; // Keep channel open
    }
  });