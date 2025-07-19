# 📊 DataHub Service Documentation

## Overview

The DataHub service provides a unified interface for merging company financial KPIs with macroeconomic indicators, aligned by fiscal year for comprehensive financial analysis.

## 🎯 Core Functionality

### `get_company_macro(symbol, kpis, macro_ids, years=10)`

**Purpose**: Retrieves and merges company KPIs with macroeconomic indicators aligned by fiscal year.

**Parameters**:
- `symbol` (str): Company stock symbol (e.g., 'MSFT', 'AAPL')
- `kpis` (List[str]): List of company KPIs to retrieve
- `macro_ids` (List[str]): List of macroeconomic series IDs
- `years` (int): Number of fiscal years to retrieve (default: 10)

**Returns**: pandas DataFrame with columns: `fiscal_year`, `symbol`, `{kpi_columns}`, `{macro_columns}`

## 📈 Available KPIs

The service supports the following company KPIs:
- `revenue`: Annual revenue
- `cost`: Cost of goods sold
- `ebitda`: Earnings before interest, taxes, depreciation, and amortization
- `eps`: Earnings per share
- `price`: Stock price

## 🌍 Available Macroeconomic Series

Current macroeconomic indicators in the database:
- `EFFR`: Effective Federal Funds Rate
- `CPIAUCSL`: Consumer Price Index for All Urban Consumers
- `GDPC1`: Real Gross Domestic Product
- `PAYEMS`: Total Nonfarm Payrolls
- `UNRATE`: Unemployment Rate

## 🔄 Resampling Logic

The service implements intelligent resampling based on the type of macroeconomic indicator:

### Rate-Based Indicators (EFFR, UNRATE)
- **Method**: Average over fiscal year
- **Rationale**: Rates represent instantaneous values, averaging provides meaningful fiscal year representation

### Level-Based Indicators (CPIAUCSL, GDPC1, PAYEMS)
- **Method**: Last value of fiscal year
- **Rationale**: Levels represent cumulative or point-in-time values, end-of-year values are most relevant

## 📊 Example Usage

```python
from services.datahub import get_company_macro

# Get MSFT data with revenue, EPS, and macro indicators
df = get_company_macro(
    symbol="MSFT",
    kpis=["revenue", "eps"],
    macro_ids=["EFFR", "CPIAUCSL"],
    years=5
)

print(df.head())
```

**Sample Output**:
```
   fiscal_year symbol      revenue  eps     EFFR  CPIAUCSL
0        2025   MSFT 7.006600e+10 None 4.330000   321.500
1        2024   MSFT 6.963200e+10 None 5.150588   317.603
2        2024   MSFT 6.558500e+10 None 5.150588   317.603
3        2024   MSFT 6.472700e+10 None 5.150588   317.603
4        2024   MSFT 6.185800e+10 None 5.150588   317.603
```

## 🧪 Testing

### Unit Tests
Run comprehensive unit tests:
```bash
cd backend
python3 test_datahub.py
```

### Simple Test
Test with real database data:
```bash
cd backend
python3 test_datahub_simple.py
```

## 🔧 Helper Functions

### `get_available_kpis()`
Returns list of available KPIs in the database.

### `get_available_macro_series()`
Returns list of available macroeconomic series in the database.

## 🏗️ Architecture

### Database Schema
- **CompanyFact**: Stores company financial data with fiscal year alignment
- **MacroFact**: Stores macroeconomic time series data

### Service Layer
- **DataHub Service**: Core business logic for data merging and resampling
- **SQLAlchemy ORM**: Database interaction and query optimization
- **Pandas**: Data manipulation and time series resampling

## 🚀 Integration Points

The DataHub service can be integrated into:

1. **API Endpoints**: Create REST endpoints for data retrieval
2. **Analysis Tools**: Feed data into financial analysis workflows
3. **Dashboard**: Power real-time financial dashboards
4. **Reporting**: Generate automated financial reports

## 📋 Error Handling

The service includes comprehensive error handling:

- **Invalid KPIs**: Raises ValueError with valid options
- **Missing Data**: Gracefully handles missing company or macro data
- **Database Errors**: Proper exception handling and logging
- **Empty Results**: Returns empty DataFrame with appropriate logging

## 🔄 Data Flow

1. **Query Company Data**: Retrieve last N fiscal years of company KPIs
2. **Determine Date Range**: Calculate fiscal year range for macro data alignment
3. **Query Macro Data**: Retrieve macroeconomic data for the date range
4. **Resample**: Apply appropriate resampling logic (average vs. last value)
5. **Merge**: Combine company and macro data by fiscal year
6. **Sort**: Return data sorted by fiscal year (descending)

## 🎯 Use Cases

### Financial Analysis
- Correlation analysis between company performance and macro factors
- Stress testing under different economic scenarios
- Trend analysis with economic context

### Risk Management
- Interest rate sensitivity analysis
- Inflation impact assessment
- Economic cycle correlation

### Investment Research
- Sector performance vs. economic indicators
- Company-specific economic sensitivity
- Macro-driven investment strategies

## 🔮 Future Enhancements

1. **Additional KPIs**: Support for more financial metrics
2. **Custom Resampling**: User-defined resampling methods
3. **Caching**: Performance optimization with data caching
4. **Real-time Updates**: Live data integration
5. **Multi-company**: Batch processing for multiple companies
6. **Advanced Analytics**: Built-in statistical analysis functions

---

**The DataHub service provides a robust foundation for integrating company financial data with macroeconomic context, enabling sophisticated financial analysis and decision-making.** 