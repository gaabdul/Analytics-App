#!/usr/bin/env python3
"""
Test script for the scenario matrix endpoint
"""

import requests
import json

def test_scenario_matrix():
    """Test the scenario matrix endpoint"""
    
    print("🧪 Testing Scenario Matrix Endpoint")
    print("=" * 50)
    
    # Test symbols
    test_symbols = ["AAPL", "MSFT", "GOOGL"]
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}:")
        print("-" * 30)
        
        try:
            response = requests.get(
                f"http://127.0.0.1:8000/scenario/matrix/{symbol}",
                timeout=10
            )
            
            if response.status_code == 200:
                results = response.json()
                print("✅ Success!")
                
                # Display results in a table format
                print(f"{'Scenario':<10} {'Net Profit':<15}")
                print("-" * 25)
                
                for result in results:
                    scenario = result.get('scenario', 'N/A')
                    net_profit = result.get('net_profit', 0)
                    
                    # Format net profit with commas
                    formatted_profit = f"${net_profit:,.0f}" if net_profit > 0 else f"${net_profit:,.0f}"
                    print(f"{scenario:<10} {formatted_profit:<15}")
                
                # Validate expected scenarios
                expected_scenarios = ["base", "+inf", "+rate", "+both"]
                actual_scenarios = [r.get('scenario') for r in results]
                
                if all(scenario in actual_scenarios for scenario in expected_scenarios):
                    print("✅ All expected scenarios present")
                else:
                    print("❌ Missing expected scenarios")
                    
                # Check if base scenario has highest profit (expected)
                base_profit = next((r.get('net_profit', 0) for r in results if r.get('scenario') == 'base'), 0)
                other_profits = [r.get('net_profit', 0) for r in results if r.get('scenario') != 'base']
                
                if all(base_profit >= profit for profit in other_profits):
                    print("✅ Base scenario has highest profit (expected)")
                else:
                    print("⚠️  Base scenario doesn't have highest profit")
                    
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Make sure it's running on http://127.0.0.1:8000")
            break
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_scenario_matrix() 