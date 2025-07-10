#!/bin/bash

# ===============================================
# Buyer Synthetic™ - Docker Run Script
# ===============================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="buyer-synthetic"
TAG=${1:-latest}
CONTAINER_NAME="buyer-synthetic-app"
PORT=${2:-8505}

echo -e "${BLUE}🚀 Running Buyer Synthetic™ Container${NC}"
echo -e "${BLUE}====================================${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if image exists
if ! docker image inspect "${IMAGE_NAME}:${TAG}" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️ Image ${IMAGE_NAME}:${TAG} not found. Building it first...${NC}"
    ./scripts/build.sh "${TAG}"
fi

# Stop and remove existing container if it exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}🛑 Stopping existing container...${NC}"
    docker stop "${CONTAINER_NAME}" > /dev/null 2>&1 || true
    docker rm "${CONTAINER_NAME}" > /dev/null 2>&1 || true
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️ .env file not found. Creating from .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}📝 Please edit .env file with your API keys and configuration.${NC}"
    else
        echo -e "${RED}❌ .env.example file not found. Please create .env manually.${NC}"
        exit 1
    fi
fi

# Create necessary directories
mkdir -p data/{input,output,temp} logs

echo -e "\n${YELLOW}📋 Container Information:${NC}"
echo -e "   Container Name: ${CONTAINER_NAME}"
echo -e "   Image: ${IMAGE_NAME}:${TAG}"
echo -e "   Port: ${PORT}"
echo -e "   Dashboard URL: http://localhost:${PORT}"

# Run the container
echo -e "\n${YELLOW}🐳 Starting container...${NC}"
docker run \
    --detach \
    --name "${CONTAINER_NAME}" \
    --publish "${PORT}:8505" \
    --env-file .env \
    --volume "$(pwd)/data:/app/data" \
    --volume "$(pwd)/logs:/app/logs" \
    --restart unless-stopped \
    "${IMAGE_NAME}:${TAG}"

# Wait a moment for container to start
sleep 5

# Check if container is running
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "\n${GREEN}✅ Container started successfully!${NC}"
    echo -e "\n${GREEN}🎉 Buyer Synthetic™ is now running!${NC}"
    echo -e "${BLUE}💡 Access the dashboard at: ${YELLOW}http://localhost:${PORT}${NC}"
    echo -e "\n${BLUE}🔧 Useful commands:${NC}"
    echo -e "   View logs: ${YELLOW}docker logs -f ${CONTAINER_NAME}${NC}"
    echo -e "   Stop container: ${YELLOW}docker stop ${CONTAINER_NAME}${NC}"
    echo -e "   Remove container: ${YELLOW}docker rm ${CONTAINER_NAME}${NC}"
    echo -e "   Container shell: ${YELLOW}docker exec -it ${CONTAINER_NAME} bash${NC}"
else
    echo -e "\n${RED}❌ Container failed to start!${NC}"
    echo -e "${YELLOW}🔍 Checking logs...${NC}"
    docker logs "${CONTAINER_NAME}"
    exit 1
fi