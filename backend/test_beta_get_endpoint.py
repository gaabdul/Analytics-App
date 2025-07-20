#!/usr/bin/env python3
"""
Test script for the GET /beta/{symbol} endpoint.
"""

import requests
import json

def test_beta_get_endpoint():
    """Test the GET beta analysis endpoint."""
    
    print("=== GET Beta Analysis Endpoint Test ===\n")
    
    # Test cases
    test_cases = [
        {
            "url": "/beta/MSFT?kpi=revenue&macro=EFFR&years=10",
            "description": "MSFT Revenue vs EFFR (10 years)"
        },
        {
            "url": "/beta/AAPL?kpi=revenue&macro=CPIAUCSL&years=5",
            "description": "AAPL Revenue vs CPI (5 years)"
        },
        {
            "url": "/beta/MSFT?kpi=revenue&macro=EFFR&years=8",
            "description": "MSFT Revenue vs EFFR (8 years)"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. Testing: {test_case['description']}")
        print(f"   URL: {test_case['url']}")
        
        try:
            # Make request to the endpoint
            response = requests.get(f"http://127.0.0.1:8000{test_case['url']}")
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("   ✅ Success!")
                print(f"   Symbol: {result['symbol']}")
                print(f"   KPI: {result['kpi']}")
                print(f"   Macro: {result['macro_variable']}")
                print(f"   Years: {result['years']}")
                print(f"   Beta: {result['beta']:.6f}")
                print(f"   R²: {result['r2']:.6f}")
                print(f"   P-value: {result['p_value']:.6f}")
                print(f"   Observations: {result['n_observations']}")
                print(f"   Plot URL: {result['plot_url']}")
                
                # Print interpretation
                interpretation = result['interpretation']
                print(f"   Significance: {interpretation['significance']}")
                print(f"   Direction: {interpretation['direction']}")
                print(f"   Strength: {interpretation['strength']}")
                print(f"   Explained Variance: {interpretation['explained_variance']}")
                
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection Error: Make sure the server is running on http://127.0.0.1:8000")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    # Test error cases
    print("4. Testing Error Cases:")
    
    error_cases = [
        {
            "url": "/beta/INVALID?kpi=revenue&macro=EFFR&years=10",
            "description": "Invalid symbol"
        },
        {
            "url": "/beta/MSFT?kpi=invalid&macro=EFFR&years=10",
            "description": "Invalid KPI"
        },
        {
            "url": "/beta/MSFT?kpi=revenue&macro=INVALID&years=10",
            "description": "Invalid macro variable"
        },
        {
            "url": "/beta/MSFT?kpi=revenue&macro=EFFR&years=1",
            "description": "Invalid years (too few)"
        },
        {
            "url": "/beta/MSFT?kpi=revenue&macro=EFFR&years=25",
            "description": "Invalid years (too many)"
        }
    ]
    
    for i, error_case in enumerate(error_cases, 1):
        print(f"   {i}. {error_case['description']}")
        
        try:
            response = requests.get(f"http://127.0.0.1:8000{error_case['url']}")
            print(f"      Status: {response.status_code}")
            if response.status_code != 200:
                print(f"      ✅ Expected error: {response.json().get('detail', 'Unknown error')}")
            else:
                print(f"      ❌ Unexpected success")
        except Exception as e:
            print(f"      ❌ Error: {e}")
        
        print()
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_beta_get_endpoint() 