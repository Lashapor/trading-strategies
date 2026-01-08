"""
Data loading utilities with caching.
"""

import pandas as pd
import yfinance as yf
import streamlit as st
from datetime import datetime


@st.cache_data(ttl=3600, show_spinner="Fetching market data...")
def fetch_stock_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch stock data from Yahoo Finance with caching.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'KO')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        DataFrame with OHLCV data
    
    Raises:
        ValueError: If ticker is invalid or data cannot be fetched
    """
    try:
        # Download data
        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            progress=False,
            auto_adjust=True  # Adjust for splits and dividends
        )
        
        if data.empty:
            raise ValueError(f"No data found for ticker '{ticker}'")
        
        # Ensure we have required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing = [col for col in required_columns if col not in data.columns]
        
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        return data
    
    except Exception as e:
        raise ValueError(f"Error fetching data for {ticker}: {str(e)}")


def validate_date_range(start_date: datetime, end_date: datetime) -> tuple:
    """
    Validate and adjust date range.
    
    Args:
        start_date: Start date
        end_date: End date
    
    Returns:
        Tuple of (start_date, end_date, error_message)
        error_message is None if validation passes
    """
    if start_date >= end_date:
        return start_date, end_date, "Start date must be before end date"
    
    # Check if range is too short
    days_diff = (end_date - start_date).days
    if days_diff < 30:
        return start_date, end_date, "Date range must be at least 30 days"
    
    # Check if end date is in the future
    if end_date > datetime.now():
        return start_date, end_date, "End date cannot be in the future"
    
    return start_date, end_date, None


def calculate_buy_hold_returns(data: pd.DataFrame) -> pd.Series:
    """
    Calculate buy and hold cumulative returns.
    
    Args:
        data: DataFrame with Close prices
    
    Returns:
        Series with cumulative returns
    """
    returns = data['Close'].pct_change().fillna(0)
    cumulative = (1 + returns).cumprod()
    return cumulative
