from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
import torch
from transformers import pipeline
from huggingface_hub import snapshot_download
import tempfile

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("transcription-service")

# Environment variables
MODEL_ID = os.getenv("ASR_MODEL_ID", "Systran/faster-whisper-tiny")
MODEL_PATH = Path(os.getenv("ASR_MODEL_PATH", "/models"))
CHUNK_LENGTH = float(os.getenv("ASR_CHUNK_LENGTH", "5"))
STRIDE_LENGTH = float(os.getenv("ASR_STRIDE_LENGTH", "1"))
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

app = FastAPI(title="Transcription Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the transcription model
@app.on_event("startup")
async def startup_event():
    global transcriber
    
    try:
        # Check if model exists locally
        model_dir = MODEL_PATH / MODEL_ID.replace("/", "_")
        
        if not model_dir.exists():
            logger.info(f"Model not found locally, downloading {MODEL_ID}...")
            model_dir = snapshot_download(
                repo_id=MODEL_ID,
                cache_dir=MODEL_PATH,
                local_dir=model_dir,
                local_dir_use_symlinks=False
            )
        else:
            logger.info(f"Using locally available model: {model_dir}")
        
        logger.info(f"Initializing transcriber with device: {DEVICE}")
        transcriber = pipeline(
            "automatic-speech-recognition",
            model=model_dir,
            device=DEVICE,
            chunk_length_s=CHUNK_LENGTH,
            stride_length_s=STRIDE_LENGTH
        )
        logger.info("Transcription model successfully loaded")
        
    except Exception as e:
        logger.error(f"Model initialization failed: {str(e)}")
        raise

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No audio file provided")
    
    try:
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file_path = temp_file.name
            content = await file.read()
            temp_file.write(content)
        
        logger.info(f"Processing audio file: {file.filename}")
        
        # Perform transcription
        result = transcriber(temp_file_path)
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        # Return the transcription result
        return {"text": result["text"] if isinstance(result, dict) else result[0]["text"]}
        
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": MODEL_ID}