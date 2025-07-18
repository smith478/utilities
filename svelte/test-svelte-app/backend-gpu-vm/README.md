# Granite Speech ASR Backend

A containerized FastAPI backend for real-time speech-to-text transcription using IBM's Granite Speech model.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- NVIDIA GPU with CUDA support
- nvidia-docker2 runtime

### Installation

1. **Clone/Setup the project:**
   ```bash
   # Ensure you have all required files:
   # - main.py
   # - transcriber_transformers.py
   # - requirements.txt
   # - Dockerfile
   # - docker-compose.yml
   ```

2. **Make scripts executable:**
   ```bash
   chmod +x build.sh run.sh
   ```

3. **Build the Docker image:**
   ```bash
   ./build.sh
   ```

4. **Run the backend:**
   ```bash
   ./run.sh
   ```

### Verification

After running, verify the backend is working:

```bash
# Check health
curl http://localhost:8000/health

# Check available personas
curl http://localhost:8000/api/personas

# Check if transcriber is ready
curl http://localhost:8000/health | jq '.transcriber_ready'
```

## 🏗️ Architecture

### Backend Structure
```
granite-speech-asr/
├── main.py                    # FastAPI application
├── transcriber_transformers.py # Granite Speech transcriber
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container definition
├── docker-compose.yml         # Service orchestration
├── build.sh                   # Build script
├── run.sh                     # Run script
├── audio_files/               # Audio file storage
├── models/                    # Model cache
└── outputs/                   # Output files
```

### API Endpoints

- `GET /health` - Health check and transcriber status
- `GET /api/personas` - Available transcription personas
- `POST /api/audio` - Upload audio for transcription
- `GET /api/audio` - List all recordings
- `GET /api/audio/{id}` - Get specific audio file
- `DELETE /api/audio/{id}` - Delete specific recording
- `DELETE /api/audio` - Clear all recordings
- `GET /api/transcription/{id}` - Get transcription result
- `POST /api/transcription/{id}/retranscribe` - Retranscribe with different persona

## 🌐 Network Configuration

### For Development Setup

The backend runs on the desktop while the frontend runs on a laptop (same network).

**Backend (Desktop):**
```bash
# After running ./run.sh, note the network IP shown
# Example: http://192.168.1.100:8000
```

**Frontend (Laptop):**
```bash
# Update your .env file
VITE_BACKEND_URL=http://192.168.1.100:8000

# Or set it when running
VITE_BACKEND_URL=http://192.168.1.100:8000 npm run dev -- --open
```

### Finding Your Network IP

```bash
# On Linux/macOS
hostname -I | awk '{print $1}'

# On Windows
ipconfig | findstr IPv4
```

## 🔧 Configuration

### Environment Variables

The backend supports these environment variables:

```bash
CUDA_VISIBLE_DEVICES=0        # GPU device to use
PYTHONPATH=/granite-speech-asr # Python path
```

### Available Personas

- `general` - General transcription
- `veterinary_radiologist` - Veterinary radiology reports
- `human_radiologist` - Human radiology reports
- `medical_general` - General medical transcription

## 📊 Monitoring

### Check Status
```bash
# Container status
docker compose ps

# Live logs
docker compose logs -f granite-speech-backend

# Resource usage
docker stats granite-speech-backend
```

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Test transcription (requires audio file)
curl -X POST -F "file=@test.wav" http://localhost:8000/api/audio
```

## 🛠️ Troubleshooting

### Common Issues

1. **NVIDIA Docker not available:**
   ```bash
   # Install nvidia-docker2
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   sudo apt-get update
   sudo apt-get install -y nvidia-docker2
   sudo systemctl restart docker
   ```

2. **Backend not starting:**
   ```bash
   # Check logs
   docker compose logs granite-speech-backend
   
   # Check GPU availability
   docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
   ```

3. **Model download issues:**
   ```bash
   # The model will download automatically on first run
   # Monitor progress in logs
   docker compose logs -f granite-speech-backend
   ```

4. **Frontend can't connect:**
   ```bash
   # Check if backend is accessible from laptop
   curl http://DESKTOP_IP:8000/health
   
   # Check firewall settings
   sudo ufw allow 8000
   ```

### Performance Tips

1. **Model caching:** The model is cached in `./models/` directory
2. **GPU memory:** Monitor GPU usage with `nvidia-smi`
3. **Audio format:** Use WAV files for best performance
4. **Concurrent requests:** The backend handles multiple requests asynchronously

## 🔄 Management Commands

```bash
# Start backend
./run.sh

# Stop backend
docker compose down

# Restart backend
docker compose restart granite-speech-backend

# Update image
./build.sh && docker compose up -d

# Clean up
docker compose down --volumes --rmi all
```

## 📈 Scaling

For production use, consider:

1. **Load balancing:** Use nginx for multiple backend instances
2. **Monitoring:** Add Prometheus/Grafana for metrics
3. **Logging:** Centralized logging with ELK stack
4. **Security:** Add authentication and HTTPS