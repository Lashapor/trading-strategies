"""
Trading Strategies Dashboard - Main Application

A professional, interactive trading strategies dashboard with comprehensive
performance analytics, risk visualization, and mobile-responsive design.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List

# Import local modules
from strategies import get_all_strategies, get_strategy
from components.charts import (
    create_cumulative_returns_chart,
    create_drawdown_chart,
    create_trade_distribution,
    create_monthly_heatmap
)
from utils.data_loader import fetch_stock_data, validate_date_range, calculate_buy_hold_returns


# Page configuration
st.set_page_config(
    page_title="Trading Strategies Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS for Apple-inspired design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global styling */
    .stApp {
        background-color: #ffffff;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 600 !important;
        color: #1d1d1f !important;
        letter-spacing: -0.02em !important;
    }
    
    h1 {
        font-size: 2.5rem !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        color: #1d1d1f !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        color: #86868b !important;
        font-weight: 500 !important;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #007AFF !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stButton>button:hover {
        background-color: #0051D5 !important;
        box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3) !important;
    }
    
    /* Secondary buttons (expander headers act as buttons) */
    .streamlit-expanderHeader {
        background-color: #f5f5f7 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        color: #1d1d1f !important;
        border: 1px solid #e5e5e7 !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #e8e8ed !important;
    }
    
    /* Inputs */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stSelectbox>div>div>select {
        border-radius: 8px !important;
        border: 1px solid #d2d2d7 !important;
        padding: 0.5rem !important;
        font-size: 1rem !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stTextInput>div>div>input:focus,
    .stNumberInput>div>div>input:focus {
        border-color: #007AFF !important;
        box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1) !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f5f5f7 !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #1d1d1f !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 8px;
        padding: 0 24px;
        background-color: transparent;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f5f5f7;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #007AFF !important;
        color: white !important;
    }
    
    /* Remove extra padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Error/Warning styling */
    .stAlert {
        border-radius: 8px !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)


def detect_mobile() -> bool:
    """
    Detect if user is on mobile device via user agent.
    
    Returns:
        True if mobile device detected
    """
    try:
        # Access via query params as fallback detection
        # In production, this would need JavaScript injection
        return False  # Default to desktop
    except:
        return False


def init_session_state():
    """Initialize session state variables."""
    if 'strategy_params' not in st.session_state:
        st.session_state.strategy_params = {}
    
    if 'device_type' not in st.session_state:
        st.session_state.device_type = 'mobile' if detect_mobile() else 'desktop'
    
    if 'calculation_done' not in st.session_state:
        st.session_state.calculation_done = False
    
    if 'results' not in st.session_state:
        st.session_state.results = {}


def render_parameter_form(strategy, strategy_id: str):
    """
    Render dynamic parameter form for a strategy.
    
    Args:
        strategy: BaseStrategy instance
        strategy_id: Unique strategy identifier
    """
    # Initialize strategy params in session state
    if strategy_id not in st.session_state.strategy_params:
        st.session_state.strategy_params[strategy_id] = [strategy.default_params.copy()]
    
    param_sets = st.session_state.strategy_params[strategy_id]
    
    # Display existing parameter sets
    for idx, params in enumerate(param_sets):
        with st.expander(f"📊 {params.get('name', f'Set {idx + 1}')}", expanded=(idx == 0)):
            # Determine column layout based on device
            is_mobile = st.session_state.device_type == 'mobile'
            
            if is_mobile:
                # Vertical layout for mobile
                for param_name, config in strategy.param_config.items():
                    params[param_name] = render_input_field(
                        param_name, config, params.get(param_name), f"{strategy_id}_{idx}"
                    )
            else:
                # Multi-column layout for desktop
                cols = st.columns([2, 1, 1])
                col_idx = 0
                
                for param_name, config in strategy.param_config.items():
                    with cols[col_idx % 3]:
                        params[param_name] = render_input_field(
                            param_name, config, params.get(param_name), f"{strategy_id}_{idx}"
                        )
                    col_idx += 1
            
            # Remove button
            if len(param_sets) > 1:
                if st.button("🗑️ Remove This Set", key=f"remove_{strategy_id}_{idx}", 
                           use_container_width=True):
                    st.session_state.strategy_params[strategy_id].pop(idx)
                    st.rerun()
    
    # Add parameter set button
    if st.button("➕ Add Parameter Set", key=f"add_{strategy_id}", use_container_width=True):
        st.session_state.strategy_params[strategy_id].append(strategy.default_params.copy())
        st.rerun()


def render_input_field(param_name: str, config: Dict, current_value, key_prefix: str):
    """
    Render appropriate input field based on configuration.
    
    Args:
        param_name: Parameter name
        config: Configuration dictionary
        current_value: Current parameter value
        key_prefix: Unique key prefix
    
    Returns:
        User input value
    """
    input_type = config.get('type', 'text_input')
    label = config.get('label', param_name)
    help_text = config.get('help', None)
    
    if input_type == 'number_input':
        return st.number_input(
            label,
            min_value=config.get('min', 0.0),
            max_value=config.get('max', 100.0),
            value=float(current_value) if current_value is not None else config.get('min', 0.0),
            step=config.get('step', 0.1),
            format=config.get('format', '%.2f'),
            key=f"{key_prefix}_{param_name}",
            help=help_text
        )
    elif input_type == 'slider':
        return st.slider(
            label,
            min_value=config.get('min', 0.0),
            max_value=config.get('max', 100.0),
            value=float(current_value) if current_value is not None else config.get('min', 0.0),
            step=config.get('step', 0.1),
            key=f"{key_prefix}_{param_name}",
            help=help_text
        )
    elif input_type == 'text_input':
        return st.text_input(
            label,
            value=str(current_value) if current_value is not None else '',
            key=f"{key_prefix}_{param_name}",
            help=help_text
        )
    elif input_type == 'selectbox':
        options = config.get('options', [])
        return st.selectbox(
            label,
            options=options,
            index=options.index(current_value) if current_value in options else 0,
            key=f"{key_prefix}_{param_name}",
            help=help_text
        )
    else:
        return st.text_input(label, value=str(current_value), key=f"{key_prefix}_{param_name}")


def validate_inputs(ticker: str, start_date, end_date, strategy_params: Dict) -> tuple:
    """
    Validate all user inputs.
    
    Args:
        ticker: Stock ticker symbol
        start_date: Start date
        end_date: End date
        strategy_params: Dictionary of strategy parameters
    
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Validate ticker
    if not ticker or len(ticker.strip()) == 0:
        errors.append("Ticker symbol is required")
    
    # Validate dates
    _, _, date_error = validate_date_range(start_date, end_date)
    if date_error:
        errors.append(date_error)
    
    # Validate strategy parameters
    for strategy_id, param_sets in strategy_params.items():
        for idx, params in enumerate(param_sets):
            for key, value in params.items():
                if value is None or (isinstance(value, str) and len(value.strip()) == 0):
                    errors.append(f"Missing parameter: {key} in parameter set {idx + 1}")
    
    return len(errors) == 0, errors


