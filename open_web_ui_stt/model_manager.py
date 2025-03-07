#!/usr/bin/env python3
import argparse
from huggingface_hub import snapshot_download
from pathlib import Path
import shutil
import logging
import os

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
        return True
        
    except Exception as e:
        logger.error(f"Failed to download {model_id}: {str(e)}")
        return False

def list_models():
    """List all locally available models"""
    if not MODEL_DIR.exists():
        logger.info("Models directory does not exist yet.")
        return
        
    models = [d.name for d in MODEL_DIR.glob("*") if d.is_dir()]
    
    if not models:
        print("\nNo models found in the local directory.")
        return
    
    print("\nAvailable models:")
    for model in models:
        size = get_directory_size(MODEL_DIR / model)
        print(f"- {model} ({format_size(size)})")

def get_directory_size(directory):
    """Get the total size of a directory in bytes"""
    total_size = 0
    for path in Path(directory).rglob('*'):
        if path.is_file():
            total_size += path.stat().st_size
    return total_size

def format_size(size_bytes):
    """Format bytes to a human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"

def remove_model(model_id: str):
    """Remove a model from the local models directory"""
    model_path = MODEL_DIR / model_id.replace("/", "_")
    
    if not model_path.exists():
        logger.error(f"Model {model_id} not found locally")
        return False
    
    try:
        shutil.rmtree(model_path)
        logger.info(f"Model {model_id} removed successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to remove {model_id}: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hugging Face Model Manager")
    subparsers = parser.add_subparsers(dest="command")
    
    # Create models directory if it doesn't exist
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    # Download command
    dl_parser = subparsers.add_parser("download", help="Download a model")
    dl_parser.add_argument("model_id", help="Hugging Face model ID")
    dl_parser.add_argument("--revision", default="main", help="Model revision")
    
    # List command
    subparsers.add_parser("list", help="List local models")
    
    # Remove command
    rm_parser = subparsers.add_parser("remove", help="Remove a model")
    rm_parser.add_argument("model_id", help="Model ID to remove")
    
    args = parser.parse_args()
    
    if args.command == "download":
        download_model(args.model_id, args.revision)
    elif args.command == "list":
        list_models()
    elif args.command == "remove":
        remove_model(args.model_id)
    else:
        parser.print_help()