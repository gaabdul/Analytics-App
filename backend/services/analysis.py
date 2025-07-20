"""
Analysis Service for calculating sensitivity (beta) of KPIs to macroeconomic variables.

This service provides functionality to perform linear regression analysis
to determine how sensitive a company KPI is to changes in macroeconomic indicators.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from statsmodels.regression.linear_model import OLS
from statsmodels.tools.tools import add_constant
import os
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

def calc_beta(df: pd.DataFrame, y_col: str, x_col: str) -> Dict:
    """
    Calculate the sensitivity (beta) of a KPI to a macroeconomic variable using linear regression.
    
    This function performs a simple linear regression y = α + βx and returns
    the beta coefficient, R-squared, and p-value. It also generates a regression plot.
    
    Args:
        df (pd.DataFrame): DataFrame containing the merged company and macro data
        y_col (str): Name of the dependent variable (KPI column)
        x_col (str): Name of the independent variable (macro column)
    
    Returns:
        Dict: Dictionary containing beta, r2, p_value, and plot_url
        
    Raises:
        ValueError: If required columns are missing or data is insufficient
        Exception: If regression analysis fails
    
    Example:
        >>> df = get_company_macro('MSFT', ['eps'], ['EFFR'], years=10)
        >>> result = calc_beta(df, 'eps', 'EFFR')
        >>> print(f"Beta: {result['beta']:.4f}, R²: {result['r2']:.4f}")
    """
    
    # Validate inputs
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    if y_col not in df.columns:
        raise ValueError(f"Column '{y_col}' not found in DataFrame. Available columns: {list(df.columns)}")
    
    if x_col not in df.columns:
        raise ValueError(f"Column '{x_col}' not found in DataFrame. Available columns: {list(df.columns)}")
    
    # Prepare data for regression
    regression_data = df[[y_col, x_col]].dropna()
    
    if len(regression_data) < 3:
        raise ValueError(f"Insufficient data for regression. Need at least 3 observations, got {len(regression_data)}")
    
    # Check if we have enough non-null values
    if regression_data[y_col].isna().sum() == len(regression_data):
        raise ValueError(f"All values for {y_col} are null")
    
    if regression_data[x_col].isna().sum() == len(regression_data):
        raise ValueError(f"All values for {x_col} are null")
    
    y = regression_data[y_col]
    x = regression_data[x_col]
    
    try:
        # Method 1: Using statsmodels (more comprehensive)
        X = add_constant(x)
        model = OLS(y, X)
        results = model.fit()
        
        # Fix indexing to use column names instead of positions
        x_col_name = x.name if hasattr(x, 'name') else x_col
        beta = results.params[x_col_name]  # Coefficient of x (not constant)
        r2 = results.rsquared
        p_value = results.pvalues[x_col_name]  # p-value for x coefficient
        
        # Method 2: Using numpy.polyfit as backup (simpler)
        # coeffs = np.polyfit(x, y, 1)
        # beta_numpy = coeffs[0]
        # y_pred = np.polyval(coeffs, x)
        # r2_numpy = 1 - np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2)
        
        # Generate regression plot
        plot_url = _create_regression_plot(x, y, y_col, x_col, beta, r2, p_value)
        
        result = {
            'beta': float(beta),
            'r2': float(r2),
            'p_value': float(p_value),
            'plot_url': plot_url,
            'n_observations': len(regression_data),
            'y_mean': float(y.mean()),
            'x_mean': float(x.mean()),
            'y_std': float(y.std()),
            'x_std': float(x.std())
        }
        
        logger.info(f"Regression analysis completed: {y_col} vs {x_col}")
        logger.info(f"Beta: {beta:.4f}, R²: {r2:.4f}, p-value: {p_value:.4f}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in regression analysis: {str(e)}")
        raise


def _create_regression_plot(x: pd.Series, y: pd.Series, y_col: str, x_col: str, 
                          beta: float, r2: float, p_value: float) -> str:
    """
    Create a regression plot and save it to static directory.
    
    Args:
        x: Independent variable data
        y: Dependent variable data
        y_col: Name of dependent variable
        x_col: Name of independent variable
        beta: Regression coefficient
        r2: R-squared value
        p_value: P-value
    
    Returns:
        str: URL path to the saved plot
    """
    
    # Set up the plot style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create scatter plot
    ax.scatter(x, y, alpha=0.7, s=60, edgecolors='black', linewidth=0.5)
    
    # Add regression line
    x_range = np.linspace(x.min(), x.max(), 100)
    y_pred = beta * x_range + (y.mean() - beta * x.mean())  # y = βx + (ȳ - βx̄)
    ax.plot(x_range, y_pred, color='red', linewidth=2, label=f'Regression Line (β={beta:.4f})')
    
    # Add trend line using numpy polyfit for comparison
    coeffs = np.polyfit(x, y, 1)
    y_trend = np.polyval(coeffs, x_range)
    ax.plot(x_range, y_trend, color='blue', linestyle='--', alpha=0.7, 
            label=f'Polyfit Line (β={coeffs[0]:.4f})')
    
    # Customize the plot
    ax.set_xlabel(f'{x_col}', fontsize=12, fontweight='bold')
    ax.set_ylabel(f'{y_col}', fontsize=12, fontweight='bold')
    ax.set_title(f'Sensitivity Analysis: {y_col} vs {x_col}', fontsize=14, fontweight='bold')
    
    # Add statistics text box
    stats_text = f'β = {beta:.4f}\nR² = {r2:.4f}\np-value = {p_value:.4f}\nn = {len(x)}'
    ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Add legend
    ax.legend(loc='upper left')
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    # Tight layout
    plt.tight_layout()
    
    # Create static directory if it doesn't exist
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    # Save plot
    plot_filename = f'beta_{y_col}_{x_col}.png'
    plot_path = os.path.join(static_dir, plot_filename)
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # Return URL path
    plot_url = f'/static/{plot_filename}'
    
    logger.info(f"Regression plot saved: {plot_path}")
    return plot_url


def calc_multiple_betas(df: pd.DataFrame, y_col: str, x_cols: list) -> Dict:
    """
    Calculate beta for multiple macroeconomic variables against a single KPI.
    
    Args:
        df (pd.DataFrame): DataFrame containing the merged data
        y_col (str): Name of the dependent variable (KPI)
        x_cols (list): List of independent variables (macro columns)
    
    Returns:
        Dict: Dictionary with results for each variable
    """
    
    results = {}
    
    for x_col in x_cols:
        try:
            result = calc_beta(df, y_col, x_col)
            results[x_col] = result
        except Exception as e:
            logger.warning(f"Failed to calculate beta for {y_col} vs {x_col}: {str(e)}")
            results[x_col] = {
                'error': str(e),
                'beta': None,
                'r2': None,
                'p_value': None,
                'plot_url': None
            }
    
    return results


def interpret_beta(beta: float, p_value: float, r2: float) -> Dict:
    """
    Interpret the regression results and provide insights.
    
    Args:
        beta (float): Regression coefficient
        p_value (float): P-value
        r2 (float): R-squared value
    
    Returns:
        Dict: Interpretation of the results
    """
    
    interpretation = {
        'significance': 'Not significant' if p_value > 0.05 else 'Significant',
        'direction': 'Positive' if beta > 0 else 'Negative',
        'strength': 'Weak' if abs(beta) < 0.1 else 'Moderate' if abs(beta) < 0.5 else 'Strong',
        'explained_variance': 'Low' if r2 < 0.1 else 'Moderate' if r2 < 0.5 else 'High',
        'insights': []
    }
    
    # Generate insights
    if p_value < 0.05:
        if beta > 0:
            interpretation['insights'].append(f"Significant positive relationship: {abs(beta):.4f} unit increase in macro variable corresponds to {abs(beta):.4f} unit increase in KPI")
        else:
            interpretation['insights'].append(f"Significant negative relationship: {abs(beta):.4f} unit increase in macro variable corresponds to {abs(beta):.4f} unit decrease in KPI")
    else:
        interpretation['insights'].append("No significant relationship found between the variables")
    
    if r2 > 0.5:
        interpretation['insights'].append(f"High explanatory power: {r2:.1%} of KPI variance explained by macro variable")
    elif r2 > 0.1:
        interpretation['insights'].append(f"Moderate explanatory power: {r2:.1%} of KPI variance explained by macro variable")
    else:
        interpretation['insights'].append(f"Low explanatory power: {r2:.1%} of KPI variance explained by macro variable")
    
    return interpretation


# Example usage and testing
if __name__ == "__main__":
    # Test the function with sample data
    try:
        from services.datahub import get_company_macro
        
        # Get sample data
        df = get_company_macro(
            symbol="MSFT",
            kpis=["revenue", "eps"],
            macro_ids=["EFFR", "CPIAUCSL"],
            years=10
        )
        
        if not df.empty:
            # Test beta calculation
            result = calc_beta(df, "revenue", "EFFR")
            print("Test successful!")
            print(f"Beta: {result['beta']:.4f}")
            print(f"R²: {result['r2']:.4f}")
            print(f"P-value: {result['p_value']:.4f}")
            print(f"Plot URL: {result['plot_url']}")
            
            # Test interpretation
            interpretation = interpret_beta(result['beta'], result['p_value'], result['r2'])
            print(f"\nInterpretation: {interpretation}")
        else:
            print("No data available for testing")
            
    except Exception as e:
        print(f"Test failed: {e}") 