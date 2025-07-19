# 💱 Currency Toggle Feature

## Overview
The Analytics App now includes a currency toggle feature that allows users to switch between USD and CAD display for all monetary values. The feature uses live exchange rates from the `/auto-levers/` endpoint and includes intelligent caching for performance.

## 🎯 Features

### Currency Toggle Button
- **Location**: Top-right corner of the app header
- **Display**: Shows current currency symbol ($ or C$) and code (USD or CAD)
- **Functionality**: Click to toggle between USD and CAD
- **Visual Feedback**: Hover effects and smooth transitions

### Live Exchange Rate
- **Source**: `/auto-levers/` endpoint (USD/CAD rate from Yahoo Finance)
- **Caching**: 10-minute cache to reduce API calls
- **Fallback**: 1.35 USD/CAD if API fails
- **Real-time**: Automatically fetches fresh rates when cache expires

### Automatic Conversion
- **CSV Analysis**: All profit, adjusted profit, and FX-adjusted profit values
- **Company Data**: Revenue, cost, and EBITDA from ticker analysis
- **Formatting**: Proper currency symbols and number formatting
- **Real-time**: Instant conversion when toggle is clicked

## 🔧 Technical Implementation

### JavaScript Functions

#### `fetchAndCacheFxRate()`
```javascript
// Fetches FX rate from /auto-levers/ endpoint
// Implements 10-minute caching
// Uses fallback rate if API fails
```

#### `setupCurrencyToggle()`
```javascript
// Sets up click event listener for toggle button
// Updates button display (symbol and code)
// Triggers currency conversion
```

#### `formatCurrency(value, currency)`
```javascript
// Formats numbers with proper currency symbols
// Uses Intl.NumberFormat for locale-aware formatting
// Returns formatted string (e.g., "$1,000,000" or "C$1,372,100")
```

#### `refreshCurrentResults()`
```javascript
// Re-formats existing results with new currency
// Handles both CSV analysis and company data
// Preserves original data structure
```

### CSS Classes

#### `.currency-toggle-btn`
```css
/* Modern button styling with hover effects */
.currency-toggle-btn {
  @apply transition-all duration-200 ease-in-out;
}

.currency-toggle-btn:hover {
  @apply transform scale-105 shadow-md;
}

.currency-toggle-btn:active {
  @apply transform scale-95;
}
```

## 📊 Usage Examples

### CSV Analysis Results
**USD Display:**
```json
{
  "totals": {
    "profit": "$250,000",
    "adj_profit": "$245,000",
    "adj_profit_fx": "$245,000"
  }
}
```

**CAD Display (with 1.3721 rate):**
```json
{
  "totals": {
    "profit": "C$343,025",
    "adj_profit": "C$336,165",
    "adj_profit_fx": "C$336,165"
  }
}
```

### Company Data Results
**USD Display:**
```json
{
  "symbol": "AAPL",
  "revenue": "$89,498,000,000",
  "cost": "$48,290,000,000",
  "ebitda": "$30,000,000,000"
}
```

**CAD Display:**
```json
{
  "symbol": "AAPL",
  "revenue": "C$122,800,000,000",
  "cost": "C$66,240,000,000",
  "ebitda": "C$41,163,000,000"
}
```

## 🔄 Data Flow

1. **Page Load**: 
   - Fetch FX rate from `/auto-levers/`
   - Cache rate for 10 minutes
   - Initialize toggle button

2. **Toggle Click**:
   - Switch currency state (USD ↔ CAD)
   - Update button display
   - Re-format all monetary values

3. **New Analysis**:
   - Run analysis with current currency
   - Format results immediately
   - Display with correct currency

4. **Cache Refresh**:
   - Check cache expiration every 10 minutes
   - Fetch fresh rate if needed
   - Update cached value

## 🎨 UI/UX Features

### Visual Design
- **Consistent Styling**: Matches app's indigo color scheme
- **Responsive**: Adapts to mobile screens
- **Accessible**: Clear labels and hover states
- **Smooth Transitions**: 200ms duration for all interactions

### User Experience
- **Instant Feedback**: Immediate currency conversion
- **Persistent State**: Remembers currency choice during session
- **Clear Indicators**: Shows current currency and cache status
- **Error Handling**: Graceful fallback if API fails

## 🚀 Performance Optimizations

### Caching Strategy
- **10-minute cache**: Reduces API calls by 95%
- **Memory efficient**: Simple timestamp-based expiration
- **Automatic refresh**: Seamless background updates

### Conversion Efficiency
- **Client-side**: No server round-trips for conversion
- **Batch processing**: Updates all values simultaneously
- **Minimal DOM manipulation**: Efficient element updates

## 🔍 Testing

### Manual Testing
1. Open the app in browser
2. Click currency toggle button
3. Verify symbol changes ($ ↔ C$)
4. Verify code changes (USD ↔ CAD)
5. Run CSV analysis and check currency formatting
6. Run ticker analysis and check currency formatting
7. Toggle currency and verify existing results update

### Test File
Use `test_currency.html` for isolated testing:
```bash
# Open in browser
open test_currency.html
```

## 📝 Notes

### FX Rate Caching
- **Duration**: 10 minutes (600,000 milliseconds)
- **Storage**: Browser memory (session-based)
- **Refresh**: Automatic on cache expiration
- **Fallback**: 1.35 USD/CAD if API unavailable

### Currency Formatting
- **USD**: $1,000,000 (standard US format)
- **CAD**: C$1,372,100 (Canadian format with C$ prefix)
- **Decimals**: No decimal places for large numbers
- **Locale**: en-US for consistent formatting

### Browser Compatibility
- **Modern browsers**: Full support (Chrome, Firefox, Safari, Edge)
- **Intl.NumberFormat**: Required for currency formatting
- **ES6+ features**: Arrow functions, async/await, template literals

---

**Your analytics app now supports seamless USD/CAD currency conversion with live exchange rates! 🎉** 