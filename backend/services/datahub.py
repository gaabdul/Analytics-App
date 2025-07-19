"""
DataHub Service for merging company KPIs with macroeconomic indicators.

This service provides functionality to query and merge company financial data
with macroeconomic indicators, aligned by fiscal year for time series analysis.
"""

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, text
from typing import List, Optional
from datetime import datetime, date
import logging

from db import CompanyFact, MacroFact, get_db

logger = logging.getLogger(__name__)

def get_company_macro(
    symbol: str, 
    kpis: List[str], 
    macro_ids: List[str], 
    years: int = 10
) -> pd.DataFrame:
    """
    Retrieve and merge company KPIs with macroeconomic indicators aligned by fiscal year.
    
    This function queries the last N fiscal years of company KPIs and resamples
    macroeconomic indicators to fiscal-year frequency. For macro indicators,
    it uses the average value over the fiscal year period.
    
    Args:
        symbol (str): Company stock symbol (e.g., 'MSFT', 'AAPL')
        kpis (List[str]): List of company KPIs to retrieve 
                         (e.g., ['revenue', 'eps', 'ebitda'])
        macro_ids (List[str]): List of macroeconomic series IDs
                              (e.g., ['EFFR', 'CPIAUCSL'])
        years (int): Number of fiscal years to retrieve (default: 10)
    
    Returns:
        pd.DataFrame: DataFrame indexed by fiscal_year with company + macro columns.
                     Columns include: fiscal_year, symbol, {kpi_columns}, {macro_columns}
    
    Raises:
        ValueError: If invalid KPIs or macro_ids are provided
        Exception: If database query fails
    
    Example:
        >>> df = get_company_macro('MSFT', ['revenue', 'eps'], ['EFFR', 'CPIAUCSL'])
        >>> print(df.columns)
        ['symbol', 'revenue', 'eps', 'EFFR', 'CPIAUCSL']
    """
    
    # Validate inputs
    valid_kpis = ['revenue', 'cost', 'ebitda', 'eps', 'price']
    for kpi in kpis:
        if kpi not in valid_kpis:
            raise ValueError(f"Invalid KPI: {kpi}. Valid KPIs: {valid_kpis}")
    
    # Get database session
    db = next(get_db())
    
    try:
        # 1. Query company KPIs for the last N fiscal years
        company_query = db.query(CompanyFact).filter(
            CompanyFact.symbol == symbol
        ).order_by(
            CompanyFact.fiscal_year.desc()
        ).limit(years)
        
        # Execute query and convert to DataFrame
        company_results = company_query.all()
        company_data = pd.DataFrame([
            {
                'fiscal_year': result.fiscal_year,
                'symbol': result.symbol,
                **{kpi: getattr(result, kpi) for kpi in kpis}
            }
            for result in company_results
        ])
        
        if company_data.empty:
            logger.warning(f"No company data found for symbol: {symbol}")
            return pd.DataFrame()
        
        # Get the fiscal year range for macro data alignment
        min_fy = company_data['fiscal_year'].min()
        max_fy = company_data['fiscal_year'].max()
        
        # 2. Query and resample macro indicators
        macro_data = {}
        
        for macro_id in macro_ids:
            # Query macro data for the fiscal year range
            # We need data from the start of the earliest fiscal year to end of latest
            macro_query = db.query(MacroFact).filter(
                and_(
                    MacroFact.series_id == macro_id,
                    MacroFact.date >= date(min_fy, 1, 1),  # Start of earliest FY
                    MacroFact.date <= date(max_fy, 12, 31)  # End of latest FY
                )
            ).order_by(MacroFact.date)
            
            # Execute query and convert to DataFrame
            macro_results = macro_query.all()
            macro_df = pd.DataFrame([
                {
                    'date': result.date,
                    'value': result.value
                }
                for result in macro_results
            ])
            
            if macro_df.empty:
                logger.warning(f"No macro data found for series: {macro_id}")
                macro_data[macro_id] = pd.Series(dtype=float)
                continue
            
            # Convert date column to datetime
            macro_df['date'] = pd.to_datetime(macro_df['date'])
            macro_df.set_index('date', inplace=True)
            
            # Resample to fiscal year frequency
            # For most macro indicators, we use the average over the fiscal year
            # For rates (like EFFR), we use the average
            # For levels (like CPI), we use the last value of the fiscal year
            if macro_id in ['EFFR', 'UNRATE']:  # Rates - use average
                resampled = macro_df['value'].resample('YE').mean()
            else:  # Levels - use last value of fiscal year
                resampled = macro_df['value'].resample('YE').last()
            
            # Align with fiscal years (assuming fiscal year ends in calendar year)
            resampled.index = resampled.index.year
            macro_data[macro_id] = resampled
        
        # 3. Merge company and macro data
        # Prepare company data
        company_result = company_data.copy()
        company_result.set_index('fiscal_year', inplace=True)
        
        # Add macro data columns
        for macro_id, macro_series in macro_data.items():
            company_result[macro_id] = macro_series
        
        # Sort by fiscal year (descending)
        company_result.sort_index(ascending=False, inplace=True)
        
        # Reset index to make fiscal_year a column
        company_result.reset_index(inplace=True)
        
        logger.info(f"Successfully merged data for {symbol}: {len(company_result)} fiscal years, "
                   f"{len(kpis)} KPIs, {len(macro_ids)} macro indicators")
        
        return company_result
        
    except Exception as e:
        logger.error(f"Error in get_company_macro: {str(e)}")
        raise
    finally:
        db.close()


def get_available_kpis() -> List[str]:
    """Get list of available KPIs in the database."""
    return ['revenue', 'cost', 'ebitda', 'eps', 'price']


def get_available_macro_series() -> List[str]:
    """Get list of available macroeconomic series in the database."""
    db = next(get_db())
    try:
        result = db.query(MacroFact.series_id).distinct().all()
        return [row[0] for row in result]
    finally:
        db.close()


# Example usage and testing
if __name__ == "__main__":
    # Test the function
    try:
        df = get_company_macro(
            symbol="MSFT", 
            kpis=["revenue", "eps"], 
            macro_ids=["EFFR", "CPIAUCSL"],
            years=5
        )
        print("Test successful!")
        print(f"DataFrame shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print("\nFirst few rows:")
        print(df.head())
    except Exception as e:
        print(f"Test failed: {e}") 