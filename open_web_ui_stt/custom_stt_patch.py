import os
import requests
import logging
from pathlib import Path
from open_webui.routers.audio import transcribe as original_transcribe

log = logging.getLogger(__name__)
CUSTOM_STT_ENDPOINT = os.getenv("CUSTOM_STT_ENDPOINT", "http://transcription-service:8000")

def custom_transcribe(request, file_path):
    if request.app.state.config.STT_ENGINE == "custom":
        try:
            log.info(f"Using custom STT service at {CUSTOM_STT_ENDPOINT}")
            
            with open(file_path, "rb") as audio_file:
                files = {"file": (Path(file_path).name, audio_file, "audio/wav")}
                response = requests.post(
                    f"{CUSTOM_STT_ENDPOINT}/transcribe",
                    files=files,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            log.error(f"Custom STT error: {str(e)}")
            raise RuntimeError(f"Custom STT service error: {str(e)}")
    else:
        return original_transcribe(request, file_path)

# Monkey patch the original function
from open_webui.routers import audio
audio.transcribe = custom_transcribe