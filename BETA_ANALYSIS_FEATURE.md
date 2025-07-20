# 📊 Beta Analysis Feature Documentation

## Overview

The Beta Analysis feature provides comprehensive sensitivity analysis to determine how sensitive a company's Key Performance Indicator (KPI) is to changes in macroeconomic variables. This is implemented through a robust analysis service and REST API endpoint.

## 🎯 Core Functionality

### `calc_beta(df, y_col, x_col)` Function

**Purpose**: Calculates the sensitivity (beta) of a KPI to a macroeconomic variable using linear regression.

**Parameters**:
- `df` (pd.DataFrame): Merged DataFrame with company and macro data
- `y_col` (str): Dependent variable (KPI column name)
- `x_col` (str): Independent variable (macro column name)

**Returns**: Dictionary containing:
- `beta`: Regression coefficient (sensitivity measure)
- `r2`: R-squared value (explanatory power)
- `p_value`: Statistical significance
- `plot_url`: URL to generated regression plot
- `n_observations`: Number of data points used
- Additional statistics (means, standard deviations)

## 🔧 Technical Implementation

### Statistical Methods

1. **Linear Regression**: Uses `statsmodels.OLS` for robust statistical analysis
2. **Data Validation**: Comprehensive input validation and error handling
3. **Plot Generation**: Creates professional regression plots with matplotlib/seaborn
4. **Interpretation**: Automated insights and significance testing

### Regression Model

```
y = α + βx + ε

Where:
- y = KPI (dependent variable)
- x = Macro variable (independent variable)
- β = Beta coefficient (sensitivity measure)
- α = Intercept
- ε = Error term
```

### Resampling Strategy

- **Rates (EFFR, UNRATE)**: Uses fiscal year average
- **Levels (CPI, GDP)**: Uses last value of fiscal year
- **Alignment**: Data aligned by fiscal year for consistent analysis

## 📈 API Endpoint

### POST `/analysis/beta`

**Request Schema**:
```json
{
  "symbol": "MSFT",
  "kpi": "revenue",
  "macro_variable": "EFFR",
  "years": 10
}
```

**Response Schema**:
```json
{
  "symbol": "MSFT",
  "kpi": "revenue",
  "macro_variable": "EFFR",
  "beta": 102527670250.895676,
  "r2": 0.098869,
  "p_value": 0.376240,
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
  "y_mean": 6.5585e+10,
  "x_mean": 5.150588,
  "y_std": 2.9632e+09,
  "x_std": 0.82
}
```

## 📊 Available KPIs and Macro Variables

### Company KPIs
- `revenue`: Annual revenue
- `eps`: Earnings per share
- `ebitda`: EBITDA
- `price`: Stock price

### Macro Variables
- `EFFR`: Federal Funds Rate
- `CPIAUCSL`: Consumer Price Index
- `UNRATE`: Unemployment Rate
- `GDP`: Gross Domestic Product

## 🎨 Visualization Features

### Regression Plots

Each analysis generates a professional regression plot showing:

1. **Scatter Plot**: Raw data points with transparency
2. **Regression Line**: Fitted linear relationship (red)
3. **Trend Line**: Numpy polyfit comparison (blue dashed)
4. **Statistics Box**: Beta, R², p-value, and sample size
5. **Professional Styling**: Clean design with proper labels

**Plot Features**:
- High-resolution (300 DPI)
- Professional color scheme
- Clear axis labels and title
- Statistical annotations
- Grid for readability

## 📋 Usage Examples

### Python Service Usage

```python
from services.datahub import get_company_macro
from services.analysis import calc_beta, interpret_beta

# Get merged data
df = get_company_macro("MSFT", ["revenue"], ["EFFR"], years=10)

# Calculate beta
result = calc_beta(df, "revenue", "EFFR")

# Get interpretation
interpretation = interpret_beta(result['beta'], result['p_value'], result['r2'])

print(f"Beta: {result['beta']:.4f}")
print(f"R²: {result['r2']:.4f}")
print(f"P-value: {result['p_value']:.4f}")
```

