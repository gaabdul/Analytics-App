# 📊 Annual Company Data Ingestion Feature

## Overview
Extended the `/ingest/company/{symbol}` endpoint to support fetching 10+ years of annual financial data from Yahoo Finance, enabling deeper trend analysis for company financials.

## 🎯 New Features

### Query Parameters
- **`years`**: Number of years to fetch (default: 20, max: 20)
- **`frequency`**: Data frequency - `quarterly` or `annual` (default: quarterly)

### Enhanced Response
- **`frequency`**: Confirms the data frequency used
- **`years_requested`**: Number of years requested
- **`years_actual`**: Actual number of years available
- **`fiscal_years`**: List of fiscal years in the data

## 🔧 Technical Implementation

### Database Schema Updates
```sql
-- Added fiscal_year column to company_facts table
ALTER TABLE company_facts ADD COLUMN fiscal_year INTEGER;
CREATE INDEX idx_company_facts_fiscal_year ON company_facts(fiscal_year);
```

### Updated SQLAlchemy Model
```python
class CompanyFact(Base):
    __tablename__ = 'company_facts'
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    date = Column(Date, nullable=False)
    fiscal_year = Column(Integer, index=True)  # NEW
    revenue = Column(Float)
    cost = Column(Float)
    ebitda = Column(Float)
```

### Enhanced Endpoint
```python
@app.get("/ingest/company/{symbol}")
async def ingest_company_data(
    symbol: str, 
    years: int = Query(20, description="Number of years to fetch (default: 20)"),
    frequency: str = Query("quarterly", description="Data frequency: 'quarterly' or 'annual'")
):
```

## 📊 Usage Examples

### Fetch 10 Years of Annual Data
```bash
curl "http://127.0.0.1:8000/ingest/company/MSFT?years=10&frequency=annual"
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

### Fetch 5 Years of Quarterly Data
```bash
curl "http://127.0.0.1:8000/ingest/company/GOOGL?years=5&frequency=quarterly"
```

**Response:**
```json
{
  "symbol": "GOOGL",
  "message": "Successfully ingested 5 quarterly records",
  "records_inserted": 5,
  "frequency": "quarterly",
  "years_requested": 5,
  "years_actual": 5,
  "date_range": {
    "earliest": "2024-03-31",
    "latest": "2025-03-31"
  },
  "fiscal_years": [2024, 2025]
}
```

## 🧪 Testing

### Test Script
Run the comprehensive test script:
```bash
./test_annual_ingest.sh
```

### Manual Testing Commands
```bash
# Test annual data ingestion
curl "http://127.0.0.1:8000/ingest/company/MSFT?years=10&frequency=annual"

# Test quarterly data ingestion
curl "http://127.0.0.1:8000/ingest/company/AAPL?years=5&frequency=quarterly"

# Test parameter validation
curl "http://127.0.0.1:8000/ingest/company/MSFT?years=25&frequency=annual"

# Retrieve stored data
curl "http://127.0.0.1:8000/data/company/MSFT"
```

## 🔄 Migration Process

### Database Migration
The migration script automatically:
1. Adds `fiscal_year` column to existing table
2. Updates existing records with fiscal year from date
3. Creates index for better query performance

```bash
cd backend
python3 migrate_add_fiscal_year.py
```

### Migration Output
```
🔄 Starting migration: Add fiscal_year column to company_facts table
============================================================
Adding fiscal_year column to company_facts table...
✅ Migration completed successfully!
   - Added fiscal_year column
   - Updated existing records with fiscal year from date
   - Created index on fiscal_year column

📋 Current table structure:
   - id (INTEGER)
   - symbol (VARCHAR)
   - date (DATE)
   - revenue (FLOAT)
   - cost (FLOAT)
   - ebitda (FLOAT)
   - fiscal_year (INTEGER)
