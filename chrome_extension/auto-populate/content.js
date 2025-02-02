console.log("Content script loaded!");

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log("Received message:", request);
    if (request.action === "extractData") {
      try {
        const data = {
          patientId: document.getElementById('patientId').value,
          patientName: document.getElementById('patientName').value,
          species: document.getElementById('species').value,
          breed: document.getElementById('breed').value,
          gender: document.getElementById('gender').value,
          weight: document.getElementById('weight').value,
          age: document.getElementById('age').value,
          dateOfBirth: document.getElementById('dateOfBirth').value,
          clinicalFindings: document.getElementById('clinicalFindings').value,
          reportFindings: document.getElementById('reportFindings').value
        };
        sendResponse({ success: true, data });
      } catch (error) {
        sendResponse({ success: false, error: error.message });
      }
      return true; // Keep channel open
    }
  });