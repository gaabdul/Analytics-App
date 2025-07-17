# Analytics App Backend

A FastAPI-based analytics application with CSV analysis, stock ticker data, and macroeconomic indicators.

## 🚀 Quick Start

### Option 1: Simple Launch (Recommended)
```bash
./launch.sh
```

### Option 2: Development Commands
```bash
# Start server
./dev.sh start

# Stop server  
./dev.sh stop

# Restart server
./dev.sh restart

# Check status
./dev.sh status

# See all commands
./dev.sh help
```

### Option 3: Manual Start
```bash
source venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

## 🌐 Access Points

- **Main App**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **API JSON**: http://localhost:8000/openapi.json

## 🔧 Features

### CSV Analysis
- Upload CSV files with Revenue and Cost columns
- Automatic profit calculation
- Adjustable economic levers (interest rates, FX, inflation, wage growth)
- Auto-fetch real-time economic data

### Stock Ticker Analysis
- Fetch real-time company financials from Yahoo Finance
- Store historical quarterly data in SQLite database
- Support for major stock symbols (AAPL, MSFT, etc.)

### Macroeconomic Analysis
- Fetch data from FRED (Federal Reserve Economic Data)
- Interactive charts with Chart.js
- Support for multiple economic indicators (EFFR, CPI, GDP, etc.)
- Historical data storage and retrieval

## 🛠️ Troubleshooting

### "Firefox can't establish a connection" Error

**Common Causes:**
1. **Port already in use**: Another process is using port 8000
2. **Virtual environment issues**: Dependencies not installed
3. **Server not started**: Background processes not running

**Solutions:**

1. **Check if server is running:**
   ```bash
   ./dev.sh status
   ```

2. **Kill existing processes:**
   ```bash
   ./dev.sh stop
   # or manually:
   pkill -f "uvicorn"
   ```

3. **Restart server:**
   ```bash
   ./dev.sh restart
   ```

4. **Check port usage:**
   ```bash
   lsof -i :8000
   ```

5. **Reinstall dependencies:**
   ```bash
   ./dev.sh install
   ```

### Virtual Environment Issues

If you see "source: no such file or directory: venv/bin/activate":

```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database Issues

If you see database errors:

```bash
# Remove and recreate database
rm analytics.db
./dev.sh start
```

## 📁 Project Structure

```
backend/
├── main.py              # FastAPI application
├── db.py                # Database models and setup
├── requirements.txt     # Python dependencies
├── launch.sh           # Simple launcher script
├── dev.sh              # Development commands
├── start_server.sh     # Robust startup script
├── stop_server.sh      # Server stop script
├── static/             # Frontend files
│   ├── index.html      # Main web interface
│   └── style.css       # Styling
└── venv/               # Virtual environment
```

## 🔑 Environment Variables

Create a `.env` file for API keys:

```bash
FRED_API_KEY=your_fred_api_key_here
```

## 📊 API Endpoints

### CSV Analysis
- `POST /analyze/` - Analyze CSV with economic levers
- `POST /upload/` - Upload CSV file
- `POST /preview/` - Preview CSV data

### Stock Data
- `GET /company/{symbol}` - Get latest company data
- `GET /ingest/company/{symbol}` - Ingest historical data
- `GET /data/company/{symbol}` - Get stored company data

### Macro Data
- `GET /ingest/macro/{series_id}` - Ingest FRED data
- `GET /macro/{series_id}` - Get stored macro data
- `GET /auto-levers/` - Get real-time economic data

## 🎯 Permanent Solution

The `launch.sh` script provides the most reliable way to start the server:

1. **Always works**: Handles all common issues automatically
2. **No conflicts**: Kills existing processes before starting
3. **Proper environment**: Activates virtual environment correctly
4. **Clear feedback**: Shows exactly what's happening

**Usage:**
```bash
cd backend
./launch.sh
```

Then open http://localhost:8000 in your browser.

## 🆘 Still Having Issues?

1. **Check the logs**: Look for error messages in the terminal
2. **Verify dependencies**: Run `./dev.sh install`
3. **Check port**: Ensure nothing else is using port 8000
4. **Restart everything**: Use `./dev.sh restart`

The server should start reliably with the `launch.sh` script! 