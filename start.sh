#!/bin/bash

# Quick start script for Fish Feeder API

set -e

echo "🐟 Fish Feeder Servo Controller Setup"
echo "======================================"
echo ""

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "✅ .env file created. You can customize it if needed."
else
    echo "✅ .env file already exists."
fi

echo ""
echo "🚀 Building and starting the container..."
docker-compose up -d --build

echo ""
echo "⏳ Waiting for the API to start..."
sleep 3

echo ""
echo "✅ Fish Feeder API is running!"
echo ""
echo "📚 Access points:"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Health Check: http://localhost:8000/health"
echo "   - Root: http://localhost:8000/"
echo ""
echo "📊 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop the service:"
echo "   docker-compose down"
echo ""

