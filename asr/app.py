import nemo.collections.asr as nemo_asr
import gradio as gr
import soundfile as sf
import numpy as np
import os
import tempfile
import logging
import torch
import librosa # For audio resampling

# --- Configuration ---
MODEL_NAME = "nvidia/parakeet-tdt-0.6b-v2"
TARGET_SAMPLE_RATE = 16000  # Expected sample rate by the model
TEMP_AUDIO_DIR = "temp_audio" # Directory to store temporary audio files

# --- Setup Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Ensure Temporary Directory Exists ---
if not os.path.exists(TEMP_AUDIO_DIR):
    try:
        os.makedirs(TEMP_AUDIO_DIR)
        logger.info(f"Created temporary audio directory: {TEMP_AUDIO_DIR}")
    except OSError as e:
        logger.error(f"Could not create temporary audio directory {TEMP_AUDIO_DIR}: {e}")
        # Fallback to system's default temp directory if custom one fails
        TEMP_AUDIO_DIR = tempfile.gettempdir()
        logger.info(f"Using system default temporary directory: {TEMP_AUDIO_DIR}")


# --- GPU Check ---
if torch.cuda.is_available():
    GPU_NAME = torch.cuda.get_device_name(0)
    logger.info(f"GPU available: {GPU_NAME}")
else:
    GPU_NAME = "CPU (Transcription will be slow)"
    logger.warning("GPU not available. Transcription will be very slow.")

# --- Load ASR Model ---
asr_model = None
try:
    logger.info(f"Loading ASR model: {MODEL_NAME}...")
    # NeMo will automatically use GPU if available and PyTorch is set up correctly.
    # It will download the model from Hugging Face if not cached locally.
    asr_model = nemo_asr.models.ASRModel.from_pretrained(model_name=MODEL_NAME)
    logger.info("ASR model loaded successfully.")
except Exception as e:
    logger.error(f"Fatal: Error loading ASR model: {e}", exc_info=True)
    # The Gradio app will still launch but show an error message.

def format_timestamps_display(timestamps_dict):
    """Formats NeMo word timestamp output for readable display in Gradio."""
    if not timestamps_dict or 'word' not in timestamps_dict or not timestamps_dict['word']:
        return "No word timestamps available or transcription was empty."

    formatted_lines = []
    for item in timestamps_dict['word']:
        start = item['start']
        end = item['end']
        word = item['word']
        formatted_lines.append(f"[{start:>6.2f}s - {end:>6.2f}s]: {word}")
    return "\n".join(formatted_lines)