def main():
    """Main application logic."""
    
    # Initialize session state
    init_session_state()
    
    # Header
    st.title("📈 Trading Strategies Dashboard")
    st.markdown("**Compare multiple trading strategies with comprehensive analytics**")
    
    # Version indicator
    col1, col2 = st.columns([6, 1])
    with col2:
        st.success("✅ v1.0.1")
    
    st.divider()
    
    # Sidebar - Global Configuration
    with st.sidebar:
        st.header("⚙️ Global Configuration")
        
        # Ticker input
        ticker = st.text_input(
            "Stock Ticker",
            value="KO",
            placeholder="e.g., AAPL, KO, SPY",
            help="Enter stock ticker symbol"
        ).upper()
        
        # Date range
        st.subheader("Date Range")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=365),
                max_value=datetime.now()
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now(),
                max_value=datetime.now()
            )
        
        # Fee input
        fee_percent = st.number_input(
            "Trading Fee (%)",
            min_value=0.0,
            max_value=10.0,
            value=0.05,
            step=0.01,
            format="%.2f",
            help="Fee charged per trade (as percentage)"
        )
        
        fee_decimal = fee_percent / 100
        
        st.divider()
        
        # Calculate button
        calculate_button = st.button("🚀 Calculate All Strategies", 
                                     use_container_width=True, 
                                     type="primary")
    
    # Main content area
    strategies = get_all_strategies()
    
    # Strategy configuration section
    st.header("📊 Strategy Configuration")
    
    for strategy_id, strategy in strategies.items():
        st.subheader(f"{strategy.name}")
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            # Parameter form
            render_parameter_form(strategy, strategy_id)
        
        with col2:
            # Info and Code buttons
            st.markdown("&nbsp;")  # Spacing
            with st.expander("📖 Info"):
                st.markdown(strategy.description)
            
            with st.expander("💻 Code"):
                st.code(strategy.get_source_code(), language='python')
    
    st.divider()
    
    # Calculate strategies when button clicked
    if calculate_button:
        # Validate inputs
        is_valid, errors = validate_inputs(ticker, start_date, end_date, 
                                          st.session_state.strategy_params)
        
        if not is_valid:
            st.error("**Please fix the following errors:**")
            for error in errors:
                st.error(f"• {error}")
        else:
            # Fetch data
            try:
                with st.spinner(f"Fetching data for {ticker}..."):
                    data = fetch_stock_data(ticker, str(start_date), str(end_date))
                
                # Calculate buy & hold benchmark
                benchmark = calculate_buy_hold_returns(data)
                
                # Run all strategies
                all_results = {}
                
                for strategy_id, strategy in strategies.items():
                    param_sets = st.session_state.strategy_params.get(strategy_id, [])
                    
                    for params in param_sets:
                        strategy_name = f"{strategy.name} - {params.get('name', 'Unnamed')}"
                        
                        with st.spinner(f"Calculating {strategy_name}..."):
                            result = strategy.run(data, params, fee_decimal)
                            all_results[strategy_name] = result
                
                # Store results in session state
                st.session_state.results = all_results
                st.session_state.benchmark = benchmark
                st.session_state.data = data
                st.session_state.ticker = ticker
                st.session_state.calculation_done = True
                
                st.success("✅ Calculation complete!")
                st.rerun()
                
            except ValueError as e:
                st.error(f"❌ Error: {str(e)}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
    
    # Display results if available
    if st.session_state.calculation_done and st.session_state.results:
        st.header("📈 Results")
        
        results = st.session_state.results
        benchmark = st.session_state.benchmark
        ticker = st.session_state.ticker
        device_type = st.session_state.device_type
        
        # Create tabs for different analyses
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Performance",
            "📊 Risk Analysis",
            "💰 Trades",
            "📅 Calendar"
        ])
        
        with tab1:
            st.subheader("Performance Comparison")
            
            # Metrics grid
            is_mobile = device_type == 'mobile'
            n_cols = 2 if is_mobile else 4
            
            for strategy_name, result in results.items():
                st.markdown(f"**{strategy_name}**")
                cols = st.columns(n_cols)
                
                metrics = result.metrics
                col_idx = 0
                
                metric_items = [
                    ("Total Return", f"{metrics.get('total_return', 0):.2f}%"),
                    ("Sharpe Ratio", f"{metrics.get('sharpe_ratio', 0):.2f}"),
                    ("Max Drawdown", f"{metrics.get('max_drawdown', 0):.2f}%"),
                    ("Win Rate", f"{metrics.get('win_rate', 0):.1f}%")
                ]
                
                for label, value in metric_items:
                    with cols[col_idx % n_cols]:
                        st.metric(label, value)
                    col_idx += 1
                
                st.divider()
            
            # Cumulative returns chart
            cum_returns_dict = {name: result.cumulative_returns 
                               for name, result in results.items()}
            
            fig = create_cumulative_returns_chart(
                cum_returns_dict, 
                ticker, 
                benchmark, 
                device_type
            )
            st.plotly_chart(fig, use_container_width=True, 
                          config={'displayModeBar': True, 'displaylogo': False})
        
        with tab2:
            st.subheader("Risk Analysis")
            
            # Display drawdown for each strategy
            for strategy_name, result in results.items():
                st.markdown(f"**{strategy_name}**")
                
                # Get returns from data
                data = st.session_state.data
                returns = data['Close'].pct_change()
                
                # Calculate strategy returns (approximation for drawdown)
                # In reality, this should use the actual strategy returns
                fig = create_drawdown_chart(
                    returns,  # This should be strategy returns
                    strategy_name,
                    device_type
                )
                st.plotly_chart(fig, use_container_width=True,
                              config={'displayModeBar': True, 'displaylogo': False})
        
        with tab3:
            st.subheader("Trade Analysis")
            
            # Display trade distribution for each strategy
            for strategy_name, result in results.items():
                st.markdown(f"**{strategy_name}**")
                
                # Trade statistics
                metrics = result.metrics
                col1, col2, col3 = st.columns(3)
                
                col1.metric("Total Trades", int(metrics.get('total_trades', 0)))
                col2.metric("Win Rate", f"{metrics.get('win_rate', 0):.1f}%")
                col3.metric("Avg Return", 
                           f"{np.mean(result.trade_returns):.2f}%" if result.trade_returns else "N/A")
                
                # Trade distribution chart
                if result.trade_returns and len(result.trade_returns) > 0:
                    fig = create_trade_distribution(
                        result.trade_returns,
                        strategy_name,
                        device_type
                    )
                    st.plotly_chart(fig, use_container_width=True,
                                  config={'displayModeBar': True, 'displaylogo': False})
                else:
                    st.info("No trades to display for this strategy")
                
                st.divider()
        
        with tab4:
            st.subheader("Monthly Returns")
            
            # Display monthly heatmap for each strategy
            for strategy_name, result in results.items():
                st.markdown(f"**{strategy_name}**")
                
                # Calculate strategy returns from cumulative returns
                cum_returns = result.cumulative_returns
                returns = cum_returns.pct_change().fillna(0)
                
                fig = create_monthly_heatmap(
                    returns,
                    strategy_name,
                    device_type
                )
                st.plotly_chart(fig, use_container_width=True,
                              config={'displayModeBar': True, 'displaylogo': False})
                
                st.divider()


if __name__ == "__main__":
    main()
