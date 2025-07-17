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
    build-essential \
    libssl-dev \
    libffi-dev \
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
COPY main.py ./
COPY transcriber_transformers.py ./

# Create directories
RUN mkdir -p audio_files models outputs

# Create a non-root user for better security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /granite-speech-asr
USER appuser

# Expose port for FastAPI server
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Default command to run the FastAPI server
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]