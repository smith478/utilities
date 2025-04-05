# Use a lightweight Python base image compatible with M1
FROM python:3.10-slim

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m researcher

# Create directories for code and data
RUN mkdir -p /app /data
RUN chown -R researcher:researcher /app /data

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Switch to non-root user
USER researcher

# Set up volume for persistent data
VOLUME ["/data"]

# Expose API port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]