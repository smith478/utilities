# Setting Up Svelte

1. Prerequisites: Ensure you have Node.js installed
- Check if installed: `node -v`
- If not, download from [nodejs.org](nodejs.org)

2. Create a new Svelte project:
```bash
# Install the SvelteKit template
npx sv create test-svelte-app

# Navigate to your project
cd test-svelte-app

# Start the development server
npm run dev -- --open
```

# Learning Path: From Basics to Backend Integration

## Exercise 1: Hello World Component
Create your first component in `src/routes/+page.svelte`:
```svelte
<script>
  let name = 'World';
</script>

<h1>Hello {name}!</h1>

<input bind:value={name} placeholder="Enter your name">

<style>
  h1 {
    color: #ff3e00;
  }
</style>
```

## Exercise 2: Building UI Components
Create a new file `src/lib/components/FormElements.svelte`:
```svelte
<script>
  // Props with default values
  export let textValue = '';
  export let options = ['Option 1', 'Option 2', 'Option 3'];
  export let selectedOption = options[0];
  
  // Function to handle selection
  function handleSelect(event) {
    selectedOption = event.target.value;
  }
</script>

<div class="form-container">
  <div class="form-group">
    <label for="textbox">Editable Text Box:</label>
    <input id="textbox" type="text" bind:value={textValue} placeholder="Type something...">
    <p>Current value: {textValue}</p>
  </div>
  
  <div class="form-group">
    <label for="dropdown">Dropdown Menu:</label>
    <select id="dropdown" value={selectedOption} on:change={handleSelect}>
      {#each options as option}
        <option value={option}>{option}</option>
      {/each}
    </select>
    <p>Selected: {selectedOption}</p>
  </div>
</div>

<style>
  .form-container {
    max-width: 400px;
    margin: 20px auto;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
  }
  
  .form-group {
    margin-bottom: 15px;
  }
  
  label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
  }
  
  input, select {
    width: 100%;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
  }
</style>
```

Now use this component in `src/routes/+page.svelte`:
```svelte
<script>
  import FormElements from '$lib/components/FormElements.svelte';
  
  let myText = 'Edit me!';
  let myOptions = ['Svelte', 'React', 'Vue', 'Angular'];
  let mySelection = 'Svelte';
</script>

<h1>Form Components Demo</h1>

<FormElements 
  textValue={myText} 
  options={myOptions} 
  selectedOption={mySelection}
/>

<p>Parent component can access: Text = {myText}, Selection = {mySelection}</p>
```

## Exercise 3: Audio Recording and Playback
Create a new component in `src/lib/components/AudioRecorder.svelte`:
```svelte
<script>
  let audioChunks = [];
  let recorder;
  let audioURL = '';
  let isRecording = false;
  
  async function startRecording() {
    audioChunks = [];
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recorder = new MediaRecorder(stream);
    
    recorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };
    
    recorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
      audioURL = URL.createObjectURL(audioBlob);
    };
    
    recorder.start();
    isRecording = true;
  }
  
  function stopRecording() {
    if (recorder && isRecording) {
      recorder.stop();
      isRecording = false;
    }
  }
</script>

<div class="audio-recorder">
  <h2>Audio Recorder</h2>
  
  <div class="controls">
    {#if isRecording}
      <button on:click={stopRecording} class="stop">Stop Recording</button>
    {:else}
      <button on:click={startRecording} class="record">Start Recording</button>
    {/if}
  </div>
  
  {#if audioURL}
    <div class="playback">
      <h3>Playback</h3>
      <audio src={audioURL} controls></audio>
    </div>
  {/if}
</div>

<style>
  .audio-recorder {
    padding: 20px;
    background-color: #f9f9f9;
    border-radius: 8px;
    margin: 20px 0;
  }
  
  .controls {
    margin: 15px 0;
  }
  
  button {
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
  }
  
  .record {
    background-color: #ff3e00;
    color: white;
  }
  
  .stop {
    background-color: #cc0000;
    color: white;
  }
  
  .playback {
    margin-top: 20px;
  }
</style>
```

Update `src/routes/+page.svelte`:
```svelte
<script>
  import FormElements from '$lib/components/FormElements.svelte';
  import AudioRecorder from '$lib/components/AudioRecorder.svelte';
  
  let myText = 'Edit me!';
  let myOptions = ['Svelte', 'React', 'Vue', 'Angular'];
  let mySelection = 'Svelte';
</script>

<h1>Form Components Demo</h1>

<FormElements 
  textValue={myText} 
  options={myOptions} 
  selectedOption={mySelection}
/>

<p>Parent component can access: Text = {myText}, Selection = {mySelection}</p>

<AudioRecorder />
```

