#!/bin/bash

# Script to download the Phi-4 model inside the Docker container

echo "Downloading Phi-4 model to shared Hugging Face cache"

# Install any additional dependencies if needed
# pip install torch torchvision torchaudio transformers accelerate scipy soundfile pillow peft safetensors sentencepiece bitsandbytes backoff

# Run a simple script to download the model to the default cache
python - << EOF
from transformers import AutoProcessor, AutoModelForCausalLM, GenerationConfig
import os

# Set model path
model_path = "microsoft/Phi-4-multimodal-instruct"

# Ensure we know where the cache is
cache_dir = os.environ.get("HF_HOME") or os.path.expanduser("~/.cache/huggingface")
print(f"Using cache directory: {cache_dir}")

try:
    # Download processor
    print("\nDownloading processor...")
    processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)

    # Download model
    print("\nDownloading model (this may take a while)...")
    model = AutoModelForCausalLM.from_pretrained(
        model_path, 
        device_map="auto", 
        torch_dtype="auto", 
        trust_remote_code=True
    )

    # Download generation config
    print("\nDownloading generation config...")
    generation_config = GenerationConfig.from_pretrained(model_path)

    print("\nDownload complete!")
    print(f"Model files are cached at: {cache_dir}")
except Exception as e:
    print(f"\nError downloading model: {e}")
    print("\nIf you're seeing dependency errors, please install the missing packages and try again.")
EOF

echo "Model download complete."