"""
Support and Resistance (S&R) Trading Strategy.

This strategy uses scaled price indicators to identify support and resistance levels.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
import streamlit as st

from .base import BaseStrategy, StrategyResult


class SupportResistanceStrategy(BaseStrategy):
    """
    Support and Resistance Strategy based on price scaling.
    
    The strategy scales prices by their order of magnitude and uses
    the fractional part as an indicator to identify support (buy) and
    resistance (sell) levels.
    """
    
    @property
    def name(self) -> str:
        return "Support & Resistance"
    
    @property
    def description(self) -> str:
        return """
        ### Support & Resistance Strategy
        
        This strategy identifies trading opportunities based on scaled price levels:
        
        **How it works:**
        1. Scale prices by their order of magnitude
        2. Calculate indicator from fractional part
        3. Buy when indicator is below buy level (support)
        4. Sell when indicator is above sell level (resistance)
        
        **Parameters:**
        - **SR Buy Level**: Threshold for buy signals (0.0 - 1.0)
        - **SR Sell Level**: Threshold for sell signals (0.0 - 1.0)
        - **Name**: Descriptive name for this parameter set
        
        **Trading Logic:**
        - Lower buy levels = More aggressive buying (more trades)
        - Higher sell levels = More aggressive selling (more trades)
        - Fees are deducted on each trade (both entry and exit)
        """
    
    @property
    def default_params(self) -> Dict[str, Any]:
        return {
            "sr_buy": 0.3,
            "sr_sell": 0.7,
            "name": "Standard"
        }
    
    @property
    def param_config(self) -> Dict[str, Dict[str, Any]]:
        return {
            "name": {
                "type": "text_input",
                "label": "Strategy Name",
                "help": "Descriptive name for this parameter set"
            },
            "sr_buy": {
                "type": "number_input",
                "label": "SR Buy Level",
                "min": 0.0,
                "max": 1.0,
                "step": 0.05,
                "format": "%.2f",
                "help": "Buy when indicator < this value"
            },
            "sr_sell": {
                "type": "number_input",
                "label": "SR Sell Level",
                "min": 0.0,
                "max": 1.0,
                "step": 0.05,
                "format": "%.2f",
                "help": "Sell when indicator > this value"
            }
        }
    
    @st.cache_data(show_spinner=False)
    def run(_self, data: pd.DataFrame, params: Dict[str, Any], fee: float = 0.0) -> StrategyResult:
        """
        Execute Support & Resistance strategy.
        
        Args:
            data: DataFrame with OHLCV data
            params: Dictionary with 'sr_buy', 'sr_sell', 'name'
            fee: Trading fee as decimal
        
        Returns:
            StrategyResult with performance metrics and trade data
        """
        df = data.copy()
        
        # Extract parameters
        buy_level = params.get('sr_buy', 0.4)
        sell_level = params.get('sr_sell', 0.6)
        
        # --- STRATEGY LOGIC ---
        # Scale price by order of magnitude
        df['scaled_price'] = df['Close'] / 10**np.floor(np.log10(df['Close']))
        
        # Calculate indicator from fractional part
        df['indicator'] = df['scaled_price'] % 1
        
        # Generate signals: 1 (Enter Long), -1 (Exit Long), 0 (No Signal)
        df['signal'] = 0
        df.loc[df['indicator'] < buy_level, 'signal'] = 1   # Buy signal
        df.loc[df['indicator'] > sell_level, 'signal'] = -1  # Sell signal

        # Calculate position (state)
        # Create a temp series to hold state changes: 1 (Long), 0 (Flat)
        # We replace 0 signals with NaN to forward fill the state
        temp_pos = df['signal'].replace(0, np.nan)
        
        # If signal is -1 (sell), we want position to be 0
        temp_pos = temp_pos.replace(-1, 0)
        
        # Forward fill to propagate position state
        df['position'] = temp_pos.ffill().fillna(0)
        # --- END STRATEGY LOGIC ---
        
        # Calculate returns
        df['market_ret'] = df['Close'].pct_change()
        
        # Strategy returns with fees
        # Fee is charged on position changes
        # Use position diff to detect actual trades
        position_change = df['position'].diff().abs().fillna(0)
        
        # Return is market return * previous position - fees
        df['strat_ret'] = df['market_ret'] * df['position'].shift(1) - fee * position_change
        
        # Cumulative returns
        df['cum_ret'] = (1 + df['strat_ret'].fillna(0)).cumprod()
        
        # Debug: Verify cumulative returns
        import streamlit as st
        st.write(f"Strategy Debug - cum_ret shape: {df['cum_ret'].shape}, range: [{df['cum_ret'].min():.4f}, {df['cum_ret'].max():.4f}]")
        st.write(f"  First 5: {df['cum_ret'].head().tolist()}")
        st.write(f"  Last 5: {df['cum_ret'].tail().tolist()}")
        st.write(f"  Index type: {type(df.index)}, Index name: {df.index.name}")
        
        # Extract trades using vectorized access
        trades_list = []
        position = 0
        entry_price = 0
        entry_date = None
        
        # Convert to numpy arrays for fast scalar access
        signals = df['signal'].to_numpy()
        closes = df['Close'].to_numpy()
        dates = df.index.to_numpy()
        
        for i in range(len(df)):
            signal = signals[i].item() if hasattr(signals[i], 'item') else signals[i]
            close_price = closes[i].item() if hasattr(closes[i], 'item') else closes[i]
            date = dates[i]
            
            if position == 0 and signal == 1:
                # Enter long position
                position = 1
                entry_price = close_price
                entry_date = date
            elif position == 1 and signal == -1:
                # Exit long position
                exit_price = close_price
                pnl = (exit_price / entry_price - 1) - 2 * fee  # 2 fees (entry + exit)
                trades_list.append({
                    'entry_date': entry_date,
                    'exit_date': date,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'pnl': pnl * 100  # Convert to percentage
                })
                position = 0
        
        trades_df = pd.DataFrame(trades_list)
        trade_returns = trades_df['pnl'].tolist() if not trades_df.empty else []
        
        # Calculate metrics
        metrics = _self._calculate_metrics(df['strat_ret'], trades_df)
        
        return StrategyResult(
            metrics=metrics,
            cumulative_returns=df['cum_ret'],
            trades=trades_df,
            trade_returns=trade_returns
        )
