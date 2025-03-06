from huggingface_hub import snapshot_download

MODEL_PATH = Path(os.getenv("ASR_MODEL_PATH", "/models"))

try:
    # Check if model exists locally
    model_dir = MODEL_PATH / os.environ["ASR_MODEL_ID"].replace("/", "_")
    
    if not model_dir.exists():
        logger.info("Model not found locally, downloading...")
        model_dir = snapshot_download(
            repo_id=os.environ["ASR_MODEL_ID"],
            cache_dir=MODEL_PATH,
            local_dir=model_dir,
            local_dir_use_symlinks=False
        )
    
    transcriber = pipeline(
        "automatic-speech-recognition",
        model=model_dir,
        device=DEVICE,
        chunk_length_s=CHUNK_LENGTH,
        stride_length_s=STRIDE_LENGTH
    )
except Exception as e:
    logger.error(f"Model initialization failed: {str(e)}")
    raise