def transcribe_audio_input(audio_source_type, audio_input_data):
    """
    Handles audio transcription from microphone or file upload.
    audio_source_type: "microphone" or "upload"
    audio_input_data: For "microphone", it's (sample_rate, numpy_array).
                       For "upload", it's a Gradio File object (tempfile wrapper).
    """
    if asr_model is None:
        logger.error("transcribe_audio_input called but ASR model is not loaded.")
        return "ASR Model not loaded. Please check server logs.", ""

    filepath_to_transcribe = None
    # Path for a temporary file that might be created and should be deleted.
    temp_file_to_delete_path = None

    try:
        if audio_source_type == "microphone" and audio_input_data is not None:
            original_sr, audio_np_array = audio_input_data
            logger.info(f"Received audio from microphone. Original SR: {original_sr}, Shape: {audio_np_array.shape}")

            if audio_np_array is None or audio_np_array.size == 0:
                return "Empty audio received from microphone.", ""

            # Ensure mono
            if audio_np_array.ndim > 1 and audio_np_array.shape[1] > 1:
                audio_np_array = np.mean(audio_np_array, axis=1) # Average channels for mono
                logger.info("Converted stereo microphone input to mono.")

            # Create a temporary WAV file to store the processed audio
            temp_fd, temp_file_to_delete_path = tempfile.mkstemp(suffix=".wav", dir=TEMP_AUDIO_DIR)
            os.close(temp_fd) # Close descriptor, soundfile/librosa will handle the file by path

            # Write (potentially resampled) audio to the temp file
            current_audio_data = audio_np_array
            current_sample_rate = original_sr

            if original_sr != TARGET_SAMPLE_RATE:
                logger.info(f"Resampling microphone audio from {original_sr}Hz to {TARGET_SAMPLE_RATE}Hz...")
                try:
                    current_audio_data = librosa.resample(y=audio_np_array.astype(np.float32), orig_sr=original_sr, target_sr=TARGET_SAMPLE_RATE)
                    current_sample_rate = TARGET_SAMPLE_RATE
                    logger.info("Resampling successful.")
                except Exception as e:
                    logger.error(f"Error during librosa resampling: {e}", exc_info=True)
                    # Fallback to using original audio if resampling fails, NeMo might handle it.
                    # Or, return error: return f"Error resampling audio: {e}", ""

            sf.write(temp_file_to_delete_path, current_audio_data, current_sample_rate)
            filepath_to_transcribe = temp_file_to_delete_path
            logger.info(f"Processed microphone audio saved to temporary file: {filepath_to_transcribe}")


        elif audio_source_type == "upload" and audio_input_data is not None:
            uploaded_file_path = audio_input_data.name # .name gives the path to the temp file Gradio creates
            logger.info(f"Received audio file for upload: {uploaded_file_path}")

            # Check file extension (basic check)
            if not (uploaded_file_path.lower().endswith(".wav") or uploaded_file_path.lower().endswith(".flac")):
                return "Invalid file type. Please upload a .wav or .flac file.", ""

            # Create a local temporary copy to ensure correct processing (especially resampling if needed)
            # This also helps avoid issues with Gradio's temp file lifecycle if processing is long.
            temp_fd, temp_file_to_delete_path = tempfile.mkstemp(suffix=os.path.splitext(uploaded_file_path)[1], dir=TEMP_AUDIO_DIR)
            os.close(temp_fd)
            import shutil
            shutil.copy(uploaded_file_path, temp_file_to_delete_path)
            filepath_to_transcribe = temp_file_to_delete_path

            # Optional: Resample uploaded file if not already 16kHz.
            # This adds robustness but also processing time.
            try:
                y, sr = librosa.load(filepath_to_transcribe, sr=None, mono=False) # Load with original SR and channels
                if y.ndim > 1: # if stereo
                    y = librosa.to_mono(y)
                if sr != TARGET_SAMPLE_RATE:
                    logger.info(f"Resampling uploaded file from {sr}Hz to {TARGET_SAMPLE_RATE}Hz...")
                    y = librosa.resample(y=y, orig_sr=sr, target_sr=TARGET_SAMPLE_RATE)
                    sf.write(filepath_to_transcribe, y, TARGET_SAMPLE_RATE)
                    logger.info(f"Resampled uploaded file saved to: {filepath_to_transcribe}")
            except Exception as e:
                logger.error(f"Could not process/resample uploaded file {filepath_to_transcribe}: {e}", exc_info=True)
                return f"Error processing uploaded file: {e}", ""
        else:
            return "No audio input provided or source type is invalid.", "", ""

        if not filepath_to_transcribe:
             return "Audio file path could not be determined.", "", ""

        logger.info(f"Starting transcription for: {filepath_to_transcribe}")
        # Perform transcription
        # The model card indicates timestamps=True is default for word, segment, char.
        transcription_results = asr_model.transcribe([filepath_to_transcribe], timestamps=True)

        if not transcription_results or len(transcription_results) == 0:
            logger.warning(f"Transcription for {filepath_to_transcribe} yielded no results.")
            return "Transcription failed or produced no output.", ""

        first_result = transcription_results[0]
        transcribed_text = first_result.text
        word_timestamps_dict = first_result.timestamp  # This is the dictionary containing 'word', 'char', 'segment'

        formatted_timestamps = format_timestamps_display(word_timestamps_dict)

        if transcribed_text:
            logger.info(f"Transcription successful for {filepath_to_transcribe}. Text: '{transcribed_text[:100]}...'")
        else:
            logger.info(f"Transcription for {filepath_to_transcribe} resulted in empty text.")
            if not formatted_timestamps: # if text is empty, timestamps might also be empty
                formatted_timestamps = "Transcription was empty."


        return transcribed_text, formatted_timestamps

    except Exception as e:
        logger.error(f"Error during transcription process: {e}", exc_info=True)
        return f"An unexpected error occurred: {e}", ""
    finally:
        # Clean up the temporary file created for processing
        if temp_file_to_delete_path and os.path.exists(temp_file_to_delete_path):
            try:
                os.remove(temp_file_to_delete_path)
                logger.info(f"Deleted temporary file: {temp_file_to_delete_path}")
            except Exception as e:
                logger.error(f"Error deleting temporary file {temp_file_to_delete_path}: {e}", exc_info=True)