## Exercise 4: Python Backend with FastAPI
Create a basic FastAPI backend:
```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your Svelte app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    name: str
    value: str

items = [
    {"name": "Item 1", "value": "Value 1"},
    {"name": "Item 2", "value": "Value 2"}
]

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}

@app.get("/api/items")
def get_items():
    return {"items": items}

@app.post("/api/items")
def add_item(item: Item):
    items.append({"name": item.name, "value": item.value})
    return {"status": "success", "items": items}
````

Run the backend:
```bash
uvicorn main:app --reload
```

## Exercise 5: Connecting Svelte to Python Backend
Create a new component for fetching and displaying data `src/lib/components/BackendConnection.svelte`:
```svelte
<script>
  import { onMount } from 'svelte';
  
  let items = [];
  let loading = true;
  let error = null;
  
  // Form data
  let newItemName = '';
  let newItemValue = '';
  
  onMount(async () => {
    try {
      const response = await fetch('http://localhost:8000/api/items');
      const data = await response.json();
      items = data.items;
      loading = false;
    } catch (e) {
      error = e.message;
      loading = false;
    }
  });
  
  async function addItem() {
    if (!newItemName || !newItemValue) return;
    
    try {
      const response = await fetch('http://localhost:8000/api/items', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: newItemName,
          value: newItemValue
        })
      });
      
      const data = await response.json();
      items = data.items;
      
      // Reset form
      newItemName = '';
      newItemValue = '';
    } catch (e) {
      error = e.message;
    }
  }
</script>

