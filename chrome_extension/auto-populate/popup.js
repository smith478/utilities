document.addEventListener('DOMContentLoaded', async () => {
    const statusDiv = document.createElement('div');
    statusDiv.id = 'status';
    document.body.insertBefore(statusDiv, document.getElementById('extractButton'));
    
    // Load saved Streamlit host
    const { streamlitHost = 'http://localhost:8501' } = await chrome.storage.sync.get('streamlitHost');
    document.getElementById('streamlitHost').value = streamlitHost;
    
    // Save Streamlit host when changed
    document.getElementById('streamlitHost').addEventListener('change', (e) => {
        chrome.storage.sync.set({ streamlitHost: e.target.value });
    });
    
    // Check if we're on a supported page
    chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
        const tab = tabs[0];
        if (!tab?.id) return;
        
        try {
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
    const streamlitHost = document.getElementById('streamlitHost').value;
    
    if (!streamlitHost) {
        statusDiv.textContent = "Please enter a Streamlit host address";
        statusDiv.style.color = "red";
        return;
    }
    
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
                data: response.data,
                streamlitHost
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