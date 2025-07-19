from fastapi import FastAPI, UploadFile, File, Form, Query
from pydantic import BaseModel
import pandas as pd
import requests
import yfinance
from dotenv import load_dotenv, find_dotenv
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from db import CompanyFact, MacroFact, SessionLocal, create_tables
from datetime import datetime
from sqlalchemy import func

load_dotenv(find_dotenv())

app = FastAPI()

app.mount('/static', StaticFiles(directory='static', html=True), name='static')

@app.get("/")
async def read_root():
    """Serve the main index.html file"""
    return FileResponse('static/index.html')

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "service": "analytics-app"
    }

# Create tables on startup
create_tables()

def fred_latest(series_id):
    """Fetch latest value from FRED API"""
    try:
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            raise ValueError("FRED_API_KEY not found in environment variables")
        
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json&sort_order=desc&limit=1"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        if "observations" in data and len(data["observations"]) > 0:
            return float(data["observations"][0]["value"])
        else:
            raise ValueError(f"No observations found for series {series_id}")
    except Exception as e:
        print(f"Error fetching FRED data for {series_id}: {e}")
        # Return fallback values based on series_id
        fallbacks = {
            "EFFR": 5.33,  # Fed Funds Rate (typical value)
            "CPIAUCSL": 3.0,  # CPI YoY % (typical inflation)
            "CES0500000030": 2.5  # Average hourly earnings % (typical wage growth)
        }
        return fallbacks.get(series_id, 0.0)

def fetch_auto_levers() -> dict:
    try:
        # Get real economic data
        interest_rate = fred_latest("EFFR") / 100  # Fed Funds % ➜ decimal
        inflation = fred_latest("CPIAUCSL") / 100  # CPI YoY %
        wage_growth = fred_latest("CES0500000030") / 100  # Avg hourly earnings %
        
        # Get USD/CAD exchange rate from Yahoo Finance
        try:
            fx_rate = yfinance.Ticker("USDCAD=X").history(period="1d")["Close"].iloc[-1]
        except Exception as e:
            print(f"Error fetching FX rate: {e}")
            fx_rate = 1.35  # Fallback USD/CAD rate
        
        return {
            "interest_rate": interest_rate,
            "fx_rate": fx_rate,
            "inflation": inflation,
            "wage_growth": wage_growth
        }
    except Exception as e:
        # Return default values if any API call fails
        print(f"Error in fetch_auto_levers: {e}")
        return {
            "interest_rate": 0.0533,
            "fx_rate": 1.35,
            "inflation": 0.03,
            "wage_growth": 0.025
        }

class Levers(BaseModel):
    interest_rate: float
    fx_rate: float
    inflation: float
    wage_growth: float

class AutoLevers(BaseModel):
    interest_rate: float
    fx_rate: float
    inflation: float
    wage_growth: float

@app.post("/upload/")
async def upload_csv(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)
    return {
        "num_rows": len(df),
        "num_columns": len(df.columns),
        "column_names": list(df.columns)
    }

@app.post("/preview/")
async def preview_csv(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)
    df["Profit"] = df["Revenue"] - df["Cost"]
    return df.head().to_dict(orient="records")

@app.post("/levers/")
async def set_levers(levers: Levers):
    return levers.dict()

@app.get("/auto-levers/")
async def get_auto_levers():
    return fetch_auto_levers()

@app.post("/analyze/")
async def analyze_csv(
    file: UploadFile = File(...),
    use_auto: bool = Query(False),
    interest_rate: float = Form(None),
    fx_rate: float = Form(None),
    inflation: float = Form(None),
    wage_growth: float = Form(None)
):
    # Get levers based on use_auto parameter
    if use_auto:
        # Call fetch_auto_levers function directly
        auto = fetch_auto_levers()
        interest_rate = auto["interest_rate"]
        fx_rate = auto["fx_rate"]
        inflation = auto["inflation"]
        wage_growth = auto["wage_growth"]
    else:
        # Use manual form fields (require them)
        if interest_rate is None or fx_rate is None or inflation is None or wage_growth is None:
            raise ValueError("All lever parameters are required when use_auto=False")
    
    df = pd.read_csv(file.file)
    df["Profit"] = df["Revenue"] - df["Cost"]
    df["Net_Margin"] = df["Profit"] / df["Revenue"]
    df["Adj_Profit"] = (df["Revenue"] * (1 + inflation)) - (df["Cost"] * (1 + wage_growth))
    df["Adj_Profit_FX"] = df["Adj_Profit"] * fx_rate
    
    return {
        "preview": df.head().to_dict(orient="records"),
        "totals": {
            "profit": float(df["Profit"].sum()),
            "adj_profit": float(df["Adj_Profit"].sum()),
            "adj_profit_fx": float(df["Adj_Profit_FX"].sum()),
            "avg_net_margin": float(df["Net_Margin"].mean())
        }
    }

