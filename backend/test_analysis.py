#!/usr/bin/env python3
"""
Test script for the Analysis service using real database data.
"""

import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.analysis import calc_beta, calc_multiple_betas, interpret_beta
from services.datahub import get_company_macro

def test_analysis_service():
    """Test the analysis service with real database data."""
    
    print("=== Analysis Service Test ===\n")
    
    # Test 1: Get sample data
    print("1. Getting sample data for MSFT...")
    try:
        df = get_company_macro(
            symbol="MSFT",
            kpis=["revenue", "eps"],
            macro_ids=["EFFR", "CPIAUCSL"],
            years=10
        )
        
        if df.empty:
            print("   No data found for MSFT")
            return
        else:
            print(f"   Retrieved {len(df)} rows of data")
            print(f"   Columns: {list(df.columns)}")
            print(f"   Sample data:")
            print(df.head().to_string(index=False))
            print()
    except Exception as e:
        print(f"   Error getting data: {e}")
        return
    
    # Test 2: Calculate beta for revenue vs EFFR
    print("2. Calculating beta for Revenue vs EFFR:")
    try:
        result = calc_beta(df, "revenue", "EFFR")
        print(f"   Beta: {result['beta']:.6f}")
        print(f"   R²: {result['r2']:.6f}")
        print(f"   P-value: {result['p_value']:.6f}")
        print(f"   Observations: {result['n_observations']}")
        print(f"   Plot URL: {result['plot_url']}")
        print()
        
        # Test interpretation
        interpretation = interpret_beta(result['beta'], result['p_value'], result['r2'])
        print("   Interpretation:")
        print(f"   - Significance: {interpretation['significance']}")
        print(f"   - Direction: {interpretation['direction']}")
        print(f"   - Strength: {interpretation['strength']}")
        print(f"   - Explained Variance: {interpretation['explained_variance']}")
        print("   - Insights:")
        for insight in interpretation['insights']:
            print(f"     * {insight}")
        print()
        
    except Exception as e:
        print(f"   Error calculating beta: {e}")
        print()
    
    # Test 3: Calculate multiple betas
    print("3. Calculating multiple betas for Revenue:")
    try:
        multiple_results = calc_multiple_betas(df, "revenue", ["EFFR", "CPIAUCSL"])
        
        for macro_var, result in multiple_results.items():
            if 'error' in result:
                print(f"   {macro_var}: Error - {result['error']}")
            else:
                print(f"   {macro_var}: β={result['beta']:.6f}, R²={result['r2']:.6f}, p={result['p_value']:.6f}")
        print()
        
    except Exception as e:
        print(f"   Error calculating multiple betas: {e}")
        print()
    
    # Test 4: Test with different KPI
    print("4. Testing with EPS (if available):")
    try:
        if 'eps' in df.columns and not df['eps'].isna().all():
            eps_result = calc_beta(df, "eps", "EFFR")
            print(f"   EPS vs EFFR: β={eps_result['beta']:.6f}, R²={eps_result['r2']:.6f}, p={eps_result['p_value']:.6f}")
        else:
            print("   EPS data not available or all null")
        print()
    except Exception as e:
        print(f"   Error testing EPS: {e}")
        print()
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_analysis_service() 