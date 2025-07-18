#!/usr/bin/env python3
"""
Audio transcription using Hugging Face Transformers with Granite Speech model.
Enhanced with persona-specific system prompts and post-processing for specialized transcription.
"""
import torch
import torchaudio
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
import click
import os
import time
import re

class GraniteTranscriber:
    def __init__(self, model_name="ibm-granite/granite-speech-3.3-8b", cache_dir="./models"):
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = None
        self.model = None
        self.tokenizer = None
        
        # Define persona-specific system prompts
        self.personas = {
            "general": {
                "name": "General Transcription",
                "system_prompt": "Knowledge Cutoff Date: April 2024.\nToday's Date: July 14, 2025.\nYou are Granite, developed by IBM. You are a helpful AI assistant specialized in accurate speech transcription."
            },
            "veterinary_radiologist": {
                "name": "Veterinary Radiologist",
                "system_prompt": """Knowledge Cutoff Date: April 2024.
Today's Date: July 14, 2025.
You are Granite, developed by IBM. You are a specialized AI assistant for veterinary radiology transcription.

You excel at transcribing veterinary diagnostic imaging reports with high accuracy. You must interpret dictated punctuation as symbols, not as words.

KEY INSTRUCTIONS:
- Replace the dictated word "period" with a "." symbol.
- Replace the dictated word "comma" with a "," symbol.
- Replace "new line" or "new paragraph" with a line break.
- Transcribe medical terminology, anatomical references, and findings with extreme precision.
- Maintain a professional, clear, and structured medical report format.

You understand and correctly spell terms related to:
- Veterinary anatomy and physiology.
- Radiological modalities (X-ray, CT, MRI, ultrasound).
- Common veterinary conditions and pathologies.

Your primary goal is to produce a clean, ready-to-use radiological report by converting dictated speech into a polished, correctly punctuated document."""
            },
            "human_radiologist": {
                "name": "Human Radiologist", 
                "system_prompt": """Knowledge Cutoff Date: April 2024.
Today's Date: July 14, 2025.
You are Granite, developed by IBM. You are a specialized AI assistant for human radiology transcription.

You excel at transcribing human diagnostic imaging reports with high accuracy. You understand:
- Human anatomy and physiology terminology
- Radiological imaging terminology (X-ray, CT, MRI, ultrasound, mammography)
- Medical report structure and DICOM standards
- Common human pathologies and findings
- Proper medical punctuation and sentence structure

When transcribing, focus on:
- Accurate medical terminology
- Proper anatomical references
- Clear, professional medical language
- Correct punctuation for medical reports
- Distinguishing between similar-sounding medical terms"""
            },
            "medical_general": {
                "name": "General Medical",
                "system_prompt": """Knowledge Cutoff Date: April 2024.
Today's Date: July 14, 2025.
You are Granite, developed by IBM. You are a specialized AI assistant for general medical transcription.

You excel at transcribing medical reports, notes, and documentation with high accuracy. You understand:
- General medical terminology
- Clinical documentation standards
- Proper medical punctuation and formatting
- Common medical procedures and findings
- Professional medical language conventions

When transcribing, focus on:
- Accurate medical terminology
- Professional medical language
- Correct punctuation for medical documentation
- Clear, concise medical communication"""
            }
        }
        
        print(f"🔧 Initializing transcriber on device: {self.device}")
        print(f"📁 Using cache directory: {self.cache_dir}")
        
    def list_personas(self):
        """List available personas."""
        print("\n📋 Available personas:")
        for key, persona in self.personas.items():
            print(f"   {key}: {persona['name']}")
        
    def load_model(self):
        """Load the model and processor."""
        if self.model is not None:
            return  # Already loaded
            
        print(f"📥 Loading model: {self.model_name}")
        start_time = time.time()
        
        try:
            os.environ["HF_HOME"] = self.cache_dir
            os.environ["TRANSFORMERS_CACHE"] = self.cache_dir
            
            self.processor = AutoProcessor.from_pretrained(
                self.model_name, cache_dir=self.cache_dir, local_files_only=True
            )
            self.tokenizer = self.processor.tokenizer
            self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir,
                local_files_only=True,
                torch_dtype=torch.float32 if self.device == "cpu" else torch.float16
            ).to(self.device)
            
            print("✅ Model loaded from local cache")
            
        except Exception as e:
            print(f"⚠️  Local model not found, downloading from Hugging Face: {e}")
            try:
                self.processor = AutoProcessor.from_pretrained(
                    self.model_name, cache_dir=self.cache_dir
                )
                self.tokenizer = self.processor.tokenizer
                self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                    self.model_name,
                    cache_dir=self.cache_dir,
                    torch_dtype=torch.float32 if self.device == "cpu" else torch.float16
                ).to(self.device)
                
                print("✅ Model downloaded and loaded from Hugging Face")
                
            except Exception as download_error:
                print(f"❌ Error loading/downloading model: {download_error}")
                raise
        
        load_time = time.time() - start_time
        print(f"✅ Model loaded successfully in {load_time:.2f} seconds")
    
    def load_audio(self, audio_path):
        """Load and validate audio file."""
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        print(f"🎵 Loading audio: {audio_path}")
        
        try:
            wav, sr = torchaudio.load(audio_path, normalize=True)
            
            if wav.shape[0] > 1:
                wav = wav.mean(dim=0, keepdim=True)
                print("📢 Converted stereo to mono")
            
            if sr != 16000:
                resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=16000)
                wav = resampler(wav)
                sr = 16000
                print(f"🔄 Resampled to 16kHz")
            
            print(f"   Sample rate: {sr}Hz")
            print(f"   Duration: {wav.shape[1] / sr:.2f} seconds")
            
            return wav, sr
            
        except Exception as e:
            print(f"❌ Error loading audio: {e}")
            raise

    def _format_report_text(self, text: str) -> str:
        """Applies post-processing rules to format the transcription."""
        print("⚙️ Applying post-processing rules...")
        
        # Define replacements for dictated punctuation
        replacements = {
            r"\s+period": ".",
            r"\s+comma": ",",
            r"\s+new paragraph": "\n\n",
            r"\s+new line": "\n",
        }
        
        # Apply replacements
        for word, symbol in replacements.items():
            text = re.sub(word, symbol, text, flags=re.IGNORECASE)

        # Capitalize the first letter of the entire text
        text = text.strip()
        if not text:
            return ""
        text = text[0].upper() + text[1:]
        
        # Capitalize the first letter after each period
        def capitalize_after_period(match):
            return match.group(1) + match.group(2).upper()

        text = re.sub(r'(\.\s+)([a-z])', capitalize_after_period, text)
        
        return text

    def transcribe(self, audio_path, persona="veterinary_radiologist", custom_prompt=None):
        """Transcribe audio file to text using specified persona."""
        self.load_model()
        
        if persona not in self.personas:
            print(f"⚠️  Unknown persona '{persona}', using 'general' instead")
            persona = "general"
        
        print(f"🎭 Using persona: {self.personas[persona]['name']}")
        
        wav, sr = self.load_audio(audio_path)
        
        assert wav.shape[0] == 1 and sr == 16000, f"Expected mono 16kHz audio, got shape {wav.shape} at {sr}Hz"
        
        print("🤖 Generating transcription...")
        start_time = time.time()
        
        try:
            prompt_text = custom_prompt or "Please transcribe this speech into written format with high accuracy."
            
            chat = [
                {"role": "system", "content": self.personas[persona]['system_prompt']},
                {"role": "user", "content": f"<|audio|>{prompt_text}"}
            ]
            
            text = self.tokenizer.apply_chat_template(
                chat, tokenize=False, add_generation_prompt=True
            )
            
            model_inputs = self.processor(
                text, wav, device=self.device, return_tensors="pt",
            ).to(self.device)
            
            with torch.no_grad():
                model_outputs = self.model.generate(
                    **model_inputs,
                    max_new_tokens=200, num_beams=4, do_sample=False, min_length=1,
                    top_p=1.0, repetition_penalty=1.0, length_penalty=1.0,
                    temperature=1.0, bos_token_id=self.tokenizer.bos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    pad_token_id=self.tokenizer.pad_token_id,
                )
            
            num_input_tokens = model_inputs["input_ids"].shape[-1]
            new_tokens = torch.unsqueeze(model_outputs[0, num_input_tokens:], dim=0)
            
            raw_transcription = self.tokenizer.batch_decode(
                new_tokens, add_special_tokens=False, skip_special_tokens=True
            )[0].strip()

            # Apply post-processing for a clean, final transcription
            final_transcription = self._format_report_text(raw_transcription)

            inference_time = time.time() - start_time
            audio_duration = wav.shape[1] / sr
            rtf = inference_time / audio_duration
            
            print(f"✅ Transcription completed in {inference_time:.2f} seconds (RTF: {rtf:.2f}x)")
            
            return final_transcription
            
        except Exception as e:
            print(f"❌ Error during transcription: {e}")
            raise

