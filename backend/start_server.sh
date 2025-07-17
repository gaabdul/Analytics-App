#!/bin/bash

# Analytics App Server Startup Script
# This script provides a reliable way to start the FastAPI server

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PORT=8000
HOST="0.0.0.0"
APP_NAME="Analytics App"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}🚀 Starting $APP_NAME Server...${NC}"

# Function to check if port is in use
check_port() {
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Port $PORT is already in use. Stopping existing processes...${NC}"
        pkill -f "uvicorn.*:$PORT" || true
        sleep 2
    fi
}

# Function to check virtual environment
check_venv() {
    if [ ! -f "venv/bin/activate" ]; then
        echo -e "${RED}❌ Virtual environment not found!${NC}"
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv venv
    fi
}

# Function to install dependencies
install_deps() {
    echo -e "${BLUE}📦 Installing/updating dependencies...${NC}"
    source venv/bin/activate
    pip install -r requirements.txt --quiet
}

# Function to start server
start_server() {
    echo -e "${BLUE}🔧 Starting server on http://$HOST:$PORT${NC}"
    echo -e "${GREEN}✅ Server will be available at: http://localhost:$PORT${NC}"
    echo -e "${GREEN}📚 API docs available at: http://localhost:$PORT/docs${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
    echo ""
    
    # Start the server with proper error handling
    source venv/bin/activate
    exec uvicorn main:app --host $HOST --port $PORT --reload --log-level info
}

# Main execution
main() {
    cd "$SCRIPT_DIR"
    
    echo -e "${BLUE}📁 Working directory: $(pwd)${NC}"
    
    # Check and stop existing processes
    check_port
    
    # Check virtual environment
    check_venv
    
    # Install dependencies
    install_deps
    
    # Start server
    start_server
}

# Run main function
main "$@" 