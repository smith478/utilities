<script>
  import { browser } from '$app/environment';

  // Get backend URL from environment variable, fallback to localhost
  const BACKEND_URL = browser ? (import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000') : 'http://localhost:8000';
  
  import { onMount } from 'svelte';
  
  // Configuration for pause detection
  const PAUSE_DETECTION_THRESHOLD = -45; // dB threshold to consider silence
  const PAUSE_DURATION_THRESHOLD = 1000; // ms of silence to consider it a pause
  const RESTART_DELAY = 10; // ms delay before restarting recording after pause
  
  let audioChunks = [];
  let recorder;
  let audioURL = '';
  let isRecording = false;
  let isAutoPaused = false;
  let recordings = [];
  let recordingStartTime;
  let recordingDuration = 0;
  let selectedRecording = null;
  let loadingRecordings = true;
  let error = null;
  let transcriptionPolling = new Set(); // Track which recordings are being polled
  
  // New variables for concatenated transcriptions
  let concatenatedTranscription = '';
  let editableTranscription = '';
  let pendingTranscriptions = new Set(); // Track which recordings we're waiting for transcriptions
  
  // For pause detection
  let audioContext;
  let analyser;
  let mediaStreamSource;
  let audioStream;
  let pauseDetectionInterval;
  let silenceStart = null;
  let sessionActive = false; // Tracks if a recording session is active (for auto restart)
  
  onMount(async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/audio`);
      const data = await response.json();
      recordings = data.recordings;
      
      // Extract any existing transcriptions to populate the editable text box
      let initialTranscription = '';
      recordings.forEach(recording => {
        if (recording.transcription && recording.transcription !== "Transcribing...") {
          initialTranscription += recording.transcription + ' ';
        } else if (recording.transcription === "Transcribing...") {
          startTranscriptionPolling(recording.id);
          pendingTranscriptions.add(recording.id);
        }
      });
      
      concatenatedTranscription = initialTranscription.trim();
      editableTranscription = concatenatedTranscription;
      
      loadingRecordings = false;
    } catch (e) {
      error = e.message;
      loadingRecordings = false;
    }
  });
  
  function initializeAudioAnalysis(stream) {
    try {
      audioContext = new (window.AudioContext || window.webkitAudioContext)();
      analyser = audioContext.createAnalyser();
      analyser.fftSize = 1024;
      analyser.smoothingTimeConstant = 0.8;
      
      mediaStreamSource = audioContext.createMediaStreamSource(stream);
      mediaStreamSource.connect(analyser);
      
      startPauseDetection();
    } catch (e) {
      console.error("Error initializing audio analysis:", e);
    }
  }
  
  function startPauseDetection() {
    if (pauseDetectionInterval) {
      clearInterval(pauseDetectionInterval);
    }
    
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    
    pauseDetectionInterval = setInterval(() => {
      if (!isRecording || !sessionActive) return;
      
      analyser.getByteFrequencyData(dataArray);
      
      // Calculate average volume level
      let sum = 0;
      for (let i = 0; i < dataArray.length; i++) {
        sum += dataArray[i];
      }
      const average = sum / dataArray.length;
      
      // Convert to decibels (rough approximation)
      const db = average === 0 ? -100 : 20 * Math.log10(average / 255);
      
      // Detect silence
      if (db < PAUSE_DETECTION_THRESHOLD) {
        if (!silenceStart) {
          silenceStart = Date.now();
        } else if (Date.now() - silenceStart > PAUSE_DURATION_THRESHOLD) {
          // We've detected a pause
          handlePauseDetected();
        }
      } else {
        silenceStart = null;
      }
    }, 100); // Check every 100ms
  }
  
  function handlePauseDetected() {
    if (isAutoPaused || !isRecording) return;
    
    console.log("Pause detected - stopping current recording");
    isAutoPaused = true;
    stopRecording(true);
    
    // Auto restart after a short delay
    setTimeout(() => {
      if (sessionActive) {
        console.log("Auto-restarting recording after pause");
        startRecording();
        isAutoPaused = false;
      }
    }, RESTART_DELAY);
  }
  
  function stopPauseDetection() {
    if (pauseDetectionInterval) {
      clearInterval(pauseDetectionInterval);
      pauseDetectionInterval = null;
    }
    
    silenceStart = null;
    
    if (audioContext && audioContext.state !== 'closed') {
      mediaStreamSource?.disconnect();
    }
  }
  
  async function startSession() {
    sessionActive = true;
    await startRecording();
  }
  
  function endSession() {
    sessionActive = false;
    stopRecording(false); // Don't auto-restart
    stopPauseDetection();
    
    if (audioStream) {
      audioStream.getTracks().forEach(track => track.stop());
      audioStream = null;
    }
    
    if (audioContext && audioContext.state !== 'closed') {
      audioContext.close();
    }
  }
  
  async function startRecording() {
    try {
      audioChunks = [];
      
      // Reuse existing stream if possible, otherwise request a new one
      if (!audioStream) {
        audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Initialize audio analysis for pause detection
        initializeAudioAnalysis(audioStream);
      }
      
      recorder = new MediaRecorder(audioStream);
      
      recorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };
      
      recorder.onstop = async () => {
        // Don't process empty recordings
        if (audioChunks.length === 0 || (audioChunks.length === 1 && audioChunks[0].size === 0)) {
          console.log("Empty recording detected, skipping");
          return;
        }
        
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        audioURL = URL.createObjectURL(audioBlob);
        
        // Calculate duration
        recordingDuration = (Date.now() - recordingStartTime) / 1000;
        
        if (recordingDuration < 0.5) {
          console.log("Recording too short, skipping");
          return;
        }
        
        // For auto-detected pauses, immediately save the recording
        if (isAutoPaused && sessionActive) {
          await saveRecordingToServer(audioBlob, recordingDuration);
          audioURL = ''; // Clear URL since we've already saved it
        } else {
          // For manual stops, show preview
          selectedRecording = {
            id: 'preview',
            timestamp: new Date().toLocaleString(),
            audioURL: audioURL,
            duration: recordingDuration,
            transcription: null
          };
        }
      };
      
      recordingStartTime = Date.now();
      recorder.start();
      isRecording = true;
    } catch (e) {
      error = e.message;
    }
  }
  
  function stopRecording(autoTriggered = false) {
    if (recorder && isRecording) {
      recorder.stop();
      isRecording = false;
      
      if (!autoTriggered) {
        sessionActive = false;
      }
    }
  }
  
  async function saveRecordingToServer(blob, duration) {
    try {
      // Create form data
      const formData = new FormData();
      formData.append('file', blob, `recording_${Date.now()}.wav`);
      formData.append('duration', duration.toString());
      
      // Send to server
      const response = await fetch(`${BACKEND_URL}/api/audio`, {
        method: 'POST',
        body: formData
      });

      // Check if the response was successful (status 2xx)
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
        throw new Error(`Server error: ${response.status} - ${errorData.detail || errorData.message || 'Failed to save recording'}`);
      }
      
      const result = await response.json();
      
      // Ensure result and result.recording exist before proceeding
      if (result && result.recording) {
        const newAudioURL = URL.createObjectURL(blob);
        result.recording.audioURL = newAudioURL; // This line caused the error

        recordings = [...recordings, result.recording];
        pendingTranscriptions.add(result.recording.id);
        startTranscriptionPolling(result.recording.id);

        return result.recording;
      } else {
        throw new Error("Invalid response from server: 'recording' data missing.");
      }
    } catch (e) {
      error = e.message;
      console.error("Error saving recording to server:", e);
      return null;
    }
  }
  
  async function saveRecording() {
    if (!audioURL) return;
    
    try {
      const audioBlob = await fetch(audioURL).then(r => r.blob());
      const savedRecording = await saveRecordingToServer(audioBlob, recordingDuration);
      
      // Clear current recording
      audioURL = '';
      
      if (savedRecording) {
        selectedRecording = savedRecording;
      }
    } catch (e) {
      error = e.message;
    }
  }
  
  function startTranscriptionPolling(recordingId) {
    if (transcriptionPolling.has(recordingId)) return;
    
    transcriptionPolling.add(recordingId);
    
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/transcription/${recordingId}`);
        const data = await response.json();
        
        // Find and update the recording
        const index = recordings.findIndex(r => r.id === recordingId);
        if (index !== -1) {
          const updatedRecording = {...recordings[index], transcription: data.transcription};
          recordings[index] = updatedRecording;
          recordings = [...recordings]; // Trigger reactivity
          
          // If selected recording is this one, update it too
          if (selectedRecording && selectedRecording.id === recordingId) {
            selectedRecording = updatedRecording;
          }
          
          // If transcription is complete, update the concatenated text
          if (data.transcription !== "Transcribing...") {
            pendingTranscriptions.delete(recordingId);
            updateConcatenatedTranscription();
            
            // Stop polling
            clearInterval(pollInterval);
            transcriptionPolling.delete(recordingId);
          }
        }
      } catch (e) {
        console.error("Error polling for transcription:", e);
      }
    }, 2000); // Poll every 2 seconds
  }
  
  function updateConcatenatedTranscription() {
    // Build concatenated transcription from all recordings
    concatenatedTranscription = '';
    recordings.forEach(recording => {
      if (recording.transcription && recording.transcription !== "Transcribing...") {
        concatenatedTranscription += recording.transcription + ' ';
      }
    });
    concatenatedTranscription = concatenatedTranscription.trim();
    
    // Update editable transcription while preserving any user edits
    if (editableTranscription === '' || 
        editableTranscription === concatenatedTranscription.substring(0, concatenatedTranscription.length - 
          (recordings[recordings.length - 1].transcription?.length || 0)).trim()) {
      // If user hasn't made edits, update directly
      editableTranscription = concatenatedTranscription;
    }
  }
  
  async function playRecording(recording) {
    selectedRecording = recording;
    
    // If it's a saved recording without local URL, fetch from server
    if (!recording.audioURL && recording.id !== 'preview') {
      try {
        // This will trigger browser to download and play the file
        window.open(`${BACKEND_URL}/api/audio/${recording.id}`, '_blank');
      } catch (e) {
        error = e.message;
      }
    }
  }
  
  function formatDuration(seconds) {
    if (!seconds) return '00:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  
  // Handle transcription text changes
  function handleTranscriptionChange(event) {
    editableTranscription = event.target.value;
  }
  
  // Clear all transcriptions and recordings
  async function clearAllRecordings() {
    // Show confirmation dialog
    const confirmed = confirm('Are you sure you want to clear all transcriptions and delete all recordings? This action cannot be undone.');
    
    if (!confirmed) {
      return;
    }
    
    try {
      // Stop any active recording session
      if (sessionActive || isRecording) {
        endSession();
      }
      
      // Clear transcription polling
      transcriptionPolling.forEach(recordingId => {
        // We can't directly clear intervals by recordingId, but they'll fail gracefully
      });
      transcriptionPolling.clear();
      pendingTranscriptions.clear();
      
      // Delete all recordings from server
      const deletePromises = recordings.map(async (recording) => {
        try {
          const response = await fetch(`${BACKEND_URL}/api/audio/${recording.id}`, {
            method: 'DELETE'
          });
          
          if (!response.ok) {
            console.warn(`Failed to delete recording ${recording.id} from server`);
          }
        } catch (e) {
          console.warn(`Error deleting recording ${recording.id}:`, e);
        }
      });
      
      // Wait for all delete operations to complete (but don't fail if some fail)
      await Promise.allSettled(deletePromises);
      
      // Clear all local state
      recordings = [];
      selectedRecording = null;
      concatenatedTranscription = '';
      editableTranscription = '';
      audioURL = '';
      
      // Clean up any local object URLs
      recordings.forEach(recording => {
        if (recording.audioURL && recording.audioURL.startsWith('blob:')) {
          URL.revokeObjectURL(recording.audioURL);
        }
      });
      
      console.log('All recordings cleared successfully');
      
    } catch (e) {
      error = `Error clearing recordings: ${e.message}`;
      console.error('Error clearing recordings:', e);
    }
  }
  
  // Cleanup on component unmount
  onMount(() => {
    return () => {
      endSession();
    };
  });
</script>

<div class="audio-recorder">
<h2>Smart Audio Recorder with Auto-Pause Detection</h2>

{#if error}
  <div class="error">Error: {error}</div>
{/if}

<div class="controls">
  {#if isRecording}
    <button on:click={endSession} class="stop">Stop Recording</button>
    <div class="recording-indicator">Recording{#if isAutoPaused}... Paused{:else}...{/if}</div>
  {:else if sessionActive}
    <button on:click={endSession} class="stop">End Session</button>
    <div class="session-active">Session active - {isAutoPaused ? 'restarting after pause' : 'waiting for audio'}</div>
  {:else}
    <button on:click={startSession} class="record">Start Recording Session</button>
    <div class="recording-info">Auto-pauses at {PAUSE_DURATION_THRESHOLD/1000}s of silence</div>
  {/if}
</div>

{#if audioURL}
  <div class="playback">
    <h3>Preview Recording ({formatDuration(recordingDuration)})</h3>
    <audio src={audioURL} controls></audio>
    <button on:click={saveRecording} class="save">Save Recording</button>
  </div>
{/if}

<!-- New editable transcription text area -->
<div class="transcription-editor">
  <div class="transcription-header">
    <h3>Transcription Text</h3>
    <button on:click={clearAllRecordings} class="clear-all" title="Clear all transcriptions and delete all recordings">
      Clear All
    </button>
  </div>
  {#if pendingTranscriptions.size > 0}
    <div class="pending-notice">
      Transcribing {pendingTranscriptions.size} recording{pendingTranscriptions.size > 1 ? 's' : ''}...
      <div class="loading-dots"></div>
    </div>
  {/if}
  <textarea 
    bind:value={editableTranscription} 
    on:input={handleTranscriptionChange}
    placeholder="Transcriptions will appear here as recordings are processed..."
    rows="8"
  ></textarea>
</div>

<div class="recordings-library">
  <h3>Recordings Library</h3>
  
  {#if loadingRecordings}
    <p>Loading recordings...</p>
  {:else if recordings.length === 0}
    <p>No recordings saved yet.</p>
  {:else}
    <div class="recordings-list">
      {#each recordings as recording}
      <div 
        class="recording-item" 
        class:selected={selectedRecording && selectedRecording.id === recording.id}
        on:click={() => playRecording(recording)}
        on:keydown={(e) => e.key === 'Enter' && playRecording(recording)}
        tabindex="0"
        role="button"
        aria-label="Play recording from {recording.timestamp}"
      >
        <div class="recording-info">
          <div class="recording-title">Recording {recording.timestamp}</div>
          <div class="recording-duration">{formatDuration(recording.duration)}</div>
        </div>
        
        <div class="recording-playback">
          {#if recording.audioURL}
            <audio src={recording.audioURL} controls></audio>
          {:else}
            <button 
              class="play-btn" 
              on:click|stopPropagation={() => playRecording(recording)}
              aria-label="Play audio"
            >
              Play
            </button>
          {/if}
        </div>
        
        <!-- Display transcription status but not content -->
        {#if recording.transcription}
          <div class="transcription-status">
            {#if recording.transcription === "Transcribing..."}
              <div class="transcribing">
                <span>Transcribing...</span>
                <div class="loading-dots"></div>
              </div>
            {:else}
              <span class="transcription-complete">✓ Transcribed</span>
            {/if}
          </div>
        {/if}
      </div>
      {/each}
    </div>
  {/if}
</div>
</div>

<style>
.audio-recorder {
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin: 20px 0;
  max-width: 700px;
}

.error {
  color: red;
  margin-bottom: 15px;
  padding: 10px;
  background-color: #ffeeee;
  border-radius: 4px;
}

.controls {
  margin: 15px 0;
  display: flex;
  align-items: center;
}

.recording-indicator {
  margin-left: 15px;
  color: #cc0000;
  font-weight: bold;
  animation: blink 1s infinite;
}

.session-active {
  margin-left: 15px;
  color: #008800;
  font-weight: bold;
}

.recording-info {
  margin-left: 15px;
  color: #666;
  font-size: 0.9em;
}

@keyframes blink {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  margin-right: 10px;
}

.record {
  background-color: #ff3e00;
  color: white;
}

.stop {
  background-color: #cc0000;
  color: white;
}

.save {
  background-color: #00cc00;
  color: white;
  margin-top: 10px;
}

.play-btn {
  background-color: #0066cc;
  color: white;
  padding: 5px 10px;
}

.clear-all {
  background-color: #dc3545;
  color: white;
  padding: 8px 16px;
  font-size: 0.9em;
}

.clear-all:hover {
  background-color: #c82333;
}

.playback {
  margin-top: 20px;
  padding: 15px;
  background-color: #f0f0f0;
  border-radius: 4px;
}

.transcription-editor {
  margin-top: 30px;
  padding: 15px;
  background-color: #f0f0f0;
  border-radius: 4px;
}

.transcription-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.transcription-header h3 {
  margin: 0;
}

.transcription-editor textarea {
  width: 100%;
  padding: 10px;
  font-size: 16px;
  line-height: 1.5;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-top: 10px;
  font-family: inherit;
}

.pending-notice {
  display: flex;
  align-items: center;
  color: #666;
  font-size: 0.9em;
  margin-bottom: 10px;
}

.recordings-library {
  margin-top: 30px;
  border-top: 1px solid #ddd;
  padding-top: 20px;
}

.recordings-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 15px;
}

.recording-item {
  padding: 15px;
  background-color: #ffffff;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.recording-item:hover {
  background-color: #f5f5f5;
}

.recording-item.selected {
  border-color: #ff3e00;
  box-shadow: 0 0 0 2px rgba(255, 62, 0, 0.2);
}

.recording-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.recording-title {
  font-weight: bold;
}

.recording-duration {
  font-size: 0.9em;
  color: #666;
}

.transcription-status {
  display: flex;
  align-items: center;
  font-size: 0.9em;
  color: #666;
}

.transcription-complete {
  color: #00aa00;
}

.transcribing {
  display: flex;
  align-items: center;
  color: #666;
}

.loading-dots {
  width: 20px;
  height: 10px;
  margin-left: 5px;
  position: relative;
}

.loading-dots:after {
  content: '...';
  animation: dots 1.5s steps(4, end) infinite;
  display: inline-block;
  width: 20px;
  text-align: left;
}

@keyframes dots {
  0%, 20% { content: '.'; }
  40% { content: '..'; }
  60% { content: '...'; }
  80%, 100% { content: ''; }
}
</style>