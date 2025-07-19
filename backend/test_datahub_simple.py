#!/usr/bin/env python3
"""
Simple test script for the DataHub service using existing database data.
"""

import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.datahub import get_company_macro, get_available_kpis, get_available_macro_series

def test_datahub_with_real_data():
    """Test the datahub service with real database data."""
    
    print("=== DataHub Service Test ===\n")
    
    # Test 1: Get available KPIs
    print("1. Available KPIs:")
    kpis = get_available_kpis()
    print(f"   {kpis}\n")
    
    # Test 2: Get available macro series
    print("2. Available Macro Series:")
    series = get_available_macro_series()
    print(f"   {series}\n")
    
    # Test 3: Get company macro data for MSFT
    print("3. Company Macro Data for MSFT:")
    try:
        df = get_company_macro(
            symbol="MSFT",
            kpis=["revenue", "eps"],
            macro_ids=["EFFR", "CPIAUCSL"],
            years=5
        )
        
        if not df.empty:
            print(f"   DataFrame shape: {df.shape}")
            print(f"   Columns: {list(df.columns)}")
            print(f"   Fiscal years: {df['fiscal_year'].tolist()}")
            print("\n   First few rows:")
            print(df.head().to_string(index=False))
        else:
            print("   No data found for MSFT")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_datahub_with_real_data() 