from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException
from pydantic import BaseModel, Field
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
from services.datahub import get_company_macro, get_available_kpis, get_available_macro_series
from services.analysis import calc_beta, calc_multiple_betas, interpret_beta
from typing import List, Optional

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

class RevenueTrend(BaseModel):
    symbol: str
    years: list[str]
    revenue: list[float]
    cagr: float
    message: str

class InterestShockRequest(BaseModel):
    symbol: str
    base_years: int = 10
    rate_delta: float

class ScenarioResult(BaseModel):
    scenario: str
    net_profit: float

class BetaAnalysisRequest(BaseModel):
    symbol: str
    kpi: str
    macro_variable: str
    years: int = 10

class BetaAnalysisResponse(BaseModel):
    symbol: str
    kpi: str
    macro_variable: str
    beta: float
    r2: float
    p_value: float
    plot_url: str
    n_observations: int
    interpretation: dict
    y_mean: float
    x_mean: float
    y_std: float
    x_std: float

class BetaGetResponse(BaseModel):
    """Response model for GET /beta/{symbol} endpoint"""
    symbol: str = Field(..., description="Company stock symbol")
    kpi: str = Field(..., description="Key Performance Indicator analyzed")
    macro_variable: str = Field(..., description="Macroeconomic variable analyzed")
    years: int = Field(..., description="Number of years of data used")
    beta: float = Field(..., description="Regression coefficient (sensitivity measure)")
    r2: float = Field(..., description="R-squared value (explanatory power)")
    p_value: float = Field(..., description="Statistical significance p-value")
    plot_url: str = Field(..., description="URL to generated regression plot")
    n_observations: int = Field(..., description="Number of data points used in analysis")
    interpretation: dict = Field(..., description="Automated interpretation of results")
    y_mean: float = Field(..., description="Mean of the KPI values")
    x_mean: float = Field(..., description="Mean of the macro variable values")
    y_std: float = Field(..., description="Standard deviation of KPI values")
    x_std: float = Field(..., description="Standard deviation of macro variable values")
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "MSFT",
                "kpi": "revenue",
                "macro_variable": "EFFR",
                "years": 10,
                "beta": 102527670250.89568,
                "r2": 0.09886894919175204,
                "p_value": 0.37624028499504447,
                "plot_url": "/static/beta_revenue_EFFR.png",
                "n_observations": 10,
                "interpretation": {
                    "significance": "Not significant",
                    "direction": "Positive",
                    "strength": "Strong",
                    "explained_variance": "Low",
                    "insights": [
                        "No significant relationship found between the variables",
                        "Low explanatory power: 9.9% of KPI variance explained by macro variable"
                    ]
                },
                "y_mean": 145785700000.0,
                "x_mean": 5.068529411764706,
                "y_std": 84612868010.13188,
                "x_std": 0.2594927844667584
            }
        }

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

@app.get("/company/{symbol}/revenue-trend", response_model=RevenueTrend)
async def get_revenue_trend(symbol: str):
    """Get 10-year revenue trend with CAGR calculation for charting"""
    try:
        # Create database session
        db = SessionLocal()
        
        try:
            # Query for the last 10 years of annual revenue data
            # Use fiscal_year for annual data, ordered by fiscal_year descending
            records = db.query(CompanyFact).filter(
                CompanyFact.symbol == symbol.upper(),
                CompanyFact.revenue.isnot(None),
                CompanyFact.revenue > 0
            ).order_by(CompanyFact.fiscal_year.desc()).all()
            
            # Deduplicate by fiscal_year, keeping the highest revenue for each year
            unique_records = {}
            for record in records:
                if record.fiscal_year is not None:
                    if record.fiscal_year not in unique_records or record.revenue > unique_records[record.fiscal_year].revenue:
                        unique_records[record.fiscal_year] = record
            
            # Convert back to list and sort by fiscal_year ascending for CAGR calculation
            records = sorted(unique_records.values(), key=lambda x: x.fiscal_year if x.fiscal_year is not None else 0)
            
            # Limit to last 10 years
            if len(records) > 10:
                records = records[-10:]
            
            if not records:
                return RevenueTrend(
                    symbol=symbol.upper(),
                    years=[],
                    revenue=[],
                    cagr=0.0,
                    message="No revenue data found for this symbol"
                )
            
            # Sort by fiscal_year ascending for CAGR calculation
            records.sort(key=lambda x: x.fiscal_year)
            
            # Extract years and revenue data
            years = [str(record.fiscal_year) for record in records]
            revenue = [float(record.revenue) for record in records]
            
            # Calculate CAGR: (End Value / Start Value)^(1/n) - 1
            if len(revenue) >= 2:
                start_revenue = revenue[0]
                end_revenue = revenue[-1]
                num_years = len(revenue) - 1
                
                if start_revenue > 0 and num_years > 0:
                    cagr = (end_revenue / start_revenue) ** (1 / num_years) - 1
                else:
                    cagr = 0.0
            else:
                cagr = 0.0
            
            return RevenueTrend(
                symbol=symbol.upper(),
                years=years,
                revenue=revenue,
                cagr=cagr,
                message=f"Retrieved {len(records)} years of revenue data"
            )
            
        finally:
            db.close()
            
    except Exception as e:
        return RevenueTrend(
            symbol=symbol.upper(),
            years=[],
            revenue=[],
            cagr=0.0,
            message=f"Error retrieving revenue trend: {str(e)}"
        )

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

@app.post("/scenario/interest-shock")
async def interest_rate_shock_scenario(request: InterestShockRequest):
    """
    Calculate the impact of interest rate changes on net profit margin.
    
    Assumptions:
    • Fixed debt level: Assumes company maintains same debt structure
    • Linear interest expense scaling: Interest expense changes proportionally with rate delta
    • Revenue and operating costs remain constant in the shock scenario
    • Uses latest available financial data for calculations
    
    Formula:
    • Base net profit margin = (Revenue - Cost - Interest Expense) / Revenue
    • Shock interest expense = Base interest expense × (1 + rate_delta)
    • Shock net profit margin = (Revenue - Cost - Shock interest expense) / Revenue
    • Delta margin = Shock margin - Base margin
    """
    try:
        # Fetch latest company financial data
        ticker = yfinance.Ticker(request.symbol)
        income_stmt = ticker.quarterly_income_stmt
        
        if income_stmt.empty:
            return {
                "symbol": request.symbol.upper(),
                "error": "No financial data available for this symbol",
                "base_margin": None,
                "shock_margin": None,
                "delta_margin": None
            }
        
        # Get the most recent quarter data
        latest_data = income_stmt.iloc[:, 0]
        
        # Extract financial metrics
        revenue = 0
        cost = 0
        interest_expense = 0
        
        # Revenue
        for col_name in ["Total Revenue", "Revenue", "TotalRevenue"]:
            if col_name in latest_data.index:
                revenue = float(latest_data[col_name])
                break
        
        # Cost of Revenue
        for col_name in ["Cost Of Revenue", "Cost of Revenue", "CostOfRevenue"]:
            if col_name in latest_data.index:
                cost = float(latest_data[col_name])
                break
        
        # Interest Expense - try different possible names
        for col_name in ["Interest Expense", "InterestExpense", "Interest Expense, Net", "Net Interest Expense"]:
            if col_name in latest_data.index:
                interest_expense = abs(float(latest_data[col_name]))  # Use absolute value
                break
        
        # If no interest expense found, try to estimate from financial statements
        if interest_expense == 0:
            # Try to get from balance sheet for debt estimation
            try:
                balance_sheet = ticker.quarterly_balance_sheet
                if not balance_sheet.empty:
                    latest_bs = balance_sheet.iloc[:, 0]
                    
                    # Look for debt-related items
                    total_debt = 0
                    for debt_col in ["Total Debt", "TotalDebt", "Long Term Debt", "LongTermDebt"]:
                        if debt_col in latest_bs.index:
                            total_debt = abs(float(latest_bs[debt_col]))
                            break
                    
                    # Estimate interest expense as 3% of total debt (typical corporate rate)
                    if total_debt > 0:
                        interest_expense = total_debt * 0.03
            except Exception as e:
                print(f"Could not estimate interest expense: {e}")
        
        # Validate we have the necessary data
        if revenue <= 0:
            return {
                "symbol": request.symbol.upper(),
                "error": "No valid revenue data available",
                "base_margin": None,
                "shock_margin": None,
                "delta_margin": None
            }
        
        # Calculate base net profit margin
        base_net_income = revenue - cost - interest_expense
        base_margin = base_net_income / revenue if revenue > 0 else 0
        
        # Calculate shock scenario
        # • Interest expense increases by rate_delta proportion
        # • Revenue and operating costs remain constant
        shock_interest_expense = interest_expense * (1 + request.rate_delta)
        shock_net_income = revenue - cost - shock_interest_expense
        shock_margin = shock_net_income / revenue if revenue > 0 else 0
        
        # Calculate delta
        delta_margin = shock_margin - base_margin
        
        return {
            "symbol": request.symbol.upper(),
            "base_margin": round(base_margin, 3),
            "shock_margin": round(shock_margin, 3),
            "delta_margin": round(delta_margin, 3),
            "details": {
                "revenue": revenue,
                "cost": cost,
                "base_interest_expense": interest_expense,
                "shock_interest_expense": shock_interest_expense,
                "rate_delta": request.rate_delta
            }
        }
        
    except Exception as e:
        return {
            "symbol": request.symbol.upper(),
            "error": f"Error calculating interest shock scenario: {str(e)}",
            "base_margin": None,
            "shock_margin": None,
            "delta_margin": None
        }

