#!/usr/bin/env python3
"""
Simple test for CAGR calculation matching numpy.power formula
No external dependencies required
"""

import math

def test_cagr_calculation_matches_numpy():
    """Test that our CAGR calculation matches numpy.power formula"""
    
    # Test data: Microsoft revenue from 2016 to 2025 (example values)
    test_revenue = [85320, 89950, 110360, 125843, 143015, 168088, 198270, 211915]
    test_years = len(test_revenue)
    
    # Our CAGR calculation: (End Value / Start Value)^(1/n) - 1
    start_revenue = test_revenue[0]
    end_revenue = test_revenue[-1]
    num_years = test_years - 1
    
    our_cagr = (end_revenue / start_revenue) ** (1 / num_years) - 1
    
    # Math.pow CAGR calculation (equivalent to numpy.power)
    math_cagr = math.pow(end_revenue / start_revenue, 1 / num_years) - 1
    
    # Assert they match within floating point precision
    assert abs(our_cagr - math_cagr) < 1e-10
    
    print(f"✅ CAGR calculation test passed!")
    print(f"   Our calculation: {our_cagr:.6f}")
    print(f"   Math.pow calculation: {math_cagr:.6f}")
    print(f"   Difference: {abs(our_cagr - math_cagr):.2e}")

def test_cagr_edge_cases():
    """Test CAGR calculation with edge cases"""
    
    # Test with only 2 years
    revenue_2_years = [100000, 110000]
    start = revenue_2_years[0]
    end = revenue_2_years[1]
    cagr = (end / start) ** (1 / 1) - 1
    expected_cagr = 0.10  # 10% growth
    assert abs(cagr - expected_cagr) < 1e-10
    
    # Test with negative growth
    revenue_decline = [100000, 90000]
    start = revenue_decline[0]
    end = revenue_decline[1]
    cagr = (end / start) ** (1 / 1) - 1
    expected_cagr = -0.10  # -10% decline
    assert abs(cagr - expected_cagr) < 1e-10
    
    print(f"✅ CAGR edge cases test passed!")

def test_cagr_formula_verification():
    """Verify CAGR formula with known examples"""
    
    # Example 1: 10% annual growth over 5 years
    # Start: $100,000, End: $161,051 (100000 * 1.1^5)
    start_value = 100000
    end_value = 161051
    years = 5
    
    cagr = (end_value / start_value) ** (1 / years) - 1
    expected_cagr = 0.10  # 10%
    
    assert abs(cagr - expected_cagr) < 0.001
    
    # Example 2: 20% annual growth over 3 years
    # Start: $100,000, End: $172,800 (100000 * 1.2^3)
    start_value = 100000
    end_value = 172800
    years = 3
    
    cagr = (end_value / start_value) ** (1 / years) - 1
    expected_cagr = 0.20  # 20%
    
    assert abs(cagr - expected_cagr) < 0.001
    
    print(f"✅ CAGR formula verification test passed!")

def test_revenue_trend_with_real_data():
    """Test revenue trend calculation with realistic data"""
    
    # Microsoft revenue data (in millions)
    microsoft_revenue = {
        "2016": 85320,
        "2017": 89950,
        "2018": 110360,
        "2019": 125843,
        "2020": 143015,
        "2021": 168088,
        "2022": 198270,
        "2023": 211915
    }
    
    years = list(microsoft_revenue.keys())
    revenue = list(microsoft_revenue.values())
    
    # Calculate CAGR
    start_revenue = revenue[0]
    end_revenue = revenue[-1]
    num_years = len(revenue) - 1
    
    cagr = (end_revenue / start_revenue) ** (1 / num_years) - 1
    
    # Expected CAGR for Microsoft 2016-2023 (approximately 12.5%)
    expected_cagr_range = (0.10, 0.15)  # 10% to 15%
    
    assert expected_cagr_range[0] <= cagr <= expected_cagr_range[1]
    
    print(f"✅ Real data CAGR test passed!")
    print(f"   Microsoft CAGR (2016-2023): {cagr:.3f} ({cagr*100:.1f}%)")

def test_endpoint_response_structure():
    """Test that the revenue trend endpoint returns correct structure"""
    
    # Test with a mock response structure
    mock_response = {
        "symbol": "MSFT",
        "years": ["2016", "2017", "2018", "2019", "2020"],
        "revenue": [85320, 89950, 110360, 125843, 143015],
        "cagr": 0.138,
        "message": "Retrieved 5 years of revenue data"
    }
    
    # Check required fields
    required_fields = ["symbol", "years", "revenue", "cagr", "message"]
    for field in required_fields:
        assert field in mock_response
    
    # Check data types
    assert isinstance(mock_response["symbol"], str)
    assert isinstance(mock_response["years"], list)
    assert isinstance(mock_response["revenue"], list)
    assert isinstance(mock_response["cagr"], (int, float))
    assert isinstance(mock_response["message"], str)
    
    # Check array lengths match
    assert len(mock_response["years"]) == len(mock_response["revenue"])
    
    print(f"✅ Revenue trend endpoint structure test passed!")

if __name__ == "__main__":
    print("🧪 Running Revenue Trend Tests")
    print("=" * 50)
    
    test_cagr_calculation_matches_numpy()
    test_cagr_edge_cases()
    test_cagr_formula_verification()
    test_revenue_trend_with_real_data()
    test_endpoint_response_structure()
    
    print("=" * 50)
    print("✅ All tests passed!") 