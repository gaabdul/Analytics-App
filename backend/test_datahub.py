"""
Unit tests for the DataHub service.

Tests the get_company_macro function to ensure it correctly merges
company KPIs with macroeconomic indicators aligned by fiscal year.
"""

import unittest
import pandas as pd
import sys
import os
from datetime import date, datetime

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.datahub import get_company_macro, get_available_kpis, get_available_macro_series
from db import CompanyFact, MacroFact, get_db, create_tables
from sqlalchemy.orm import Session


class TestDataHub(unittest.TestCase):
    """Test cases for the DataHub service."""
    
    def setUp(self):
        """Set up test database and sample data."""
        # Create tables
        create_tables()
        
        # Get database session
        self.db = next(get_db())
        
        # Insert test company data
        self._insert_test_company_data()
        
        # Insert test macro data
        self._insert_test_macro_data()
    
    def tearDown(self):
        """Clean up after tests."""
        self.db.close()
    
    def _insert_test_company_data(self):
        """Insert test company data for MSFT."""
        test_company_data = [
            CompanyFact(
                symbol='MSFT',
                date=date(2024, 6, 30),
                fiscal_year=2024,
                revenue=211915000000.0,
                cost=65863000000.0,
                ebitda=101000000000.0,
                eps=11.06,
                price=415.26
            ),
            CompanyFact(
                symbol='MSFT',
                date=date(2023, 6, 30),
                fiscal_year=2023,
                revenue=211915000000.0,
                cost=65863000000.0,
                ebitda=101000000000.0,
                eps=9.81,
                price=337.79
            ),
            CompanyFact(
                symbol='MSFT',
                date=date(2022, 6, 30),
                fiscal_year=2022,
                revenue=198270000000.0,
                cost=62020000000.0,
                ebitda=83000000000.0,
                eps=9.65,
                price=249.22
            ),
            CompanyFact(
                symbol='MSFT',
                date=date(2021, 6, 30),
                fiscal_year=2021,
                revenue=168088000000.0,
                cost=52959000000.0,
                ebitda=70000000000.0,
                eps=8.05,
                price=252.18
            ),
            CompanyFact(
                symbol='MSFT',
                date=date(2020, 6, 30),
                fiscal_year=2020,
                revenue=143015000000.0,
                cost=46066000000.0,
                ebitda=53000000000.0,
                eps=5.76,
                price=203.51
            )
        ]
        
        for data in test_company_data:
            self.db.add(data)
        self.db.commit()
    
    def _insert_test_macro_data(self):
        """Insert test macroeconomic data."""
        # EFFR data (daily rates for 2020-2024)
        effr_data = [
            # 2020 data
            MacroFact(series_id='EFFR', date=date(2020, 6, 30), value=0.09),
            MacroFact(series_id='EFFR', date=date(2020, 12, 31), value=0.08),
            # 2021 data
            MacroFact(series_id='EFFR', date=date(2021, 6, 30), value=0.06),
            MacroFact(series_id='EFFR', date=date(2021, 12, 31), value=0.08),
            # 2022 data
            MacroFact(series_id='EFFR', date=date(2022, 6, 30), value=1.58),
            MacroFact(series_id='EFFR', date=date(2022, 12, 31), value=4.33),
            # 2023 data
            MacroFact(series_id='EFFR', date=date(2023, 6, 30), value=5.08),
            MacroFact(series_id='EFFR', date=date(2023, 12, 31), value=5.33),
            # 2024 data
            MacroFact(series_id='EFFR', date=date(2024, 6, 30), value=5.33),
        ]
        
        # CPIAUCSL data (monthly CPI for 2020-2024)
        cpi_data = [
            # 2020 data
            MacroFact(series_id='CPIAUCSL', date=date(2020, 6, 30), value=257.797),
            MacroFact(series_id='CPIAUCSL', date=date(2020, 12, 31), value=260.474),
            # 2021 data
            MacroFact(series_id='CPIAUCSL', date=date(2021, 6, 30), value=271.696),
            MacroFact(series_id='CPIAUCSL', date=date(2021, 12, 31), value=278.802),
            # 2022 data
            MacroFact(series_id='CPIAUCSL', date=date(2022, 6, 30), value=296.311),
            MacroFact(series_id='CPIAUCSL', date=date(2022, 12, 31), value=296.797),
            # 2023 data
            MacroFact(series_id='CPIAUCSL', date=date(2023, 6, 30), value=305.109),
            MacroFact(series_id='CPIAUCSL', date=date(2023, 12, 31), value=306.746),
            # 2024 data
            MacroFact(series_id='CPIAUCSL', date=date(2024, 6, 30), value=314.175),
        ]
        
        for data in effr_data + cpi_data:
            self.db.add(data)
        self.db.commit()
    
    def test_get_company_macro_basic(self):
        """Test basic functionality of get_company_macro."""
        df = get_company_macro(
            symbol='MSFT',
            kpis=['revenue', 'eps'],
            macro_ids=['EFFR', 'CPIAUCSL'],
            years=5
        )
        
        # Assert DataFrame has expected structure
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 5)  # 5 fiscal years
        self.assertIn('fiscal_year', df.columns)
        self.assertIn('symbol', df.columns)
        self.assertIn('revenue', df.columns)
        self.assertIn('eps', df.columns)
        self.assertIn('EFFR', df.columns)
        self.assertIn('CPIAUCSL', df.columns)
        
        # Assert fiscal years are in descending order
        fiscal_years = df['fiscal_year'].tolist()
        self.assertEqual(fiscal_years, [2024, 2023, 2022, 2021, 2020])
        
        # Assert symbol is correct
        self.assertTrue(all(df['symbol'] == 'MSFT'))
    
    def test_get_company_macro_data_accuracy(self):
        """Test that the merged data is accurate."""
        df = get_company_macro(
            symbol='MSFT',
            kpis=['revenue', 'eps', 'price'],
            macro_ids=['EFFR', 'CPIAUCSL'],
            years=3
        )
        
        # Check 2024 data
        fy_2024 = df[df['fiscal_year'] == 2024].iloc[0]
        self.assertEqual(fy_2024['revenue'], 211915000000.0)
        self.assertEqual(fy_2024['eps'], 11.06)
        self.assertEqual(fy_2024['price'], 415.26)
        
        # Check macro data (should be resampled to fiscal year)
        # EFFR for 2024 should be around 5.33 (average)
        self.assertAlmostEqual(fy_2024['EFFR'], 5.33, places=2)
        # CPIAUCSL for 2024 should be the last value of the year
        self.assertAlmostEqual(fy_2024['CPIAUCSL'], 314.175, places=3)
    
    def test_get_company_macro_invalid_kpi(self):
        """Test that invalid KPIs raise ValueError."""
        with self.assertRaises(ValueError):
            get_company_macro(
                symbol='MSFT',
                kpis=['revenue', 'invalid_kpi'],
                macro_ids=['EFFR'],
                years=5
            )
    
    def test_get_company_macro_empty_result(self):
        """Test behavior when no company data is found."""
        df = get_company_macro(
            symbol='INVALID_SYMBOL',
            kpis=['revenue'],
            macro_ids=['EFFR'],
            years=5
        )
        
        self.assertTrue(df.empty)
    
    def test_get_company_macro_missing_macro_data(self):
        """Test behavior when macro data is missing."""
        df = get_company_macro(
            symbol='MSFT',
            kpis=['revenue'],
            macro_ids=['EFFR', 'INVALID_MACRO'],
            years=3
        )
        
        # Should still return company data
        self.assertEqual(len(df), 3)
        self.assertIn('EFFR', df.columns)
        self.assertIn('INVALID_MACRO', df.columns)
        # Missing macro data should be NaN
        self.assertTrue(df['INVALID_MACRO'].isna().all())
    
    def test_get_available_kpis(self):
        """Test get_available_kpis function."""
        kpis = get_available_kpis()
        expected_kpis = ['revenue', 'cost', 'ebitda', 'eps', 'price']
        self.assertEqual(kpis, expected_kpis)
    
    def test_get_available_macro_series(self):
        """Test get_available_macro_series function."""
        series = get_available_macro_series()
        # The test database already has some series, so we check that our test series are included
        expected_test_series = ['EFFR', 'CPIAUCSL']
        for test_series in expected_test_series:
            self.assertIn(test_series, series)
    
    def test_get_company_macro_resampling_logic(self):
        """Test that macro data is correctly resampled."""
        df = get_company_macro(
            symbol='MSFT',
            kpis=['revenue'],
            macro_ids=['EFFR', 'CPIAUCSL'],
            years=2
        )
        
        # EFFR should be averaged (rate)
        # 2024: average of 5.33 = 5.33
        # 2023: average of 5.08 and 5.33 = 5.205
        fy_2024 = df[df['fiscal_year'] == 2024].iloc[0]
        fy_2023 = df[df['fiscal_year'] == 2023].iloc[0]
        
        self.assertAlmostEqual(fy_2024['EFFR'], 5.33, places=2)
        self.assertAlmostEqual(fy_2023['EFFR'], 5.205, places=2)
        
        # CPIAUCSL should be last value (level)
        # 2024: last value = 314.175
        # 2023: last value = 306.746
        self.assertAlmostEqual(fy_2024['CPIAUCSL'], 314.175, places=3)
        self.assertAlmostEqual(fy_2023['CPIAUCSL'], 306.746, places=3)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2) 