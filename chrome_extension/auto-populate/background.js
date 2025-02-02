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
        
        // First get the current window
        chrome.windows.getCurrent({}, (currentWindow) => {
            // Then look for Streamlit tabs across all windows
            chrome.tabs.query({}, (tabs) => {
                // First try to find a Streamlit tab in the current window
                let streamlitTab = tabs.find(tab => 
                    tab.url?.includes('localhost:8501') && 
                    tab.windowId === currentWindow.id
                );
                
                // If no tab found in current window, look in other windows
                if (!streamlitTab) {
                    streamlitTab = tabs.find(tab => 
                        tab.url?.includes('localhost:8501')
                    );
                }
                
                if (streamlitTab) {
                    // If tab is in a different window, bring that window to front
                    if (streamlitTab.windowId !== currentWindow.id) {
                        chrome.windows.update(streamlitTab.windowId, { 
                            focused: true 
                        });
                    }
                    
                    // Update the tab URL and activate it
                    chrome.tabs.update(streamlitTab.id, {
                        url: streamlitUrl,
                        active: true
                    }, () => {
                        console.log("Updated existing Streamlit tab in window:", streamlitTab.windowId);
                        sendResponse({ success: true });
                    });
                } else {
                    // Create new tab in current window if none exists
                    chrome.tabs.create({
                        url: streamlitUrl,
                        active: true
                    }, (tab) => {
                        console.log("Created new Streamlit tab:", tab.id);
                        sendResponse({ success: true });
                    });
                }
            });
        });
        
        return true; // Keep message channel open for async response
    }
});