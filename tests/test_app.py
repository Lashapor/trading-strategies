"""
Comprehensive tests for trading strategies dashboard.
Run with: python -m pytest tests/test_app.py -v
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.data_loader import validate_date_range, calculate_buy_hold_returns
from strategies.support_resistance import SupportResistanceStrategy
from components.charts import (
    create_cumulative_returns_chart,
    create_drawdown_chart,
    create_trade_distribution,
    create_monthly_heatmap
)


class TestDateValidation:
    """Test date validation to prevent Series ambiguity errors."""
    
    def test_validate_with_date_objects(self):
        """Test with date objects."""
        start = date(2023, 1, 1)
        end = date(2024, 1, 1)
        _, _, error = validate_date_range(start, end)
        assert error is None
    
    def test_validate_with_datetime_objects(self):
        """Test with datetime objects."""
        start = datetime(2023, 1, 1)
        end = datetime(2024, 1, 1)
        _, _, error = validate_date_range(start, end)
        assert error is None
    
    def test_validate_mixed_date_types(self):
        """Test with mixed date and datetime objects."""
        start = date(2023, 1, 1)
        end = datetime(2024, 1, 1)
        _, _, error = validate_date_range(start, end)
        assert error is None
    
    def test_validate_start_after_end(self):
        """Test error when start date is after end date."""
        start = date(2024, 1, 1)
        end = date(2023, 1, 1)
        _, _, error = validate_date_range(start, end)
        assert error == "Start date must be before end date"
    
    def test_validate_range_too_short(self):
        """Test error when date range is less than 30 days."""
        start = date(2024, 1, 1)
        end = date(2024, 1, 15)
        _, _, error = validate_date_range(start, end)
        assert error == "Date range must be at least 30 days"
    
    def test_validate_future_date(self):
        """Test error when end date is in the future."""
        start = datetime.now().date() - timedelta(days=100)
        end = datetime.now().date() + timedelta(days=10)
        _, _, error = validate_date_range(start, end)
        assert error == "End date cannot be in the future"


class TestSeriesHandling:
    """Test proper handling of pandas Series to avoid ambiguity errors."""
    
    def setup_method(self):
        """Create sample data for tests."""
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        self.sample_data = pd.DataFrame({
            'Open': np.random.uniform(90, 110, len(dates)),
            'High': np.random.uniform(95, 115, len(dates)),
            'Low': np.random.uniform(85, 105, len(dates)),
            'Close': np.random.uniform(90, 110, len(dates)),
            'Volume': np.random.randint(1000000, 10000000, len(dates))
        }, index=dates)
        
        self.returns = self.sample_data['Close'].pct_change().fillna(0)
    
    def test_buy_hold_returns_not_empty(self):
        """Test that buy and hold returns calculation works."""
        result = calculate_buy_hold_returns(self.sample_data)
        assert isinstance(result, pd.Series)
        assert len(result) > 0
        assert not result.empty  # Proper Series check
    
    def test_benchmark_series_check(self):
        """Test benchmark Series is properly checked before use."""
        benchmark = calculate_buy_hold_returns(self.sample_data)
        
        # This should NOT raise "Series is ambiguous" error
        if benchmark is not None and not (isinstance(benchmark, pd.Series) and benchmark.empty):
            assert True
        else:
            pytest.fail("Benchmark check failed")
    
    def test_empty_series_handling(self):
        """Test handling of empty Series."""
        empty_series = pd.Series(dtype=float)
        
        # Correct way to check
        assert empty_series.empty
        
        # This would cause error: if not empty_series:
        # Instead use: if empty_series.empty:


class TestStrategyExecution:
    """Test strategy execution without errors."""
    
    def setup_method(self):
        """Create sample data for strategy testing."""
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        prices = 100 * (1 + np.random.randn(len(dates)).cumsum() * 0.01)
        self.sample_data = pd.DataFrame({
            'Open': prices * 0.99,
            'High': prices * 1.01,
            'Low': prices * 0.98,
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, len(dates))
        }, index=dates)
    
    def test_sr_strategy_runs(self):
        """Test S&R strategy executes without errors."""
        strategy = SupportResistanceStrategy()
        params = {'sr_buy': 0.4, 'sr_sell': 0.6, 'name': 'Test'}
        
        result = strategy.run(self.sample_data, params, fee=0.001)
        
        assert result is not None
        assert 'total_return' in result.metrics
        assert isinstance(result.cumulative_returns, pd.Series)
        assert not result.cumulative_returns.empty
    
    def test_sr_strategy_with_no_trades(self):
        """Test S&R strategy handles case with no trades."""
        strategy = SupportResistanceStrategy()
        # Extreme parameters that won't trigger trades
        params = {'sr_buy': 0.01, 'sr_sell': 0.99, 'name': 'No Trades'}
        
        result = strategy.run(self.sample_data, params, fee=0.001)
        
        assert result is not None
        assert result.metrics['total_trades'] >= 0
        assert isinstance(result.trade_returns, list)


class TestChartCreation:
    """Test chart creation functions handle edge cases."""
    
    def setup_method(self):
        """Create sample data for chart testing."""
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        self.cum_returns = pd.Series(
            (1 + np.random.randn(len(dates)) * 0.01).cumprod(),
            index=dates
        )
        self.returns = pd.Series(
            np.random.randn(len(dates)) * 0.01,
            index=dates
        )
        self.trade_returns = [1.5, -0.8, 2.3, -1.2, 0.9, 1.8, -0.5]
    
    def test_cumulative_returns_chart_with_benchmark(self):
        """Test chart creation with benchmark."""
        results_dict = {'Strategy 1': self.cum_returns}
        
        # Should not raise Series ambiguity error
        fig = create_cumulative_returns_chart(
            results_dict,
            'TEST',
            self.cum_returns,
            'desktop'
        )
        assert fig is not None
    
    def test_cumulative_returns_chart_without_benchmark(self):
        """Test chart creation without benchmark."""
        results_dict = {'Strategy 1': self.cum_returns}
        
        fig = create_cumulative_returns_chart(
            results_dict,
            'TEST',
            None,
            'desktop'
        )
        assert fig is not None
    
    def test_drawdown_chart_creation(self):
        """Test drawdown chart handles Series properly."""
        fig = create_drawdown_chart(self.returns, 'Test Strategy', 'desktop')
        assert fig is not None
    
    def test_trade_distribution_with_trades(self):
        """Test trade distribution with valid trades."""
        fig = create_trade_distribution(self.trade_returns, 'Test', 'desktop')
        assert fig is not None
    
    def test_trade_distribution_empty_trades(self):
        """Test trade distribution with no trades."""
        fig = create_trade_distribution([], 'Test', 'desktop')
        assert fig is not None
    
    def test_monthly_heatmap_creation(self):
        """Test monthly heatmap creation."""
        fig = create_monthly_heatmap(self.returns, 'Test', 'desktop')
        assert fig is not None
    
    def test_monthly_heatmap_empty_data(self):
        """Test monthly heatmap with empty data."""
        empty_returns = pd.Series(dtype=float)
        fig = create_monthly_heatmap(empty_returns, 'Test', 'desktop')
        assert fig is not None
    
    def test_monthly_heatmap_no_datetime_index(self):
        """Test monthly heatmap with non-datetime index."""
        invalid_returns = pd.Series([0.01, 0.02, -0.01])
        fig = create_monthly_heatmap(invalid_returns, 'Test', 'desktop')
        assert fig is not None


class TestDataIntegrity:
    """Test data integrity and type consistency."""
    
    def test_series_comparison_safety(self):
        """Test safe Series comparison patterns."""
        series = pd.Series([1, 2, 3])
        
        # Correct patterns
        assert not series.empty
        assert len(series) > 0
        assert series.any()
        
        # These would cause "ambiguous" error:
        # if series:  # BAD
        # if not series:  # BAD
    
    def test_none_vs_empty_series(self):
        """Test distinguishing None from empty Series."""
        none_series = None
        empty_series = pd.Series(dtype=float)
        valid_series = pd.Series([1, 2, 3])
        
        # Safe checks
        assert none_series is None
        assert empty_series.empty
        assert not valid_series.empty
        
        # Combined check
        def is_valid_series(s):
            return s is not None and (not isinstance(s, pd.Series) or not s.empty)
        
        assert not is_valid_series(none_series)
        assert not is_valid_series(empty_series)
        assert is_valid_series(valid_series)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
