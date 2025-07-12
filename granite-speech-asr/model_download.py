#!/usr/bin/env python3
"""
Pre-download Granite Speech model to avoid cold start delays.
"""
import os
import time
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
import torch

def download_model(model_name="ibm-granite/granite-speech-3.3-8b", cache_dir=None):
    """
    Download and cache the Granite Speech model.
    
    Args:
        model_name: Hugging Face model name
        cache_dir: Custom cache directory (optional)
    """
    print(f"📥 Downloading model: {model_name}")
    start_time = time.time()
    
    try:
        # Set cache directory if specified
        if cache_dir:
            os.environ["HF_HOME"] = cache_dir
            os.environ["TRANSFORMERS_CACHE"] = cache_dir
        
        # Download processor
        print("📥 Downloading processor...")
        processor = AutoProcessor.from_pretrained(model_name)
        
        # Download model
        print("📥 Downloading model...")
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        
        download_time = time.time() - start_time
        print(f"✅ Model downloaded successfully in {download_time:.2f} seconds")
        
        # Get model size info
        param_count = sum(p.numel() for p in model.parameters())
        print(f"📊 Model parameters: {param_count:,}")
        
        # Check if model is cached
        cache_path = processor.tokenizer.name_or_path
        print(f"📁 Model cached at: {cache_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download Granite Speech model")
    parser.add_argument("--model", "-m", default="ibm-granite/granite-speech-3.3-8b", 
                       help="Hugging Face model name")
    parser.add_argument("--cache-dir", "-c", default=None, 
                       help="Custom cache directory")
    
    args = parser.parse_args()
    
    print("🚀 Granite Speech Model Downloader")
    print("=" * 40)
    
    success = download_model(args.model, args.cache_dir)
    
    if success:
        print("🎉 Download complete!")
    else:
        print("❌ Download failed!")
        exit(1)