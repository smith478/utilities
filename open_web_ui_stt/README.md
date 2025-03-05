The goal here is to customize the speech-to-text (STT) or automatic speech recognition (ASR) model use in Open WebUI. 

Key Features:
- Real-time WebSocket transcription
- Batch processing endpoint
- Automatic GPU detection
- Model configuration via environment variables
- Health check endpoint
- Proper audio chunk handling
- Error handling and logging

Usage:
Access Open WebUI at http://localhost:3000
Go to Settings → Audio
Set STT Engine to "custom"
Save settings

To Change Models:
```yaml
# In docker-compose.yml
transcription-service:
  environment:
    - ASR_MODEL_ID=facebook/wav2vec2-large-960h-lv60-self  # Example model
```

```bash
docker-compose up -d --build transcription-service
```

Verification:

```bash
# Check service health
curl http://localhost:8000/health

# Test batch transcription
curl -X POST -F "file=@audio.wav" http://localhost:8000/transcribe
```