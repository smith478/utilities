#!/bin/bash

# File: run_fastrtc.sh

# Improved check for working NVIDIA GPU setup
if command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null
then
    echo "NVIDIA GPU detected and accessible. Using GPU container."
    GPU_FLAG="--gpus all"
else
    echo "No working NVIDIA GPU detected. Using CPU container."
    GPU_FLAG=""
fi

# Get the host's IP address for network access
HOST_IP=$(hostname -I | awk '{print $1}')
echo "Your host IP is: $HOST_IP"
echo "After running fastrtc/whisper_remote.py you can access the application at http://$HOST_IP:7860"

# Create the HuggingFace cache directory if it doesn't exist
HF_CACHE_DIR="$HOME/.cache/huggingface"
mkdir -p $HF_CACHE_DIR

# Run the Docker container with the FastRTC application
docker run $GPU_FLAG \
    --name phi4-fastrtc \
    -it --rm \
    -p 7860:7860 \
    -v $HF_CACHE_DIR:/root/.cache/huggingface \
    -v $(pwd):/phi4-audio-transcriber \
    phi4-audio-transcriber:latest # \
    # python /phi4-audio-transcriber/fastrtc/whisper_remote.py