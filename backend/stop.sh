#!/bin/bash

echo "Stopping server..."

# Kill any uvicorn processes
pkill -f uvicorn 2>/dev/null || true

# Kill any process using port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

echo "Server stopped." 