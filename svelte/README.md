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