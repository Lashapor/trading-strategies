# GitHub Copilot Instructions

## Project Overview

This is a professional trading strategies dashboard built with Streamlit, Plotly, and Python. The application allows users to backtest and compare multiple trading strategies with comprehensive performance analytics, risk visualization, and mobile-responsive design.

## Architecture Pattern

### Strategy System
- **Base Class**: All strategies inherit from `BaseStrategy` in `strategies/base.py`
- **Registry Pattern**: Strategies auto-register in `strategies/__init__.py` via `STRATEGIES` dict
- **Result Container**: Use `StrategyResult` dataclass for standardized outputs
- **Caching**: Apply `@st.cache_data` decorator to strategy `run()` methods

### Module Organization
```
strategies/     - Trading strategy implementations
components/     - Reusable UI components (charts, forms)
utils/          - Shared utilities (data loading, helpers)
.streamlit/     - Streamlit configuration
```

## Coding Conventions

### Python Style
- Use type hints for all function parameters and return values
- Follow PEP 8 naming conventions (snake_case for functions/variables)
- Add comprehensive docstrings to all classes and functions
- Keep functions focused and under 50 lines when possible

### Strategy Development Pattern
```python
class NewStrategy(BaseStrategy):
    @property
    def name(self) -> str:
        return "Strategy Display Name"
    
    @property
    def description(self) -> str:
        return """Markdown description with:
        - How it works
        - Parameters explanation
        - Trading logic
        """
    
    @property
    def default_params(self) -> Dict[str, Any]:
        return {"param1": 0.5, "name": "Standard"}
    
    @property
    def param_config(self) -> Dict[str, Dict[str, Any]]:
        return {
            "param1": {
                "type": "number_input",  # or "slider", "text_input", "selectbox"
                "label": "Display Label",
                "min": 0.0,
                "max": 1.0,
                "step": 0.05,
                "format": "%.2f",
                "help": "Tooltip text"
            }
        }
    
    @st.cache_data(show_spinner=False)
    def run(_self, data: pd.DataFrame, params: Dict[str, Any], fee: float = 0.0) -> StrategyResult:
        # Note: Use _self instead of self in cached methods
        df = data.copy()
        
        # Calculate signals
        df['signal'] = 0  # 1 = Buy, -1 = Sell, 0 = Hold
        
        # Calculate returns
        df['market_ret'] = df['Close'].pct_change()
        signal_change = df['signal'].diff().abs().fillna(0)
        df['strat_ret'] = df['market_ret'] * df['signal'].shift(1) - fee * signal_change
        
        # Cumulative returns
        df['cum_ret'] = (1 + df['strat_ret'].fillna(0)).cumprod()
        
        # Extract trades and calculate metrics
        trades_df = _self._extract_trades(df)
        metrics = _self._calculate_metrics(df['strat_ret'], trades_df)
        
        return StrategyResult(
            metrics=metrics,
            cumulative_returns=df['cum_ret'],
            trades=trades_df,
            trade_returns=trades_df['pnl'].tolist() if len(trades_df) > 0 else []
        )
```

### Adding New Strategies
1. Create file in `strategies/` directory (e.g., `moving_average.py`)
2. Implement class inheriting from `BaseStrategy`
3. Import in `strategies/__init__.py`
4. Add to `STRATEGIES` dictionary
5. Strategy automatically appears in dashboard

## UI/UX Guidelines

### Design Principles (Apple-Inspired)
- **Colors**: Use defined palette in `components/charts.py`
  - Primary Blue: `#007AFF`
  - Green: `#34C759` (positive)
  - Red: `#FF3B30` (negative)
  - Background: `#f5f5f7`
  - Text: `#1d1d1f`
- **Typography**: Inter font family (fallback to system fonts)
- **Spacing**: 8px base unit, use multiples (8, 16, 24, 32)
- **Border Radius**: 8px for all rounded corners
- **Shadows**: Subtle, use `rgba(0, 0, 0, 0.08)` for elevation

### Streamlit Components
- Always use `use_container_width=True` for charts and dataframes
- Use `st.columns()` for responsive layouts (max 2 cols on mobile, 4 on desktop)
- Prefer `st.expander()` over nested containers for collapsible sections
- Use `st.tabs()` for organizing different analysis views
- Apply `help` parameter to inputs for inline documentation

### Chart Creation with Plotly
```python
def create_chart(data, device_type='desktop'):
    fig = go.Figure()
    
    # Add traces with Apple colors
    fig.add_trace(go.Scatter(
        x=data.index,
        y=data.values,
        line=dict(color='#007AFF', width=2.5),
        hovertemplate='<b>Value</b><br>%{x}<br>%{y:.2f}<extra></extra>'
    ))
    
    # Apply consistent styling
    fig.update_layout(
        title={'text': 'Title', 'x': 0.5, 'xanchor': 'center'},
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, -apple-system, sans-serif', color='#1d1d1f'),
        hovermode='x unified'
    )
    
    # Responsive sizing
    return create_responsive_chart(fig, device_type)
```

## Performance Best Practices

