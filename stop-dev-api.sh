#!/bin/bash

# Random Toolbox API - DEV Environment Stop Script
# This script stops the development API server running on localhost:8001

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

echo -e "${BLUE}🛑 Random Toolbox API - DEV Environment Stop${NC}"
echo "=============================================="

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
        echo -e "${BLUE}💡 Try manually: kill -9 $pid${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Successfully stopped API server (PID: $pid)${NC}"
        return 0
    fi
}

# Function to cleanup lockfile
cleanup_lockfile() {
    if [ -f "$LOCKFILE" ]; then
        local lockfile_pid=$(cat "$LOCKFILE" 2>/dev/null || echo "")
        if [ ! -z "$lockfile_pid" ]; then
            if ! kill -0 "$lockfile_pid" 2>/dev/null; then
                echo -e "${BLUE}🧹 Removing stale lockfile (PID: $lockfile_pid no longer exists)${NC}"
                rm -f "$LOCKFILE"
            fi
        else
            echo -e "${BLUE}🧹 Removing empty lockfile${NC}"
            rm -f "$LOCKFILE"
        fi
    fi
}

# Main execution
echo -e "${BLUE}🔍 Searching for API server on port $DEV_PORT...${NC}"

# Check for running processes on the port
if server_pid=$(check_api_server); then
    echo -e "${YELLOW}📍 Found process running on port $DEV_PORT${NC}"
    
    # Get additional info
    process_cmd=$(get_process_info "$server_pid")
    echo "  • Process: $process_cmd"
    echo "  • PID: $server_pid"
    
    # Confirm before stopping
    echo ""
    echo -e "${BLUE}Do you want to stop this API server? (y/N)${NC}"
    read -p "Enter choice: " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if stop_api_server "$server_pid"; then
            echo ""
            echo -e "${GREEN}🎉 API server stopped successfully!${NC}"
        else
            echo ""
            echo -e "${RED}❌ Failed to stop API server${NC}"
            exit 1
        fi
    else
        echo -e "${BLUE}👍 Keeping API server running${NC}"
        exit 0
    fi
else
    echo -e "${GREEN}✅ No API server found running on port $DEV_PORT${NC}"
fi

# Cleanup lockfile
cleanup_lockfile

# Additional cleanup
echo ""
echo -e "${BLUE}🧹 Additional cleanup:${NC}"

# Check for any remaining Python Flask processes
flask_processes=$(pgrep -f "flask.*run\|python.*api" 2>/dev/null || echo "")
if [ ! -z "$flask_processes" ]; then
    echo -e "${YELLOW}⚠️  Found additional Flask/API processes:${NC}"
    echo "$flask_processes" | while read -r pid; do
        if [ ! -z "$pid" ]; then
            cmd=$(get_process_info "$pid")
            echo "  • PID: $pid ($cmd)"
        fi
    done
    echo ""
    echo -e "${BLUE}Do you want to stop these as well? (y/N)${NC}"
    read -p "Enter choice: " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "$flask_processes" | while read -r pid; do
            if [ ! -z "$pid" ] && kill -0 "$pid" 2>/dev/null; then
                echo -e "${YELLOW}⏹️  Stopping Flask process (PID: $pid)${NC}"
                kill -TERM "$pid" 2>/dev/null || true
                sleep 1
                if kill -0 "$pid" 2>/dev/null; then
                    kill -KILL "$pid" 2>/dev/null || true
                fi
            fi
        done
        echo -e "${GREEN}✅ Additional processes stopped${NC}"
    fi
else
    echo -e "${GREEN}✅ No additional Flask/API processes found${NC}"
fi

# Deactivate virtual environment if active
if [ ! -z "$VIRTUAL_ENV" ]; then
    echo -e "${BLUE}🐍 Deactivating virtual environment${NC}"
    deactivate 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}🏁 API server cleanup completed!${NC}"
echo ""
echo -e "${BLUE}💡 Tips:${NC}"
echo "  • To start API server: ./start-dev-api.sh"
echo "  • To run direct Flask dev: python src/api/app.py"
echo "  • Port $DEV_PORT is now available for other processes"