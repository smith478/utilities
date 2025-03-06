#!/usr/bin/env python3
import argparse
from huggingface_hub import snapshot_download
from pathlib import Path
import shutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("model-manager")

MODEL_DIR = Path("./models").resolve()

def download_model(model_id: str, revision: str = "main"):
    """Download a model and store it in the local models directory"""
    try:
        logger.info(f"Downloading {model_id}...")
        
        # Create model-specific directory
        model_path = MODEL_DIR / model_id.replace("/", "_")
        model_path.mkdir(parents=True, exist_ok=True)
        
        # Download using huggingface_hub
        snapshot_download(
            repo_id=model_id,
            revision=revision,
            local_dir=model_path,
            local_dir_use_symlinks=False,
            resume_download=True
        )
        
        logger.info(f"Model saved to: {model_path}")
        
    except Exception as e:
        logger.error(f"Failed to download {model_id}: {str(e)}")
        raise

def list_models():
    """List all locally available models"""
    models = [d.name for d in MODEL_DIR.glob("*") if d.is_dir()]
    print("\nAvailable models:")
    print("\n".join(models) if models else "No models found")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hugging Face Model Manager")
    subparsers = parser.add_subparsers(dest="command")
    
    # Download command
    dl_parser = subparsers.add_parser("download", help="Download a model")
    dl_parser.add_argument("model_id", help="Hugging Face model ID")
    dl_parser.add_argument("--revision", default="main", help="Model revision")
    
    # List command
    subparsers.add_parser("list", help="List local models")
    
    args = parser.parse_args()
    
    if args.command == "download":
        download_model(args.model_id, args.revision)
    elif args.command == "list":
        list_models()
    else:
        parser.print_help()