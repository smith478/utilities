#!/usr/bin/env python3
"""
Pre-download ASR models to avoid cold start delays.
Supports both IBM Granite and NVIDIA Parakeet models.
"""
import os
import time
import argparse

def download_granite_model(model_name="ibm-granite/granite-speech-3.3-8b", cache_dir=None):
    """
    Download and cache the Granite Speech model.
    
    Args:
        model_name: Hugging Face model name
        cache_dir: Custom cache directory (optional)
    """
    print(f"📥 Downloading Granite model: {model_name}")
    
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
        print(f"✅ Granite model downloaded successfully in {download_time:.2f} seconds")
        
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
        print(f"❌ Error downloading Granite model: {e}")
        return False

def download_parakeet_model(model_name="nvidia/parakeet-tdt-0.6b-v2", cache_dir=None):
    """
    Download and cache the Parakeet model using NeMo.
    
    Args:
        model_name: NeMo model name
        cache_dir: Custom cache directory (optional)
    """
    print(f"📥 Downloading Parakeet model: {model_name}")
    
    # Set cache directory - default to ./models if not specified
    if cache_dir is None:
        cache_dir = os.path.join(os.path.dirname(__file__), "models")
    
    # Ensure cache directory exists
    os.makedirs(cache_dir, exist_ok=True)
    
    # Set NeMo cache directory
    os.environ["NEMO_CACHE"] = cache_dir
    
    print(f"📁 Using cache directory: {cache_dir}")
    
    try:
        import nemo.collections.asr as nemo_asr
        
        start_time = time.time()
        
        # Download and instantiate the model
        print("📥 Downloading NeMo model...")
        asr_model = nemo_asr.models.ASRModel.from_pretrained(model_name=model_name)
        
        download_time = time.time() - start_time
        print(f"✅ Parakeet model downloaded successfully in {download_time:.2f} seconds")
        
        # Get model info
        print(f"📊 Model type: {type(asr_model).__name__}")
        print(f"📊 Model language: {getattr(asr_model, 'language', 'Unknown')}")
        
        # Show cache size
        nemo_cache_path = os.path.join(cache_dir, "NeMo")
        if os.path.exists(nemo_cache_path):
            cache_size = sum(
                os.path.getsize(os.path.join(dirpath, filename))
                for dirpath, dirnames, filenames in os.walk(nemo_cache_path)
                for filename in filenames
            )
            print(f"📦 Cache size: {cache_size / (1024**3):.2f} GB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error downloading Parakeet model: {e}")
        return False

def download_model(model_name, cache_dir=None):
    """
    Download model based on model name - automatically detects model type.
    
    Args:
        model_name: Model name (either Granite or Parakeet)
        cache_dir: Custom cache directory (optional)
    """
    if "granite" in model_name.lower():
        return download_granite_model(model_name, cache_dir)
    elif "parakeet" in model_name.lower():
        return download_parakeet_model(model_name, cache_dir)
    else:
        # Try Granite first, then Parakeet if it fails
        print(f"⚠️ Unknown model type, trying Granite format first...")
        if download_granite_model(model_name, cache_dir):
            return True
        print(f"⚠️ Granite format failed, trying Parakeet format...")
        return download_parakeet_model(model_name, cache_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download ASR models")
    parser.add_argument("--model", "-m", default="ibm-granite/granite-speech-3.3-8b", 
                       help="Model name (Granite or Parakeet)")
    parser.add_argument("--cache-dir", "-c", default=None, 
                       help="Custom cache directory (default: ./models)")
    parser.add_argument("--all", action="store_true",
                       help="Download all supported models")
    
    args = parser.parse_args()
    
    print("🚀 ASR Model Downloader")
    print("=" * 40)
    
    if args.all:
        # Download all supported models
        models = [
            "ibm-granite/granite-speech-3.3-8b",
            "nvidia/parakeet-tdt-0.6b-v2"
        ]
        
        success_count = 0
        for model in models:
            print(f"\n📥 Downloading {model}...")
            if download_model(model, args.cache_dir):
                success_count += 1
        
        print(f"\n🎉 Downloaded {success_count}/{len(models)} models successfully!")
    else:
        # Download single model
        success = download_model(args.model, args.cache_dir)
        
        if success:
            print("🎉 Download complete!")
        else:
            print("❌ Download failed!")
            exit(1)