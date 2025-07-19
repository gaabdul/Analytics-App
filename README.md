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
- **📱 Web Interface**: User-friendly HTML form for data upload and analysis

## 🏗️ Architecture

```
Analytics App/
├── backend/
│   ├── main.py              # FastAPI application with all endpoints
│   ├── db.py                # SQLAlchemy database models and configuration
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables (API keys)
│   ├── static/
│   │   └── index.html       # Web interface for data upload
│   ├── analytics.db         # SQLite database (auto-generated)
│   └── venv/               # Virtual environment
├── sample_financials.csv    # Example data file
└── README.md               # This file
```

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.13 **Database**: SQLite with SQLAlchemy ORM
- **Data Processing**: Pandas
- **Economic Data**: FRED API (Federal Reserve)
- **Financial Data**: Yahoo Finance API
- **Server**: Uvicorn ASGI server
- **Frontend**: HTML/CSS/JavaScript

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
uvicorn main:app --reload --host 0.0 --port 8000
```

### 5. Access the Platform
- **Web Interface**: http://localhost:8000/
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000# 📚 API Reference

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
  preview": [...],
 totals: {
    profit": 11500
    adj_profit":1196.75
   adj_profit_fx": 16397   avg_net_margin":0.318
  }
}
```

#### `GET /auto-levers/`
Get real-time economic indicators.

**Response:**
```json
[object Object]  interest_rate": 00533 fx_rate": 1.3698,
 inflation: 0.3,
 wage_growth": 0.025
}
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

## 📈 Use Cases

- **Financial Modeling**: Incorporate real economic factors into projections
- **Risk Analysis**: Assess impact of inflation and interest rate changes
- **Investment Research**: Analyze company performance with macro context
- **Long-term Trend Analysis**: 10+ years of annual data for revenue growth and margin trends
- **Annual vs Quarterly Comparison**: Seasonal patterns and fiscal year analysis
- **Academic Research**: Economic data analysis and visualization
- **Business Planning**: Scenario analysis with real economic indicators

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature`)
4.Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Federal Reserve Economic Data (FRED)](https://fred.stlouisfed.org/) for economic indicators
- [Yahoo Finance](https://finance.yahoo.com/) for financial data
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [Pandas](https://pandas.pydata.org/) for data manipulation

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check the API documentation at `/docs`
- Review the example data in `sample_financials.csv`

---

**Built with ❤️ for financial analytics** 