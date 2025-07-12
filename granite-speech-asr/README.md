# Granite Speech ASR Docker Setup

This guide will help you set up the Granite Speech ASR service using Docker on your Linux desktop with GPU support.

## Prerequisites

1. **NVIDIA GPU** with CUDA support
2. **Docker** installed
3. **NVIDIA Container Toolkit** installed
4. **Docker Compose** installed

### Install NVIDIA Container Toolkit

```bash
# Add NVIDIA package repositories
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Install nvidia-container-toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Restart Docker
sudo systemctl restart docker
```

## Quick Start

1. **Create project directory and copy files:**
   ```bash
   git clone repo
   ```

2. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

3. **Test the service:**
   ```bash
   # Check if service is running
   curl http://localhost:8000/health
   
   # Test transcription with an audio file
   curl -X POST "http://localhost:8000/transcribe" \
        -H "Content-Type: multipart/form-data" \
        -F "audio_file=@/path/to/your/audio.wav"
   ```

## Alternative: Manual Docker Commands

If you prefer not to use Docker Compose:

```bash
# Build the image
docker build -t granite-speech-asr .

# Run the container
docker run -it --gpus all \
  -p 8000:8000 \
  -v $(pwd)/recordings:/granite-speech-asr/recordings \
  -v $(pwd)/outputs:/granite-speech-asr/outputs \
  -v $(pwd)/models:/granite-speech-asr/models \
  granite-speech-asr

# Inside the container, download the model and start the server
python model_download.py
python api_server.py

# Run transcription on a wav file in /recordings
python transcriber_transformers.py recordings/recording_*.wav
```

## Usage Examples

### 1. Upload Audio File via API

```bash
curl -X POST "http://localhost:8000/transcribe" \
     -H "Content-Type: multipart/form-data" \
     -F "audio_file=@recording.wav" \
     -F "custom_prompt=Please transcribe this audio clearly"
```

### 2. Transcribe from URL

```bash
curl -X POST "http://localhost:8000/transcribe_url" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "audio_url=https://example.com/audio.wav"
```

### 3. Python Client Example

```python
import requests

# Upload file
with open("audio.wav", "rb") as f:
    files = {"audio_file": f}
    response = requests.post("http://localhost:8000/transcribe", files=files)
    result = response.json()
    
print(f"Transcription: {result['transcription']}")
print(f"Inference time: {result['inference_time']:.2f}s")
print(f"Real-time factor: {result['real_time_factor']:.2f}x")
```

## API Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `POST /transcribe` - Transcribe uploaded audio file
- `POST /transcribe_url` - Transcribe audio from URL

## File Structure

```
granite-speech-asr/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── transcriber_transformers.py    
├── audio_recorder.py              
├── api_server.py                  
├── model_download.py              
├── recordings/                    
├── outputs/                       
└── models/                        
```

## Troubleshooting

### GPU Not Detected

Check if NVIDIA runtime is available:
```bash
docker run --rm --gpus all nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04 nvidia-smi
```

### Model Download Issues

If the model fails to download, try:
```bash
# Enter the container
docker exec -it granite-speech-asr bash

# Download model manually
python model_download.py --model ibm-granite/granite-speech-3.3-8b
```

### Memory Issues

If you encounter CUDA out of memory errors:
1. Reduce batch size in the transcriber
2. Use smaller model variants
3. Enable mixed precision training

### Port Already in Use

If port 8000 is already in use:
```bash
# Change the port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

## Performance Tips

1. **Pre-download models** using the model_download.py script
2. **Use GPU** for faster inference (automatically detected)
3. **Persistent storage** for model cache to avoid re-downloading
4. **Single worker** configuration to avoid loading model multiple times

## Development

To run in development mode with auto-reload:

```bash
# Modify docker-compose.yml command:
command: >
  bash -c "
    python model_download.py &&
    uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
  "
```

## Security Notes

- The service runs without authentication (add auth for production)
- Temporary files are cleaned up automatically
- Consider rate limiting for production use
- Use HTTPS in production environments