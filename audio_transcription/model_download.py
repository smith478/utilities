import os
from transformers import AutoModelForCausalLM, AutoProcessor, GenerationConfig
import torch

def download_phi4_model(local_cache_dir=None, device="auto"):
    """
    Download and cache the Phi-4-multimodal-instruct model from Huggingface.
    
    Parameters:
    -----------
    local_cache_dir : str, optional
        Directory to store the model. If None, uses the default Huggingface cache.
    device : str, optional
        Device to load the model onto. Options: "auto", "cpu", "cuda", "mps".
        
    Returns:
    --------
    tuple
        (model, processor, generation_config) - The loaded model components
    """
    print(f"Downloading and caching Phi-4-multimodal-instruct model...")
    model_path = "microsoft/Phi-4-multimodal-instruct"
    
    # Determine device map
    if device == "auto":
        if torch.cuda.is_available():
            device_map = "cuda"
            print("Using CUDA GPU")
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            device_map = "mps"
            print("Using Apple MPS (Metal)")
        else:
            device_map = "cpu"
            print("Using CPU")
    else:
        device_map = device
        print(f"Using specified device: {device}")
    
    # Set appropriate attention implementation based on hardware
    if device_map == "cuda" and torch.cuda.get_device_capability()[0] >= 8:
        # Ampere or later GPU (3090, 4090, etc.)
        attn_implementation = "flash_attention_2"
    else:
        attn_implementation = "eager"
    
    # Load processor
    processor = AutoProcessor.from_pretrained(
        model_path, 
        trust_remote_code=True,
        cache_dir=local_cache_dir
    )
    
    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        device_map=device_map,
        torch_dtype="auto",
        trust_remote_code=True,
        _attn_implementation=attn_implementation,
        cache_dir=local_cache_dir
    )
    
    # Load generation config
    generation_config = GenerationConfig.from_pretrained(
        model_path,
        cache_dir=local_cache_dir
    )
    
    print(f"Model successfully loaded to {device_map}")
    return model, processor, generation_config