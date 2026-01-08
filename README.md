# Trading Strategies Dashboard

A professional, interactive trading strategies dashboard built with Streamlit and Plotly. Compare multiple trading strategies with comprehensive performance analytics, risk visualization, and mobile-responsive design.

## Features

- 📈 **Multiple Strategy Support**: Easily add and compare different trading strategies
- 📊 **Comprehensive Analytics**: Cumulative returns, drawdown analysis, monthly heatmaps, trade distributions
- 🎨 **Apple-Inspired Design**: Clean, minimalist UI with responsive layouts
- 📱 **Mobile Responsive**: Optimized for desktop, tablet, and mobile devices
- ⚡ **Performance Optimized**: Intelligent caching for fast calculations
- 🔧 **Configurable Parameters**: Dynamic parameter inputs for strategy customization

## Installation

### Local Development

```bash
# Clone the repository
git clone <your-repo-url>
cd trading-strategies

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Deploy to Streamlit Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Select `app.py` as the main file
5. Deploy!

## Usage

1. **Configure Global Parameters**:
   - Enter stock ticker symbol (e.g., KO, AAPL, SPY)
   - Select date range using calendar pickers
   - Set trading fee percentage

2. **Add Strategy Parameters**:
   - Each strategy has customizable parameters
   - Add multiple parameter sets to compare variations
   - Use descriptive names for each parameter set

3. **View Results**:
   - **Performance Tab**: Cumulative returns and key metrics
   - **Risk Analysis Tab**: Drawdown charts and risk metrics
   - **Trades Tab**: Trade distribution and statistics
   - **Calendar Tab**: Monthly returns heatmap

4. **Explore Strategy Details**:
   - Click 📖 Info to see strategy description
   - Click 💻 Code to view implementation

## Adding New Strategies

1. Create a new file in `strategies/` (e.g., `moving_average.py`)
2. Inherit from `BaseStrategy` class
3. Implement required methods:
   - `name`, `description` properties
   - `default_params`, `param_config` properties
   - `run(data, params)` method
4. Import in `strategies/__init__.py`
5. Add to `STRATEGIES` dictionary

The strategy will automatically appear in the dashboard!

## Project Structure

```
trading-strategies/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── strategies/
│   ├── __init__.py            # Strategy registry
│   ├── base.py                # Base strategy class
│   └── support_resistance.py  # S&R strategy implementation
├── components/
│   └── charts.py              # Plotly chart components
└── utils/
    └── data_loader.py         # Data fetching with caching
```

## Technologies

- **Streamlit**: Web application framework
- **Plotly**: Interactive charts and visualizations
- **yfinance**: Stock market data
- **Pandas**: Data manipulation
- **NumPy**: Numerical computations

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Feel free to submit issues and pull requests.
