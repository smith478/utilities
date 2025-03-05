import torch
from transformers import pipeline
from fastapi import FastAPI, WebSocket, HTTPException
import uvicorn
import numpy as np
import base64
import logging
import wave
import io
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("transcription-service")

app = FastAPI()

# Configuration
MODEL_ID = os.getenv("ASR_MODEL_ID", "openai/whisper-large-v3")
DEVICE = 0 if torch.cuda.is_available() else "cpu"
CHUNK_LENGTH = int(os.getenv("ASR_CHUNK_LENGTH", 5))
STRIDE_LENGTH = int(os.getenv("ASR_STRIDE_LENGTH", 1))
SAMPLE_RATE = 16000

logger.info(f"Initializing ASR model: {MODEL_ID}")

try:
    transcriber = pipeline(
        "automatic-speech-recognition",
        model=MODEL_ID,
        device=DEVICE,
        chunk_length_s=CHUNK_LENGTH,
        stride_length_s=STRIDE_LENGTH
    )
except Exception as e:
    logger.error(f"Failed to initialize model: {str(e)}")
    raise

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": MODEL_ID}

@app.websocket("/ws/transcribe")
async def websocket_transcription(websocket: WebSocket):
    await websocket.accept()
    logger.info("New WebSocket connection")
    
    audio_buffer = []
    try:
        while True:
            data = await websocket.receive_bytes()
            
            # Convert bytes to numpy array
            audio = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
            audio_buffer.append(audio)
            
            if len(audio_buffer) >= 3:  # Process every 3 chunks
                combined = np.concatenate(audio_buffer)
                result = transcriber(combined, sampling_rate=SAMPLE_RATE)
                await websocket.send_text(result["text"])
                audio_buffer = [audio_buffer[-1]]  # Keep last chunk for context
                
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close(code=1011)

@app.post("/transcribe")
async def batch_transcription(file: UploadFile = File(...)):
    try:
        # Read and convert audio file
        audio_bytes = await file.read()
        audio = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Process audio
        result = transcriber(audio, sampling_rate=SAMPLE_RATE)
        return {"text": result["text"]}
        
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Transcription failed")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)