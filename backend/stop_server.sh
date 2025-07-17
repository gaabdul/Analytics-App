#!/bin/bash

# Analytics App Server Stop Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PORT=8000

echo -e "${BLUE}🛑 Stopping Analytics App Server...${NC}"

# Kill any uvicorn processes on port 8000
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}Found server running on port $PORT. Stopping...${NC}"
    pkill -f "uvicorn.*:$PORT" || true
    sleep 2
    
    # Check if still running
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}❌ Failed to stop server. You may need to kill it manually.${NC}"
        echo -e "${YELLOW}Try: lsof -ti:$PORT | xargs kill -9${NC}"
    else
        echo -e "${GREEN}✅ Server stopped successfully!${NC}"
    fi
else
    echo -e "${GREEN}✅ No server found running on port $PORT${NC}"
fi

# Also kill any other uvicorn processes
pkill -f "uvicorn.*main:app" || true

echo -e "${GREEN}✅ Cleanup complete!${NC}" 