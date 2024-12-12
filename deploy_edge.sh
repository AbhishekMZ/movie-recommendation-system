#!/bin/bash

# Edge deployment script
echo "Starting edge deployment..."

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Please install Docker first."
    exit 1
fi

# Build optimized Docker image for edge devices
docker build -t movie-recommender-edge -f Dockerfile.edge .

# Start the containers with resource limits suitable for edge devices
docker-compose -f docker-compose.edge.yml up -d

echo "Edge deployment complete!"
echo "Access the application at http://localhost:8000"