### API Usage

```bash
curl -X POST "http://localhost:8000/analysis/beta" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "MSFT",
    "kpi": "revenue",
    "macro_variable": "EFFR",
    "years": 10
  }'
```

### JavaScript/Frontend Usage

```javascript
const response = await fetch('/analysis/beta', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    symbol: 'MSFT',
    kpi: 'revenue',
    macro_variable: 'EFFR',
    years: 10
  })
});

const result = await response.json();
console.log(`Beta: ${result.beta}`);
console.log(`R²: ${result.r2}`);
```

## 🔍 Interpretation Guide

### Beta Coefficient (β)
- **Positive β**: KPI increases with macro variable
- **Negative β**: KPI decreases with macro variable
- **Magnitude**: Strength of relationship

### R-squared (R²)
- **0.0-0.1**: Low explanatory power
- **0.1-0.5**: Moderate explanatory power
- **0.5-1.0**: High explanatory power

### P-value
- **< 0.05**: Statistically significant relationship
- **≥ 0.05**: No significant relationship

### Automated Insights

The system provides automated interpretation including:
- Statistical significance assessment
- Relationship direction and strength
- Explanatory power evaluation
- Actionable insights for decision-making

## 🧪 Testing

### Service Testing
```bash
cd backend
python3 test_analysis.py
```

### Endpoint Testing
```bash
cd backend
python3 test_beta_endpoint.py
```

### Manual Testing
```bash
# Start server
cd backend && python3 main.py

# Test endpoint
curl -X POST "http://localhost:8000/analysis/beta" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"MSFT","kpi":"revenue","macro_variable":"EFFR","years":10}'
```

## 🔧 Dependencies

### New Dependencies Added
- `matplotlib==3.8.4`: Plotting library
- `seaborn==0.13.2`: Statistical visualization
- `scipy==1.13.1`: Scientific computing
- `statsmodels==0.14.1`: Statistical modeling

### Installation
```bash
cd backend
pip install matplotlib seaborn scipy statsmodels
```

## 📁 File Structure

```
backend/
├── services/
│   ├── analysis.py          # Main analysis service
│   └── datahub.py           # Data merging service
├── static/
│   ├── beta_*.png           # Generated regression plots
│   └── ...
├── test_analysis.py         # Service tests
├── test_beta_endpoint.py    # Endpoint tests
└── main.py                  # FastAPI app with beta endpoint
```

## 🚀 Deployment

### Local Development
```bash
cd backend
python3 main.py
```

### Production
```bash
# Using the existing deployment scripts
./start_persistent.sh start
```

## 📈 Business Applications

### Risk Management
- Assess exposure to interest rate changes
- Evaluate inflation sensitivity
- Monitor economic risk factors

### Strategic Planning
- Understand macro-economic drivers
- Plan for different economic scenarios
- Optimize business strategies

### Investment Analysis
- Evaluate company resilience
- Compare sector sensitivities
- Identify investment opportunities

## 🔮 Future Enhancements

### Planned Features
1. **Multiple Regression**: Analyze multiple macro variables simultaneously
2. **Time Series Analysis**: Account for temporal dependencies
3. **Sector Comparison**: Compare sensitivities across industries
4. **Scenario Modeling**: Project KPI changes under different macro scenarios
5. **Interactive Plots**: Dynamic visualization with plotly

### Advanced Analytics
1. **Non-linear Relationships**: Polynomial and exponential models
2. **Lagged Effects**: Time-delayed impact analysis
3. **Volatility Analysis**: Risk-adjusted sensitivity measures
4. **Confidence Intervals**: Statistical uncertainty quantification

---

**The Beta Analysis feature provides powerful insights into how macroeconomic factors influence company performance, enabling data-driven decision making and risk management.** 🎯 