@app.get("/company/{symbol}")
async def get_company_financials(symbol: str):
    """Get latest quarterly financial data for a company symbol"""
    try:
        ticker = yfinance.Ticker(symbol)
        income_stmt = ticker.quarterly_income_stmt
        
        if income_stmt.empty:
            return {
                "symbol": symbol,
                "revenue": 0,
                "cost": 0,
                "ebitda": 0,
                "error": "No financial data available"
            }
        
        # Get the most recent quarter (first column)
        latest_data = income_stmt.iloc[:, 0]
        
        # Try different possible column names for revenue and cost
        revenue = 0
        cost = 0
        ebitda = 0
        
        # Revenue - try different possible names
        for col_name in ["Total Revenue", "Revenue", "TotalRevenue"]:
            if col_name in latest_data.index:
                revenue = float(latest_data[col_name])
                break
        
        # Cost of Revenue - try different possible names
        for col_name in ["Cost Of Revenue", "Cost of Revenue", "CostOfRevenue"]:
            if col_name in latest_data.index:
                cost = float(latest_data[col_name])
                break
        
        # EBITDA
        if "EBITDA" in latest_data.index:
            ebitda = float(latest_data["EBITDA"])
        
        return {
            "symbol": symbol,
            "revenue": revenue,
            "cost": cost,
            "ebitda": ebitda
        }
    except Exception as e:
        return {
            "symbol": symbol,
            "revenue": 0,
            "cost": 0,
            "ebitda": 0,
            "error": f"Error fetching data: {str(e)}"
        }

@app.get("/ingest/company/{symbol}")
async def ingest_company_data(
    symbol: str, 
    years: int = Query(20, description="Number of years to fetch (default: 20)"),
    frequency: str = Query("quarterly", description="Data frequency: 'quarterly' or 'annual'")
):
    """Ingest company financial data from Yahoo Finance
    
    Args:
        symbol: Stock symbol (e.g., MSFT, AAPL)
        years: Number of years to fetch (default: 20, max: 20)
        frequency: Data frequency - 'quarterly' or 'annual' (default: quarterly)
    """
    try:
        # Validate parameters
        if years > 20:
            years = 20  # Yahoo Finance limit
        if frequency not in ["quarterly", "annual"]:
            frequency = "quarterly"
        
        # Get ticker data
        ticker = yfinance.Ticker(symbol)
        
        # Get financial statements based on frequency
        if frequency == "annual":
            income_stmt = ticker.income_stmt
            balance_sheet = ticker.balance_sheet
        else:
            income_stmt = ticker.quarterly_income_stmt
            balance_sheet = ticker.quarterly_balance_sheet
        
        if income_stmt.empty:
            return {
                "symbol": symbol,
                "message": "No financial data available",
                "records_inserted": 0,
                "frequency": frequency,
                "years_requested": years
            }
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Prepare data for bulk insert
            records_to_insert = []
            
            # Get the most recent years of data
            available_dates = list(income_stmt.columns)
            if len(available_dates) > years:
                available_dates = available_dates[:years]
            
            for date_str in available_dates:
                # Convert date string to datetime
                date_obj = pd.to_datetime(date_str).date()
                fiscal_year = date_obj.year
                
                # Get data for this period
                period_data = income_stmt[date_str]
                
                # Extract values with fallbacks
                revenue = 0
                cost = 0
                ebitda = 0
                
                # Try different possible column names for revenue and cost
                for col_name in ["Total Revenue", "Revenue", "TotalRevenue"]:
                    if col_name in period_data.index:
                        revenue = float(period_data[col_name])
                        break
                
                for col_name in ["Cost Of Revenue", "Cost of Revenue", "CostOfRevenue"]:
                    if col_name in period_data.index:
                        cost = float(period_data[col_name])
                        break
                
                if "EBITDA" in period_data.index:
                    ebitda = float(period_data["EBITDA"])
                
                # Create record
                record = CompanyFact(
                    symbol=symbol.upper(),
                    date=date_obj,
                    fiscal_year=fiscal_year,
                    revenue=revenue,
                    cost=cost,
                    ebitda=ebitda
                )
                records_to_insert.append(record)
            
            # Bulk insert
            db.bulk_save_objects(records_to_insert)
            db.commit()
            
            return {
                "symbol": symbol.upper(),
                "message": f"Successfully ingested {len(records_to_insert)} {frequency} records",
                "records_inserted": len(records_to_insert),
                "frequency": frequency,
                "years_requested": years,
                "years_actual": len(available_dates),
                "date_range": {
                    "earliest": min([r.date for r in records_to_insert]).isoformat(),
                    "latest": max([r.date for r in records_to_insert]).isoformat()
                },
                "fiscal_years": sorted(list(set([r.fiscal_year for r in records_to_insert])))
            }
            
        finally:
            db.close()
            
    except Exception as e:
        return {
            "symbol": symbol,
            "message": f"Error ingesting data: {str(e)}",
            "records_inserted": 0,
            "frequency": frequency,
            "years_requested": years
        }

