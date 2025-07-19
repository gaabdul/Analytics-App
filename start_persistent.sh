#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
LOG_FILE="$BACKEND_DIR/analytics.log"
PID_FILE="$BACKEND_DIR/analytics.pid"

# Function to start the server
start_server() {
    echo "$(date): Starting Analytics App server..." >> "$LOG_FILE"
    cd "$BACKEND_DIR"
    source venv/bin/activate
    python -m uvicorn main:app --host 127.0.0.1 --port 8000 >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "Server started with PID $(cat $PID_FILE)"
    echo "Logs: $LOG_FILE"
    echo "API docs: http://127.0.0.1:8000/docs"
}

# Function to stop the server
stop_server() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "Stopping server with PID $PID..."
            kill "$PID"
            rm "$PID_FILE"
        else
            echo "Server not running"
            rm "$PID_FILE"
        fi
    else
        echo "No PID file found"
    fi
}

# Function to restart the server
restart_server() {
    echo "Restarting server..."
    stop_server
    sleep 2
    start_server
}

# Function to check if server is running
check_server() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            return 0
        else
            return 1
        fi
    else
        return 1
    fi
}

# Function to monitor and auto-restart
monitor_server() {
    echo "Starting server monitor..."
    while true; do
        if ! check_server; then
            echo "$(date): Server crashed, restarting..." >> "$LOG_FILE"
            start_server
        fi
        sleep 30
    done
}

# Main script logic
case "$1" in
    start)
        if check_server; then
            echo "Server is already running"
        else
            start_server
        fi
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        if check_server; then
            echo "Server is running (PID: $(cat $PID_FILE))"
        else
            echo "Server is not running"
        fi
        ;;
    monitor)
        monitor_server
        ;;
    logs)
        tail -f "$LOG_FILE"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|monitor|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the server"
        echo "  stop    - Stop the server"
        echo "  restart - Restart the server"
        echo "  status  - Check server status"
        echo "  monitor - Start auto-restart monitor"
        echo "  logs    - Show live logs"
        exit 1
        ;;
esac 