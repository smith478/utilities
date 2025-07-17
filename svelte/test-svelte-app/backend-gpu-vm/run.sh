#!/bin/bash

# Run script for Granite Speech ASR Backend
set -e

echo "🚀 Starting Granite Speech ASR Backend..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if image exists
if ! docker image inspect granite-speech-asr:latest > /dev/null 2>&1; then
    echo "❌ Docker image not found. Please run ./build.sh first."
    exit 1
fi

# Create necessary directories if they don't exist
mkdir -p audio_files models outputs

# Stop existing container if running
if docker ps -q -f name=granite-speech-backend > /dev/null; then
    echo "🛑 Stopping existing container..."
    docker-compose down
fi

# Start the service
echo "🔄 Starting backend service..."
docker-compose up -d granite-speech-backend

# Wait for the service to be healthy
echo "⏳ Waiting for backend to be ready..."
timeout=120
counter=0

while [ $counter -lt $timeout ]; do
    if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is ready and healthy!"
        break
    fi
    
    if [ $counter -eq 0 ]; then
        echo -n "   Waiting"
    fi
    echo -n "."
    sleep 2
    counter=$((counter + 2))
done

if [ $counter -ge $timeout ]; then
    echo ""
    echo "❌ Backend failed to start within ${timeout} seconds"
    echo "📋 Checking logs..."
    docker-compose logs granite-speech-backend
    exit 1
fi

echo ""
echo "🎉 Backend is running successfully!"
echo "📡 API available at: http://localhost:8000"
echo "🏥 Health check: http://localhost:8000/health"
echo ""
echo "🔍 To check logs: docker-compose logs -f granite-speech-backend"
echo "🛑 To stop: docker-compose down"

# Get the container's IP address for network access
CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' granite-speech-backend)
HOST_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "🌐 Network access information:"
echo "   Local access: http://localhost:8000"
echo "   Network access: http://${HOST_IP}:8000"
echo "   Container IP: ${CONTAINER_IP}"
echo ""
echo "💡 For frontend development, use: http://${HOST_IP}:8000"