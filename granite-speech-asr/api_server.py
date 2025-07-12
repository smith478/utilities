#!/usr/bin/env python3
"""
FastAPI server for Granite Speech ASR service.
"""
import os
import tempfile
import time
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel
import torch

# Import the transcriber from your existing code
from transcriber_transformers import GraniteTranscriber

app = FastAPI(
    title="Granite Speech ASR Service",
    description="Audio transcription service using IBM Granite Speech model",
    version="1.0.0"
)

# Global transcriber instance
transcriber = None

class TranscriptionResponse(BaseModel):
    transcription: str
    inference_time: float
    audio_duration: float
    real_time_factor: float
    model_name: str

@app.on_event("startup")
async def startup_event():
    """Initialize the transcriber on startup."""
    global transcriber
    print("🚀 Starting Granite Speech ASR Service")
    print(f"🔧 CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"🔧 GPU: {torch.cuda.get_device_name(0)}")
        print(f"🔧 CUDA version: {torch.version.cuda}")
    
    try:
        transcriber = GraniteTranscriber()
        # Pre-load the model to avoid cold start delays
        transcriber.load_model()
        print("✅ Granite Speech model loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "message": "Granite Speech ASR Service",
        "version": "1.0.0",
        "cuda_available": torch.cuda.is_available(),
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": transcriber is not None,
        "cuda_available": torch.cuda.is_available()
    }

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    custom_prompt: Optional[str] = Form(None)
):
    """
    Transcribe uploaded audio file.
    
    Args:
        audio_file: Audio file to transcribe (WAV, MP3, etc.)
        custom_prompt: Optional custom transcription prompt
    
    Returns:
        TranscriptionResponse with transcription and metadata
    """
    if transcriber is None:
        raise HTTPException(status_code=503, detail="Transcriber not initialized")
    
    # Validate file type
    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Expected audio file, got {audio_file.content_type}"
        )
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_path = temp_file.name
        
        try:
            # Write uploaded file to temporary location
            contents = await audio_file.read()
            temp_file.write(contents)
            temp_file.flush()
            
            # Perform transcription
            start_time = time.time()
            transcription = transcriber.transcribe(temp_path, custom_prompt=custom_prompt)
            inference_time = time.time() - start_time
            
            # Calculate audio duration for RTF
            import torchaudio
            wav, sr = torchaudio.load(temp_path)
            audio_duration = wav.shape[1] / sr
            rtf = inference_time / audio_duration
            
            return TranscriptionResponse(
                transcription=transcription,
                inference_time=inference_time,
                audio_duration=audio_duration,
                real_time_factor=rtf,
                model_name=transcriber.model_name
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

@app.post("/transcribe_url")
async def transcribe_from_url(
    audio_url: str = Form(...),
    custom_prompt: Optional[str] = Form(None)
):
    """
    Transcribe audio from URL.
    
    Args:
        audio_url: URL of the audio file to transcribe
        custom_prompt: Optional custom transcription prompt
    
    Returns:
        TranscriptionResponse with transcription and metadata
    """
    if transcriber is None:
        raise HTTPException(status_code=503, detail="Transcriber not initialized")
    
    try:
        import requests
        
        # Download audio file
        response = requests.get(audio_url, stream=True)
        response.raise_for_status()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_path = temp_file.name
            for chunk in response.iter_content(chunk_size=8192):
                temp_file.write(chunk)
            temp_file.flush()
            
            # Perform transcription
            start_time = time.time()
            transcription = transcriber.transcribe(temp_path, custom_prompt=custom_prompt)
            inference_time = time.time() - start_time
            
            # Calculate audio duration for RTF
            import torchaudio
            wav, sr = torchaudio.load(temp_path)
            audio_duration = wav.shape[1] / sr
            rtf = inference_time / audio_duration
            
            # Clean up
            os.unlink(temp_path)
            
            return TranscriptionResponse(
                transcription=transcription,
                inference_time=inference_time,
                audio_duration=audio_duration,
                real_time_factor=rtf,
                model_name=transcriber.model_name
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1  # Single worker to avoid model loading multiple times
    )