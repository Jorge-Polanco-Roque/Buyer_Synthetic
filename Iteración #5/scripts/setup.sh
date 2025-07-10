#!/bin/bash

# ===============================================
# Buyer Synthetic™ - Setup Script
# ===============================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Buyer Synthetic™ - Docker Setup${NC}"
echo -e "${BLUE}=================================${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    echo -e "${BLUE}💡 Visit: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not available. Please install Docker Compose.${NC}"
    echo -e "${BLUE}💡 Visit: https://docs.docker.com/compose/install/${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is installed and running${NC}"

# Make scripts executable
echo -e "${YELLOW}🔧 Setting up scripts...${NC}"
chmod +x scripts/*.sh

# Setup environment file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 Setting up environment file...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ Created .env from .env.example${NC}"
        echo -e "${YELLOW}⚠️ Please edit .env file with your configuration:${NC}"
        echo -e "   - Add your OPENAI_API_KEY"
        echo -e "   - Configure other settings as needed"
    else
        echo -e "${RED}❌ .env.example not found${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating directories...${NC}"
mkdir -p data/{input,output,temp} logs

echo -e "${GREEN}✅ Directories created${NC}"

# Build the Docker image
echo -e "\n${YELLOW}🔨 Building Docker image...${NC}"
./scripts/build.sh

echo -e "\n${GREEN}🎉 Setup completed successfully!${NC}"
echo -e "\n${BLUE}💡 Next steps:${NC}"
echo -e "   1. Edit .env file with your API keys"
echo -e "   2. Run: ${YELLOW}./scripts/run.sh${NC}"
echo -e "   3. Or use: ${YELLOW}docker-compose up${NC}"
echo -e "   4. Access dashboard at: ${YELLOW}http://localhost:8505${NC}"

echo -e "\n${BLUE}🔧 Available commands:${NC}"
echo -e "   Build: ${YELLOW}./scripts/build.sh${NC}"
echo -e "   Run: ${YELLOW}./scripts/run.sh${NC}"
echo -e "   Stop: ${YELLOW}docker-compose down${NC}"
echo -e "   Logs: ${YELLOW}docker-compose logs -f${NC}"