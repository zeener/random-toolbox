#!/bin/bash

# Random Toolbox Docker Build Script
# Usage: ./scripts/docker-build.sh [production|development] [version]

set -e

# Default values
BUILD_TYPE=${1:-production}
VERSION=${2:-latest}
IMAGE_NAME="random-toolbox"
REGISTRY=${DOCKER_REGISTRY:-""}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Validate build type
if [[ "$BUILD_TYPE" != "production" && "$BUILD_TYPE" != "development" ]]; then
    error "Build type must be 'production' or 'development'"
fi

log "Building Random Toolbox Docker image..."
log "Build type: $BUILD_TYPE"
log "Version: $VERSION"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    error "Docker is not running. Please start Docker and try again."
fi

# Build the image
if [[ "$BUILD_TYPE" == "production" ]]; then
    log "Building production image with multi-stage Dockerfile..."
    docker build \
        --target production \
        --file Dockerfile.multi-stage \
        --tag "${IMAGE_NAME}:${VERSION}" \
        --tag "${IMAGE_NAME}:latest" \
        --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        --build-arg VCS_REF="$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
        .
else
    log "Building development image..."
    docker build \
        --target development \
        --file Dockerfile.multi-stage \
        --tag "${IMAGE_NAME}:${VERSION}-dev" \
        --tag "${IMAGE_NAME}:dev" \
        .
fi

# Test the build
log "Testing the built image..."
if [[ "$BUILD_TYPE" == "production" ]]; then
    # Test production image
    docker run --rm --detach --name "test-${IMAGE_NAME}" \
        --publish 5600:5600 \
        "${IMAGE_NAME}:${VERSION}" &
    
    CONTAINER_ID=$!
    sleep 5
    
    # Health check
    if curl -f http://localhost:5600/api/v1/health > /dev/null 2>&1; then
        log "✅ Health check passed"
    else
        warn "❌ Health check failed"
    fi
    
    # Stop test container
    docker stop "test-${IMAGE_NAME}" > /dev/null 2>&1 || true
else
    log "Development image built successfully - use docker-compose for testing"
fi

# Display image info
log "Build completed successfully!"
docker images | grep "${IMAGE_NAME}" | head -5

# Optional: Push to registry
if [[ -n "$REGISTRY" ]]; then
    log "Pushing to registry: $REGISTRY"
    if [[ "$BUILD_TYPE" == "production" ]]; then
        docker tag "${IMAGE_NAME}:${VERSION}" "${REGISTRY}/${IMAGE_NAME}:${VERSION}"
        docker push "${REGISTRY}/${IMAGE_NAME}:${VERSION}"
    else
        docker tag "${IMAGE_NAME}:${VERSION}-dev" "${REGISTRY}/${IMAGE_NAME}:${VERSION}-dev"
        docker push "${REGISTRY}/${IMAGE_NAME}:${VERSION}-dev"
    fi
fi

log "Docker build process completed! 🎉"
echo ""
echo -e "${BLUE}Usage examples:${NC}"
echo "  Production: docker run -p 5600:5600 ${IMAGE_NAME}:${VERSION}"
echo "  Development: docker-compose -f docker-compose.dev.yml up"
echo "  Testing: docker-compose -f docker-compose.dev.yml --profile test up random-toolbox-test"