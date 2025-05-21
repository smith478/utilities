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
import nemo.collections.asr as nemo_asr

app = FastAPI()

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

AUDIO_DIR = "audio_files"
os.makedirs(AUDIO_DIR, exist_ok=True)

recordings = []

# Initialize ASR model (NVIDIA NeMo Parakeet)
asr_model = None

def initialize_asr():
    global asr_model
    try:
        print("Initializing NVIDIA NeMo ASR model (nvidia/parakeet-tdt-0.6b-v2)... This may take a while on first run.")
        # Load the Parakeet model from NeMo
        asr_model = nemo_asr.models.ASRModel.from_pretrained(model_name="nvidia/parakeet-tdt-0.6b-v2")
        
        # Check for GPU and move model to GPU if available
        if torch.cuda.is_available():
            asr_model.to(torch.device("cuda"))
            print(f"ASR model loaded on CUDA device: {torch.cuda.get_device_name(0)}")
        else:
            print("ASR model loaded on CPU. CUDA not available or not configured correctly in the environment.")
            print("For optimal performance with Parakeet, ensure NVIDIA drivers, CUDA, and Docker GPU support are correctly set up.")
        
        print("NVIDIA NeMo ASR model initialized successfully.")
    except Exception as e:
        print(f"Error initializing NeMo ASR model: {e}")
        asr_model = None 


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(async_initialize_asr())

async def async_initialize_asr():
    await asyncio.to_thread(initialize_asr)

async def transcribe_audio(file_path: str) -> str:
    global asr_model 
    if asr_model is None:
        print("ASR model not yet initialized or initialization failed. Attempting to initialize now...")
        # Try to initialize synchronously if not already done, though ideally it's done at startup.
        # This is a fallback and might delay the first transcription request significantly.
        initialize_asr() 
        if asr_model is None:
            print("ASR model could not be initialized. Transcription failed.")
            raise RuntimeError("ASR model is not available for transcription.")
    
    print(f"Transcribing audio file: {file_path} using NVIDIA NeMo Parakeet...")
    try:
        # NeMo's transcribe method expects a list of file paths
        # It returns a list of ASRResult objects or just strings depending on configuration and version.
        transcription_results = await asyncio.to_thread(asr_model.transcribe, [file_path])
        
        if transcription_results and len(transcription_results) > 0:
            # The result for Parakeet should have a .text attribute if it's an ASRResult object.
            # If it's just a list of strings, then transcription_results[0] is the text.
            # Based on model card (output[0].text), it's likely an object.
            transcribed_text = transcription_results[0].text if hasattr(transcription_results[0], 'text') else transcription_results[0]
            print(f"Transcription successful. Text: {transcribed_text[:100]}...")
            return transcribed_text
        else:
            print("Transcription returned no results or an unexpected format.")
            return "Transcription failed or produced no output."
    except Exception as e:
        print(f"Error during transcription: {e}")
        # Optionally, re-raise or return a specific error message
        # For robustness, ensure asr_model is still valid or attempt re-initialization if appropriate
        return f"Transcription error: {str(e)}"


# --- Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI (NVIDIA Parakeet ASR Backend)!"}

@app.get("/api/items")
def get_items():
    return {"items": items}

@app.post("/api/items")
def add_item(item: Item):
    items.append({"name": item.name, "value": item.value})
    return {"status": "success", "items": items}

@app.post("/api/audio")
async def upload_audio(file: UploadFile = File(...), duration: Optional[float] = None):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    recording_id = f"rec_{int(time.time())}"
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ".wav"
    filename = f"{recording_id}{file_extension}"
    
    file_path = os.path.join(AUDIO_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    transcription = "Transcribing..." 
    
    recording = AudioRecording(
        id=recording_id,
        timestamp=timestamp,
        filename=filename,
        duration=duration,
        transcription=transcription
    )
    
    recordings.append(recording.dict())
    
    asyncio.create_task(update_transcription(recording_id, file_path))
    
    return {"status": "success", "recording": recording.dict()}

async def update_transcription(recording_id: str, file_path: str):
    try:
        transcription = await transcribe_audio(file_path)
        for rec in recordings:
            if rec["id"] == recording_id:
                rec["transcription"] = transcription
                print(f"Updated transcription for {recording_id}: {transcription[:100]}...")
                break
    except Exception as e:
        error_message = f"Transcription error: {str(e)}"
        print(f"Error updating transcription for {recording_id}: {e}")
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
                    media_type="audio/wav", # Assuming WAV, Parakeet also supports FLAC
                    filename=rec["filename"]
                )
    raise HTTPException(status_code=404, detail="Recording not found")

@app.delete("/api/audio/{recording_id}")
def delete_recording(recording_id: str):
    global recordings
    recording_to_delete = None
    for i, rec in enumerate(recordings):
        if rec["id"] == recording_id:
            recording_to_delete = recordings.pop(i)
            break
    
    if not recording_to_delete:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    file_path = os.path.join(AUDIO_DIR, recording_to_delete["filename"])
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Deleted file: {file_path}")
        except OSError as e:
            print(f"Error deleting file {file_path}: {e}")
    
    return {"status": "success", "message": f"Recording {recording_id} deleted"}

@app.delete("/api/audio")
def clear_all_recordings():
    global recordings
    deleted_count = 0
    failed_deletes = []
    
    for rec in recordings:
        file_path = os.path.join(AUDIO_DIR, rec["filename"])
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                deleted_count += 1
            except OSError as e:
                print(f"Error deleting file {file_path}: {e}")
                failed_deletes.append(rec["filename"])
    
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