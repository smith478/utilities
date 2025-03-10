# Phi-4 Multimodal Audio Transcription Setup

This guide explains how to set up and use the Phi-4 multimodal model for audio transcription on both M1 MacBook Pro (CPU) and Linux with 3090Ti GPU.

## Files Overview

- `model_downloader.py`: Utility to download and cache the model
- `audio_transcriber.py`: Core transcription functionality
- `streamlit_app.py`: Web interface for audio upload and transcription
- `Dockerfile.cpu`: Docker configuration for M1 MacBook
- `Dockerfile.gpu`: Docker configuration for Linux with GPU
- `requirements.txt`: Python dependencies
- `docker-compose.yml`: Orchestration for both environments

## Setup Instructions

### Option 1: Direct Python Installation

1. Create a new directory and save all the provided files
2. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```bash
   streamlit run streamlit_app.py
   ```

### Option 2: Docker Setup for M1 MacBook

1. Create a new directory and save all the provided files
2. Rename `Dockerfile.cpu` to `Dockerfile`
3. Build and run the Docker container:
   ```bash
   docker build -t phi4-mac .
   docker run -p 8501:8501 -v $(pwd):/app phi4-mac
   ```
4. Access the application at http://localhost:8501

### Option 3: Docker Setup for Linux with 3090Ti GPU

1. Create a new directory and save all the provided files
2. Rename `Dockerfile.gpu` to `Dockerfile`
3. Ensure NVIDIA Docker runtime is installed:
   ```bash
   # Install NVIDIA Container Toolkit
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
   sudo systemctl restart docker
   ```
4. Build and run the Docker container:
   ```bash
   docker build -t phi4-gpu .
   docker run --gpus all -p 8501:8501 -v $(pwd):/app phi4-gpu
   ```
5. Access the application at http://localhost:8501

### Option 4: Using Docker Compose

For easier management of both environments:

```bash
# For M1 MacBook
docker-compose up phi4-cpu

# For Linux with GPU
docker-compose up phi4-gpu
```

## Jupyter Notebook Usage

If you prefer using a Jupyter notebook:

1. Install the requirements
2. Start Jupyter:
   ```bash
   jupyter notebook
   ```
3. Create a new notebook and import the utility functions:
   ```python
   from model_downloader import download_phi4_model
   from audio_transcriber import transcribe_audio
   
   # Load the model
   model, processor, generation_config = download_phi4_model()
   
   # Transcribe audio
   transcription = transcribe_audio("path/to/your/audio.mp3", model, processor, generation_config)
   print(transcription)
   ```

## Command Line Usage

You can also use the transcriber directly from the command line:

```bash
python audio_transcriber.py path/to/your/audio.mp3
```

## Important Notes

- First-time model download will take significant time (~10 GB)
- For optimal performance on the GPU, the container uses CUDA 12.1 with cuDNN 8
- The M1 version uses CPU mode, which will be slower but still functional
- Model cache is preserved across container restarts using Docker volumes