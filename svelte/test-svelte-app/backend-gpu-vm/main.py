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
import logging
from transcriber_transformers import GraniteTranscriber

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Changed to allow all origins for network access
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
    persona: Optional[str] = "veterinary_radiologist"

items = [
    {"name": "Item 1", "value": "Value 1"},
    {"name": "Item 2", "value": "Value 2"}
]

# Create directory for audio storage
AUDIO_DIR = "audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Store audio metadata
recordings = []

# Initialize Granite transcriber
transcriber = None

def initialize_transcriber():
    global transcriber
    try:
        transcriber = GraniteTranscriber(
            model_name="ibm-granite/granite-speech-3.3-8b",
            cache_dir="./models"
        )
        logger.info("Granite transcriber initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Granite transcriber: {e}")
        raise

# Initialize transcriber in the background
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up application...")
    # Run in a separate thread to avoid blocking startup
    asyncio.create_task(async_initialize_transcriber())

async def async_initialize_transcriber():
    try:
        # Run the CPU-bound operation in a thread pool
        await asyncio.to_thread(initialize_transcriber)
        logger.info("Transcriber initialization completed")
    except Exception as e:
        logger.error(f"Error during transcriber initialization: {e}")

async def transcribe_audio(file_path, persona="veterinary_radiologist"):
    if transcriber is None:
        logger.info("Transcriber not yet initialized, initializing now...")
        await asyncio.to_thread(initialize_transcriber)
    
    try:
        # Run transcription in a thread pool to avoid blocking
        result = await asyncio.to_thread(
            transcriber.transcribe, 
            file_path, 
            persona=persona
        )
        return result
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise

@app.get("/")
def read_root():
    return {"message": "Hello from Granite Speech FastAPI!", "status": "running"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "transcriber_ready": transcriber is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/personas")
def get_personas():
    """Get available transcription personas"""
    if transcriber is None:
        return {"personas": {}}
    return {"personas": transcriber.personas}

@app.get("/api/items")
def get_items():
    return {"items": items}

@app.post("/api/items")
def add_item(item: Item):
    items.append({"name": item.name, "value": item.value})
    return {"status": "success", "items": items}

@app.post("/api/audio")
async def upload_audio(
    file: UploadFile = File(...), 
    duration: Optional[float] = None,
    persona: Optional[str] = "veterinary_radiologist"
):
    # Generate timestamp and filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    recording_id = f"rec_{int(time.time())}"
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".wav"
    filename = f"{recording_id}{file_extension}"
    
    # Save the file
    file_path = os.path.join(AUDIO_DIR, filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Audio file saved: {file_path}")
    except Exception as e:
        logger.error(f"Error saving audio file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save audio file")
    
    # Transcribe the audio asynchronously
    transcription = "Transcribing..." # Initial state
    
    # Create recording object
    recording = AudioRecording(
        id=recording_id,
        timestamp=timestamp,
        filename=filename,
        duration=duration,
        transcription=transcription,
        persona=persona
    )
    
    # Add to recordings list
    recordings.append(recording.dict())
    
    # Start async transcription
    asyncio.create_task(update_transcription(recording_id, file_path, persona))
    
    return {"status": "success", "recording": recording.dict()}

async def update_transcription(recording_id, file_path, persona="veterinary_radiologist"):
    try:
        logger.info(f"Starting transcription for {recording_id} with persona {persona}")
        # Perform actual transcription
        transcription = await transcribe_audio(file_path, persona=persona)
        
        # Update recording with transcription
        for rec in recordings:
            if rec["id"] == recording_id:
                rec["transcription"] = transcription
                logger.info(f"Transcription completed for {recording_id}")
                break
    except Exception as e:
        # Handle errors
        error_message = f"Transcription error: {str(e)}"
        logger.error(error_message)
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
            logger.info(f"Deleted file: {file_path}")
        except OSError as e:
            logger.error(f"Error deleting file {file_path}: {e}")
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
                logger.info(f"Deleted file: {file_path}")
            except OSError as e:
                logger.error(f"Error deleting file {file_path}: {e}")
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

@app.post("/api/transcription/{recording_id}/retranscribe")
async def retranscribe(recording_id: str, persona: str = "veterinary_radiologist"):
    """Retranscribe a recording with a different persona"""
    # Find the recording
    recording = None
    for rec in recordings:
        if rec["id"] == recording_id:
            recording = rec
            break
    
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    # Update persona and reset transcription
    recording["persona"] = persona
    recording["transcription"] = "Retranscribing..."
    
    # Start transcription
    file_path = os.path.join(AUDIO_DIR, recording["filename"])
    asyncio.create_task(update_transcription(recording_id, file_path, persona))
    
    return {"status": "success", "message": "Retranscription started"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)