#!/bin/bash

# Audio Transcription Setup Script
# This script sets up the environment for audio transcription experiments

echo "🚀 Setting up Audio Transcription Environment"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python packages
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Make scripts executable
echo "🔐 Making scripts executable..."
chmod +x audio_recorder.py
chmod +x transcriber_transformers.py
chmod +x transcriber_vllm.py

# Test PyAudio installation
echo "🧪 Testing PyAudio installation..."
python3 -c "import pyaudio; print('✅ PyAudio working')" 2>/dev/null || {
    echo -e "${RED}❌ PyAudio installation failed${NC}"
    echo -e "${YELLOW}💡 Try installing with: pip install --global-option='build_ext' --global-option='-I/opt/homebrew/include' --global-option='-L/opt/homebrew/lib' pyaudio${NC}"
}

# Test torch installation
echo "🧪 Testing PyTorch installation..."
python3 -c "import torch; print(f'✅ PyTorch {torch.__version__} working')" 2>/dev/null || {
    echo -e "${RED}❌ PyTorch installation failed${NC}"
}

# Test transformers installation
echo "🧪 Testing transformers installation..."
python3 -c "from transformers import AutoTokenizer; print('✅ Transformers working')" 2>/dev/null || {
    echo -e "${RED}❌ Transformers installation failed${NC}"
}

echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo "📋 Usage Examples:"
echo "=================="
echo ""
echo "1. Record audio (manual stop):"
echo "   ./audio_recorder.py"
echo ""
echo "2. Record audio (10 seconds):"
echo "   ./audio_recorder.py -d 10"
echo ""
echo "3. Record with custom filename:"
echo "   ./audio_recorder.py -f my_recording.wav"
echo ""
echo "4. Transcribe with transformers:"
echo "   ./transcriber_transformers.py recordings/recording_*.wav"
echo ""
echo "5. Transcribe with vLLM (if supported):"
echo "   ./transcriber_vllm.py recordings/recording_*.wav"
echo ""
echo "6. Docker usage:"
echo "   docker build -t audio-transcriber ."
echo "   docker run -it --rm -v \$(pwd)/recordings:/app/recordings audio-transcriber"
echo ""
echo -e "${YELLOW}💡 Note: vLLM may have limited support on CPU-only macOS systems.${NC}"
echo -e "${YELLOW}💡 For best results, use the transformers version first.${NC}"
echo ""
echo -e "${GREEN}Happy transcribing! 🎤✨${NC}"