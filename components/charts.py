"""
Plotly chart components for trading strategy visualization.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List


# Apple-inspired color palette
COLORS = {
    'blue': '#007AFF',
    'green': '#34C759',
    'orange': '#FF9500',
    'pink': '#FF2D55',
    'purple': '#5856D6',
    'teal': '#00C7BE',
    'red': '#FF3B30',
    'gray': '#8E8E93'
}

COLOR_LIST = [COLORS['blue'], COLORS['green'], COLORS['orange'], 
              COLORS['pink'], COLORS['purple'], COLORS['teal']]


def create_responsive_chart(fig, device_type: str = 'desktop'):
    """
    Apply responsive styling to Plotly figure.
    
    Args:
        fig: Plotly figure object
        device_type: 'mobile', 'tablet', or 'desktop'
    
    Returns:
        Modified figure with responsive settings
    """
    if device_type == 'mobile':
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=60, b=20),
            font=dict(size=10),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5,
                font=dict(size=9)
            )
        )
    else:
        fig.update_layout(
            height=500,
            margin=dict(l=60, r=50, t=80, b=50),
            font=dict(size=12)
        )
    
    return fig


def create_cumulative_returns_chart(
    results_dict: Dict[str, pd.Series],
    symbol: str = '',
    benchmark: pd.Series = None,
    device_type: str = 'desktop'
) -> go.Figure:
    """
    Create cumulative returns comparison chart.
    
    Args:
        results_dict: Dictionary mapping strategy names to cumulative return Series
        symbol: Stock symbol for title
        benchmark: Optional benchmark cumulative returns (e.g., Buy & Hold)
        device_type: Device type for responsive styling
    
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    # Debug: Print data info
    import streamlit as st
    st.write(f"**Chart Debug:** Benchmark empty: {benchmark is None or (isinstance(benchmark, pd.Series) and benchmark.empty)}")
    st.write(f"Number of strategies: {len(results_dict)}")
    
    # Add benchmark if provided
    if benchmark is not None and not (isinstance(benchmark, pd.Series) and benchmark.empty):
        fig.add_trace(go.Scatter(
            x=benchmark.index,
            y=(benchmark - 1) * 100,  # Convert to percentage
            mode='lines',
            name='Buy & Hold',
            line=dict(color=COLORS['gray'], width=2, dash='dash'),
            hovertemplate='<b>Buy & Hold</b><br>Date: %{x|%Y-%m-%d}<br>Return: %{y:.2f}%<extra></extra>'
        ))
    
    # Add strategy traces
    for idx, (strategy_name, cum_returns) in enumerate(results_dict.items()):
        fig.add_trace(go.Scatter(
            x=cum_returns.index,
            y=(cum_returns - 1) * 100,  # Convert to percentage
            mode='lines',
            name=strategy_name,
            line=dict(color=COLOR_LIST[idx % len(COLOR_LIST)], width=2.5),
            hovertemplate=f'<b>{strategy_name}</b><br>Date: %{{x|%Y-%m-%d}}<br>Return: %{{y:.2f}}%<extra></extra>'
        ))
    
    # Apply styling
    title_text = f'Cumulative Returns - {symbol}' if symbol else 'Cumulative Returns'
    
    fig.update_layout(
        title={
            'text': title_text,
            'x': 0.5,
            'y': 0.95,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20 if device_type == 'mobile' else 24, 
                     'family': 'Inter, -apple-system, sans-serif'}
        },
        xaxis=dict(
            title='Date',
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.1)',
            showline=True,
            linewidth=1,
            linecolor='rgba(128, 128, 128, 0.3)'
        ),
        yaxis=dict(
            title='Cumulative Return (%)',
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128, 128, 128, 0.1)',
            showline=True,
            linewidth=1,
            linecolor='rgba(128, 128, 128, 0.3)',
            tickformat='.2f',
            ticksuffix='%'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        font=dict(
            family='Inter, -apple-system, sans-serif',
            color='#1d1d1f'
        )
    )
    
    # Apply responsive settings
    fig = create_responsive_chart(fig, device_type)
    
    return fig


def create_drawdown_chart(
    returns_series: pd.Series,
    strategy_name: str = 'Strategy',
    device_type: str = 'desktop'
) -> go.Figure:
    """
    Create drawdown area chart.
    
    Args:
        returns_series: Series of strategy returns
        strategy_name: Name for the chart title
        device_type: Device type for responsive styling
    
    Returns:
        Plotly figure object
    """
    # Calculate cumulative returns
    cumulative = (1 + returns_series.fillna(0)).cumprod()
    
    # Calculate running maximum
    running_max = cumulative.expanding().max()
    
    # Calculate drawdown (negative values)
    drawdown = (cumulative - running_max) / running_max * 100
    
    fig = go.Figure()
    
    # Add area chart
    fig.add_trace(go.Scatter(
        x=drawdown.index,
        y=drawdown,
        fill='tozeroy',
        fillcolor='rgba(255, 59, 48, 0.3)',
        line=dict(color=COLORS['red'], width=2),
        name='Drawdown',
        hovertemplate='Date: %{x|%Y-%m-%d}<br>Drawdown: %{y:.2f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': f'{strategy_name} - Drawdown',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20 if device_type == 'mobile' else 24,
                     'family': 'Inter, -apple-system, sans-serif'}
        },
        xaxis_title='Date',
        yaxis_title='Drawdown (%)',
        yaxis=dict(ticksuffix='%'),
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, -apple-system, sans-serif', color='#1d1d1f'),
        showlegend=False
    )
    
    # Apply responsive settings
    fig = create_responsive_chart(fig, device_type)
    
    return fig


