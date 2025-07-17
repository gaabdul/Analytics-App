#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the backend directory
cd "$SCRIPT_DIR/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found in backend directory"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Kill any existing processes on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "No processes on port 8000"

# Start the server
echo "Starting Analytics App server on http://127.0.0.1:8000"
echo "API docs available at: http://127.0.0.1:8000/docs"
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload 