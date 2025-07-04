# Audio Transcription with Granite Speech

A comprehensive audio transcription toolkit using IBM's Granite Speech model with support for both Hugging Face Transformers and vLLM backends.

## Features

- **High-quality transcription** using IBM Granite Speech 3.3-8B model
- **Flexible recording** with manual or timed audio capture
- **Multiple backends** supporting both Transformers and vLLM
- **16kHz WAV output** optimized for speech recognition
- **Docker support** for containerized deployment
- **Cross-platform** compatibility (macOS, Linux)
- **Modern Python tooling** with uv for fast dependency management

## Quick Start

### 1. Clone and Setup

```bash
# Make setup script executable and run
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Install uv (if not already installed)
- Install system dependencies (portaudio, ffmpeg)
- Create a Python virtual environment with uv
- Install all required packages using uv sync
- Set up directory structure
- Test installations

### 2. Record Audio

```bash
# Record with manual stop (press Enter to stop)
uv run ./audio_recorder.py

# Record for 10 seconds
uv run ./audio_recorder.py -d 10

# Record with custom filename
uv run ./audio_recorder.py -f my_recording.wav

# Record to specific directory
uv run ./audio_recorder.py -o /path/to/recordings/
```

### 3. Transcribe Audio

```bash
# Using Transformers (recommended)
uv run ./transcriber_transformers.py recordings/recording_20241229_143022.wav

# Using vLLM (experimental, limited macOS support)
uv run ./transcriber_vllm.py recordings/recording_20241229_143022.wav

# With custom prompt
uv run ./transcriber_transformers.py -p "Please transcribe this meeting recording" recordings/my_file.wav

# Save output to file
uv run ./transcriber_transformers.py -o transcription.txt recordings/my_file.wav
```

## Manual Installation

### Prerequisites

**Install uv (if not already installed):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

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
sudo apt-get install portaudio19-dev ffmpeg
```

### Python Setup with uv

```bash
# Initialize project (if pyproject.toml doesn't exist)
uv init --name audio-transcription --python 3.11

# Install dependencies
uv sync

# Make scripts executable (Unix/macOS only)
chmod +x *.py
```

### Adding New Dependencies

```bash
# Add a new package
uv add package-name

# Add development dependencies
uv add --dev pytest black ruff

# Add with version constraints
uv add "torch>=2.0.0"
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

# Inside container, run transcription (uv environment is already active)
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
uv run ./audio_recorder.py --help

Options:
  -o, --output TEXT        Output directory for recordings [default: recordings/]
  -f, --filename TEXT      Specific filename [default: timestamp]
  -d, --duration INTEGER   Recording duration in seconds [default: manual stop]
  -sr, --sample-rate INTEGER  Sample rate [default: 16000]
```

### Transcription Options

```bash
uv run ./transcriber_transformers.py --help

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
uv run ./transcriber_transformers.py -m "openai/whisper-large-v3" recordings/audio.wav
```

## Development

### Working with uv

```bash
# Install development dependencies
uv sync --dev

# Run tests
uv run pytest

# Format code
uv run black .

# Lint code
uv run ruff check .

# Add new dependencies
uv add requests

# Update dependencies
uv sync --upgrade

# Show dependency tree
uv tree
```

### Virtual Environment Management

```bash
# Activate virtual environment manually
source .venv/bin/activate

# Or use uv run for one-off commands
uv run python script.py

# Check environment info
uv python list
```

## Troubleshooting

### Common Issues

**uv Not Found:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env

# Or use pip as fallback
pip install uv
```

**PyAudio Installation Failed (macOS):**
```bash
# Install system dependencies first
brew install portaudio

# Then retry
uv sync
```

**vLLM Not Working:**
- vLLM has limited support on CPU-only systems, especially macOS
- Use the Transformers version instead: `uv run transcriber_transformers.py`
- Ensure you have sufficient RAM (8GB+ recommended)

**Audio Recording Issues:**
```bash
# Test audio devices
uv run python -c "import pyaudio; p = pyaudio.PyAudio(); print('Audio devices:', p.get_device_count()); p.terminate()"

# Check microphone permissions (macOS)
# System Preferences > Security & Privacy > Privacy > Microphone
```

**Model Download Issues:**
```bash
# Clear cache and retry
rm -rf models/
HF_HOME=./models uv run python transcriber_transformers.py recordings/test.wav
```

**Lock File Issues:**
```bash
# Remove lock file and reinstall
rm uv.lock
uv sync
```

### Performance Tips

1. **CPU Optimization**: The Transformers version works better on CPU-only systems
2. **Memory Usage**: Close other applications for better performance
3. **Audio Quality**: Use 16kHz mono WAV files for best results
4. **Model Caching**: First run downloads ~13GB model - be patient!
5. **Fast Installation**: uv provides much faster dependency resolution and installation

## File Structure

```
audio-transcription/
├── audio_recorder.py          # Audio recording script
├── transcriber_transformers.py # Transformers-based transcription
├── transcriber_vllm.py        # vLLM-based transcription (experimental)
├── pyproject.toml             # Project configuration and dependencies
├── uv.lock                    # Lock file for reproducible installs
├── setup.sh                   # Automated setup script
├── Dockerfile                 # Container configuration
├── README.md                  # This file
├── recordings/                # Audio files directory
├── models/                    # Cached models directory
├── outputs/                   # Transcription outputs
└── .venv/                     # Python virtual environment (created by uv)
```

## Examples

### Complete Workflow

```bash
# 1. Record a 30-second audio clip
uv run ./audio_recorder.py -d 30 -f interview.wav

# 2. Transcribe with custom prompt
uv run ./transcriber_transformers.py \
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
  uv run ./transcriber_transformers.py "$file" -o "outputs/$(basename "$file" .wav).txt"
done
```