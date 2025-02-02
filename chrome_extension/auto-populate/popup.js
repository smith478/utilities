document.addEventListener('DOMContentLoaded', () => {
    const statusDiv = document.createElement('div');
    statusDiv.id = 'status';
    statusDiv.style.marginBottom = '10px';
    document.body.insertBefore(statusDiv, document.getElementById('extractButton'));
    
    // Check if we're on a supported page
    chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
        const tab = tabs[0];
        if (!tab?.id) return;
        
        try {
            // Test the connection to the content script
            await chrome.tabs.sendMessage(tab.id, { action: "ping" });
            statusDiv.textContent = "Ready to extract data";
            statusDiv.style.color = "green";
        } catch (error) {
            statusDiv.textContent = "Not on a supported page";
            statusDiv.style.color = "red";
            document.getElementById("extractButton").disabled = true;
        }
    });
});

document.getElementById("extractButton").addEventListener("click", async () => {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = "Extracting data...";
    
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        
        if (!tab?.id) {
            throw new Error("No active tab found");
        }
        
        console.log("Attempting to extract data from:", tab.url);
        
        const response = await chrome.tabs.sendMessage(tab.id, { action: "extractData" });
        console.log("Extraction response:", response);
        
        if (response?.success) {
            statusDiv.textContent = "Sending to Streamlit...";
            
            chrome.runtime.sendMessage({
                action: "sendToStreamlit",
                data: response.data
            }, (response) => {
                if (chrome.runtime.lastError) {
                    throw new Error(chrome.runtime.lastError.message);
                }
                statusDiv.textContent = "Data sent successfully!";
                statusDiv.style.color = "green";
            });
        } else {
            throw new Error(response?.error || "Failed to extract data");
        }
    } catch (error) {
        console.error("Error:", error);
        statusDiv.textContent = `Error: ${error.message}`;
        statusDiv.style.color = "red";
    }
});