#!/bin/bash

# Build script for Granite Speech ASR Backend
set -e

echo "🏗️  Building Granite Speech ASR Backend..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if NVIDIA Docker runtime is available
if ! docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi > /dev/null 2>&1; then
    echo "❌ NVIDIA Docker runtime not available. Please install nvidia-docker2."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p audio_files models outputs

# Build the Docker image
echo "🔨 Building Docker image..."
docker-compose build granite-speech-backend

# Verify the build
if [ $? -eq 0 ]; then
    echo "✅ Build completed successfully!"
    echo "🎉 You can now run the backend with: ./run.sh"
else
    echo "❌ Build failed!"
    exit 1
fi

# Show image info
echo "📊 Image information:"
docker images granite-speech-asr:latest