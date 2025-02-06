console.log("Content script loaded for:", window.location.href);

// Helper function to find elements by multiple possible selectors (case-insensitive and space-aware)
function findElement(selectors) {
    // Helper to create variations of a selector
    function getVariations(selector) {
        const variations = [
            selector,
            selector.toLowerCase(),
            selector.toUpperCase(),
            selector.replace(/([A-Z])/g, ' $1').trim(), // camelCase to spaces
            selector.replace(/\s+/g, ''), // remove spaces
            selector.replace(/\s+/g, '_'), // spaces to underscore
            selector.split(/(?=[A-Z])/).join(' ') // camelCase to spaces
        ];
        return [...new Set(variations)]; // Remove duplicates
    }

    for (const selector of selectors) {
        // Get all variations of the selector
        const selectorVariations = getVariations(selector);
        
        // Try finding by ID first
        const allElements = document.getElementsByTagName('*');
        for (const element of allElements) {
            if (element.id && selectorVariations.some(variation => 
                element.id.toLowerCase().replace(/[\s_]+/g, '') === variation.toLowerCase().replace(/[\s_]+/g, '')
            )) {
                return element;
            }
        }
        
        // Try other selectors
        for (const variation of selectorVariations) {
            try {
                const elementByQuery = document.querySelector(
                    `[name="${variation}" i], 
                     [class*="${variation}" i],
                     [data-field="${variation}" i],
                     #${variation}`
                );
                if (elementByQuery) return elementByQuery;
            } catch (e) {
                console.log(`Selector error for ${variation}, trying next...`);
            }
        }
    }
    return null;
}

// Wait for page to be fully loaded
function waitForElements(timeout = 5000) {
    return new Promise((resolve, reject) => {
        const startTime = Date.now();
        
        const checkElements = () => {
            // Check if any of our target elements exist
            const anyElement = findElement(['Patient Name', 'PatientName', 'patientName']);
            
            if (anyElement) {
                resolve();
            } else if (Date.now() - startTime > timeout) {
                reject(new Error("Timed out waiting for elements"));
            } else {
                setTimeout(checkElements, 100);
            }
        };
        
        checkElements();
    });
}

// Test the connection when the script loads
chrome.runtime.sendMessage({ action: "contentScriptLoaded" }, response => {
    console.log("Content script connection test:", response);
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log("Content script received message:", request);
    
    if (request.action === "extractData") {
        // Use async function to handle the wait
        (async () => {
            try {
                // Wait for elements to load
                await waitForElements();
                
                const data = {
                    patientId: findElement(['Patient Id', 'PatientId', 'Patient ID', 'patientId'])?.value || '',
                    patientName: findElement(['Patient Name', 'PatientName', 'patientName'])?.value || '',
                    species: findElement(['Species', 'species'])?.value || '',
                    breed: findElement(['Breed', 'breed'])?.value || '',
                    gender: findElement(['Gender', 'gender', 'Sex'])?.value || '',
                    weight: findElement(['Weight', 'weight'])?.value || '',
                    age: findElement(['Age', 'age'])?.value || '',
                    dateOfBirth: findElement(['Date of Birth', 'DateOfBirth', 'Date Of Birth', 'DOB'])?.value || '',
                    clinicalFindings: findElement(['Clinical Findings', 'ClinicalFindings', 'Clinical Finding'])?.value || '',
                    reportFindings: findElement(['Report Findings', 'ReportFindings', 'Report Finding'])?.value || ''
                };

                // Add debugging information
                console.log("Found elements:", Object.entries(data).map(([key, value]) => `${key}: ${value ? 'Found' : 'Not found'}`));

                // Validate that we actually got some data
                const hasData = Object.values(data).some(value => value !== '');
                if (!hasData) {
                    throw new Error("No data found on page. Please inspect the page source to verify correct element IDs.");
                }
                
                console.log("Extracted data:", data);
                sendResponse({ success: true, data });
            } catch (error) {
                console.error("Extraction error:", error);
                sendResponse({ success: false, error: error.message });
            }
        })();
        
        return true; // Keep the message channel open
    }
});