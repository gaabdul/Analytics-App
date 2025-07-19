# 🚀 Persistent Analytics App Setup Guide

Your analytics app keeps crashing? Here are **4 different solutions** to keep it running 24/7:

## 🎯 Quick Start (Recommended for macOS)

### Option 1: LaunchAgent (Best for macOS)
```bash
# Copy the LaunchAgent to your user directory
cp com.analytics.app.plist ~/Library/LaunchAgents/

# Load the service
launchctl load ~/Library/LaunchAgents/com.analytics.app.plist

# Start the service
launchctl start com.analytics.app
```

**To stop:**
```bash
launchctl stop com.analytics.app
launchctl unload ~/Library/LaunchAgents/com.analytics.app.plist
```

### Option 2: Improved Script with Auto-restart
```bash
# Start the server with monitoring
./start_persistent.sh start

# Start the auto-restart monitor (in a separate terminal)
./start_persistent.sh monitor

# Check status
./start_persistent.sh status

# View logs
./start_persistent.sh logs
```

### Option 3: Docker (Most Reliable)
```bash
# Build and start with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option 4: Systemd Service (Linux)
```bash
# Copy service file (requires sudo)
sudo cp analytics-app.service /etc/systemd/system/

# Enable and start
sudo systemctl enable analytics-app
sudo systemctl start analytics-app

# Check status
sudo systemctl status analytics-app
```

## 🔧 Troubleshooting

### Check if server is running:
```bash
curl http://127.0.0.1:8000/
```

### Check logs:
- **LaunchAgent**: `tail -f backend/analytics.log`
- **Script**: `./start_persistent.sh logs`
- **Docker**: `docker-compose logs -f`
- **Systemd**: `sudo journalctl -u analytics-app -f`

### Common Issues:

1. **Port 8000 already in use:**
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```

2. **Virtual environment issues:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Permission issues:**
   ```bash
   chmod +x start_persistent.sh
   ```

## 📊 Monitoring

### Health Check Endpoint
Add this to your `main.py` for better monitoring:

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
```

### Auto-restart on Crash
All solutions above include automatic restart capabilities:
- **LaunchAgent**: `KeepAlive=true` restarts automatically
- **Script**: Monitor function checks every 30 seconds
- **Docker**: `restart: unless-stopped` policy
- **Systemd**: `Restart=always` policy

## 🎯 Recommendation

For **macOS users**: Use **LaunchAgent** (Option 1) - it's native, reliable, and starts automatically when you log in.

For **maximum reliability**: Use **Docker** (Option 3) - it's isolated, consistent, and handles crashes gracefully.

For **development**: Use the **improved script** (Option 2) - gives you full control and visibility.

## 🔄 Auto-start on Boot

### macOS (LaunchAgent)
Already configured - will start when you log in.

### Linux (Systemd)
```bash
sudo systemctl enable analytics-app
```

### Docker
```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc)
docker-compose -f /path/to/your/app/docker-compose.yml up -d
```

## 📈 Performance Tips

1. **Database optimization**: The SQLite database is already optimized
2. **Memory usage**: Monitor with `htop` or Activity Monitor
3. **Log rotation**: Docker and LaunchAgent handle this automatically
4. **API rate limits**: FRED API has generous limits for normal use

## 🆘 Emergency Stop

If you need to stop everything immediately:

```bash
# Kill all processes on port 8000
lsof -ti:8000 | xargs kill -9

# Stop LaunchAgent
launchctl stop com.analytics.app

# Stop Docker
docker-compose down

# Stop systemd
sudo systemctl stop analytics-app
```

---

**Your analytics app will now run continuously and restart automatically if it crashes! 🎉** 