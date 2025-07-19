# 📊 Financial Analytics Platform

A comprehensive financial analytics platform that combines CSV data analysis with real-time economic indicators to provide powerful insights for financial modeling and decision-making.

## 🚀 Overview

This platform enables users to upload financial CSV data and analyze it using real-time economic indicators from authoritative sources like the Federal Reserve (FRED) and Yahoo Finance. Perfect for financial analysts, researchers, and anyone needing to incorporate macroeconomic factors into their financial analysis.

## ✨ Key Features

- **📈 Real-time Economic Data**: Integrates live data from FRED API (Federal Reserve)
- **💱 Live Exchange Rates**: Real-time currency conversion via Yahoo Finance
- **📊 CSV Analysis**: Upload and analyze financial data with pandas
- **🔧 Economic Levers**: Adjustable parameters for inflation, interest rates, wage growth
- **🏢 Company Financials**: Fetch quarterly and annual financial data for any public company
- **📅 Annual Data Support**: 10+ years of annual financial data for trend analysis
- **💾 Data Persistence**: SQLite database for storing historical data
- **🌐 RESTful API**: Complete API with automatic documentation
- **🎨 Modern Web Interface**: Beautiful, responsive UI with drag-and-drop functionality
- **📊 Interactive Charts**: Real-time data visualization with Chart.js
- **🔄 Scenario Analysis**: Interest rate shock and matrix analysis tools
- **💬 Real-time Notifications**: User feedback and status updates

## 🎨 Modern UI/UX Features

### **Design System**
- **Glassmorphism Effects**: Semi-transparent cards with backdrop blur
- **Gradient Backgrounds**: Beautiful blue-to-slate color schemes
- **Responsive Design**: Perfect on desktop, tablet, and mobile
- **Interactive Elements**: Hover effects, animations, and micro-interactions

### **User Experience**
- **Drag & Drop Upload**: Intuitive file upload with visual feedback
- **Tab Navigation**: Clean, organized interface with icons
- **Real-time Notifications**: Toast notifications for user feedback
- **Loading States**: Visual feedback during operations
- **Currency Toggle**: Easy USD/CAD switching with live rates

### **Data Visualization**
- **Interactive Charts**: Modern Chart.js implementation
- **Scenario Tables**: Beautiful data tables with color coding
- **Progress Indicators**: Visual loading and processing feedback

## 🏗️ Architecture

```
Analytics App/
├── backend/
│   ├── main.py              # FastAPI application with all endpoints
│   ├── db.py                # SQLAlchemy database models and configuration
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables (API keys)
│   ├── static/
│   │   └── index.html       # Modern web interface with Tailwind CSS
│   ├── analytics.db         # SQLite database (auto-generated)
│   └── venv/               # Virtual environment
├── sample_financials.csv    # Example data file
├── docker-compose.yml       # Docker deployment configuration
├── Dockerfile              # Container configuration
└── README.md               # This file
```

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.13+)
- **Database**: SQLite with SQLAlchemy ORM
- **Data Processing**: Pandas
- **Economic Data**: FRED API (Federal Reserve)
- **Financial Data**: Yahoo Finance API
- **Server**: Uvicorn ASGI server
- **Frontend**: HTML5, Tailwind CSS, JavaScript (ES6+)
- **UI Components**: Font Awesome icons, Chart.js
- **Styling**: Modern CSS with gradients and animations
- **Deployment**: Docker support with docker-compose

## 📋 Prerequisites

