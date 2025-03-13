#!/bin/bash

# Improved check for working NVIDIA GPU setup
if command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null
then
    echo "NVIDIA GPU detected and accessible. Using GPU container."
    GPU_FLAG="--gpus all"
else
    echo "No working NVIDIA GPU setup detected. Using CPU container."
    GPU_FLAG=""
fi

# Create the HuggingFace cache directory if it doesn't exist
HF_CACHE_DIR="$HOME/.cache/huggingface"
mkdir -p $HF_CACHE_DIR

# Run the Docker container with interactive shell
# Mount the HuggingFace cache directory and the current directory
docker run $GPU_FLAG \
    --name phi4-audio-transcriber \
    -it --rm \
    -p 8501:8501 \
    -p 8888:8888 \
    -v $HF_CACHE_DIR:/root/.cache/huggingface \
    -v $(pwd):/phi4-audio-transcriber \
    phi4-audio-transcriber:latest