### Caching Strategy
- **Data Loading**: Always use `@st.cache_data(ttl=3600)` for API calls
  ```python
  @st.cache_data(ttl=3600, show_spinner="Loading...")
  def fetch_data(ticker: str, start: str, end: str):
      return yf.download(ticker, start, end)
  ```

- **Calculations**: Cache expensive computations
  ```python
  @st.cache_data(show_spinner=False)
  def calculate_indicators(data: pd.DataFrame):
      # Heavy computation
      return results
  ```

- **Session State**: Use for UI state only, not computation results
  ```python
  if 'strategy_params' not in st.session_state:
      st.session_state.strategy_params = {}
  ```

### Data Handling
- Always copy DataFrames before modification: `df = data.copy()`
- Use `.fillna(0)` for returns calculations to avoid NaN propagation
- Ensure datetime index for time series data
- Validate inputs before expensive operations

## Common Patterns

### Input Validation
```python
def validate_inputs(ticker, start_date, end_date, params):
    errors = []
    
    if not ticker or len(ticker.strip()) == 0:
        errors.append("Ticker required")
    
    if start_date >= end_date:
        errors.append("Start date must be before end date")
    
    return len(errors) == 0, errors
```

### Error Handling
```python
try:
    data = fetch_stock_data(ticker, start, end)
except ValueError as e:
    st.error(f"❌ Error: {str(e)}")
    return
except Exception as e:
    st.error(f"❌ Unexpected error: {str(e)}")
    st.stop()
```

### Responsive Layouts
```python
is_mobile = st.session_state.device_type == 'mobile'
n_cols = 2 if is_mobile else 4

cols = st.columns(n_cols)
for idx, metric in enumerate(metrics):
    with cols[idx % n_cols]:
        st.metric(metric.label, metric.value)
```

## Testing Guidelines

### Strategy Testing
- Test with different date ranges (short, medium, long)
- Test with high/low volatility stocks
- Verify fee calculations are correct
- Check edge cases (no trades, all winning trades, all losing trades)

### Data Validation
- Ensure data exists for given ticker and date range
- Check for missing values in OHLCV data
- Validate date range is at least 30 days
- Handle market holidays and weekends

## Dependencies

### Core Libraries
- `streamlit>=1.30.0` - Web framework
- `plotly>=5.18.0` - Interactive charts
- `yfinance>=0.2.0` - Market data
- `pandas>=2.0.0` - Data manipulation
- `numpy>=1.24.0` - Numerical computations
- `scipy>=1.10.0` - Statistical functions

### Import Conventions
```python
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, List, Any
from datetime import datetime, timedelta
```

## Git Workflow

### Branch Naming
- `feature/strategy-name` - New strategies
- `feature/component-name` - New UI components
- `fix/issue-description` - Bug fixes
- `refactor/area` - Code improvements

### Commit Messages
- Use conventional commits format
- Examples:
  - `feat(strategy): add RSI strategy`
  - `fix(charts): correct drawdown calculation`
  - `refactor(data): improve caching performance`
  - `docs(readme): update deployment instructions`

## Deployment Checklist

Before deploying to Streamlit Cloud:
1. ✓ Test locally with `streamlit run app.py`
2. ✓ Verify all dependencies in `requirements.txt`
3. ✓ Check `.gitignore` excludes `venv/`, `data/`, `.DS_Store`
4. ✓ Ensure `.streamlit/config.toml` has correct settings
5. ✓ Update `README.md` with any new features
6. ✓ Test with different tickers and date ranges
7. ✓ Verify mobile responsiveness in browser DevTools

## Common Tasks

### Add a New Metric
1. Calculate in strategy `run()` method
2. Add to metrics dict returned by `_calculate_metrics()`
3. Display in appropriate tab in `app.py` using `st.metric()`

### Add a New Chart Type
1. Create function in `components/charts.py`
2. Follow Plotly pattern with responsive styling
3. Use Apple color palette
4. Add to appropriate tab in `app.py`

### Modify Strategy Logic
1. Edit the strategy's `run()` method
2. Update signal calculation
3. Recalculate returns with fees
4. Update tests and documentation

## Code Quality

### Before Committing
- Run code through linter (flake8, black)
- Check type hints with mypy
- Ensure docstrings are complete
- Test locally with multiple scenarios
- Update README if public API changes

### Code Review Focus
- Strategy logic correctness (especially signal generation)
- Fee calculation accuracy
- Performance optimization opportunities
- UI/UX consistency with Apple design
- Mobile responsiveness
- Error handling completeness

## Performance Targets

- Data fetch: < 3 seconds for 1 year of daily data
- Strategy calculation: < 2 seconds per parameter set
- Chart rendering: < 1 second
- Page load: < 2 seconds (after data cached)

## Security Notes

- Never commit API keys or secrets
- Use `.streamlit/secrets.toml` for sensitive data (gitignored)
- Validate all user inputs before processing
- Sanitize ticker symbols to prevent injection
- Keep dependencies updated for security patches

## Future Enhancements

Ideas for extending the project:
- Add more technical indicators (RSI, MACD, Bollinger Bands)
- Implement walk-forward analysis
- Add Monte Carlo simulation
- Export results to CSV/PDF
- Add user authentication for saved strategies
- Implement real-time data streaming
- Add portfolio optimization features
- Create strategy comparison matrix
