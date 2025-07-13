#!/usr/bin/env python3
"""
Pre-download Granite Speech model to avoid cold start delays.
"""
import os
import time
import argparse

def download_model(model_name="ibm-granite/granite-speech-3.3-8b", cache_dir=None):
    """
    Download and cache the Granite Speech model.
    
    Args:
        model_name: Hugging Face model name
        cache_dir: Custom cache directory (optional)
    """
    print(f"📥 Downloading model: {model_name}")
    
    # Set cache directory - default to ./models if not specified
    if cache_dir is None:
        cache_dir = os.path.join(os.path.dirname(__file__), "models")
    
    # Ensure cache directory exists
    os.makedirs(cache_dir, exist_ok=True)
    
    # Set environment variables for Hugging Face cache BEFORE importing transformers
    os.environ["HF_HOME"] = cache_dir
    os.environ["TRANSFORMERS_CACHE"] = cache_dir
    os.environ["HF_DATASETS_CACHE"] = cache_dir
    
    print(f"📁 Using cache directory: {cache_dir}")
    
    # Now import transformers after setting environment variables
    from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
    import torch
    
    start_time = time.time()
    
    try:
        # Download processor
        print("📥 Downloading processor...")
        processor = AutoProcessor.from_pretrained(model_name, cache_dir=cache_dir)
        
        # Download model
        print("📥 Downloading model...")
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        
        download_time = time.time() - start_time
        print(f"✅ Model downloaded successfully in {download_time:.2f} seconds")
        
        # Get model size info
        param_count = sum(p.numel() for p in model.parameters())
        print(f"📊 Model parameters: {param_count:,}")
        
        # Show actual cache location
        model_cache_path = os.path.join(cache_dir, "models--" + model_name.replace("/", "--"))
        print(f"📁 Model should be cached at: {model_cache_path}")
        if os.path.exists(model_cache_path):
            print(f"✅ Model cache directory exists")
            # Show cache size
            cache_size = sum(
                os.path.getsize(os.path.join(dirpath, filename))
                for dirpath, dirnames, filenames in os.walk(model_cache_path)
                for filename in filenames
            )
            print(f"📦 Cache size: {cache_size / (1024**3):.2f} GB")
        else:
            print(f"⚠️ Model cache directory not found - check cache configuration")
        
        return True
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download Granite Speech model")
    parser.add_argument("--model", "-m", default="ibm-granite/granite-speech-3.3-8b", 
                       help="Hugging Face model name")
    parser.add_argument("--cache-dir", "-c", default=None, 
                       help="Custom cache directory (default: ./models)")
    
    args = parser.parse_args()
    
    print("🚀 Granite Speech Model Downloader")
    print("=" * 40)
    
    success = download_model(args.model, args.cache_dir)
    
    if success:
        print("🎉 Download complete!")
    else:
        print("❌ Download failed!")
        exit(1)