- Python 3.13+
- FRED API key (free from [Federal Reserve](https://fred.stlouisfed.org/docs/api/api_key.html))

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd Analytics-App
cd backend
```

### 2. Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure API Keys
Create `backend/.env`:
```env
FRED_API_KEY=your_fred_api_key_here
```

### 4. Run the Application
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access the Platform
- **Web Interface**: http://localhost:8000/
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 🎯 Using the Modern Interface

### **CSV Analysis Tab**
1. **Drag & Drop**: Simply drag your CSV file onto the upload area
2. **Economic Levers**: Adjust interest rates, FX rates, inflation, and wage growth
3. **Auto Mode**: Toggle to use real-time economic data
4. **Run Analysis**: Click the button to process your data

### **Company Data Tab**
1. **Search**: Enter any stock symbol (e.g., AAPL, MSFT, GOOGL)
2. **Fetch Data**: Get real-time financial information
3. **Results**: View formatted company financials

### **Scenario Analysis Tab**
1. **Interest Rate Shock**: Analyze impact of rate changes on profit margins
2. **Scenario Matrix**: Compare multiple economic scenarios
3. **Visual Results**: Beautiful tables and charts showing impacts

### **Macro Data Tab**
1. **Select Indicator**: Choose from economic indicators
2. **Fetch Data**: Get historical time series
3. **Interactive Charts**: Visualize trends over time

## 📚 API Reference

### Core Analysis Endpoints

#### `POST /analyze/`
Analyze CSV data with economic levers.

**Parameters:**
- `use_auto` (bool): Use real-time economic data
- `file` (file): CSV file with Revenue and Cost columns
- `interest_rate`, `fx_rate`, `inflation`, `wage_growth` (float): Manual levers

**Response:**
```json
{
  "preview": [...],
  "totals": {
    "profit": 11500,
    "adj_profit": 1196.75,
    "adj_profit_fx": 16397,
    "avg_net_margin": 0.318
  }
}
```

#### `GET /auto-levers/`
Get real-time economic indicators.

**Response:**
```json
{
  "interest_rate": 0.0533,
  "fx_rate": 1.3698,
  "inflation": 0.03,
  "wage_growth": 0.025
}
```

### Scenario Analysis Endpoints

#### `POST /scenario/interest-shock`
Analyze the impact of interest rate changes on profit margins.

**Request Body:**
```json
{
  "symbol": "AAPL",
  "rate_delta": 0.01
}
```

**Response:**
```json
{
  "symbol": "AAPL",
  "base_margin": 0.245,
  "shock_margin": 0.238,
  "delta_margin": -0.007,
  "details": {
    "revenue": 394328000000,
    "cost": 297784000000,
    "base_interest_expense": 3933000000,
    "shock_interest_expense": 4330000000
  }
}
```

#### `GET /scenario/matrix/{symbol}`
Generate scenario matrix with combined inflation and interest rate effects.

**Response:**
```json
[
  {
    "scenario": "base",
    "net_profit": 39432800000
  },
  {
    "scenario": "+inf",
    "net_profit": 39038472000
  },
  {
    "scenario": "+rate",
    "net_profit": 39032800000
  },
  {
    "scenario": "+both",
    "net_profit": 38638472000
  }
]
```

### Company Data Endpoints

#### `GET /company/{symbol}`
Get latest quarterly financials for any public company.

#### `GET /ingest/company/{symbol}`
Bulk import company financial data with flexible parameters.

**Query Parameters:**
- `years` (int): Number of years to fetch (1-20, default: 20)
- `frequency` (str): Data frequency - `quarterly` or `annual` (default: quarterly)

**Examples:**
```bash
# Fetch 10 years of annual data
curl "http://localhost:8000/ingest/company/MSFT?years=10&frequency=annual"

# Fetch 5 years of quarterly data
curl "http://localhost:8000/ingest/company/AAPL?years=5&frequency=quarterly"
```

**Response:**
```json
{
  "symbol": "MSFT",
  "message": "Successfully ingested 4 annual records",
  "records_inserted": 4,
  "frequency": "annual",
  "years_requested": 10,
  "years_actual": 4,
  "date_range": {
    "earliest": "2021-06-30",
    "latest": "2024-06-30"
  },
  "fiscal_years": [2021, 2022, 2023, 2024]
}
```

#### `GET /data/company/{symbol}`
Retrieve stored historical company data.

### Macroeconomic Data Endpoints

#### `POST /ingest/macro/{series_id}`
Import full history of economic indicators (EFFR, CPIAUCSL, etc.).

#### `GET /macro/{series_id}`
Retrieve stored macroeconomic time series data.

## 📊 Data Sources

### Economic Indicators (FRED API)
- **EFFR**: Federal Funds Rate (interest rates)
- **CPIAUCSL**: Consumer Price Index (inflation)
- **CES050030**: Average Hourly Earnings (wage growth)

### Financial Data (Yahoo Finance)
- **Exchange Rates**: Real-time USD/CAD conversion
- **Company Financials**: Quarterly income statements
- **Historical Data**: 20+ years of financial history

## 🔧 Configuration

### Environment Variables
```env
FRED_API_KEY=your_fred_api_key_here
```

### Database Schema
- **company_facts**: Historical company financial data
- **macro_facts**: Economic indicator time series

## 🐳 Docker Deployment

### Quick Docker Setup
```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Docker Build
```bash
# Build image
docker build -t analytics-app .

# Run container
docker run -p 8000:8000 analytics-app
```

## 📈 Use Cases

- **Financial Modeling**: Incorporate real economic factors into projections
- **Risk Analysis**: Assess impact of inflation and interest rate changes
- **Investment Research**: Analyze company performance with macro context
- **Long-term Trend Analysis**: 10+ years of annual data for revenue growth and margin trends
- **Annual vs Quarterly Comparison**: Seasonal patterns and fiscal year analysis
- **Academic Research**: Economic data analysis and visualization
- **Business Planning**: Scenario analysis with real economic indicators
- **Interactive Dashboards**: Modern web interface for data exploration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Federal Reserve Economic Data (FRED)](https://fred.stlouisfed.org/) for economic indicators
- [Yahoo Finance](https://finance.yahoo.com/) for financial data
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [Pandas](https://pandas.pydata.org/) for data manipulation
- [Tailwind CSS](https://tailwindcss.com/) for the modern styling framework
- [Chart.js](https://www.chartjs.org/) for interactive data visualization

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check the API documentation at `/docs`
- Review the example data in `sample_financials.csv`

---

**Built with ❤️ for modern financial analytics** 