```

## 📈 Data Sources

### Yahoo Finance Integration
- **Annual Data**: `ticker.income_stmt` and `ticker.balance_sheet`
- **Quarterly Data**: `ticker.quarterly_income_stmt` and `ticker.quarterly_balance_sheet`
- **Data Fields**: Revenue, Cost of Revenue, EBITDA
- **Date Range**: Up to 20 years (Yahoo Finance limit)

### Financial Metrics Captured
- **Revenue**: Total Revenue, Revenue, TotalRevenue
- **Cost**: Cost Of Revenue, Cost of Revenue, CostOfRevenue
- **EBITDA**: EBITDA (Earnings Before Interest, Taxes, Depreciation, Amortization)

## 🛡️ Error Handling

### Parameter Validation
- **Years**: Capped at 20 (Yahoo Finance limit)
- **Frequency**: Must be 'quarterly' or 'annual' (defaults to quarterly)
- **Symbol**: Case-insensitive, converted to uppercase

### Graceful Degradation
- **No Data**: Returns empty result with descriptive message
- **API Errors**: Returns error message with details
- **Partial Data**: Processes available data and reports actual count

## 🚀 Performance Optimizations

### Database Indexing
- **Primary Index**: `symbol` for fast company lookups
- **Date Index**: `date` for chronological queries
- **Fiscal Year Index**: `fiscal_year` for annual analysis

### Bulk Operations
- **Bulk Insert**: Uses SQLAlchemy `bulk_save_objects` for efficiency
- **Transaction Management**: Proper commit/rollback handling
- **Memory Management**: Processes data in chunks

## 📊 Sample Data Analysis

### Microsoft (MSFT) - 10 Years Annual
```json
{
  "symbol": "MSFT",
  "records_inserted": 4,
  "fiscal_years": [2021, 2022, 2023, 2024],
  "date_range": {
    "earliest": "2021-06-30",
    "latest": "2024-06-30"
  }
}
```

### Apple (AAPL) - 10 Years Annual
```json
{
  "symbol": "AAPL",
  "records_inserted": 5,
  "fiscal_years": [2020, 2021, 2022, 2023, 2024],
  "date_range": {
    "earliest": "2020-09-30",
    "latest": "2024-09-30"
  }
}
```

## 🔍 Query Examples

### Retrieve Annual Data by Fiscal Year
```sql
SELECT * FROM company_facts 
WHERE symbol = 'MSFT' 
AND fiscal_year >= 2020 
ORDER BY fiscal_year DESC;
```

### Compare Annual vs Quarterly
```sql
-- Annual data
SELECT fiscal_year, AVG(revenue) as avg_revenue 
FROM company_facts 
WHERE symbol = 'MSFT' 
GROUP BY fiscal_year 
ORDER BY fiscal_year;

-- Quarterly data
SELECT strftime('%Y', date) as year, AVG(revenue) as avg_revenue 
FROM company_facts 
WHERE symbol = 'MSFT' 
GROUP BY year 
ORDER BY year;
```

## 🎯 Use Cases

### 1. Long-term Trend Analysis
- Revenue growth over 10+ years
- Cost structure evolution
- EBITDA margin trends

### 2. Annual vs Quarterly Comparison
- Seasonal patterns in quarterly data
- Annual performance summaries
- Fiscal year analysis

### 3. Cross-company Analysis
- Industry benchmarking
- Peer comparison
- Market share analysis

## 🔧 Future Enhancements

### Potential Additions
- **Balance Sheet Data**: Assets, liabilities, equity
- **Cash Flow Data**: Operating, investing, financing cash flows
- **Additional Metrics**: ROE, ROA, debt ratios
- **Custom Date Ranges**: Start/end date parameters
- **Data Export**: CSV/Excel export functionality

### API Improvements
- **Pagination**: For large datasets
- **Filtering**: By date range, fiscal year
- **Aggregation**: Pre-calculated metrics
- **Caching**: Redis integration for performance

---

**The annual company data ingestion feature is now fully operational! 🎉**

Test it with: `curl "http://127.0.0.1:8000/ingest/company/MSFT?years=10&frequency=annual"` 