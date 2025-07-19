# Scenario Matrix Frontend Table Schema

## Endpoint
`GET /scenario/matrix/{symbol}`

## Response Format
```json
[
  {"scenario": "base", "net_profit": 41921420000.0},
  {"scenario": "+inf", "net_profit": 41416500000.0},
  {"scenario": "+rate", "net_profit": 41891964200.0},
  {"scenario": "+both", "net_profit": 41387044200.0}
]
```

## Frontend Table Schema

### Field Order
1. **Scenario** (string) - Scenario identifier
2. **Net Profit** (number) - Projected net profit in dollars

### Table Structure
| Column | Type | Description | Example |
|--------|------|-------------|---------|
| Scenario | string | Scenario name/identifier | "base", "+inf", "+rate", "+both" |
| Net Profit | currency | Projected net profit | $41,921,420,000 |

### Scenario Descriptions
- **base**: No changes to inflation or interest rates
- **+inf**: +1% inflation affecting cost of goods sold
- **+rate**: +1% interest rate affecting interest expense  
- **+both**: +1% both inflation and interest rate

### Frontend Implementation Notes

#### Data Formatting
- **Net Profit**: Format as currency with commas and dollar sign
- **Scenario**: Display with proper labels (e.g., "Base", "+1% Inflation", etc.)

#### Table Features
- Sortable by Net Profit (descending by default)
- Color coding: Base scenario in green, others in neutral colors
- Percentage change calculation from base scenario
- Responsive design for mobile/desktop

#### Example Frontend Code
```javascript
// Format currency
const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value);
};

// Calculate percentage change from base
const calculateChange = (baseValue, currentValue) => {
  return ((currentValue - baseValue) / baseValue * 100).toFixed(2);
};
```

#### Dashboard Integration
- Add to existing analytics dashboard
- Include company selector dropdown
- Real-time data refresh capability
- Export to CSV/PDF functionality 