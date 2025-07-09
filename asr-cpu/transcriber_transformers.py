#!/usr/bin/env python3
"""
Audio transcription using Hugging Face Transformers with Granite Speech model.
"""
import torch
import torchaudio
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
import click
import os
import time

class GraniteTranscriber:
    def __init__(self, model_name="ibm-granite/granite-speech-3.3-8b"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = None
        self.model = None
        self.tokenizer = None
        
        print(f"🔧 Initializing transcriber on device: {self.device}")
        
    def load_model(self):
        """Load the model and processor."""
        if self.model is not None:
            return  # Already loaded
            
        print(f"📥 Loading model: {self.model_name}")
        start_time = time.time()
        
        try:
            self.processor = AutoProcessor.from_pretrained(self.model_name)
            self.tokenizer = self.processor.tokenizer
            self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32 if self.device == "cpu" else torch.float16
            ).to(self.device)
            
            load_time = time.time() - start_time
            print(f"✅ Model loaded successfully in {load_time:.2f} seconds")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def load_audio(self, audio_path):
        """Load and validate audio file."""
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        print(f"🎵 Loading audio: {audio_path}")
        
        try:
            wav, sr = torchaudio.load(audio_path, normalize=True)
            
            # Ensure mono audio
            if wav.shape[0] > 1:
                wav = wav.mean(dim=0, keepdim=True)
                print("📢 Converted stereo to mono")
            
            # Resample to 16kHz if needed
            if sr != 16000:
                resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=16000)
                wav = resampler(wav)
                sr = 16000
                print(f"🔄 Resampled from {sr}Hz to 16kHz")
            
            print(f"   Sample rate: {sr}Hz")
            print(f"   Duration: {wav.shape[1] / sr:.2f} seconds")
            print(f"   Shape: {wav.shape}")
            
            return wav, sr
            
        except Exception as e:
            print(f"❌ Error loading audio: {e}")
            raise
    
    def transcribe(self, audio_path, custom_prompt=None):
        """Transcribe audio file to text."""
        # Load model if not already loaded
        self.load_model()
        
        # Load audio
        wav, sr = self.load_audio(audio_path)
        
        # Validate audio format
        assert wav.shape[0] == 1 and sr == 16000, f"Expected mono 16kHz audio, got shape {wav.shape} at {sr}Hz"
        
        print("🤖 Generating transcription...")
        start_time = time.time()
        
        try:
            # Create chat prompt
            prompt_text = custom_prompt or "can you transcribe the speech into a written format?"
            
            chat = [
                {
                    "role": "system",
                    "content": "Knowledge Cutoff Date: April 2024.\nToday's Date: April 9, 2025.\nYou are Granite, developed by IBM. You are a helpful AI assistant",
                },
                {
                    "role": "user",
                    "content": f"<|audio|>{prompt_text}",
                }
            ]
            
            text = self.tokenizer.apply_chat_template(
                chat, tokenize=False, add_generation_prompt=True
            )
            
            # Process audio and text
            model_inputs = self.processor(
                text,
                wav,
                device=self.device,
                return_tensors="pt",
            ).to(self.device)
            
            # Generate transcription
            with torch.no_grad():
                model_outputs = self.model.generate(
                    **model_inputs,
                    max_new_tokens=200,
                    num_beams=4,
                    do_sample=False,
                    min_length=1,
                    top_p=1.0,
                    repetition_penalty=1.0,
                    length_penalty=1.0,
                    temperature=1.0,
                    bos_token_id=self.tokenizer.bos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    pad_token_id=self.tokenizer.pad_token_id,
                )
            
            # Extract new tokens (excluding input)
            num_input_tokens = model_inputs["input_ids"].shape[-1]
            new_tokens = torch.unsqueeze(model_outputs[0, num_input_tokens:], dim=0)
            
            # Decode output
            output_text = self.tokenizer.batch_decode(
                new_tokens, add_special_tokens=False, skip_special_tokens=True
            )
            
            transcription = output_text[0].strip()
            
            inference_time = time.time() - start_time
            audio_duration = wav.shape[1] / sr
            rtf = inference_time / audio_duration  # Real-time factor
            
            print(f"✅ Transcription completed in {inference_time:.2f} seconds")
            print(f"   Real-time factor: {rtf:.2f}x")
            
            return transcription
            
        except Exception as e:
            print(f"❌ Error during transcription: {e}")
            raise

@click.command()
@click.argument('audio_path', type=click.Path(exists=True))
@click.option('--model', '-m', default="ibm-granite/granite-speech-3.3-8b", help='Hugging Face model name')
@click.option('--prompt', '-p', default=None, help='Custom transcription prompt')
@click.option('--output', '-o', default=None, help='Output file for transcription (default: print to stdout)')
def main(audio_path, model, prompt, output):
    """Transcribe audio file using Granite Speech model."""
    
    try:
        # Initialize transcriber
        transcriber = GraniteTranscriber(model_name=model)
        
        # Perform transcription
        transcription = transcriber.transcribe(audio_path, custom_prompt=prompt)
        
        # Output results
        print("\n" + "="*50)
        print("📝 TRANSCRIPTION RESULT:")
        print("="*50)
        print(transcription.upper())
        print("="*50)
        
        # Save to file if requested
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(transcription)
            print(f"💾 Transcription saved to: {output}")
        
    except Exception as e:
        print(f"❌ Transcription failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()