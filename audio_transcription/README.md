# Phi-4 Multimodal Audio Transcription Setup

This guide explains how to set up and use the Phi-4 multimodal model for audio transcription with an interactive Docker workflow.

## Workflow Overview

This setup:
1. Uses a Docker container as an interactive development environment
2. Mounts your local project directory to the container
3. Shares the HuggingFace cache between host and container 
4. Allows running Streamlit or Jupyter from within the container

## Prerequisite: Install the NVIDIA Container Toolkit:

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings

# Add NVIDIA repo
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /etc/apt/keyrings/nvidia.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/etc/apt/keyrings/nvidia.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Update and install
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configure the Docker daemon
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```
Test the NVIDIA Container Toolkit:
```bash
sudo docker run --rm --gpus all nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04 nvidia-smi
```

## Step 1: Build the Docker Image

First, build the Docker image:

```bash
# Make the script executable
chmod +x build.sh

# Build the image
sudo ./build.sh
```

## Step 2: Run the Docker Container

Launch the interactive container:

```bash
# Make the script executable
chmod +x run.sh

# Run the container
sudo ./run.sh
```

This will:
- Start an interactive bash shell in the container
- Mount your current directory to /phi4-audio-transcriber in the container
- Mount your HuggingFace cache (~/.cache/huggingface) to the container
- Map ports for Streamlit (8501) and Jupyter (8888)

## Step 3: Download Model (Inside the Container)

Once inside the container, you can download the model:

```bash
python -c "from model_download import download_phi4_model; download_phi4_model()"
```

The model will be downloaded to the shared HuggingFace cache directory.

## Step 4: Run Applications (Inside the Container)

### Run Streamlit App
```bash
streamlit run streamlit_app.py
```
Access from host: http://localhost:8501

### Run Jupyter Lab
```bash
jupyter lab --ip 0.0.0.0 --no-browser --allow-root --NotebookApp.token=''
```
Access from host: http://localhost:8888

## File Structure

```
project/
├── model_download.py        # Utility to download and cache the model
├── audio_transcriber.py       # Core transcription functionality
├── streamlit_app.py           # Web interface
├── Dockerfile                 # Docker configuration
├── requirements.txt           # Python dependencies
├── build.sh                   # Script to build the Docker image
└── run.sh                     # Script to run the container
```

## How the Caching Works

1. The ~/.cache/huggingface directory on your host is mounted to /root/.cache/huggingface in the container
2. When you download the model inside the container, it's stored in the shared cache
3. Any other containers can use the same cache to avoid re-downloading
4. Your host applications can also use the same cached models

## Important Notes

- GPU acceleration works automatically if NVIDIA drivers and Docker GPU support are properly configured
- The model is about 10GB in size, so ensure you have enough disk space
- All changes to files in the mounted directory are reflected on your host system