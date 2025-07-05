FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    ffmpeg \
    git \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy project configuration and required files for dependency resolution
COPY pyproject.toml ./
COPY README.md ./

# Copy lock file if it exists
COPY uv.lock* ./

# Install dependencies
RUN if [ -f "uv.lock" ]; then \
        uv sync --frozen --no-dev; \
    else \
        uv sync --no-dev; \
    fi

# Copy application files
COPY . .

# Create directories for audio files
RUN mkdir -p /app/recordings /app/models /app/outputs

# Set environment variables
ENV PYTHONPATH=/app
ENV HF_HOME=/app/models
ENV PATH="/app/.venv/bin:$PATH"

# Default command runs in the uv environment
CMD ["bash"]