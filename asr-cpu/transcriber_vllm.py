#!/usr/bin/env python3
"""
Audio transcription using vLLM with Granite Speech model.
"""
import os
import time
import click
import torchaudio
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest

class GraniteVLLMTranscriber:
    def __init__(self, model_name="ibm-granite/granite-speech-3.3-8b"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        
        print(f"🔧 Initializing vLLM transcriber with model: {model_name}")
        
    def load_model(self):
        """Load the vLLM model and tokenizer."""
        if self.model is not None:
            return  # Already loaded
            
        print(f"📥 Loading vLLM model: {self.model_name}")
        start_time = time.time()
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Initialize vLLM model
            # Note: vLLM may not work on CPU-only macOS, but we'll try with optimized settings
            self.model = LLM(
                model=self.model_name,
                enable_lora=True,
                max_lora_rank=64,
                max_model_len=2048,  # Reduced for lower resource devices
                limit_mm_per_prompt={"audio": 1},
                # CPU-specific optimizations
                tensor_parallel_size=1,
                gpu_memory_utilization=0.0,  # Force CPU usage
                enforce_eager=True,  # Disable CUDA graphs for CPU
            )
            
            load_time = time.time() - start_time
            print(f"✅ vLLM model loaded successfully in {load_time:.2f} seconds")
            
        except Exception as e:
            print(f"❌ Error loading vLLM model: {e}")
            print("💡 Note: vLLM may not be fully supported on CPU-only macOS.")
            print("💡 Consider using the transformers version instead.")
            raise
    
    def get_prompt(self, question: str, has_audio: bool = True):
        """Build the input prompt to send to vLLM."""
        if has_audio:
            question = f"<|audio|>{question}"
        
        chat = [
            {
                "role": "user",
                "content": question
            }
        ]
        
        return self.tokenizer.apply_chat_template(chat, tokenize=False)
    
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
                print(f"🔄 Resampled to 16kHz")
            
            print(f"   Sample rate: {sr}Hz")
            print(f"   Duration: {wav.shape[1] / sr:.2f} seconds")
            print(f"   Shape: {wav.shape}")
            
            # Convert to format expected by vLLM
            # vLLM expects (audio_data, sample_rate) tuple
            audio_data = wav.squeeze(0).numpy()  # Remove channel dimension
            
            return (audio_data, sr)
            
        except Exception as e:
            print(f"❌ Error loading audio: {e}")
            raise
    
    def transcribe(self, audio_path, custom_prompt=None):
        """Transcribe audio file to text using vLLM."""
        # Load model if not already loaded
        self.load_model()
        
        # Load audio
        audio = self.load_audio(audio_path)
        
        print("🤖 Generating transcription with vLLM...")
        start_time = time.time()
        
        try:
            # Create prompt
            question = custom_prompt or "can you transcribe the speech into a written format?"
            prompt_with_audio = self.get_prompt(question=question, has_audio=True)
            
            # Prepare inputs
            inputs = {
                "prompt": prompt_with_audio,
                "multi_modal_data": {
                    "audio": audio,
                }
            }
            
            # Generate transcription
            outputs = self.model.generate(
                inputs,
                sampling_params=SamplingParams(
                    temperature=0.2,
                    max_tokens=200,
                    top_p=1.0,
                ),
                lora_request=[LoRARequest("speech", 1, self.model_name)]
            )
            
            transcription = outputs[0].outputs[0].text.strip()
            
            inference_time = time.time() - start_time
            audio_duration = len(audio[0]) / audio[1]  # length / sample_rate
            rtf = inference_time / audio_duration  # Real-time factor
            
            print(f"✅ Transcription completed in {inference_time:.2f} seconds")
            print(f"   Real-time factor: {rtf:.2f}x")
            
            return transcription
            
        except Exception as e:
            print(f"❌ Error during vLLM transcription: {e}")
            raise
    
    def test_text_only(self, question="What is the capital of Brazil?"):
        """Test the model with text-only input (no LoRA)."""
        self.load_model()
        
        print(f"🧪 Testing text-only generation: '{question}'")
        
        try:
            prompt = self.get_prompt(question=question, has_audio=False)
            
            outputs = self.model.generate(
                {"prompt": prompt},
                sampling_params=SamplingParams(
                    temperature=0.2,
                    max_tokens=12,
                ),
                # No LoRA for text-only
            )
            
            response = outputs[0].outputs[0].text.strip()
            print(f"✅ Text-only response: {response}")
            return response
            
        except Exception as e:
            print(f"❌ Error during text-only test: {e}")
            raise

@click.command()
@click.argument('audio_path', type=click.Path(exists=True))
@click.option('--model', '-m', default="ibm-granite/granite-speech-3.3-8b", help='Hugging Face model name')
@click.option('--prompt', '-p', default=None, help='Custom transcription prompt')
@click.option('--output', '-o', default=None, help='Output file for transcription')
@click.option('--test-text', is_flag=True, help='Run text-only test first')
def main(audio_path, model, prompt, output, test_text):
    """Transcribe audio file using vLLM with Granite Speech model."""
    
    try:
        # Initialize transcriber
        transcriber = GraniteVLLMTranscriber(model_name=model)
        
        # Optional text-only test
        if test_text:
            print("🧪 Running text-only test...")
            transcriber.test_text_only()
            print()
        
        # Perform transcription
        transcription = transcriber.transcribe(audio_path, custom_prompt=prompt)
        
        # Output results
        print("\n" + "="*50)
        print("📝 TRANSCRIPTION RESULT (vLLM):")
        print("="*50)
        print(transcription.upper())
        print("="*50)
        
        # Save to file if requested
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(transcription)
            print(f"💾 Transcription saved to: {output}")
        
    except Exception as e:
        print(f"❌ vLLM transcription failed: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   - vLLM has limited CPU support on macOS")
        print("   - Try using transcriber_transformers.py instead")
        print("   - Ensure you have sufficient RAM (8GB+ recommended)")
        exit(1)

if __name__ == "__main__":
    main()