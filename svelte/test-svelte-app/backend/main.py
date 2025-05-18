from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
import time
from datetime import datetime
import asyncio
import torch
from transformers import pipeline

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
    transcription: Optional[str] = None

items = [
    {"name": "Item 1", "value": "Value 1"},
    {"name": "Item 2", "value": "Value 2"}
]

# Create directory for audio storage
AUDIO_DIR = "audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Store audio metadata
recordings = []

# Initialize ASR pipeline
# Using whisper-small as it has good performance on Mac M1
# Note: This will download the model on first run
asr_pipeline = None

def initialize_asr():
    global asr_pipeline
    # We're using Whisper small model which works well on M1 Macs
    asr_pipeline = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-small",
        device="mps" if torch.backends.mps.is_available() else "cpu"
    )
    print(f"ASR model initialized on device: {'MPS (Apple Silicon)' if torch.backends.mps.is_available() else 'CPU'}")

# Initialize ASR in the background
@app.on_event("startup")
async def startup_event():
    # Run in a separate thread to avoid blocking startup
    asyncio.create_task(async_initialize_asr())

async def async_initialize_asr():
    # Run the CPU-bound operation in a thread pool
    await asyncio.to_thread(initialize_asr)

async def transcribe_audio(file_path):
    if asr_pipeline is None:
        print("ASR model not yet initialized, initializing now...")
        await asyncio.to_thread(initialize_asr)
    
    # Run transcription in a thread pool to avoid blocking
    result = await asyncio.to_thread(asr_pipeline, file_path)
    return result["text"]

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
    
    # Transcribe the audio asynchronously
    transcription = "Transcribing..." # Initial state
    
    # Create recording object
    recording = AudioRecording(
        id=recording_id,
        timestamp=timestamp,
        filename=filename,
        duration=duration,
        transcription=transcription
    )
    
    # Add to recordings list
    recordings.append(recording.dict())
    
    # Start async transcription
    asyncio.create_task(update_transcription(recording_id, file_path))
    
    return {"status": "success", "recording": recording.dict()}

async def update_transcription(recording_id, file_path):
    try:
        # Perform actual transcription
        transcription = await transcribe_audio(file_path)
        
        # Update recording with transcription
        for rec in recordings:
            if rec["id"] == recording_id:
                rec["transcription"] = transcription
                break
    except Exception as e:
        # Handle errors
        error_message = f"Transcription error: {str(e)}"
        for rec in recordings:
            if rec["id"] == recording_id:
                rec["transcription"] = error_message
                break

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
    
    raise HTTPException(status_code=404, detail="Recording not found")

@app.delete("/api/audio/{recording_id}")
def delete_recording(recording_id: str):
    """Delete a specific recording and its file"""
    global recordings
    
    # Find the recording
    recording_to_delete = None
    for i, rec in enumerate(recordings):
        if rec["id"] == recording_id:
            recording_to_delete = recordings.pop(i)
            break
    
    if not recording_to_delete:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    # Delete the physical file
    file_path = os.path.join(AUDIO_DIR, recording_to_delete["filename"])
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
        except OSError as e:
            print(f"Error deleting file {file_path}: {e}")
            # Don't raise an error here since we already removed from recordings list
    
    return {"status": "success", "message": f"Recording {recording_id} deleted"}

@app.delete("/api/audio")
def clear_all_recordings():
    """Delete all recordings and their files"""
    global recordings
    
    deleted_count = 0
    failed_deletes = []
    
    # Delete all physical files
    for rec in recordings:
        file_path = os.path.join(AUDIO_DIR, rec["filename"])
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                deleted_count += 1
                print(f"Deleted file: {file_path}")
            except OSError as e:
                print(f"Error deleting file {file_path}: {e}")
                failed_deletes.append(rec["filename"])
    
    # Clear the recordings list
    recordings_count = len(recordings)
    recordings.clear()
    
    if failed_deletes:
        return {
            "status": "partial_success",
            "message": f"Cleared {recordings_count} recordings from database, deleted {deleted_count} files",
            "failed_deletes": failed_deletes
        }
    else:
        return {
            "status": "success", 
            "message": f"Successfully cleared {recordings_count} recordings and deleted {deleted_count} files"
        }

@app.get("/api/transcription/{recording_id}")
def get_transcription(recording_id: str):
    for rec in recordings:
        if rec["id"] == recording_id:
            return {"transcription": rec.get("transcription", "Not available")}
    
    raise HTTPException(status_code=404, detail="Recording not found")