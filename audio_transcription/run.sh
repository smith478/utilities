#!/bin/bash

# Script to run the appropriate Docker container based on the environment

# Detect the platform
if [[ "$(uname -m)" == "arm64" ]]; then
    echo "Detected M1 Mac (arm64 architecture)"
    ENV="mac"
elif [[ "$(lspci | grep -i nvidia)" != "" ]]; then
    echo "Detected NVIDIA GPU"
    ENV="gpu"
else
    echo "No specific hardware detected, defaulting to CPU"
    ENV="cpu"
fi

# Ask for confirmation or allow override
read -p "Run for environment [$ENV]? (Enter to confirm, or type 'mac'/'gpu'/'cpu'): " response
if [[ ! -z "$response" ]]; then
    ENV=$response
fi

# Make sure Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build and run the appropriate container
case $ENV in
    mac|cpu)
        echo "Building and running for CPU/Mac environment..."
        docker-compose up phi4-cpu
        ;;
    gpu)
        echo "Building and running for GPU environment..."
        # Check for nvidia-smi
        if ! command -v nvidia-smi &> /dev/null; then
            echo "Warning: nvidia-smi not found. Make sure NVIDIA drivers are installed."
        fi
        docker-compose up phi4-gpu
        ;;
    *)
        echo "Invalid environment: $ENV"
        exit 1
        ;;
esac