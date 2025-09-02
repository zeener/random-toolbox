#!/bin/bash

# Random Toolbox API - INT Environment Startup Script
# This script starts the integration API environment using Docker on localhost:8002

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INT_PORT=8002
CONTAINER_NAME="random-toolbox-api"
NETWORK_NAME="random-toolbox-network"
LOCKFILE="/tmp/random-toolbox-api-int.lock"

echo -e "${BLUE}🐳 Random Toolbox API - INT Environment Startup${NC}"
echo "================================================="

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running. Please start Docker Desktop and try again.${NC}"
        return 1
    fi
    return 0
}

# Function to check if container is running
check_container() {
    local container_id=$(docker ps -q -f name="^${CONTAINER_NAME}$" 2>/dev/null || echo "")
    if [ ! -z "$container_id" ]; then
        echo "$container_id"
        return 0
    fi
    return 1
}

# Function to check if container exists (stopped)
check_container_exists() {
    local container_id=$(docker ps -aq -f name="^${CONTAINER_NAME}$" 2>/dev/null || echo "")
    if [ ! -z "$container_id" ]; then
        echo "$container_id"
        return 0
    fi
    return 1
}

# Function to check if port is in use
check_port() {
    local pid=$(lsof -ti:$INT_PORT 2>/dev/null || echo "")
    if [ ! -z "$pid" ]; then
        echo "$pid"
        return 0
    fi
    return 1
}

# Function to stop and remove container
stop_container() {
    local container_id=$1
    echo -e "${YELLOW}⏹️  Stopping container: $container_id${NC}"
    
    # Stop the container
    docker stop "$container_id" >/dev/null 2>&1 || true
    
    # Remove the container
    docker rm "$container_id" >/dev/null 2>&1 || true
    
    echo -e "${GREEN}✅ Container stopped and removed${NC}"
}

# Function to create network if it doesn't exist
create_network() {
    if ! docker network ls | grep -q "$NETWORK_NAME"; then
        echo -e "${BLUE}🌐 Creating Docker network: $NETWORK_NAME${NC}"
        docker network create "$NETWORK_NAME" >/dev/null 2>&1
        echo -e "${GREEN}✅ Network created successfully${NC}"
    else
        echo -e "${GREEN}✅ Network $NETWORK_NAME already exists${NC}"
    fi
}

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up...${NC}"
    if [ -f "$LOCKFILE" ]; then
        rm -f "$LOCKFILE"
    fi
    exit 0
}

# Set up cleanup trap
trap cleanup INT TERM

# Check if Docker is running
echo -e "${BLUE}🔍 Checking Docker status...${NC}"
if ! check_docker; then
    exit 1
fi

# Check for existing containers and port usage
echo -e "${BLUE}🔍 Checking for existing containers and port usage...${NC}"

# Check if port is in use by non-Docker process
if port_pid=$(check_port); then
    # Check if it's our container
    if running_container=$(check_container); then
        echo -e "${YELLOW}⚠️  Found running container: $running_container${NC}"
    else
        echo -e "${RED}❌ Port $INT_PORT is in use by another process (PID: $port_pid)${NC}"
        echo -e "${BLUE}Please stop the process using port $INT_PORT and try again.${NC}"
        exit 1
    fi
fi

# Handle existing containers
if existing_container=$(check_container); then
    echo -e "${YELLOW}⚠️  Found running container: $existing_container${NC}"
    
    # Ask user what to do
    echo -e "${BLUE}Choose an option:${NC}"
    echo "1) Restart the existing container"
    echo "2) Stop and rebuild container"
    echo "3) Exit (keep existing container running)"
    
    read -p "Enter your choice (1-3): " choice
    
    case $choice in
        1)
            echo -e "${BLUE}🔄 Restarting existing container...${NC}"
            docker restart "$existing_container" >/dev/null
            echo -e "${GREEN}✅ Container restarted successfully${NC}"
            echo -e "${GREEN}🌐 API server is available at: http://localhost:$INT_PORT${NC}"
            exit 0
            ;;
        2)
            stop_container "$existing_container"
            ;;
        3)
            echo -e "${BLUE}👍 Keeping existing container running${NC}"
            echo -e "${GREEN}🌐 API server is available at: http://localhost:$INT_PORT${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Invalid choice, exiting${NC}"
            exit 1
            ;;
    esac
elif existing_stopped=$(check_container_exists); then
    echo -e "${YELLOW}⚠️  Found stopped container: $existing_stopped${NC}"
    echo -e "${BLUE}🧹 Removing stopped container...${NC}"
    docker rm "$existing_stopped" >/dev/null 2>&1
    echo -e "${GREEN}✅ Stopped container removed${NC}"
fi

# Create lockfile
echo $$ > "$LOCKFILE"

# Check if necessary files exist
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}❌ Dockerfile not found. Please ensure Docker configuration exists.${NC}"
    exit 1
fi

if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ docker-compose.yml not found. Please ensure Docker configuration exists.${NC}"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ requirements.txt not found. Please ensure you're in the correct project directory.${NC}"
    exit 1
fi

# Create network
create_network

# Display environment information
echo ""
echo -e "${BLUE}🔧 Environment Configuration:${NC}"
echo "  • Environment: INT (Integration)"
echo "  • API: http://localhost:$INT_PORT"
echo "  • Health: http://localhost:$INT_PORT/api/v1/health"
echo "  • Documentation: http://localhost:$INT_PORT/api"
echo "  • Network: $NETWORK_NAME"
echo ""

# Build and start the container
echo -e "${GREEN}🏗️  Building Docker image...${NC}"
docker-compose build

echo ""
echo -e "${GREEN}🚀 Starting INT API environment...${NC}"

# Start the container
docker-compose up -d

# Wait for container to be ready
echo -e "${BLUE}⏳ Waiting for container to be ready...${NC}"
sleep 5

# Check if container started successfully
if running_container=$(check_container); then
    echo ""
    echo -e "${GREEN}✅ API server started successfully!${NC}"
    echo "  • Container ID: $running_container"
    echo "  • URL: http://localhost:$INT_PORT"
    echo "  • Health: http://localhost:$INT_PORT/api/v1/health"
    echo "  • Documentation: http://localhost:$INT_PORT/api"
    echo "  • Network: $NETWORK_NAME"
    echo ""
    echo -e "${BLUE}💡 Tips:${NC}"
    echo "  • API endpoints are available at /api/v1/*"
    echo "  • Use 'docker-compose logs -f' to view container logs"
    echo "  • Use 'docker-compose down' to stop the environment"
    echo "  • Container supports automatic restarts"
    echo ""
    
    # Show recent logs
    echo -e "${BLUE}📋 Recent container logs:${NC}"
    docker-compose logs --tail=10
    
    echo ""
    echo -e "${GREEN}🎉 INT API environment is ready!${NC}"
    echo -e "${BLUE}🌐 Access the API at: http://localhost:$INT_PORT${NC}"
    
else
    echo -e "${RED}❌ Failed to start INT API environment${NC}"
    echo -e "${BLUE}📋 Container logs:${NC}"
    docker-compose logs
    cleanup
    exit 1
fi