@app.get("/scenario/matrix/{symbol}", response_model=list[ScenarioResult])
async def get_scenario_matrix(symbol: str):
    """
    Generate scenario matrix showing combined effects of ±1% inflation and ±1% interest rate changes on net profit.
    
    Scenarios:
    • base: No changes to inflation or interest rates
    • +inf: +1% inflation affecting cost of goods sold
    • +rate: +1% interest rate affecting interest expense
    • +both: +1% both inflation and interest rate
    
    Assumptions:
    • Inflation affects cost of goods sold linearly
    • Interest rate changes affect interest expense proportionally
    • Revenue remains constant across all scenarios
    • Uses latest available financial data
    """
    try:
        # Fetch latest company financial data
        ticker = yfinance.Ticker(symbol)
        income_stmt = ticker.quarterly_income_stmt
        
        if income_stmt.empty:
            return [
                ScenarioResult(scenario="error", net_profit=0)
            ]
        
        # Get the most recent quarter data
        latest_data = income_stmt.iloc[:, 0]
        
        # Extract financial metrics
        revenue = 0
        cost_of_goods_sold = 0
        interest_expense = 0
        
        # Revenue
        for col_name in ["Total Revenue", "Revenue", "TotalRevenue"]:
            if col_name in latest_data.index:
                revenue = float(latest_data[col_name])
                break
        
        # Cost of Goods Sold
        for col_name in ["Cost Of Revenue", "Cost of Revenue", "CostOfRevenue", "Cost of Goods Sold"]:
            if col_name in latest_data.index:
                cost_of_goods_sold = float(latest_data[col_name])
                break
        
        # Interest Expense
        for col_name in ["Interest Expense", "InterestExpense", "Interest Expense, Net", "Net Interest Expense"]:
            if col_name in latest_data.index:
                interest_expense = abs(float(latest_data[col_name]))  # Use absolute value
                break
        
        # If no interest expense found, try to estimate from balance sheet
        if interest_expense == 0:
            try:
                balance_sheet = ticker.quarterly_balance_sheet
                if not balance_sheet.empty:
                    latest_bs = balance_sheet.iloc[:, 0]
                    
                    # Look for debt-related items
                    total_debt = 0
                    for debt_col in ["Total Debt", "TotalDebt", "Long Term Debt", "LongTermDebt"]:
                        if debt_col in latest_bs.index:
                            total_debt = abs(float(latest_bs[debt_col]))
                            break
                    
                    # Estimate interest expense as 3% of total debt
                    if total_debt > 0:
                        interest_expense = total_debt * 0.03
            except Exception as e:
                print(f"Could not estimate interest expense: {e}")
        
        # Validate we have the necessary data
        if revenue <= 0:
            return [
                ScenarioResult(scenario="error", net_profit=0)
            ]
        
        # Calculate base net profit
        base_net_profit = revenue - cost_of_goods_sold - interest_expense
        
        # Define scenarios
        scenarios = [
            {
                "name": "base",
                "inflation_delta": 0.0,
                "rate_delta": 0.0
            },
            {
                "name": "+inf",
                "inflation_delta": 0.01,  # +1%
                "rate_delta": 0.0
            },
            {
                "name": "+rate",
                "inflation_delta": 0.0,
                "rate_delta": 0.01  # +1%
            },
            {
                "name": "+both",
                "inflation_delta": 0.01,  # +1%
                "rate_delta": 0.01  # +1%
            }
        ]
        
        # Calculate net profit for each scenario
        results = []
        for scenario in scenarios:
            # Apply inflation effect to cost of goods sold
            adjusted_cost = cost_of_goods_sold * (1 + scenario["inflation_delta"])
            
            # Apply interest rate effect to interest expense
            adjusted_interest = interest_expense * (1 + scenario["rate_delta"])
            
            # Calculate net profit
            net_profit = revenue - adjusted_cost - adjusted_interest
            
            results.append(ScenarioResult(
                scenario=scenario["name"],
                net_profit=round(net_profit, 0)  # Round to nearest dollar
            ))
        
        return results
        
    except Exception as e:
        return [
            ScenarioResult(scenario="error", net_profit=0)
        ]

