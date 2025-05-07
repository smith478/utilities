# Base image: NVIDIA CUDA for PyTorch
# Using CUDA 12.1.1 which is compatible with PyTorch 2.2+ and Ampere GPUs like RTX 3090Ti
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# For NVIDIA Docker runtime
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility
ENV NVIDIA_VISIBLE_DEVICES all

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3-pip \
    python3.10-venv \
    libsndfile1 \
    ffmpeg \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Make python3.10 the default python and pip
RUN ln -s /usr/bin/python3.10 /usr/bin/python3 && \
    ln -s /usr/bin/pip3 /usr/bin/pip

# Upgrade pip
RUN python3 -m pip install --no-cache-dir --upgrade pip

# Install PyTorch (version 2.2.1 with CUDA 12.1)
# Refer to https://pytorch.org/get-started/previous-versions/ for official commands
RUN python3 -m pip install --no-cache-dir \
    torch==2.2.1 \
    torchvision==0.17.1 \
    torchaudio==2.2.1 \
    --index-url https://download.pytorch.org/whl/cu121

# Install NVIDIA NeMo Toolkit (ASR dependencies)
# The model card implies NeMo 2.2; this typically refers to the model's training/compatibility,
# not necessarily a strict NeMo toolkit version number. Using a recent stable version is usually fine.
# For example, nemo_toolkit version 1.23.0 is a recent stable version.
RUN python3 -m pip install --no-cache-dir 'nemo_toolkit[asr]==1.23.0'

# Install Gradio and other Python dependencies for audio processing
RUN python3 -m pip install --no-cache-dir \
    gradio \
    soundfile \
    librosa \
    # Add any other specific dependencies your app.py might need

# Create app directory
WORKDIR /app

# Create a directory for temporary audio files and grant permissions
RUN mkdir /app/temp_audio && chmod -R 777 /app/temp_audio
ENV TEMP_AUDIO_DIR=/app/temp_audio

# Copy application code
COPY ./app.py /app/app.py
# If you have a requirements.txt, you could use it here:
# COPY ./requirements.txt /app/requirements.txt
# RUN python3 -m pip install --no-cache-dir -r /app/requirements.txt

# Expose the port Gradio will run on (default is 7860)
EXPOSE 7860

# Healthcheck (optional, but good practice)
# This checks if the Gradio server is responding on port 7860.
# Adjust the path if your Gradio app has a specific health endpoint or main page.
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:7860/ || exit 1
  
# Command to run the application
# Using `python3 -u` for unbuffered Python output, good for Docker logs
CMD ["python3", "-u", "app.py"]