#!/usr/bin/env python3
"""
Audio recorder script for creating 16kHz WAV files.
"""
import pyaudio
import wave
import click
import os
from datetime import datetime
import threading
import time

class AudioRecorder:
    def __init__(self, sample_rate=16000, channels=1, chunk_size=1024):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.format = pyaudio.paInt16
        self.audio = pyaudio.PyAudio()
        self.recording = False
        self.frames = []
        
    def start_recording(self):
        """Start recording audio."""
        self.frames = []
        self.recording = True
        
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        print("Recording started... Press Enter to stop")
        
        while self.recording:
            data = stream.read(self.chunk_size)
            self.frames.append(data)
        
        stream.stop_stream()
        stream.close()
        print("Recording stopped.")
    
    def stop_recording(self):
        """Stop recording audio."""
        self.recording = False
    
    def save_recording(self, filename):
        """Save recorded audio to WAV file."""
        if not self.frames:
            print("No audio recorded!")
            return False
            
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(self.frames))
        
        print(f"Audio saved to: {filename}")
        return True
    
    def record_fixed_duration(self, duration_seconds):
        """Record for a fixed duration."""
        self.frames = []
        
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        print(f"Recording for {duration_seconds} seconds...")
        
        for i in range(0, int(self.sample_rate / self.chunk_size * duration_seconds)):
            data = stream.read(self.chunk_size)
            self.frames.append(data)
        
        stream.stop_stream()
        stream.close()
        print("Recording completed.")
    
    def close(self):
        """Clean up audio resources."""
        self.audio.terminate()

def input_listener(recorder):
    """Listen for user input to stop recording."""
    input()
    recorder.stop_recording()

@click.command()
@click.option('--output', '-o', default='recordings/', help='Output directory for recordings')
@click.option('--filename', '-f', default=None, help='Specific filename (default: timestamp)')
@click.option('--duration', '-d', type=int, default=None, help='Recording duration in seconds (default: manual stop)')
@click.option('--sample-rate', '-sr', default=16000, help='Sample rate (default: 16kHz)')
def main(output, filename, duration, sample_rate):
    """Record audio and save as WAV file at 16kHz."""
    
    # Create recorder
    recorder = AudioRecorder(sample_rate=sample_rate)
    
    try:
        if duration:
            # Fixed duration recording
            recorder.record_fixed_duration(duration)
        else:
            # Manual stop recording
            # Start recording in a separate thread
            record_thread = threading.Thread(target=recorder.start_recording)
            record_thread.start()
            
            # Listen for user input to stop
            input_thread = threading.Thread(target=input_listener, args=(recorder,))
            input_thread.start()
            
            # Wait for recording to finish
            record_thread.join()
            input_thread.join()
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.wav"
        
        # Ensure .wav extension
        if not filename.endswith('.wav'):
            filename += '.wav'
        
        # Full path
        filepath = os.path.join(output, filename)
        
        # Save recording
        if recorder.save_recording(filepath):
            print(f"✅ Successfully saved: {filepath}")
            print(f"   Sample rate: {sample_rate}Hz")
            print(f"   Channels: 1 (mono)")
            print(f"   Duration: {len(recorder.frames) * recorder.chunk_size / sample_rate:.2f} seconds")
        
    except KeyboardInterrupt:
        print("\n🛑 Recording interrupted by user")
        recorder.stop_recording()
    
    except Exception as e:
        print(f"❌ Error during recording: {e}")
    
    finally:
        recorder.close()

if __name__ == "__main__":
    main()