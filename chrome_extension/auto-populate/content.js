console.log("Content script loaded for:", window.location.href);

// Helper function to extract text content using a selector
function extractText(selector) {
    const element = document.querySelector(selector);
    return element ? element.textContent.trim() : '';
}

// Wait for dynamic content using MutationObserver
function waitForDynamicContent(selector, timeout = 5000) {
    return new Promise((resolve, reject) => {
        const startTime = Date.now();

        const observer = new MutationObserver(() => {
            if (document.querySelector(selector)) {
                observer.disconnect();
                resolve();
            } else if (Date.now() - startTime > timeout) {
                observer.disconnect();
                reject(new Error(`Timed out waiting for ${selector}`));
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        // Initial check in case content already exists
        if (document.querySelector(selector)) {
            observer.disconnect();
            resolve();
        }
    });
}

// Test the connection when the script loads
chrome.runtime.sendMessage({ action: "contentScriptLoaded" }, response => {
    console.log("Content script connection test:", response);
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "extractData") {
        (async () => {
            try {
                // Wait for the main container to load
                await waitForDynamicContent('body > div.wrapper > div.content-wrapper > section.content.report_page_data');

                // Extract data using the provided selectors
                const data = {
                    patientId: extractText('body > div.wrapper > div.content-wrapper > section.content.report_page_data > div:nth-child(1) > div.col-md-8 > div > div > div > div:nth-child(1) > div:nth-child(2) > div > div.box-body > table > tbody > tr:nth-child(1) > td'),
                    patientName: extractText('body > div.wrapper > div.content-wrapper > section.content.report_page_data > div:nth-child(1) > div.col-md-8 > div > div > div > div:nth-child(1) > div:nth-child(2) > div > div.box-body > table > tbody > tr:nth-child(2) > td'),
                    species: extractText('body > div.wrapper > div.content-wrapper > section.content.report_page_data > div:nth-child(1) > div.col-md-8 > div > div > div > div:nth-child(1) > div:nth-child(2) > div > div.box-body > table > tbody > tr:nth-child(3) > td'),
                    breed: extractText('body > div.wrapper > div.content-wrapper > section.content.report_page_data > div:nth-child(1) > div.col-md-8 > div > div > div > div:nth-child(1) > div:nth-child(2) > div > div.box-body > table > tbody > tr:nth-child(4) > td'),
                    gender: extractText('body > div.wrapper > div.content-wrapper > section.content.report_page_data > div:nth-child(1) > div.col-md-8 > div > div > div > div:nth-child(1) > div:nth-child(2) > div > div.box-body > table > tbody > tr:nth-child(5) > td'),
                    weight: extractText('body > div.wrapper > div.content-wrapper > section.content.report_page_data > div:nth-child(1) > div.col-md-8 > div > div > div > div:nth-child(1) > div:nth-child(2) > div > div.box-body > table > tbody > tr:nth-child(6) > td'),
                    age: extractText('body > div.wrapper > div.content-wrapper > section.content.report_page_data > div:nth-child(1) > div.col-md-8 > div > div > div > div:nth-child(1) > div:nth-child(2) > div > div.box-body > table > tbody > tr:nth-child(7) > td'),
                    dateOfBirth: extractText('body > div.wrapper > div.content-wrapper > section.content.report_page_data > div:nth-child(1) > div.col-md-8 > div > div > div > div:nth-child(1) > div:nth-child(2) > div > div.box-body > table > tbody > tr:nth-child(8) > td'),
                    clinicalFindings: extractText('#clinic-finding-information-box > div > div > div > table > tbody > tr.clinical-finding-view-box-2806.clinical-finding-view-field-container > td'),
                    clinicalQuestion: extractText('#clinic-finding-information-box > div > div > div > table > tbody > tr.clinical-finding-view-box-2808.clinical-finding-view-field-container > td'),
                    comparisonStudy: extractText('#clinic-finding-information-box > div > div > div > table > tbody > tr.clinical-finding-view-box-2809.clinical-finding-view-field-container > td'),
                    reportFindings: extractText('#report-information-box > div > table > tbody > tr.report-view-box-2810.report-view-field-container > td:nth-child(2)')
                };

                // Log the extracted data for debugging
                console.log("Extracted Data:", data);

                // Send the data back to the extension
                sendResponse({ success: true, data });
            } catch (error) {
                console.error("Extraction error:", error);
                sendResponse({ success: false, error: error.message });
            }
        })();

        // Return true to keep the message channel open for async response
        return true;
    }
});