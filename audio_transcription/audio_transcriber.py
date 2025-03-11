import torch
import os
import io
import soundfile as sf
from transformers import AutoModelForCausalLM, AutoProcessor, GenerationConfig
from pathlib import Path

def transcribe_audio(audio_file_path, model=None, processor=None, generation_config=None):
    """
    Transcribe an audio file using Phi-4-multimodal-instruct.
    
    Parameters:
    -----------
    audio_file_path : str
        Path to the audio file to transcribe
    model : AutoModelForCausalLM, optional
        Pre-loaded model, if None will download
    processor : AutoProcessor, optional
        Pre-loaded processor, if None will download
    generation_config : GenerationConfig, optional
        Pre-loaded generation config, if None will download
        
    Returns:
    --------
    str
        The transcribed text
    """
    # Import the download function locally to avoid circular imports
    from model_downloader import download_phi4_model
    
    # Load model components if not provided
    if model is None or processor is None or generation_config is None:
        model, processor, generation_config = download_phi4_model()
    
    # Define prompt structure
    user_prompt = '<|user|>'
    assistant_prompt = '<|assistant|>'
    prompt_suffix = '<|end|>'
    
    # Create the transcription prompt
    transcription_prompt = "Transcribe the audio to text."
    prompt = f'{user_prompt}<|audio_1|>{transcription_prompt}{prompt_suffix}{assistant_prompt}'
    print(f'Processing audio file: {audio_file_path}')
    
    # Load audio file
    audio_path = Path(audio_file_path)
    audio, samplerate = sf.read(audio_path)
    
    # Process with the model
    device = next(model.parameters()).device
    inputs = processor(text=prompt, audios=[(audio, samplerate)], return_tensors='pt').to(device)
    
    # Generate transcription
    generate_ids = model.generate(
        **inputs,
        max_new_tokens=1000,
        generation_config=generation_config,
    )
    generate_ids = generate_ids[:, inputs['input_ids'].shape[1]:]
    transcription = processor.batch_decode(
        generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )[0]
    
    return transcription

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Transcribe audio using Phi-4 model")
    parser.add_argument("audio_file", help="Path to the audio file to transcribe")
    parser.add_argument("--device", default="auto", help="Device to use: 'cpu', 'cuda', 'mps', or 'auto'")
    args = parser.parse_args()
    
    # Import the download function
    from model_downloader import download_phi4_model
    
    # Download and load the model
    model, processor, generation_config = download_phi4_model(device=args.device)
    
    # Transcribe the audio
    transcription = transcribe_audio(args.audio_file, model, processor, generation_config)
    
    # Print the result
    print("\nTranscription:")
    print("--------------")
    print(transcription)