import streamlit as st
import os
import tempfile
from model_downloader import download_phi4_model
from audio_transcriber import transcribe_audio

st.set_page_config(page_title="Phi-4 Audio Transcription", page_icon="🎤")

# Determine cache directory based on environment
def get_cache_dir():
    """Get the appropriate Hugging Face cache directory, respecting environment variables"""
    # Check for environment variable (set in Docker)
    env_cache_dir = os.environ.get("HF_HOME") or os.environ.get("TRANSFORMERS_CACHE")
    if env_cache_dir:
        return env_cache_dir
    
    # Default cache directory
    return os.path.expanduser("~/.cache/huggingface")

@st.cache_resource
def load_model():
    """Load the Phi-4 model with caching to avoid reloading"""
    cache_dir = get_cache_dir()
    return download_phi4_model(local_cache_dir=cache_dir)

st.title("Phi-4 Audio Transcription")
st.write("Upload an audio file to transcribe it using Microsoft's Phi-4 multimodal model.")

# Display cache information
cache_dir = get_cache_dir()
st.info(f"Using Hugging Face cache: {cache_dir}")

# Model loading status
with st.spinner("Loading Phi-4 model... This might take a few minutes."):
    model, processor, generation_config = load_model()
    st.success("Model loaded successfully!")

# File uploader
audio_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "flac", "ogg", "m4a"])

if audio_file is not None:
    # Display audio player
    st.audio(audio_file)
    
    # Create a temporary file to save the uploaded audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio_file.name)[1]) as tmp_file:
        tmp_file.write(audio_file.getvalue())
        tmp_filepath = tmp_file.name
    
    # Transcribe button
    if st.button("Transcribe Audio"):
        with st.spinner("Transcribing..."):
            transcription = transcribe_audio(tmp_filepath, model, processor, generation_config)
            
            # Display transcription
            st.subheader("Transcription")
            st.write(transcription)
            
            # Add a download button for the transcription
            st.download_button(
                label="Download Transcription",
                data=transcription,
                file_name=f"{os.path.splitext(audio_file.name)[0]}_transcription.txt",
                mime="text/plain"
            )
        
        # Clean up temp file
        os.unlink(tmp_filepath)