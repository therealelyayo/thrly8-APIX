#!/bin/bash

echo "Updating package lists..."
sudo apt-get update

echo "Installing Docker and Docker Compose..."
sudo apt-get install -y docker.io docker-compose

echo "Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

echo "Building and starting Docker containers..."
docker-compose build
docker-compose up -d

echo "Installation and deployment complete."
echo "Backend running on http://localhost:8000"
echo "Frontend running on http://localhost:3000"
