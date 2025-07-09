#!/bin/bash

# Audio Transcription Setup Script (using uv)
# This script sets up the environment for audio transcription experiments

echo "🚀 Setting up Audio Transcription Environment with uv"
echo "====================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}⚠️  uv not found. Installing uv...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
    
    # Check if installation was successful
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}❌ uv installation failed${NC}"
        echo "Please install uv manually: https://docs.astral.sh/uv/getting-started/installation/"
        exit 1
    fi
fi

echo -e "${GREEN}✅ uv is available${NC}"

# Check if running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${GREEN}✅ Detected macOS${NC}"
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo -e "${YELLOW}⚠️  Homebrew not found. Please install Homebrew first:${NC}"
        echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    
    # Install system dependencies
    echo "📦 Installing system dependencies..."
    brew install portaudio ffmpeg
    
else
    echo -e "${YELLOW}⚠️  This script is optimized for macOS. For Linux, install:${NC}"
    echo "   sudo apt-get install portaudio19-dev ffmpeg"
fi

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p recordings
mkdir -p models
mkdir -p outputs

# Initialize uv project if pyproject.toml doesn't exist
if [ ! -f "pyproject.toml" ]; then
    echo "🏗️  Initializing uv project..."
    uv init --name audio-transcription --python 3.11
fi

# Create virtual environment and install dependencies
echo "🐍 Creating virtual environment and installing dependencies with uv..."
uv sync

# Make scripts executable
echo "🔐 Making scripts executable..."
chmod +x audio_recorder.py
chmod +x transcriber_transformers.py
chmod +x transcriber_vllm.py

# Test installations using uv run
echo "🧪 Testing PyAudio installation..."
uv run python -c "import pyaudio; print('✅ PyAudio working')" 2>/dev/null || {
    echo -e "${RED}❌ PyAudio installation failed${NC}"
    echo -e "${YELLOW}💡 This might be due to missing system dependencies. On macOS, try:${NC}"
    echo "   brew install portaudio"
    echo -e "${YELLOW}💡 On Linux, try:${NC}"
    echo "   sudo apt-get install portaudio19-dev"
}

# Test torch installation
echo "🧪 Testing PyTorch installation..."
uv run python -c "import torch; print(f'✅ PyTorch {torch.__version__} working')" 2>/dev/null || {
    echo -e "${RED}❌ PyTorch installation failed${NC}"
}

# Test transformers installation
echo "🧪 Testing transformers installation..."
uv run python -c "from transformers import AutoTokenizer; print('✅ Transformers working')" 2>/dev/null || {
    echo -e "${RED}❌ Transformers installation failed${NC}"
}

echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo "📋 Usage Examples:"
echo "=================="
echo ""
echo "1. Record audio (manual stop):"
echo "   uv run ./audio_recorder.py"
echo ""
echo "2. Record audio (10 seconds):"
echo "   uv run ./audio_recorder.py -d 10"
echo ""
echo "3. Record with custom filename:"
echo "   uv run ./audio_recorder.py -f my_recording.wav"
echo ""
echo "4. Transcribe with transformers:"
echo "   uv run ./transcriber_transformers.py recordings/recording_*.wav"
echo ""
echo "5. Transcribe with vLLM (if supported):"
echo "   uv run ./transcriber_vllm.py recordings/recording_*.wav"
echo ""
echo "6. Activate virtual environment manually:"
echo "   source .venv/bin/activate"
echo ""
echo "7. Install additional packages:"
echo "   uv add package-name"
echo ""
echo "8. Install development dependencies:"
echo "   uv sync --dev"
echo ""
echo -e "${YELLOW}💡 Note: vLLM may have limited support on CPU-only macOS systems.${NC}"
echo -e "${YELLOW}💡 For best results, use the transformers version first.${NC}"
echo ""
echo -e "${GREEN}Happy transcribing! 🎤✨${NC}"