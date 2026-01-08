"""
Base strategy interface for trading strategies.
All strategies must inherit from BaseStrategy and implement required methods.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List
import pandas as pd
import inspect


@dataclass
class StrategyResult:
    """Standardized result container for strategy backtests."""
    
    metrics: Dict[str, float]  # Performance metrics (returns, sharpe, etc.)
    cumulative_returns: pd.Series  # Cumulative returns series with datetime index
    trades: pd.DataFrame  # Trade history
    trade_returns: List[float]  # Individual trade returns for distribution


class BaseStrategy(ABC):
    """
    Abstract base class for trading strategies.
    
    All strategies inherit from this class and implement:
    - Properties: name, description, default_params, param_config
    - Methods: run(data, params)
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy display name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """
        Strategy explanation in markdown format.
        Displayed in the Info section.
        """
        pass
    
    @property
    @abstractmethod
    def default_params(self) -> Dict[str, Any]:
        """
        Default parameter values.
        
        Example:
            {"sr_buy": 0.4, "sr_sell": 0.6, "name": "Standard"}
        """
        pass
    
    @property
    @abstractmethod
    def param_config(self) -> Dict[str, Dict[str, Any]]:
        """
        Parameter UI configuration for Streamlit inputs.
        
        Example:
            {
                "sr_buy": {
                    "type": "number_input",
                    "label": "SR Buy Level",
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "format": "%.2f"
                },
                "name": {
                    "type": "text_input",
                    "label": "Strategy Name"
                }
            }
        
        Supported types: number_input, slider, text_input, selectbox
        """
        pass
    
    @abstractmethod
    def run(self, data: pd.DataFrame, params: Dict[str, Any], fee: float = 0.0) -> StrategyResult:
        """
        Execute strategy with given parameters.
        
        Args:
            data: DataFrame with OHLCV data (columns: Open, High, Low, Close, Volume)
            params: Dictionary of strategy parameters
            fee: Trading fee as decimal (e.g., 0.001 for 0.1%)
        
        Returns:
            StrategyResult with metrics, cumulative returns, trades, and trade returns
        """
        pass
    
    def get_source_code(self) -> str:
        """Return the strategy's source code."""
        return inspect.getsource(self.__class__)
    
    def _calculate_metrics(self, returns: pd.Series, trades: pd.DataFrame = None) -> Dict[str, float]:
        """
        Calculate standard performance metrics.
        
        Args:
            returns: Series of strategy returns
            trades: Optional DataFrame with trade information
        
        Returns:
            Dictionary of metrics
        """
        import numpy as np
        
        # Clean returns
        returns_clean = returns.fillna(0)
        
        # Cumulative returns
        cumulative = (1 + returns_clean).cumprod()
        total_return = (cumulative.iloc[-1] - 1) * 100  # Convert to percentage
        
        # Annualized metrics (assuming 252 trading days)
        n_periods = len(returns_clean)
        years = n_periods / 252
        annual_return = ((cumulative.iloc[-1]) ** (1 / years) - 1) * 100 if years > 0 else 0
        
        # Risk metrics
        annual_volatility = returns_clean.std() * np.sqrt(252) * 100
        
        # Sharpe ratio (assuming 0% risk-free rate)
        sharpe = (annual_return / annual_volatility) if annual_volatility > 0 else 0
        
        # Maximum drawdown
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        # Trade statistics
        if trades is not None and not trades.empty:
            winning_trades = len(trades[trades['pnl'] > 0]) if 'pnl' in trades.columns else 0
            total_trades = len(trades)
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        else:
            total_trades = 0
            win_rate = 0
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'total_trades': total_trades,
            'win_rate': win_rate
        }
