#!/bin/bash

# Simple launcher for Analytics App
# This script will start the server and keep it running

echo "🚀 Starting Analytics App Server..."

# Kill any existing processes
pkill -f "uvicorn.*main:app" || true
sleep 1

# Activate virtual environment and start server
cd "$(dirname "$0")"
source venv/bin/activate

echo "📍 Server starting on http://localhost:8000"
echo "📚 API docs: http://localhost:8000/docs"
echo "⏹️  Press Ctrl+C to stop"
echo ""

# Start the server
exec uvicorn main:app --host 127.0.0.1 --port 8000 --reload 