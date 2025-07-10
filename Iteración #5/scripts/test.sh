#!/bin/bash

# ===============================================
# Buyer Synthetic™ - Docker Test Script
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
CONTAINER_NAME="buyer-synthetic-test"

echo -e "${BLUE}🧪 Testing Buyer Synthetic™ Container${NC}"
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

# Stop and remove existing test container if it exists
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}🛑 Removing existing test container...${NC}"
    docker stop "${CONTAINER_NAME}" > /dev/null 2>&1 || true
    docker rm "${CONTAINER_NAME}" > /dev/null 2>&1 || true
fi

echo -e "\n${YELLOW}🧪 Running integration tests in container...${NC}"

# Run tests in container
docker run \
    --name "${CONTAINER_NAME}" \
    --env OPENAI_API_KEY="test-key" \
    --volume "$(pwd)/data:/app/data" \
    --workdir /app \
    "${IMAGE_NAME}:${TAG}" \
    python test_langgraph_integration.py

# Check test results
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Integration tests passed!${NC}"
    TEST_RESULT="PASSED"
else
    echo -e "\n${RED}❌ Integration tests failed!${NC}"
    TEST_RESULT="FAILED"
fi

# Cleanup test container
docker rm "${CONTAINER_NAME}" > /dev/null 2>&1 || true

# Additional health check test
echo -e "\n${YELLOW}🔍 Running health check test...${NC}"

# Start container for health check
docker run \
    --detach \
    --name "${CONTAINER_NAME}-health" \
    --publish "8507:8505" \
    --env OPENAI_API_KEY="test-key" \
    "${IMAGE_NAME}:${TAG}"

# Wait for container to start
sleep 15

# Check if container is healthy
HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' "${CONTAINER_NAME}-health" 2>/dev/null || echo "none")

if [ "$HEALTH_STATUS" = "healthy" ] || curl -f http://localhost:8507/_stcore/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
    HEALTH_RESULT="PASSED"
else
    echo -e "${RED}❌ Health check failed!${NC}"
    echo -e "${YELLOW}🔍 Container logs:${NC}"
    docker logs "${CONTAINER_NAME}-health"
    HEALTH_RESULT="FAILED"
fi

# Cleanup health check container
docker stop "${CONTAINER_NAME}-health" > /dev/null 2>&1 || true
docker rm "${CONTAINER_NAME}-health" > /dev/null 2>&1 || true

# Final results
echo -e "\n${BLUE}📊 Test Results Summary${NC}"
echo -e "${BLUE}======================${NC}"
echo -e "Integration Tests: $([ "$TEST_RESULT" = "PASSED" ] && echo -e "${GREEN}✅ PASSED${NC}" || echo -e "${RED}❌ FAILED${NC}")"
echo -e "Health Check: $([ "$HEALTH_RESULT" = "PASSED" ] && echo -e "${GREEN}✅ PASSED${NC}" || echo -e "${RED}❌ FAILED${NC}")"

if [ "$TEST_RESULT" = "PASSED" ] && [ "$HEALTH_RESULT" = "PASSED" ]; then
    echo -e "\n${GREEN}🎉 All tests passed! Container is ready for deployment.${NC}"
    exit 0
else
    echo -e "\n${RED}💥 Some tests failed. Please check the logs and fix issues.${NC}"
    exit 1
fi