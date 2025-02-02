chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "contentScriptLoaded") {
        sendResponse({ status: "Connected successfully" });
        return true;
    }
    
    if (request.action === "sendToStreamlit") {
        // Get the Streamlit host from the request
        const streamlitHost = request.streamlitHost?.trim() || 'http://localhost:8501';
        const rawData = JSON.stringify(request.data);
        const timestamp = Date.now();
        
        // Ensure the host ends with a trailing slash for consistent URL joining
        const baseUrl = streamlitHost.endsWith('/') ? streamlitHost : `${streamlitHost}/`;
        const streamlitUrl = `${baseUrl}?data=${encodeURIComponent(rawData)}&_=${timestamp}`;
        
        console.log("Attempting to navigate to:", streamlitUrl);
        
        // Get the current window
        chrome.windows.getCurrent({}, (currentWindow) => {
            // Look for Streamlit tabs across all windows
            chrome.tabs.query({}, (tabs) => {
                // Try to find a Streamlit tab in the current window
                let streamlitTab = tabs.find(tab => 
                    tab.url?.includes(streamlitHost) && 
                    tab.windowId === currentWindow.id
                );
                
                // If no tab found in current window, look in other windows
                if (!streamlitTab) {
                    streamlitTab = tabs.find(tab => 
                        tab.url?.includes(streamlitHost)
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
        
        return true;
    }
});