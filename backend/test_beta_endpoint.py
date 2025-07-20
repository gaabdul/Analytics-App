#!/usr/bin/env python3
"""
Test script for the beta analysis endpoint.
"""

import requests
import json

def test_beta_analysis_endpoint():
    """Test the beta analysis endpoint."""
    
    print("=== Beta Analysis Endpoint Test ===\n")
    
    # Test data
    test_request = {
        "symbol": "MSFT",
        "kpi": "revenue",
        "macro_variable": "EFFR",
        "years": 10
    }
    
    print("1. Testing beta analysis endpoint...")
    print(f"   Request: {json.dumps(test_request, indent=2)}")
    print()
    
    try:
        # Make request to the endpoint
        response = requests.post(
            "http://127.0.0.1:8000/analysis/beta",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Success!")
            print(f"   Beta: {result['beta']:.6f}")
            print(f"   R²: {result['r2']:.6f}")
            print(f"   P-value: {result['p_value']:.6f}")
            print(f"   Observations: {result['n_observations']}")
            print(f"   Plot URL: {result['plot_url']}")
            print()
            
            # Print interpretation
            print("   Interpretation:")
            interpretation = result['interpretation']
            print(f"   - Significance: {interpretation['significance']}")
            print(f"   - Direction: {interpretation['direction']}")
            print(f"   - Strength: {interpretation['strength']}")
            print(f"   - Explained Variance: {interpretation['explained_variance']}")
            print("   - Insights:")
            for insight in interpretation['insights']:
                print(f"     * {insight}")
            print()
            
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            print()
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection Error: Make sure the server is running on http://127.0.0.1:8000")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print()
    
    # Test with different parameters
    print("2. Testing with different parameters...")
    
    test_cases = [
        {"symbol": "AAPL", "kpi": "revenue", "macro_variable": "EFFR", "years": 5},
        {"symbol": "MSFT", "kpi": "revenue", "macro_variable": "CPIAUCSL", "years": 8},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"   Test {i}: {test_case['symbol']} {test_case['kpi']} vs {test_case['macro_variable']}")
        
        try:
            response = requests.post(
                "http://127.0.0.1:8000/analysis/beta",
                json=test_case,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"     ✅ Beta: {result['beta']:.6f}, R²: {result['r2']:.6f}, p: {result['p_value']:.6f}")
            else:
                print(f"     ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"     ❌ Error: {e}")
        
        print()
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_beta_analysis_endpoint() 