@app.post("/analysis/beta", response_model=BetaAnalysisResponse)
async def calculate_beta_analysis(request: BetaAnalysisRequest):
    """
    Calculate the sensitivity (beta) of a KPI to a macroeconomic variable.
    
    This endpoint performs linear regression analysis to determine how sensitive
    a company's KPI is to changes in macroeconomic indicators.
    
    Args:
        request: BetaAnalysisRequest containing symbol, kpi, macro_variable, and years
    
    Returns:
        BetaAnalysisResponse with regression results, plot URL, and interpretation
    """
    try:
        # Get merged data using DataHub service
        df = get_company_macro(
            symbol=request.symbol.upper(),
            kpis=[request.kpi],
            macro_ids=[request.macro_variable],
            years=request.years
        )
        
        if df.empty:
            return {
                "symbol": request.symbol.upper(),
                "kpi": request.kpi,
                "macro_variable": request.macro_variable,
                "error": "No data available for the specified parameters",
                "beta": 0.0,
                "r2": 0.0,
                "p_value": 1.0,
                "plot_url": "",
                "n_observations": 0,
                "interpretation": {"error": "No data available"},
                "y_mean": 0.0,
                "x_mean": 0.0,
                "y_std": 0.0,
                "x_std": 0.0
            }
        
        # Calculate beta using Analysis service
        result = calc_beta(df, request.kpi, request.macro_variable)
        
        # Get interpretation
        interpretation = interpret_beta(result['beta'], result['p_value'], result['r2'])
        
        return BetaAnalysisResponse(
            symbol=request.symbol.upper(),
            kpi=request.kpi,
            macro_variable=request.macro_variable,
            beta=result['beta'],
            r2=result['r2'],
            p_value=result['p_value'],
            plot_url=result['plot_url'],
            n_observations=result['n_observations'],
            interpretation=interpretation,
            y_mean=result['y_mean'],
            x_mean=result['x_mean'],
            y_std=result['y_std'],
            x_std=result['x_std']
        )
        
    except Exception as e:
        return {
            "symbol": request.symbol.upper(),
            "kpi": request.kpi,
            "macro_variable": request.macro_variable,
            "error": f"Error calculating beta analysis: {str(e)}",
            "beta": 0.0,
            "r2": 0.0,
            "p_value": 1.0,
            "plot_url": "",
            "n_observations": 0,
            "interpretation": {"error": str(e)},
            "y_mean": 0.0,
            "x_mean": 0.0,
            "y_std": 0.0,
            "x_std": 0.0
        }

