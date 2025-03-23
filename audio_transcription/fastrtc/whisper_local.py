import json
from pathlib import Path

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
    audio_to_bytes,
    get_twilio_turn_credentials,
)
from gradio.utils import get_space
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

cur_dir = Path(__file__).parent

load_dotenv()

# Path where the model will be stored
MODEL_PATH = Path("./models/whisper-large-v3")

# Function to load or download Whisper model
def get_whisper_pipeline():
    model_id = "openai/whisper-large-v3"
    
    # Create the model directory if it doesn't exist
    MODEL_PATH.mkdir(parents=True, exist_ok=True)
    
    # Check if model already exists locally
    if (MODEL_PATH / "pytorch_model.bin").exists() or list(MODEL_PATH.glob("*.safetensors")):
        print("Loading Whisper model from disk...")
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        torch_dtype = torch.float16 if device == "mps" else torch.float32
        
        # Load model and processor from local storage
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            MODEL_PATH,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True
        )
        processor = AutoProcessor.from_pretrained(MODEL_PATH)
    else:
        print("Downloading Whisper model (first run only)...")
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        torch_dtype = torch.float16 if device == "mps" else torch.float32
        
        # Download model and processor and save to disk
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True
        )
        processor = AutoProcessor.from_pretrained(model_id)
        
        # Save model and processor locally
        model.save_pretrained(MODEL_PATH)
        processor.save_pretrained(MODEL_PATH)
    
    # Move model to appropriate device
    model.to(device)
    
    # Create and return the pipeline
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        max_new_tokens=128,
        chunk_length_s=30,
        batch_size=16,
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