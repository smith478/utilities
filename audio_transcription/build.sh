#!/bin/bash

# Build the Docker image
echo "Building Docker image for Phi-4 Audio Transcription project..."
docker build -t phi4-audio-transcriber:latest -f Dockerfile.gpu .

echo "Build complete!"
echo "To run the container, use: ./run.sh"