#!/bin/bash

# Kill any existing uvicorn processes
pkill -f uvicorn 2>/dev/null || true

# Kill any process using port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Wait a moment for processes to fully terminate
sleep 2

# Activate virtual environment and start server
source venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000 --reload 