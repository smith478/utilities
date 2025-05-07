How to Use:

Prerequisites:

NVIDIA Drivers: Ensure you have the latest NVIDIA drivers installed on your Linux desktop that support CUDA 12.1 or newer.
NVIDIA Container Toolkit: Install the NVIDIA Container Toolkit to enable GPU access for Docker containers: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
Docker: Install Docker Engine.
Directory Structure:
Create a directory for your project, e.g., parakeet-asr/, and place app.py and Dockerfile inside it.

Build the Docker Image:
Open a terminal in the parakeet-asr/ directory and run:

Bash

docker build -t parakeet-asr-app .
This might take some time as it downloads the base image and installs all dependencies.

Run the Docker Container:
Once the image is built, run the container:

Bash

docker run --gpus all -p 7860:7860 --rm parakeet-asr-app
--gpus all: Crucial for enabling NVIDIA GPU access within the container.
-p 7860:7860: Maps port 7860 from the container to port 7860 on your host machine.
--rm: Automatically removes the container when it exits (useful for testing).
parakeet-asr-app: The name you tagged your image with.
Access the Application:
Open your web browser and navigate to http://localhost:7860.

Usage:

Record Audio: Go to the "Record Audio" tab, click the microphone button, record your speech, and then click "Transcribe Microphone Audio."
Upload File: Go to the "Upload Audio File" tab, upload a .wav or .flac file, and click "Transcribe Uploaded File."
Key Improvements and Considerations in these files:

Robust Audio Handling: The app.py now explicitly uses librosa for resampling audio from both microphone and file uploads to the required 16kHz mono format. This is critical for model accuracy.
Temporary File Management: Uses a dedicated temp_audio directory (created within the Docker image) and Python's tempfile module for safer handling of temporary audio files, with cleanup.
Error Handling: More detailed logging and error messages in app.py and Gradio UI, especially for model loading.
Dockerfile Optimizations:
Uses a specific CUDA 12.1 base image suitable for PyTorch 2.2+ and your Ampere GPU.
Pins versions for PyTorch and NeMo for better reproducibility. nemo_toolkit[asr]==1.23.0 is a recent stable version.
Includes libsndfile1 and ffmpeg which are common dependencies for audio processing.
Adds a basic HEALTHCHECK to the Dockerfile.
Gradio UI: Clearer instructions, interactive buttons disabled if the model fails to load, and uses gr.File for uploads.
Microphone Input: The type="numpy" for gr.Audio microphone input provides the sample rate and NumPy array, which is then explicitly processed.
Dependencies: librosa is added for robust resampling.