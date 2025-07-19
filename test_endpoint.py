#!/usr/bin/env python3
"""
Test script for the interest rate shock scenario endpoint
"""

import requests
import json
import time

def test_interest_shock_endpoint():
    """Test the interest shock endpoint with various scenarios"""
    
    base_url = "http://127.0.0.1:8000"
    
    # Test cases
    test_cases = [
        {
            "name": "AAPL +100bps shock",
            "data": {"symbol": "AAPL", "rate_delta": 0.01}
        },
        {
            "name": "AAPL +200bps shock", 
            "data": {"symbol": "AAPL", "rate_delta": 0.02}
        },
        {
            "name": "MSFT +150bps shock",
            "data": {"symbol": "MSFT", "rate_delta": 0.015}
        }
    ]
    
    print("🧪 Testing Interest Rate Shock Scenario Endpoint")
    print("=" * 60)
    
    # First check if server is running
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Server is running and healthy")
        else:
            print("❌ Server health check failed")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://127.0.0.1:8000")
        return
    
    print()
    
    # Test each scenario
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            response = requests.post(
                f"{base_url}/scenario/interest-shock",
                json=test_case['data'],
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Success!")
                print(f"   Base Margin: {result.get('base_margin', 'N/A')}")
                print(f"   Shock Margin: {result.get('shock_margin', 'N/A')}")
                print(f"   Delta Margin: {result.get('delta_margin', 'N/A')}")
                
                # Validate the results make sense
                if result.get('delta_margin', 0) <= 0:
                    print("   ✅ Delta is negative (expected for interest rate increase)")
                else:
                    print("   ⚠️  Delta is positive (unexpected)")
                    
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        
        print()

if __name__ == "__main__":
    test_interest_shock_endpoint() 