@app.get("/data/company/{symbol}")
async def get_stored_company_data(symbol: str):
    """Retrieve stored company financial data from the database"""
    try:
        # Create database session
        db = SessionLocal()
        
        try:
            # Query for the company's data, ordered by date (most recent first)
            records = db.query(CompanyFact).filter(
                CompanyFact.symbol == symbol.upper()
            ).order_by(CompanyFact.date.desc()).all()
            
            if not records:
                return {
                    "symbol": symbol.upper(),
                    "message": "No stored data found for this symbol",
                    "records": [],
                    "count": 0
                }
            
            # Convert records to dictionary format
            data_records = []
            for record in records:
                data_records.append({
                    "date": record.date.isoformat(),
                    "revenue": record.revenue,
                    "cost": record.cost,
                    "ebitda": record.ebitda,
                    "profit": record.revenue - record.cost if record.revenue and record.cost else None,
                    "net_margin": (record.revenue - record.cost) / record.revenue if record.revenue and record.cost and record.revenue != 0 else None
                })
            
            return {
                "symbol": symbol.upper(),
                "message": f"Retrieved {len(data_records)} records",
                "records": data_records,
                "count": len(data_records),
                "date_range": {
                    "earliest": min([r.date for r in records]).isoformat(),
                    "latest": max([r.date for r in records]).isoformat()
                }
            }
            
        finally:
            db.close()
            
    except Exception as e:
        return {
            "symbol": symbol,
            "message": f"Error retrieving data: {str(e)}",
            "records": [],
            "count": 0
        }

@app.post("/ingest/macro/{series_id}")
async def ingest_macro_data(series_id: str):
    """Ingest full history of macroeconomic data from FRED"""
    try:
        # Get FRED API key
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            return {
                "series_id": series_id,
                "message": "FRED_API_KEY not found in environment variables",
                "inserted": 0
            }
        
        # Fetch full history from FRED
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        if "observations" not in data or not data["observations"]:
            return {
                "series_id": series_id,
                "message": "No observations found for this series",
                "inserted": 0
            }
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Check if data already exists for this series
            existing_count = db.query(MacroFact).filter(
                MacroFact.series_id == series_id.upper()
            ).count()
            
            if existing_count > 0:
                return {
                    "series_id": series_id.upper(),
                    "message": f"Data already exists for {series_id} ({existing_count} records). Use existing data for charting.",
                    "inserted": 0,
                    "existing_records": existing_count
                }
            
            # Prepare data for bulk insert
            records_to_insert = []
            
            for observation in data["observations"]:
                # Skip observations with missing values
                if observation["value"] == ".":
                    continue
                
                # Convert date string to datetime
                date_obj = pd.to_datetime(observation["date"]).date()
                
                # Convert value to float
                try:
                    value = float(observation["value"])
                except (ValueError, TypeError):
                    continue
                
                # Create record
                record = MacroFact(
                    series_id=series_id.upper(),
                    date=date_obj,
                    value=value
                )
                records_to_insert.append(record)
            
            # Bulk insert
            db.bulk_save_objects(records_to_insert)
            db.commit()
            
            return {
                "series_id": series_id.upper(),
                "message": f"Successfully ingested {len(records_to_insert)} observations",
                "inserted": len(records_to_insert)
            }
            
        finally:
            db.close()
            
    except Exception as e:
        return {
            "series_id": series_id,
            "message": f"Error ingesting data: {str(e)}",
            "inserted": 0
        }

@app.get("/macro/{series_id}")
async def get_macro_data(series_id: str):
    """Retrieve stored macroeconomic data from the database"""
    try:
        # Create database session
        db = SessionLocal()
        
        try:
            # Query for the series data, ordered by date (most recent first)
            # Get unique dates to avoid duplicates
            records = db.query(MacroFact).filter(
                MacroFact.series_id == series_id.upper()
            ).group_by(MacroFact.date).order_by(MacroFact.date.desc()).limit(200).all()  # Get more records for better charting
            
            if not records:
                return {
                    "series_id": series_id.upper(),
                    "message": "No stored data found for this series",
                    "records": [],
                    "count": 0
                }
            
            # Convert records to dictionary format
            data_records = []
            for record in records:
                data_records.append({
                    "date": record.date.isoformat(),
                    "value": record.value
                })
            
            return {
                "series_id": series_id.upper(),
                "message": f"Retrieved {len(data_records)} records",
                "records": data_records,
                "count": len(data_records),
                "date_range": {
                    "earliest": min([r.date for r in records]).isoformat(),
                    "latest": max([r.date for r in records]).isoformat()
                }
            }
            
        finally:
            db.close()
            
    except Exception as e:
        return {
            "series_id": series_id,
            "message": f"Error retrieving data: {str(e)}",
            "records": [],
            "count": 0
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
