# Use NVIDIA CUDA base image
FROM nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04

WORKDIR /granite-speech-asr

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH="/granite-speech-asr"
ENV CUDA_VISIBLE_DEVICES=0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    python3.11-dev \
    git \
    ffmpeg \
    libsndfile1 \
    portaudio19-dev \
    libasound2-dev \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set Python alias and fix pip
RUN ln -sf /usr/bin/python3.11 /usr/bin/python
RUN ln -sf /usr/bin/python3.11 /usr/local/bin/python

# Upgrade pip and ensure it's using the correct Python
RUN python -m pip install --upgrade pip

# Install torch and related packages first (CUDA 12.4 compatible)
RUN python -m pip install torch>=2.0.0 torchvision>=0.15.0 torchaudio>=2.0.0 --index-url https://download.pytorch.org/whl/cu124

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY transcriber_transformers.py ./
COPY audio_recorder.py ./
COPY api_server.py ./
COPY model_download.py ./

# Create directories
RUN mkdir -p recordings models outputs

# Make scripts executable
RUN chmod +x transcriber_transformers.py audio_recorder.py

# Expose ports for API server
EXPOSE 8000

# Set default entrypoint
ENTRYPOINT ["/bin/bash"]