# --- Gradio Interface Definition ---
with gr.Blocks(title="NVIDIA Parakeet ASR Service", theme=gr.themes.Soft()) as demo:
    gr.Markdown(f"""
    # Speech-to-Text with NVIDIA Parakeet TDT 0.6b v2
    Transcribe English audio to text with punctuation, capitalization, and word-level timestamps.
    Powered by `nvidia/parakeet-tdt-0.6b-v2` using NVIDIA NeMo.
    Running on: **{GPU_NAME}**.
    """)

    if asr_model is None:
        gr.Markdown("## ⚠️ ASR MODEL FAILED TO LOAD! ⚠️")
        gr.Markdown("The application will not be able to transcribe audio. Please check the server logs for errors related to model loading.")

    with gr.Tabs():
        with gr.TabItem("Record Audio"):
            mic_input_audio = gr.Audio(sources=["microphone"], type="numpy", label="Record from Microphone",
                                       info=f"Audio will be resampled to {TARGET_SAMPLE_RATE}Hz mono if necessary.")
            mic_submit_button = gr.Button("Transcribe Microphone Audio", variant="primary", interactive=asr_model is not None)

        with gr.TabItem("Upload Audio File"):
            # Using gr.File for more control over the file object server-side
            upload_input_audio = gr.File(label="Upload Audio File",
                                         file_types=['.wav', '.flac', 'audio/wav', 'audio/flac'],
                                         info=f"Please upload a .wav or .flac file. It will be converted to {TARGET_SAMPLE_RATE}Hz mono if necessary.")
            upload_submit_button = gr.Button("Transcribe Uploaded File", variant="primary", interactive=asr_model is not None)

    with gr.Row():
        transcription_output_textbox = gr.Textbox(label="Transcription Result", lines=10, interactive=False, show_copy_button=True)

    with gr.Row():
        timestamp_output_textbox = gr.Textbox(label="Word Timestamps", lines=15, interactive=False, show_copy_button=True)

    # --- Event Handlers ---
    mic_submit_button.click(
        fn=lambda audio_data: transcribe_audio_input(audio_source_type="microphone", audio_input_data=audio_data),
        inputs=[mic_input_audio],
        outputs=[transcription_output_textbox, timestamp_output_textbox],
        api_name="transcribe_microphone" # For API access if needed
    )

    upload_submit_button.click(
        fn=lambda file_obj: transcribe_audio_input(audio_source_type="upload", audio_input_data=file_obj),
        inputs=[upload_input_audio],
        outputs=[transcription_output_textbox, timestamp_output_textbox],
        api_name="transcribe_upload" # For API access if needed
    )

    gr.Markdown("---")
    gr.Examples(
        examples=[
            # Provide a path to a sample .wav file if you include one in your Docker image or a downloadable URL
            # Example using a well-known sample (ensure it's accessible by the app if local)
            # [os.path.join(os.path.dirname(__file__), "sample1.wav")] # if you add sample1.wav next to app.py
        ],
        inputs=[upload_input_audio], # This tells Gradio which input component these examples are for
        outputs=[transcription_output_textbox, timestamp_output_textbox],
        fn=lambda file_obj: transcribe_audio_input(audio_source_type="upload", audio_input_data=file_obj),
        cache_examples=False, # Set to True if examples are static and processing is slow
        label="Example Audio Files (if provided)"
    )
    gr.Markdown(f"Model: `{MODEL_NAME}`. Ensure microphone permissions are granted in your browser.")


if __name__ == "__main__":
    if asr_model is None:
        logger.critical("ASR model could not be loaded. Gradio interface will be limited. Check logs for errors.")
        # The Gradio app will still launch and display the error message about the model.
    else:
        logger.info("ASR model loaded. Ready to start Gradio application.")

    logger.info("Starting Gradio application...")
    demo.launch(
        server_name="0.0.0.0",  # Makes it accessible outside the Docker container on your network
        server_port=7860,
        show_error=True # Shows Python errors in the browser (for debugging, disable in production)
    )