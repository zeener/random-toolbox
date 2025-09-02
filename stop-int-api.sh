#!/bin/bash

# Random Toolbox API - INT Environment Stop Script  
# This script stops the integration API environment Docker containers

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

echo -e "${BLUE}🐳 Random Toolbox API - INT Environment Stop${NC}"
echo "=============================================="

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Docker is not running. Cannot check containers.${NC}"
        return 1
    fi
    return 0
}

# Function to check if container is running
check_running_container() {
    local container_id=$(docker ps -q -f name="^${CONTAINER_NAME}$" 2>/dev/null || echo "")
    if [ ! -z "$container_id" ]; then
        echo "$container_id"
        return 0
    fi
    return 1
}

# Function to check if container exists (stopped)
check_stopped_container() {
    local container_id=$(docker ps -aq -f name="^${CONTAINER_NAME}$" 2>/dev/null | head -1 || echo "")
    if [ ! -z "$container_id" ]; then
        # Check if it's not running
        local running_id=$(docker ps -q -f name="^${CONTAINER_NAME}$" 2>/dev/null || echo "")
        if [ -z "$running_id" ]; then
            echo "$container_id"
            return 0
        fi
    fi
    return 1
}

# Function to get container info
get_container_info() {
    local container_id=$1
    local status=$(docker inspect --format='{{.State.Status}}' "$container_id" 2>/dev/null || echo "unknown")
    local created=$(docker inspect --format='{{.Created}}' "$container_id" 2>/dev/null | cut -d'T' -f1 || echo "unknown")
    echo "Status: $status, Created: $created"
}

# Function to stop container using docker-compose
stop_with_compose() {
    echo -e "${BLUE}🔄 Stopping with docker-compose...${NC}"
    
    if [ -f "docker-compose.yml" ]; then
        docker-compose down
        echo -e "${GREEN}✅ Docker-compose stop completed${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  docker-compose.yml not found, using direct Docker commands${NC}"
        return 1
    fi
}

# Function to stop container directly
stop_container_direct() {
    local container_id=$1
    container_info=$(get_container_info "$container_id")
    
    echo -e "${YELLOW}⏹️  Stopping container directly...${NC}"
    echo "  • Container ID: $container_id"
    echo "  • $container_info"
    echo "  • Port: $INT_PORT"
    
    # Stop the container
    echo -e "${BLUE}🛑 Stopping container...${NC}"
    docker stop "$container_id" >/dev/null 2>&1 || true
    
    # Remove the container
    echo -e "${BLUE}🗑️  Removing container...${NC}"
    docker rm "$container_id" >/dev/null 2>&1 || true
    
    echo -e "${GREEN}✅ Container stopped and removed${NC}"
}

# Function to cleanup network
cleanup_network() {
    # Check if network exists and has no connected containers
    if docker network ls | grep -q "$NETWORK_NAME"; then
        local connected_containers=$(docker network inspect "$NETWORK_NAME" --format='{{len .Containers}}' 2>/dev/null || echo "0")
        
        if [ "$connected_containers" = "0" ]; then
            echo -e "${BLUE}🌐 Removing empty network: $NETWORK_NAME${NC}"
            docker network rm "$NETWORK_NAME" >/dev/null 2>&1 || true
            echo -e "${GREEN}✅ Network removed${NC}"
        else
            echo -e "${BLUE}🌐 Network $NETWORK_NAME has other containers connected, keeping it${NC}"
        fi
    else
        echo -e "${GREEN}✅ Network $NETWORK_NAME doesn't exist${NC}"
    fi
}

# Function to cleanup lockfile
cleanup_lockfile() {
    if [ -f "$LOCKFILE" ]; then
        lockfile_pid=$(cat "$LOCKFILE" 2>/dev/null || echo "")
        if [ ! -z "$lockfile_pid" ]; then
            echo -e "${BLUE}🧹 Removing lockfile (PID: $lockfile_pid)${NC}"
        else
            echo -e "${BLUE}🧹 Removing empty lockfile${NC}"
        fi
        rm -f "$LOCKFILE"
    fi
}

# Main execution
echo -e "${BLUE}🔍 Checking Docker and containers...${NC}"

# Check if Docker is running
if ! check_docker; then
    echo -e "${YELLOW}⚠️  Cannot check containers without Docker running${NC}"
    cleanup_lockfile
    exit 0
fi

# Check for running containers
if running_container=$(check_running_container); then
    echo -e "${YELLOW}📍 Found running container: $running_container${NC}"
    
    # Get container info
    container_info=$(get_container_info "$running_container")
    echo "  • $container_info"
    
    # Confirm before stopping
    echo ""
    echo -e "${BLUE}Do you want to stop the API server? (y/N)${NC}"
    read -p "Enter choice: " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${BLUE}Choose stop method:${NC}"
        echo "1) Use docker-compose down (recommended)"
        echo "2) Stop container directly"  
        echo "3) Cancel"
        
        read -p "Enter choice (1-3): " method_choice
        
        case $method_choice in
            1)
                if ! stop_with_compose; then
                    echo -e "${YELLOW}⚠️  Fallback to direct container stop${NC}"
                    stop_container_direct "$running_container"
                fi
                ;;
            2)
                stop_container_direct "$running_container"
                ;;
            3)
                echo -e "${BLUE}👍 Keeping API server running${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Invalid choice, using docker-compose${NC}"
                if ! stop_with_compose; then
                    stop_container_direct "$running_container"
                fi
                ;;
        esac
        
        echo ""
        echo -e "${GREEN}🎉 API server stopped successfully!${NC}"
        
    else
        echo -e "${BLUE}👍 Keeping API server running${NC}"
        exit 0
    fi
    
elif stopped_container=$(check_stopped_container); then
    echo -e "${YELLOW}📍 Found stopped container: $stopped_container${NC}"
    
    # Get container info
    container_info=$(get_container_info "$stopped_container")
    echo "  • $container_info"
    
    echo ""
    echo -e "${BLUE}Do you want to remove the stopped container? (y/N)${NC}"
    read -p "Enter choice: " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}🗑️  Removing stopped container...${NC}"
        docker rm "$stopped_container" >/dev/null 2>&1 || true
        echo -e "${GREEN}✅ Stopped container removed${NC}"
    else
        echo -e "${BLUE}👍 Keeping stopped container${NC}"
    fi
    
else
    echo -e "${GREEN}✅ No containers found for $CONTAINER_NAME${NC}"
fi

# Cleanup operations
echo ""
echo -e "${BLUE}🧹 Cleanup operations:${NC}"

# Cleanup lockfile
cleanup_lockfile

# Ask about network cleanup
echo ""
echo -e "${BLUE}Do you want to cleanup the network? (y/N)${NC}"
read -p "Enter choice: " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    cleanup_network
else
    echo -e "${BLUE}👍 Keeping network $NETWORK_NAME${NC}"
fi

# Additional Docker cleanup
echo ""
echo -e "${BLUE}Do you want to run additional Docker cleanup? (y/N)${NC}"
echo "  • Remove unused containers, networks, images"
read -p "Enter choice: " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}🧹 Running Docker system prune...${NC}"
    docker system prune -f
    echo -e "${GREEN}✅ Docker cleanup completed${NC}"
fi

echo ""
echo -e "${GREEN}🏁 API server cleanup completed!${NC}"
echo ""
echo -e "${BLUE}💡 Tips:${NC}"
echo "  • To start API server: ./start-int-api.sh"
echo "  • To check Docker containers: docker ps -a"
echo "  • Port $INT_PORT is now available for other processes"
echo "  • To remove all stopped containers: docker container prune"