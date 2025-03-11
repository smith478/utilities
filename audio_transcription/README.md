# Phi-4 Multimodal Audio Transcription Setup

This guide explains how to set up and use the Phi-4 multimodal model for audio transcription efficiently by sharing the model cache between your host system and Docker containers.

## Updated Approach

The key improvement in this setup is that the model is downloaded **once** to your host machine's Hugging Face cache directory (`~/.cache/huggingface`), and then Docker containers mount this directory to avoid re-downloading.

## Step 1: Download the Model to Host Machine

Before running Docker, download the model to your host machine:

```bash
# Make the script executable
chmod +x download_model.sh

# Run the download script
./download_model.sh
```

This will download the Phi-4 model (~10GB) to your host machine's default Hugging Face cache directory.

## Step 2: Run the Appropriate Docker Container

Use the provided run script to automatically detect your environment and start the appropriate Docker container:

```bash
# Make the script executable
chmod +x run.sh

# Run the script
./run.sh
```

The script will:
1. Detect if you're on an M1 Mac or have an NVIDIA GPU
2. Ask for confirmation or allow you to override
3. Start the appropriate container using docker-compose

## Manual Docker Compose Usage

If you prefer to run commands manually:

```bash
# For M1 MacBook
docker-compose up phi4-cpu

# For Linux with GPU
docker-compose up phi4-gpu
```

## Direct Python Installation (No Docker)

If you prefer to run without Docker:

1. Create a new directory and save all the provided files
2. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```bash
   streamlit run streamlit_app.py
   ```

## File Structure

```
project/
├── model_downloader.py        # Utility to download and cache the model
├── audio_transcriber.py       # Core transcription functionality
├── streamlit_app.py           # Web interface
├── Dockerfile.cpu             # Docker configuration for M1 MacBook
├── Dockerfile.gpu             # Docker configuration for Linux with GPU
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # Docker configuration with volume mounts
├── download_model.sh          # Script to download model to host
└── run.sh                     # Script to run the appropriate container
```

## How the Caching Works

1. The `download_model.sh` script downloads the model to your host's `~/.cache/huggingface` directory
2. The docker-compose.yml mounts this directory to `/root/.cache/huggingface` in the container
3. The application looks for the model in this cache directory first before downloading

## Important Notes

- The M1 version uses CPU/MPS mode, which will be slower but still functional
- The Linux version with 3090Ti uses CUDA for maximum performance
- The model is about 10GB in size, so ensure you have enough disk space
- If you update to a newer version of the model, you may need to clear the cache