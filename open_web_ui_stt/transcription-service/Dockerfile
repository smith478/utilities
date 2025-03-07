FROM python:3.10-slim

WORKDIR /app

# Install required packages
RUN pip install --no-cache-dir transformers torch torchaudio datasets soundfile huggingface_hub fastapi uvicorn python-multipart

# Copy application code
COPY transcription_server.py .

# Expose the port the app will run on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "transcription_server:app", "--host", "0.0.0.0", "--port", "8000"]