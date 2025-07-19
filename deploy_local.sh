#!/bin/bash

echo "🚀 Local Analytics App Deployment"
echo "=================================="

# Kill any existing processes on port 8000
echo "📋 Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Start the server in background
echo "🌐 Starting server..."
python3 main.py &
SERVER_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 5

# Test the server health
echo "🏥 Testing server health..."
if curl -s http://127.0.0.1:8000/health > /dev/null; then
    echo "✅ Server is healthy!"
else
    echo "❌ Server health check failed"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

# Test the new interest shock endpoint
echo "🧪 Testing interest shock endpoint..."
echo "Testing with AAPL +100bps shock:"
curl -X POST http://127.0.0.1:8000/scenario/interest-shock \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","rate_delta":0.01}' | jq '.'

echo ""
echo "Testing with AAPL +200bps shock:"
curl -X POST http://127.0.0.1:8000/scenario/interest-shock \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","rate_delta":0.02}' | jq '.'

echo ""
echo "🎉 Deployment successful!"
echo "📊 Server running on: http://127.0.0.1:8000"
echo "📚 API docs: http://127.0.0.1:8000/docs"
echo "🛑 To stop server: kill $SERVER_PID"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="

# Keep the script running
wait $SERVER_PID 