@click.command()
@click.argument('audio_path', type=click.Path(exists=True))
@click.option('--model', '-m', default="ibm-granite/granite-speech-3.3-8b", help='Hugging Face model name')
@click.option('--cache-dir', '-c', default="./models", help='Cache directory for models')
@click.option('--persona', '-r', default="veterinary_radiologist", help='Transcription persona')
@click.option('--list-personas', is_flag=True, help='List available personas and exit')
@click.option('--prompt', '-p', default=None, help='Custom transcription prompt')
@click.option('--output', '-o', default=None, help='Output file for transcription')
def main(audio_path, model, cache_dir, persona, list_personas, prompt, output):
    """Transcribe audio file using Granite Speech model with persona-specific prompts."""
    transcriber = GraniteTranscriber(model_name=model, cache_dir=cache_dir)
    
    if list_personas:
        transcriber.list_personas()
        return
    
    try:
        transcription = transcriber.transcribe(audio_path, persona=persona, custom_prompt=prompt)
        
        print("\n" + "="*50)
        print("📝 TRANSCRIPTION RESULT:")
        print("="*50)
        print(transcription)
        print("="*50)
        
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(transcription)
            print(f"💾 Transcription saved to: {output}")
        
    except Exception as e:
        print(f"❌ Transcription failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()