def create_trade_distribution(
    trade_returns: List[float],
    strategy_name: str = 'Strategy',
    device_type: str = 'desktop'
) -> go.Figure:
    """
    Create trade return distribution histogram.
    
    Args:
        trade_returns: List of individual trade returns (as percentages)
        strategy_name: Name for the chart title
        device_type: Device type for responsive styling
    
    Returns:
        Plotly figure object
    """
    if not trade_returns or len(trade_returns) == 0:
        # Return empty chart with message
        fig = go.Figure()
        fig.add_annotation(
            text="No trades to display",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color=COLORS['gray'])
        )
        fig.update_layout(
            title=f'{strategy_name} - Trade Distribution',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        return fig
    
    # Calculate statistics
    mean_return = np.mean(trade_returns)
    median_return = np.median(trade_returns)
    
    # Create color scale based on values
    colors_mapped = [COLORS['green'] if x > 0 else COLORS['red'] for x in trade_returns]
    
    fig = go.Figure()
    
    # Create histogram
    fig.add_trace(go.Histogram(
        x=trade_returns,
        nbinsx=min(30, len(trade_returns) // 2 + 1),
        name='Trade Returns',
        marker=dict(
            color=trade_returns,
            colorscale=[[0, COLORS['red']], [0.5, COLORS['gray']], [1, COLORS['green']]],
            line=dict(color='white', width=1),
            cmid=0
        ),
        hovertemplate='Return: %{x:.2f}%<br>Count: %{y}<extra></extra>'
    ))
    
    # Add mean line
    fig.add_vline(
        x=mean_return,
        line_dash="dash",
        line_color=COLORS['blue'],
        line_width=2,
        annotation_text=f"Mean: {mean_return:.2f}%",
        annotation_position="top"
    )
    
    fig.update_layout(
        title={
            'text': f'{strategy_name} - Trade Distribution',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20 if device_type == 'mobile' else 24,
                     'family': 'Inter, -apple-system, sans-serif'}
        },
        xaxis_title='Return (%)',
        yaxis_title='Frequency',
        xaxis=dict(ticksuffix='%'),
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, -apple-system, sans-serif', color='#1d1d1f')
    )
    
    # Apply responsive settings
    fig = create_responsive_chart(fig, device_type)
    
    return fig


def create_monthly_heatmap(
    returns_series: pd.Series,
    strategy_name: str = 'Strategy',
    device_type: str = 'desktop'
) -> go.Figure:
    """
    Create monthly returns heatmap.
    
    Args:
        returns_series: Series of daily returns with datetime index
        strategy_name: Name for the chart title
        device_type: Device type for responsive styling
    
    Returns:
        Plotly figure object
    """
    # Check if series is empty or doesn't have DatetimeIndex
    if returns_series.empty or not isinstance(returns_series.index, pd.DatetimeIndex):
        # Return empty chart with message
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data for monthly heatmap",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color=COLORS['gray'])
        )
        fig.update_layout(
            title=f'{strategy_name} - Monthly Returns',
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        return fig
    
    # Resample to monthly returns (ME = Month End, replacing deprecated 'M')
    monthly_returns = returns_series.resample('ME').apply(
        lambda x: (1 + x).prod() - 1
    ) * 100  # Convert to percentage
    
    if len(monthly_returns) == 0:
        # Return empty chart with message
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data for monthly heatmap",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color=COLORS['gray'])
        )
        fig.update_layout(
            title=f'{strategy_name} - Monthly Returns',
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        return fig
    
    # Create pivot table: rows=years, columns=months
    pivot = monthly_returns.to_frame('returns')
    pivot['year'] = pivot.index.year
    pivot['month'] = pivot.index.strftime('%b')
    
    # Pivot: years as rows, months as columns
    pivot_table = pivot.pivot(index='year', columns='month', values='returns')
    
    # Ensure correct month order
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Reindex to include all months (fill missing with NaN)
    pivot_table = pivot_table.reindex(columns=month_order)
    
    # Create text annotations (rounded values)
    text = pivot_table.round(1).astype(str)
    text = text.replace('nan', '')
    
    fig = px.imshow(
        pivot_table,
        labels=dict(x="Month", y="Year", color="Return (%)"),
        x=month_order,
        y=pivot_table.index,
        color_continuous_scale='RdYlGn',
        color_continuous_midpoint=0,
        aspect="auto",
        text_auto=False
    )
    
    # Add custom text annotations
    fig.update_traces(
        text=text.values,
        texttemplate='%{text}',
        textfont={"size": 10 if device_type == 'mobile' else 12}
    )
    
    fig.update_layout(
        title={
            'text': f'{strategy_name} - Monthly Returns',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20 if device_type == 'mobile' else 24,
                     'family': 'Inter, -apple-system, sans-serif'}
        },
        xaxis=dict(side='top', title=''),
        yaxis=dict(title=''),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, -apple-system, sans-serif', color='#1d1d1f')
    )
    
    # Apply responsive settings
    fig = create_responsive_chart(fig, device_type)
    
    return fig
