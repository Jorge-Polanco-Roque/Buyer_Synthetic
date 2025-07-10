#!/bin/bash

# ===============================================
# Buyer Synthetic™ - Docker Build Script
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
FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"

echo -e "${BLUE}🚀 Building Buyer Synthetic™ Docker Image${NC}"
echo -e "${BLUE}=============================================${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}❌ Dockerfile not found in current directory.${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Build Information:${NC}"
echo -e "   Image Name: ${FULL_IMAGE_NAME}"
echo -e "   Build Context: $(pwd)"
echo -e "   Docker Version: $(docker --version)"

# Build the image
echo -e "\n${YELLOW}🔨 Building Docker image...${NC}"
docker build \
    --tag "${FULL_IMAGE_NAME}" \
    --file Dockerfile \
    --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
    --build-arg VERSION="${TAG}" \
    .

# Check if build was successful
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Docker image built successfully!${NC}"
    
    # Show image information
    echo -e "\n${YELLOW}📊 Image Information:${NC}"
    docker images "${IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    
    echo -e "\n${GREEN}🎉 Build completed successfully!${NC}"
    echo -e "${BLUE}💡 Next steps:${NC}"
    echo -e "   1. Run: ${YELLOW}docker run -p 8505:8505 ${FULL_IMAGE_NAME}${NC}"
    echo -e "   2. Or use: ${YELLOW}./scripts/run.sh${NC}"
    echo -e "   3. Or use: ${YELLOW}docker-compose up${NC}"
else
    echo -e "\n${RED}❌ Docker build failed!${NC}"
    exit 1
fi