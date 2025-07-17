#!/bin/bash

# Analytics App Development Script
# Provides easy commands for development

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to show usage
show_usage() {
    echo -e "${BLUE}Analytics App Development Commands:${NC}"
    echo ""
    echo -e "${GREEN}Usage:${NC} ./dev.sh [command]"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo "  start     - Start the development server"
    echo "  stop      - Stop the development server"
    echo "  restart   - Restart the development server"
    echo "  status    - Check server status"
    echo "  logs      - Show server logs"
    echo "  install   - Install/update dependencies"
    echo "  test      - Run tests"
    echo "  clean     - Clean up temporary files"
    echo "  help      - Show this help message"
    echo ""
    echo -e "${GREEN}Examples:${NC}"
    echo "  ./dev.sh start    # Start server"
    echo "  ./dev.sh stop     # Stop server"
    echo "  ./dev.sh restart  # Restart server"
}

# Function to check server status
check_status() {
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Server is running on http://localhost:8000${NC}"
        echo -e "${GREEN}📚 API docs: http://localhost:8000/docs${NC}"
        return 0
    else
        echo -e "${RED}❌ Server is not running${NC}"
        return 1
    fi
}

# Function to install dependencies
install_deps() {
    echo -e "${BLUE}📦 Installing dependencies...${NC}"
    cd "$SCRIPT_DIR"
    source venv/bin/activate
    pip install -r requirements.txt --quiet
    echo -e "${GREEN}✅ Dependencies installed!${NC}"
}

# Function to clean up
cleanup() {
    echo -e "${BLUE}🧹 Cleaning up...${NC}"
    cd "$SCRIPT_DIR"
    
    # Remove Python cache files
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # Remove temporary files
    rm -f .DS_Store 2>/dev/null || true
    
    echo -e "${GREEN}✅ Cleanup complete!${NC}"
}

# Function to run tests
run_tests() {
    echo -e "${BLUE}🧪 Running tests...${NC}"
    cd "$SCRIPT_DIR"
    source venv/bin/activate
    python -m pytest test_*.py -v || echo -e "${YELLOW}No tests found${NC}"
}

# Main command handler
case "${1:-help}" in
    "start")
        echo -e "${BLUE}🚀 Starting Analytics App Server...${NC}"
        ./start_server.sh
        ;;
    "stop")
        echo -e "${BLUE}🛑 Stopping Analytics App Server...${NC}"
        ./stop_server.sh
        ;;
    "restart")
        echo -e "${BLUE}🔄 Restarting Analytics App Server...${NC}"
        ./stop_server.sh
        sleep 2
        ./start_server.sh
        ;;
    "status")
        check_status
        ;;
    "logs")
        echo -e "${BLUE}📋 Server logs (if running):${NC}"
        if check_status >/dev/null 2>&1; then
            echo -e "${YELLOW}Server is running. Check terminal for logs.${NC}"
        else
            echo -e "${RED}Server is not running.${NC}"
        fi
        ;;
    "install")
        install_deps
        ;;
    "test")
        run_tests
        ;;
    "clean")
        cleanup
        ;;
    "help"|*)
        show_usage
        ;;
esac 