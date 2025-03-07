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

## Transcription service

Usage Instructions:

Download Models:
```bash
# Download a model
python3 model-manager.py download openai/whisper-large-v3

# Download different model
python3 model-manager.py download facebook/wav2vec2-large-960h-lv60-self
```

List Local Models:
```bash
python3 model-manager.py list
```

Run with Docker:
```bash
# Start services using local models
docker-compose up -d
```

Key Features:
Models stored in `./models` directory (easy to manage/backup)
Avoids redundant downloads
Supports both local and remote models
Clear model organization
Automatic fallback to download if model missing
Version control friendly

Directory Structure After Use:
.
├── models/                              
├── transcription-service/               
│   ├── Dockerfile                       
│   └── transcription_server.py          
├── docker-compose.yml                   
├── model-manager.py                     
└── custom_stt_patch.py 

To Switch Models:
Stop services: `docker-compose stop transcription-service`
Update ASR_MODEL_ID in docker-compose.yml
Restart: `docker-compose up -d`