@app.get("/beta/{symbol}", response_model=BetaGetResponse)
async def get_beta_analysis(
    symbol: str,
    kpi: str = Query(..., description="Key Performance Indicator to analyze", example="revenue"),
    macro: str = Query(..., description="Macroeconomic variable to analyze", example="EFFR"),
    years: int = Query(10, description="Number of years of data to use", ge=3, le=20, example=10)
):
    """
    Calculate the sensitivity (beta) of a KPI to a macroeconomic variable using GET request.
    
    This endpoint provides a user-friendly way to analyze how sensitive a company's KPI
    is to changes in macroeconomic indicators through a simple GET request.
    
    **Parameters:**
    - **symbol**: Company stock symbol (e.g., MSFT, AAPL, GOOGL)
    - **kpi**: Key Performance Indicator to analyze (revenue, eps, ebitda, price)
    - **macro**: Macroeconomic variable to analyze (EFFR, CPIAUCSL, UNRATE, GDP)
    - **years**: Number of years of data to use (3-20, default: 10)
    
    **Returns:**
    - Beta coefficient (sensitivity measure)
    - R-squared value (explanatory power)
    - P-value (statistical significance)
    - Plot URL for visualization
    - Automated interpretation and insights
    
    **Example:**
    ```
    GET /beta/MSFT?kpi=revenue&macro=EFFR&years=10
    ```
    
    **Available KPIs:** revenue, eps, ebitda, price
    **Available Macro Variables:** EFFR, CPIAUCSL, UNRATE, GDP
    """
    try:
        # Validate symbol
        symbol = symbol.upper().strip()
        if not symbol or len(symbol) > 10:
            raise HTTPException(status_code=400, detail="Invalid symbol format")
        
        # Validate KPI
        available_kpis = get_available_kpis()
        if kpi.lower() not in [k.lower() for k in available_kpis]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid KPI '{kpi}'. Available KPIs: {available_kpis}"
            )
        
        # Validate macro variable
        available_macros = get_available_macro_series()
        if macro.upper() not in available_macros:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid macro variable '{macro}'. Available variables: {available_macros}"
            )
        
        # Validate years
        if years < 3 or years > 20:
            raise HTTPException(
                status_code=400, 
                detail="Years must be between 3 and 20"
            )
        
        # Get merged data using DataHub service
        df = get_company_macro(
            symbol=symbol,
            kpis=[kpi],
            macro_ids=[macro.upper()],
            years=years
        )
        
        if df.empty:
            raise HTTPException(
                status_code=404, 
                detail=f"No data available for {symbol} with the specified parameters"
            )
        
        # Calculate beta using Analysis service
        result = calc_beta(df, kpi, macro.upper())
        
        # Get interpretation
        interpretation = interpret_beta(result['beta'], result['p_value'], result['r2'])
        
        return BetaGetResponse(
            symbol=symbol,
            kpi=kpi,
            macro_variable=macro.upper(),
            years=years,
            beta=result['beta'],
            r2=result['r2'],
            p_value=result['p_value'],
            plot_url=result['plot_url'],
            n_observations=result['n_observations'],
            interpretation=interpretation,
            y_mean=result['y_mean'],
            x_mean=result['x_mean'],
            y_std=result['y_std'],
            x_std=result['x_std']
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error calculating beta analysis: {str(e)}"
        )

@app.get("/test-endpoint")
async def test_endpoint():
    """Simple test endpoint to verify server is running updated code"""
    return {"message": "Test endpoint working", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