<div class="backend-demo">
  <h2>Backend Connection Demo</h2>
  
  {#if loading}
    <p>Loading data from Python backend...</p>
  {:else if error}
    <p class="error">Error: {error}</p>
  {:else}
    <div class="items-list">
      <h3>Items from Backend:</h3>
      {#each items as item}
        <div class="item">
          <strong>{item.name}:</strong> {item.value}
        </div>
      {/each}
    </div>
  {/if}
  
  <div class="add-item-form">
    <h3>Add New Item</h3>
    <div class="form-group">
      <input type="text" bind:value={newItemName} placeholder="Item Name">
    </div>
    <div class="form-group">
      <input type="text" bind:value={newItemValue} placeholder="Item Value">
    </div>
    <button on:click={addItem}>Add Item</button>
  </div>
</div>

<style>
  .backend-demo {
    max-width: 600px;
    margin: 20px auto;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
  }
  
  .error {
    color: red;
  }
  
  .items-list {
    margin-bottom: 20px;
  }
  
  .item {
    padding: 10px;
    margin: 5px 0;
    background-color: #f5f5f5;
    border-radius: 4px;
  }
  
  .add-item-form {
    padding-top: 15px;
    border-top: 1px solid #eee;
  }
  
  .form-group {
    margin-bottom: 10px;
  }
  
  button {
    background-color: #ff3e00;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
  }
</style>
```

## Exercise 6: Saving and Replaying Audio Recordings
We'll enhance the audio recorder to save recordings with timestamps and create a playback library.
1. First, update the Python backend (backend/main.py):
```python
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
import time
from datetime import datetime

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    name: str
    value: str

class AudioRecording(BaseModel):
    id: str
    timestamp: str
    filename: str
    duration: Optional[float] = None

items = [
    {"name": "Item 1", "value": "Value 1"},
    {"name": "Item 2", "value": "Value 2"}
]

# Create directory for audio storage
AUDIO_DIR = "audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Store audio metadata
recordings = []

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}

@app.get("/api/items")
def get_items():
    return {"items": items}

@app.post("/api/items")
def add_item(item: Item):
    items.append({"name": item.name, "value": item.value})
    return {"status": "success", "items": items}

@app.post("/api/audio")
async def upload_audio(file: UploadFile = File(...), duration: Optional[float] = None):
    # Generate timestamp and filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    recording_id = f"rec_{int(time.time())}"
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".wav"
    filename = f"{recording_id}{file_extension}"
    
    # Save the file
    file_path = os.path.join(AUDIO_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Save metadata
    recording = AudioRecording(
        id=recording_id,
        timestamp=timestamp,
        filename=filename,
        duration=duration
    )
    recordings.append(recording.dict())
    
    return {"status": "success", "recording": recording.dict()}

@app.get("/api/audio")
def get_recordings():
    return {"recordings": recordings}

@app.get("/api/audio/{recording_id}")
def get_audio_file(recording_id: str):
    for rec in recordings:
        if rec["id"] == recording_id:
            file_path = os.path.join(AUDIO_DIR, rec["filename"])
            if os.path.exists(file_path):
                return FileResponse(
                    path=file_path, 
                    media_type="audio/wav", 
                    filename=rec["filename"]
                )
    
    return {"error": "Recording not found"}, 404
```
2. Create an improved audio recorder
Update `src/lib/components/AudioRecorderAdvanced.svelte`:
```svelte
<script>
  import { onMount } from 'svelte';
  
  let audioChunks = [];
  let recorder;
  let audioURL = '';
  let isRecording = false;
  let recordings = [];
  let recordingStartTime;
  let recordingDuration = 0;
  let selectedRecording = null;
  let loadingRecordings = true;
  let error = null;
  
  onMount(async () => {
    try {
      const response = await fetch('http://localhost:8000/api/audio');
      const data = await response.json();
      recordings = data.recordings;
      loadingRecordings = false;
    } catch (e) {
      error = e.message;
      loadingRecordings = false;
    }
  });
  
  async function startRecording() {
    try {
      audioChunks = [];
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      recorder = new MediaRecorder(stream);
      
      recorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };
      
      recorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        audioURL = URL.createObjectURL(audioBlob);
        
        // Calculate duration
        recordingDuration = (Date.now() - recordingStartTime) / 1000;
        
        // Save as temporary preview before uploading
        selectedRecording = {
          id: 'preview',
          timestamp: new Date().toLocaleString(),
          audioURL: audioURL,
          duration: recordingDuration
        };
      };
      
      recordingStartTime = Date.now();
      recorder.start();
      isRecording = true;
    } catch (e) {
      error = e.message;
    }
  }
  
  function stopRecording() {
    if (recorder && isRecording) {
      recorder.stop();
      isRecording = false;
    }
  }
  
  async function saveRecording() {
    if (!audioURL) return;
    
    try {
      // Create form data
      const formData = new FormData();
      const audioBlob = await fetch(audioURL).then(r => r.blob());
      formData.append('file', audioBlob, `recording_${Date.now()}.wav`);
      formData.append('duration', recordingDuration.toString());
      
      // Send to server
      const response = await fetch('http://localhost:8000/api/audio', {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      
      // Add to recordings list with local URL until page reload
      result.recording.audioURL = audioURL;
      recordings = [...recordings, result.recording];
      
      // Clear current recording
      audioURL = '';
      selectedRecording = result.recording;
    } catch (e) {
      error = e.message;
    }
  }
  
  async function playRecording(recording) {
    selectedRecording = recording;
    
    // If it's a saved recording without local URL, fetch from server
    if (!recording.audioURL && recording.id !== 'preview') {
      try {
        // This will trigger browser to download and play the file
        window.open(`http://localhost:8000/api/audio/${recording.id}`, '_blank');
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
</script>

<div class="audio-recorder">
  <h2>Advanced Audio Recorder</h2>
  
  {#if error}
    <div class="error">Error: {error}</div>
  {/if}
  
  <div class="controls">
    {#if isRecording}
      <button on:click={stopRecording} class="stop">Stop Recording</button>
      <div class="recording-indicator">Recording...</div>
    {:else}
      <button on:click={startRecording} class="record">Start Recording</button>
    {/if}
  </div>
  
  {#if audioURL}
    <div class="playback">
      <h3>Preview Recording ({formatDuration(recordingDuration)})</h3>
      <audio src={audioURL} controls></audio>
      <button on:click={saveRecording} class="save">Save Recording</button>
    </div>
  {/if}
  
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
          >
            <div class="recording-info">
              <div class="recording-title">Recording {recording.timestamp}</div>
              <div class="recording-duration">{formatDuration(recording.duration)}</div>
            </div>
            {#if recording.audioURL}
              <audio src={recording.audioURL} controls></audio>
            {:else}
              <button class="play-btn" on:click|stopPropagation={() => playRecording(recording)}>
                Play
              </button>
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
    max-width: 600px;
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
  
  .playback {
    margin-top: 20px;
    padding: 15px;
    background-color: #f0f0f0;
    border-radius: 4px;
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
</style>
```
3. Update src/routes/+page.svelte to include the new component:
```svelte
<script>
  import FormElements from '$lib/components/FormElements.svelte';
  import AudioRecorder from '$lib/components/AudioRecorder.svelte';
  import AudioRecorderAdvanced from '$lib/components/AudioRecorderAdvanced.svelte';
  
  let myText = 'Edit me!';
  let myOptions = ['Svelte', 'React', 'Vue', 'Angular'];
  let mySelection = 'Svelte';
</script>

<h1>Form Components Demo</h1>

<FormElements 
  textValue={myText} 
  options={myOptions} 
  selectedOption={mySelection}
/>

<p>Parent component can access: Text = {myText}, Selection = {mySelection}</p>

<AudioRecorderAdvanced />
```

# Speech to text with Parakeet

We will set this up assuming that the backend application is running on a separate machine. This can be convenient if you want a server with a GPU to run the core ASR model.

To run the frontend application with local backend we can use:
```bash
npm run dev -- --open
```
Now if we want to run a remote backend (on the same network), use:
```bash
VITE_BACKEND_URL=http://<DESKTOP_IP>:8000 npm run dev -- --open

# For example
VITE_BACKEND_URL=http://192.168.1.100:8000 npm run dev -- --open
```

## TODO 
- Refactor the application - especially the audio recorder component
- X Add dark mode
- Update the UI to have findings/recommendations
- Try to use OpenHands with Devstral to make the updates above