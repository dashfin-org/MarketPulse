import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import streamlit as st
import logging

logger = logging.getLogger(__name__)

def create_price_chart(symbol, title, period="1mo", interval="1d"):
    """
    Create a price chart for a given symbol with specified period and interval
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            logger.warning(f"No data available for {symbol} with period={period}, interval={interval}")
            return None
        
        # Create candlestick chart for daily or longer intervals
        # Use line chart for intraday intervals
        fig = go.Figure()
        
        if interval in ['1m', '5m', '15m', '30m'] and len(hist) > 100:
            # Use line chart for intraday with many data points
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=hist['Close'],
                mode='lines',
                name=symbol,
                line=dict(color='blue', width=2)
            ))
        else:
            # Use candlestick chart for longer intervals or fewer data points
            fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name=symbol
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Date/Time",
            yaxis_title="Price",
            template="plotly_white",
            height=400,
            showlegend=False
        )
        
        # Remove range selector
        fig.update_layout(xaxis_rangeslider_visible=False)
        
        return fig
    except Exception as e:
        logger.error(f"Error creating price chart for {symbol}: {str(e)}")
        return None

def create_performance_chart(data_dict):
    """
    Create a performance comparison chart for multiple assets
    """
    try:
        if not data_dict:
            return None
        
        # Prepare data for plotting
        symbols = list(data_dict.keys())
        prices = [data_dict[symbol]['price'] for symbol in symbols]
        changes = [data_dict[symbol]['change_pct'] for symbol in symbols]
        
        # Create bar chart
        fig = go.Figure()
        
        # Color bars based on performance
        colors = ['green' if change >= 0 else 'red' for change in changes]
        
        fig.add_trace(go.Bar(
            x=symbols,
            y=changes,
            marker_color=colors,
            text=[f"{change:+.2f}%" for change in changes],
            textposition='auto',
        ))
        
        fig.update_layout(
            title="Sector Performance Comparison (% Change)",
            xaxis_title="Sector ETFs",
            yaxis_title="% Change",
            template="plotly_white",
            height=400,
            showlegend=False
        )
        
        # Add horizontal line at 0
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.7)
        
        return fig
    except Exception as e:
        logger.error(f"Error creating performance chart: {str(e)}")
        return None

def create_vix_interpretation_chart(vix_value):
    """
    Create a gauge chart for VIX interpretation
    """
    try:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = vix_value,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "VIX Volatility Level"},
            delta = {'reference': 20},
            gauge = {
                'axis': {'range': [None, 50]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 20], 'color': "lightgreen"},
                    {'range': [20, 30], 'color': "yellow"},
                    {'range': [30, 50], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 30
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            template="plotly_white"
        )
        
        return fig
    except Exception as e:
        logger.error(f"Error creating VIX gauge chart: {str(e)}")
        return None

def create_yield_curve_chart(yields_data):
    """
    Create a yield curve chart
    """
    try:
        maturities = ['3M', '6M', '1Y', '2Y', '5Y', '10Y', '20Y', '30Y']
        # This is a simplified example - in practice, you'd fetch actual yield data
        sample_yields = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.2, 4.3]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=maturities,
            y=sample_yields,
            mode='lines+markers',
            name='US Treasury Yield Curve',
            line=dict(color='blue', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="US Treasury Yield Curve",
            xaxis_title="Maturity",
            yaxis_title="Yield (%)",
            template="plotly_white",
            height=400,
            showlegend=False
        )
        
        return fig
    except Exception as e:
        logger.error(f"Error creating yield curve chart: {str(e)}")
        return None

def create_correlation_heatmap(symbols, period="1mo"):
    """
    Create a correlation heatmap for multiple assets
    """
    try:
        # Fetch data for all symbols
        data = {}
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            if not hist.empty:
                data[symbol] = hist['Close'].pct_change().dropna()
        
        if not data:
            return None
        
        # Create correlation matrix
        df = pd.DataFrame(data)
        corr_matrix = df.corr()
        
        # Create heatmap
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdBu_r",
            title="Asset Correlation Matrix"
        )
        
        fig.update_layout(
            height=500,
            template="plotly_white"
        )
        
        return fig
    except Exception as e:
        logger.error(f"Error creating correlation heatmap: {str(e)}")
        return None

def create_volume_chart(symbol, period="1mo"):
    """
    Create a volume chart for a given symbol
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty or 'Volume' not in hist.columns:
            return None
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=hist.index,
            y=hist['Volume'],
            name='Volume',
            marker_color='lightblue'
        ))
        
        fig.update_layout(
            title=f"{symbol} Trading Volume",
            xaxis_title="Date",
            yaxis_title="Volume",
            template="plotly_white",
            height=300,
            showlegend=False
        )
        
        return fig
    except Exception as e:
        logger.error(f"Error creating volume chart for {symbol}: {str(e)}")
        return None

def create_chart_from_db_data(df, symbol, interval_name):
    """
    Create a price chart from database DataFrame
    """
    try:
        if df.empty:
            return None
        
        fig = go.Figure()
        
        # Always use line chart for database data
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['price'],
            mode='lines+markers',
            name=f'{symbol} Price',
            line=dict(color='blue', width=2),
            marker=dict(size=4)
        ))
        
        fig.update_layout(
            title=f"{symbol} - {interval_name} (From Database)",
            xaxis_title="Time",
            yaxis_title="Price ($)",
            template="plotly_white",
            height=400,
            showlegend=False,
            xaxis=dict(
                type='date',
                tickformat='%Y-%m-%d %H:%M'
            )
        )
        
        return fig
    except Exception as e:
        logger.error(f"Error creating chart from database data: {str(e)}")
        return None

def create_enhanced_price_chart(symbol, interval_key, use_yfinance=True):
    """
    Create enhanced price chart using intervals system
    """
    try:
        from utils.intervals import FinanceIntervals
        
        # Get interval configuration
        params = FinanceIntervals.get_yfinance_params(interval_key)
        title = FinanceIntervals.get_chart_title(symbol, interval_key)
        
        if not params or not use_yfinance:
            return None
        
        return create_price_chart(
            symbol=symbol,
            title=title,
            period=params['period'],
            interval=params['interval']
        )
        
    except Exception as e:
        logger.error(f"Error creating enhanced price chart for {symbol}: {str(e)}")
        return None
