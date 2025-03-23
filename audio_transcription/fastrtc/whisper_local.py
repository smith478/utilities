import json
from pathlib import Path
import os

import gradio as gr
import numpy as np
import torch
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastrtc import (
    AdditionalOutputs,
    ReplyOnPause,
    Stream,
    get_twilio_turn_credentials,
)
from gradio.utils import get_space
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

# Load environment variables first (from .env file if present)
load_dotenv()

# Get cache directory from environment variable or use default
HF_CACHE_DIR = os.environ.get("HF_CACHE_DIR", os.path.expanduser("~/.cache/huggingface"))
os.environ["TRANSFORMERS_CACHE"] = os.path.join(HF_CACHE_DIR, "hub")

# Set device and model precision via environment variables
USE_MPS = os.environ.get("USE_MPS", "1") == "1"  # Default to using MPS if available
USE_FP16 = os.environ.get("USE_FP16", "1") == "1"  # Default to using FP16 precision

# Current directory reference
cur_dir = Path(__file__).parent

# Function to load Whisper model using configured cache
def get_whisper_pipeline():
    model_id = os.environ.get("WHISPER_MODEL", "openai/whisper-large-v3")
    
    # Select the appropriate device based on environment settings
    device = "mps" if USE_MPS and torch.backends.mps.is_available() else "cpu"
    torch_dtype = torch.float16 if USE_FP16 and device == "mps" else torch.float32
    
    print(f"Loading Whisper model '{model_id}' on {device} device with {torch_dtype} precision")
    print(f"Using cache directory: {os.environ['TRANSFORMERS_CACHE']}")
    
    # Load model and processor
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id,
        torch_dtype=torch_dtype,
        low_cpu_mem_usage=True,
        use_safetensors=True
    )
    processor = AutoProcessor.from_pretrained(model_id)
    
    # Move model to appropriate device
    model.to(device)
    
    # Get configurable pipeline parameters
    batch_size = int(os.environ.get("WHISPER_BATCH_SIZE", "16"))
    chunk_length = int(os.environ.get("WHISPER_CHUNK_LENGTH", "30"))
    max_new_tokens = int(os.environ.get("WHISPER_MAX_NEW_TOKENS", "128"))
    
    # Create and return the pipeline
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        max_new_tokens=max_new_tokens,
        chunk_length_s=chunk_length,
        batch_size=batch_size,
        return_timestamps=True
    )
    return pipe

# Initialize the Whisper pipeline
whisper_pipeline = get_whisper_pipeline()

async def transcribe(audio: tuple[int, np.ndarray]):
    # Convert audio to the format expected by the pipeline
    sample_rate, audio_data = audio
    
    # Ensure audio is mono (if stereo)
    if len(audio_data.shape) > 1 and audio_data.shape[1] > 1:
        audio_data = np.mean(audio_data, axis=1)
    
    # Process with Whisper
    result = whisper_pipeline({"sampling_rate": sample_rate, "raw": audio_data})
    
    # Format similar to Groq API response
    transcript = result.get("text", "")
    yield AdditionalOutputs(transcript)

stream = Stream(
    ReplyOnPause(transcribe),
    modality="audio",
    mode="send",
    additional_outputs=[
        gr.Textbox(label="Transcript"),
    ],
    additional_outputs_handler=lambda a, b: a + " " + b,
    rtc_configuration=get_twilio_turn_credentials() if get_space() else None,
    concurrency_limit=5 if get_space() else None,
    time_limit=90 if get_space() else None,
)

app = FastAPI()

stream.mount(app)


@app.get("/transcript")
def _(webrtc_id: str):
    async def output_stream():
        async for output in stream.output_stream(webrtc_id):
            transcript = output.args[0]
            yield f"event: output\ndata: {transcript}\n\n"

    return StreamingResponse(output_stream(), media_type="text/event-stream")


@app.get("/")
def index():
    rtc_config = get_twilio_turn_credentials() if get_space() else None
    html_content = (cur_dir / "index.html").read_text()
    html_content = html_content.replace("__RTC_CONFIGURATION__", json.dumps(rtc_config))
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import os

    if (mode := os.getenv("MODE")) == "UI":
        stream.ui.launch(server_port=7860, server_name="0.0.0.0")
    elif mode == "PHONE":
        stream.fastphone(host="0.0.0.0", port=7860)
    else:
        import uvicorn

        uvicorn.run(app, host="0.0.0.0", port=7860)