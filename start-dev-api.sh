#!/bin/bash

# Random Toolbox API - DEV Environment Startup Script
# This script starts the development API server on localhost:8001

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEV_PORT=8001
LOCKFILE="/tmp/random-toolbox-api-dev.lock"
PYTHON_CMD="python3"

echo -e "${BLUE}🚀 Random Toolbox API - DEV Environment Startup${NC}"
echo "================================================="

# Function to check if API server is running
check_api_server() {
    local pid=$(lsof -ti:$DEV_PORT 2>/dev/null || echo "")
    if [ ! -z "$pid" ]; then
        echo "$pid"
        return 0
    fi
    return 1
}

# Function to get process info
get_process_info() {
    local pid=$1
    local cmd=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
    echo "$cmd"
}

# Function to stop API server
stop_api_server() {
    local pid=$1
    local cmd=$(get_process_info "$pid")
    
    echo -e "${YELLOW}⏹️  Stopping API server...${NC}"
    echo "  • PID: $pid"
    echo "  • Process: $cmd"
    echo "  • Port: $DEV_PORT"
    
    # Try graceful shutdown first
    echo -e "${BLUE}🤝 Attempting graceful shutdown...${NC}"
    kill -TERM "$pid" 2>/dev/null || true
    
    # Wait for graceful shutdown
    local count=0
    while kill -0 "$pid" 2>/dev/null && [ $count -lt 10 ]; do
        sleep 1
        count=$((count + 1))
        echo -n "."
    done
    echo ""
    
    # Check if process is still running
    if kill -0 "$pid" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Graceful shutdown timeout, forcing termination...${NC}"
        kill -KILL "$pid" 2>/dev/null || true
        sleep 2
    fi
    
    # Verify the process is stopped
    if kill -0 "$pid" 2>/dev/null; then
        echo -e "${RED}❌ Failed to stop process (PID: $pid)${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Successfully stopped API server (PID: $pid)${NC}"
        return 0
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

# Check if API server is already running
echo -e "${BLUE}🔍 Checking for existing API server on port $DEV_PORT...${NC}"

if existing_pid=$(check_api_server); then
    echo -e "${YELLOW}⚠️  Found existing API server running (PID: $existing_pid)${NC}"
    
    # Get additional info
    process_cmd=$(get_process_info "$existing_pid")
    echo "  • Process: $process_cmd"
    echo "  • PID: $existing_pid"
    
    # Ask user what to do
    echo ""
    echo -e "${BLUE}Choose an option:${NC}"
    echo "1) Restart the existing server"
    echo "2) Kill existing and start new"
    echo "3) Exit (keep existing server running)"
    
    read -p "Enter your choice (1-3): " choice
    
    case $choice in
        1|2)
            if stop_api_server "$existing_pid"; then
                echo -e "${GREEN}✅ Ready to start new API server${NC}"
            else
                echo -e "${RED}❌ Failed to stop existing server, exiting${NC}"
                exit 1
            fi
            ;;
        3)
            echo -e "${BLUE}👍 Keeping existing server running${NC}"
            echo -e "${GREEN}🌐 API server is available at: http://localhost:$DEV_PORT${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Invalid choice, exiting${NC}"
            exit 1
            ;;
    esac
else
    echo -e "${GREEN}✅ No existing API server found${NC}"
fi

# Create lockfile
echo $$ > "$LOCKFILE"

# Check if we're in the right directory
if [ ! -f "src/api/app.py" ]; then
    echo -e "${RED}❌ src/api/app.py not found. Please run this script from the random-toolbox project root directory.${NC}"
    exit 1
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ requirements.txt not found. Please ensure you're in the correct project directory.${NC}"
    exit 1
fi

# Check Python environment
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}📦 Virtual environment not found. Creating...${NC}"
    $PYTHON_CMD -m venv .venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source .venv/bin/activate

# Check if requirements are installed
echo -e "${BLUE}📦 Checking dependencies...${NC}"
if ! pip list | grep -q flask; then
    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Dependencies installed${NC}"
fi

# Display environment information
echo ""
echo -e "${BLUE}🔧 Environment Configuration:${NC}"
echo "  • Environment: DEV"
echo "  • API: http://localhost:$DEV_PORT"
echo "  • Health: http://localhost:$DEV_PORT/api/v1/health"
echo "  • Documentation: http://localhost:$DEV_PORT/api"
echo ""

# Start the API server
echo -e "${GREEN}🚀 Starting DEV API server...${NC}"
echo ""

# Set environment variable for port
export PORT=$DEV_PORT

# Start the server and capture PID
python src/api/app.py &
SERVER_PID=$!

# Update lockfile with server PID
echo $SERVER_PID > "$LOCKFILE"

# Wait a moment for server to start
sleep 3

# Check if server started successfully
if kill -0 "$SERVER_PID" 2>/dev/null; then
    echo ""
    echo -e "${GREEN}✅ API server started successfully!${NC}"
    echo "  • PID: $SERVER_PID"
    echo "  • URL: http://localhost:$DEV_PORT"
    echo "  • Health: http://localhost:$DEV_PORT/api/v1/health"
    echo "  • Documentation: http://localhost:$DEV_PORT/api"
    echo ""
    echo -e "${BLUE}💡 Tips:${NC}"
    echo "  • API endpoints are available at /api/v1/*"
    echo "  • Press Ctrl+C to stop the server"
    echo "  • Server supports auto-reload in debug mode"
    echo "  • Check health endpoint for API status"
    echo ""
    
    # Wait for the server process
    wait $SERVER_PID
    
else
    echo -e "${RED}❌ Failed to start API server${NC}"
    cleanup
    exit 1
fi