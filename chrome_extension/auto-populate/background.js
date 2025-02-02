chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "contentScriptLoaded") {
        sendResponse({ status: "Connected successfully" });
        return true;
    }
    
    if (request.action === "sendToStreamlit") {
        const rawData = JSON.stringify(request.data);
        const timestamp = Date.now();
        const streamlitUrl = `http://localhost:8501/?data=${encodeURIComponent(rawData)}&_=${timestamp}`;
        
        console.log("Attempting to navigate to:", streamlitUrl);
        
        // First, check if Streamlit tab exists
        chrome.tabs.query({}, (tabs) => {
            const streamlitTab = tabs.find(tab => tab.url?.includes('localhost:8501'));
            
            if (streamlitTab) {
                // Force a navigation to the new URL
                chrome.tabs.update(streamlitTab.id, {
                    url: streamlitUrl
                }, () => {
                    // After update, activate the tab
                    chrome.tabs.update(streamlitTab.id, { active: true });
                    console.log("Updated and activated existing Streamlit tab");
                    sendResponse({ success: true });
                });
            } else {
                // Create new tab if none exists
                chrome.tabs.create({
                    url: streamlitUrl,
                    active: true
                }, (tab) => {
                    console.log("Created new Streamlit tab:", tab.id);
                    sendResponse({ success: true });
                });
            }
        });
        
        return true; // Keep message channel open for async response
    }
});