console.log("Content script loaded for:", window.location.href);

// Test the connection when the script loads
chrome.runtime.sendMessage({ action: "contentScriptLoaded" }, response => {
    console.log("Content script connection test:", response);
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log("Content script received message:", request);
    
    if (request.action === "extractData") {
        try {
            const data = {
                patientId: document.getElementById('patientId')?.value || '',
                patientName: document.getElementById('patientName')?.value || '',
                species: document.getElementById('species')?.value || '',
                breed: document.getElementById('breed')?.value || '',
                gender: document.getElementById('gender')?.value || '',
                weight: document.getElementById('weight')?.value || '',
                age: document.getElementById('age')?.value || '',
                dateOfBirth: document.getElementById('dateOfBirth')?.value || '',
                clinicalFindings: document.getElementById('clinicalFindings')?.value || '',
                reportFindings: document.getElementById('reportFindings')?.value || ''
            };

            // Validate that we actually got some data
            const hasData = Object.values(data).some(value => value !== '');
            if (!hasData) {
                throw new Error("No data found on page. Please check if you're on the correct website.");
            }
            
            console.log("Extracted data:", data);
            sendResponse({ success: true, data });
        } catch (error) {
            console.error("Extraction error:", error);
            sendResponse({ success: false, error: error.message });
        }
    }
    return true; // Keep the message channel open
});