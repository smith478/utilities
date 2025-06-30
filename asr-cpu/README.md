# Audio Transcription with Granite Speech

A comprehensive audio transcription toolkit using IBM's Granite Speech model with support for both Hugging Face Transformers and vLLM backends.

## Features

- **High-quality transcription** using IBM Granite Speech 3.3-8B model
- **Flexible recording** with manual or timed audio capture
- **Multiple backends** supporting both Transformers and vLLM
- **16kHz WAV output** optimized for speech recognition
- **Docker support** for containerized deployment
- **Cross-platform** compatibility (macOS, Linux)

## Quick Start

### 1. Clone and Setup

```bash
# Make setup script executable and run
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Install system dependencies (portaudio, ffmpeg)
- Create a Python virtual environment
- Install all required packages
- Set up directory structure
- Test installations

### 2. Record Audio

```bash
# Record with manual stop (press Enter to stop)
./audio_recorder.py

# Record for 10 seconds
./audio_recorder.py -d 10

# Record with custom filename
./audio_recorder.py -f my_recording.wav

# Record to specific directory
./audio_recorder.py -o /path/to/recordings/
```

### 3. Transcribe Audio

```bash
# Using Transformers (recommended)
./transcriber_transformers.py recordings/recording_20241229_143022.wav

# Using vLLM (experimental, limited macOS support)
./transcriber_vllm.py recordings/recording_20241229_143022.wav

# With custom prompt
./transcriber_transformers.py -p "Please transcribe this meeting recording" recordings/my_file.wav

# Save output to file
./transcriber_transformers.py -o transcription.txt recordings/my_file.wav
```

## Manual Installation

### Prerequisites

**macOS:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install system dependencies
brew install portaudio ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install portaudio19-dev ffmpeg python3-venv python3-pip
```

### Python Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Make scripts executable (Unix/macOS only)
chmod +x *.py
```

## Docker Usage

### Build Image

```bash
docker build -t audio-transcriber .
```

### Run Container

```bash
# Interactive mode with volume mounting
docker run -it --rm \
  -v $(pwd)/recordings:/app/recordings \
  -v $(pwd)/outputs:/app/outputs \
  audio-transcriber

# Inside container, run transcription
python transcriber_transformers.py recordings/your_audio.wav
```

### Docker Compose (Optional)

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  transcriber:
    build: .
    volumes:
      - ./recordings:/app/recordings
      - ./outputs:/app/outputs
      - ./models:/app/models
    environment:
      - HF_HOME=/app/models
    stdin_open: true
    tty: true
```

Run with:
```bash
docker-compose up -d
docker-compose exec transcriber bash
```

## Configuration

### Audio Recording Options

```bash
./audio_recorder.py --help

Options:
  -o, --output TEXT        Output directory for recordings [default: recordings/]
  -f, --filename TEXT      Specific filename [default: timestamp]
  -d, --duration INTEGER   Recording duration in seconds [default: manual stop]
  -sr, --sample-rate INTEGER  Sample rate [default: 16000]
```

### Transcription Options

```bash
./transcriber_transformers.py --help

Options:
  -m, --model TEXT    Hugging Face model name [default: ibm-granite/granite-speech-3.3-8b]
  -p, --prompt TEXT   Custom transcription prompt
  -o, --output TEXT   Output file for transcription
```

## Models

### Default Model
- **ibm-granite/granite-speech-3.3-8b**: High-quality speech-to-text model
- Automatically downloaded on first use
- Cached in `models/` directory

### Custom Models
You can use other compatible speech models:

```bash
# Use a different model
./transcriber_transformers.py -m "openai/whisper-large-v3" recordings/audio.wav
```

## Troubleshooting

### Common Issues

**PyAudio Installation Failed (macOS):**
```bash
# Try with explicit paths
pip install --global-option='build_ext' \
  --global-option='-I/opt/homebrew/include' \
  --global-option='-L/opt/homebrew/lib' \
  pyaudio
```

**vLLM Not Working:**
- vLLM has limited support on CPU-only systems, especially macOS
- Use the Transformers version instead: `transcriber_transformers.py`
- Ensure you have sufficient RAM (8GB+ recommended)

**Audio Recording Issues:**
```bash
# Test audio devices
python3 -c "import pyaudio; p = pyaudio.PyAudio(); print('Audio devices:', p.get_device_count()); p.terminate()"

# Check microphone permissions (macOS)
# System Preferences > Security & Privacy > Privacy > Microphone
```

**Model Download Issues:**
```bash
# Clear cache and retry
rm -rf models/
HF_HOME=./models python transcriber_transformers.py recordings/test.wav
```

### Performance Tips

1. **CPU Optimization**: The Transformers version works better on CPU-only systems
2. **Memory Usage**: Close other applications for better performance
3. **Audio Quality**: Use 16kHz mono WAV files for best results
4. **Model Caching**: First run downloads ~13GB model - be patient!

## File Structure

```
audio-transcription/
├── audio_recorder.py          # Audio recording script
├── transcriber_transformers.py # Transformers-based transcription
├── transcriber_vllm.py        # vLLM-based transcription (experimental)
├── requirements.txt           # Python dependencies
├── setup.sh                  # Automated setup script
├── Dockerfile                # Container configuration
├── README.md                 # This file
├── recordings/               # Audio files directory
├── models/                   # Cached models directory
├── outputs/                  # Transcription outputs
└── venv/                    # Python virtual environment
```

## Examples

### Complete Workflow

```bash
# 1. Record a 30-second audio clip
./audio_recorder.py -d 30 -f interview.wav

# 2. Transcribe with custom prompt
./transcriber_transformers.py \
  -p "Please transcribe this interview, including speaker identification" \
  -o interview_transcript.txt \
  recordings/interview.wav

# 3. View results
cat interview_transcript.txt
```

### Batch Processing

```bash
# Transcribe all WAV files in recordings directory
for file in recordings/*.wav; do
  echo "Processing: $file"
  ./transcriber_transformers.py "$file" -o "outputs/$(basename "$file" .wav).txt"
done
```