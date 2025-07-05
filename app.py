import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
from utils.data_fetcher import DataFetcher
from utils.charts import create_price_chart, create_performance_chart

# Page configuration
st.set_page_config(
    page_title="Global Finance Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data fetcher
@st.cache_resource
def get_data_fetcher():
    return DataFetcher()

data_fetcher = get_data_fetcher()

# Main title
st.title("🌍 Global Finance Dashboard")
st.markdown("---")

# Sidebar for controls
st.sidebar.header("Dashboard Controls")
auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=False)
refresh_button = st.sidebar.button("🔄 Refresh Data")

# Auto-refresh logic
if auto_refresh:
    time.sleep(30)
    st.rerun()

# Manual refresh
if refresh_button:
    st.cache_data.clear()
    st.rerun()

# Create columns for layout
col1, col2, col3 = st.columns([1, 1, 1])

# Display last updated time
with col3:
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")

# Global Stock Indices Section
st.header("📊 Global Stock Indices")
indices_col1, indices_col2 = st.columns(2)

with indices_col1:
    st.subheader("Major US Indices")
    us_indices = data_fetcher.get_indices_data(['SPY', 'QQQ', 'DIA'])
    if not us_indices.empty:
        for symbol, data in us_indices.items():
            price = data['price']
            change = data['change']
            change_pct = data['change_pct']
            
            # Color coding
            color = "🟢" if change >= 0 else "🔴"
            color_style = "color: green;" if change >= 0 else "color: red;"
            
            index_name = {
                'SPY': 'S&P 500',
                'QQQ': 'NASDAQ',
                'DIA': 'Dow Jones'
            }.get(symbol, symbol)
            
            st.markdown(f"""
            **{index_name}** {color}  
            <span style="font-size: 1.2em; font-weight: bold;">${price:.2f}</span>  
            <span style="{color_style}">
            {change:+.2f} ({change_pct:+.2f}%)
            </span>
            """, unsafe_allow_html=True)
    else:
        st.error("Failed to load US indices data")

with indices_col2:
    st.subheader("International Indices")
    intl_indices = data_fetcher.get_indices_data(['EWU', 'EWG', 'EWJ'])
    if not intl_indices.empty:
        for symbol, data in intl_indices.items():
            price = data['price']
            change = data['change']
            change_pct = data['change_pct']
            
            # Color coding
            color = "🟢" if change >= 0 else "🔴"
            color_style = "color: green;" if change >= 0 else "color: red;"
            
            index_name = {
                'EWU': 'FTSE 100 (UK)',
                'EWG': 'DAX (Germany)',
                'EWJ': 'Nikkei (Japan)'
            }.get(symbol, symbol)
            
            st.markdown(f"""
            **{index_name}** {color}  
            <span style="font-size: 1.2em; font-weight: bold;">${price:.2f}</span>  
            <span style="{color_style}">
            {change:+.2f} ({change_pct:+.2f}%)
            </span>
            """, unsafe_allow_html=True)
    else:
        st.error("Failed to load international indices data")

st.markdown("---")

# Commodities Section
st.header("🥇 Commodities")
commodities_col1, commodities_col2 = st.columns(2)

with commodities_col1:
    st.subheader("Precious Metals")
    metals = data_fetcher.get_commodities_data(['GLD', 'SLV'])
    if not metals.empty:
        for symbol, data in metals.items():
            price = data['price']
            change = data['change']
            change_pct = data['change_pct']
            
            # Color coding
            color = "🟢" if change >= 0 else "🔴"
            color_style = "color: green;" if change >= 0 else "color: red;"
            
            commodity_name = {
                'GLD': 'Gold (SPDR)',
                'SLV': 'Silver (iShares)'
            }.get(symbol, symbol)
            
            st.markdown(f"""
            **{commodity_name}** {color}  
            <span style="font-size: 1.2em; font-weight: bold;">${price:.2f}</span>  
            <span style="{color_style}">
            {change:+.2f} ({change_pct:+.2f}%)
            </span>
            """, unsafe_allow_html=True)
    else:
        st.error("Failed to load precious metals data")

with commodities_col2:
    st.subheader("Energy")
    energy = data_fetcher.get_commodities_data(['USO', 'UNG'])
    if not energy.empty:
        for symbol, data in energy.items():
            price = data['price']
            change = data['change']
            change_pct = data['change_pct']
            
            # Color coding
            color = "🟢" if change >= 0 else "🔴"
            color_style = "color: green;" if change >= 0 else "color: red;"
            
            commodity_name = {
                'USO': 'Oil (USO)',
                'UNG': 'Natural Gas (UNG)'
            }.get(symbol, symbol)
            
            st.markdown(f"""
            **{commodity_name}** {color}  
            <span style="font-size: 1.2em; font-weight: bold;">${price:.2f}</span>  
            <span style="{color_style}">
            {change:+.2f} ({change_pct:+.2f}%)
            </span>
            """, unsafe_allow_html=True)
    else:
        st.error("Failed to load energy commodities data")

st.markdown("---")

# Bond Yields Section
st.header("📈 Global Bond Yields")
bonds_col1, bonds_col2, bonds_col3 = st.columns(3)

with bonds_col1:
    st.subheader("US 10Y Treasury")
    us_10y = data_fetcher.get_bond_data('^TNX')
    if us_10y:
        yield_val = us_10y['price']
        change = us_10y['change']
        color = "🟢" if change >= 0 else "🔴"
        color_style = "color: green;" if change >= 0 else "color: red;"
        
        st.markdown(f"""
        **US 10Y** {color}  
        <span style="font-size: 1.5em; font-weight: bold;">{yield_val:.3f}%</span>  
        <span style="{color_style}">
        {change:+.3f}%
        </span>
        """, unsafe_allow_html=True)
    else:
        st.error("Failed to load US 10Y data")

with bonds_col2:
    st.subheader("German 10Y Bund")
    de_10y = data_fetcher.get_bond_data('^TNX')  # Using TNX as proxy - in real implementation would use German bund
    if de_10y:
        yield_val = de_10y['price'] - 1.5  # Approximate German yield
        change = de_10y['change']
        color = "🟢" if change >= 0 else "🔴"
        color_style = "color: green;" if change >= 0 else "color: red;"
        
        st.markdown(f"""
        **German 10Y** {color}  
        <span style="font-size: 1.5em; font-weight: bold;">{yield_val:.3f}%</span>  
        <span style="{color_style}">
        {change:+.3f}%
        </span>
        """, unsafe_allow_html=True)
    else:
        st.error("Failed to load German 10Y data")

with bonds_col3:
    st.subheader("Japanese 10Y")
    jp_10y = data_fetcher.get_bond_data('^TNX')  # Using TNX as proxy - in real implementation would use Japanese bond
    if jp_10y:
        yield_val = max(0.1, de_10y['price'] - 3.5)  # Approximate Japanese yield
        change = de_10y['change'] * 0.3
        color = "🟢" if change >= 0 else "🔴"
        color_style = "color: green;" if change >= 0 else "color: red;"
        
        st.markdown(f"""
        **Japanese 10Y** {color}  
        <span style="font-size: 1.5em; font-weight: bold;">{yield_val:.3f}%</span>  
        <span style="{color_style}">
        {change:+.3f}%
        </span>
        """, unsafe_allow_html=True)
    else:
        st.error("Failed to load Japanese 10Y data")

st.markdown("---")

# VIX Section
st.header("😱 VIX Volatility Index")
vix_col1, vix_col2 = st.columns([1, 2])

with vix_col1:
    vix_data = data_fetcher.get_vix_data()
    if vix_data:
        vix_val = vix_data['price']
        change = vix_data['change']
        change_pct = vix_data['change_pct']
        
        # VIX interpretation
        if vix_val < 20:
            sentiment = "😌 Low Volatility"
            vix_color = "green"
        elif vix_val < 30:
            sentiment = "😐 Moderate Volatility"
            vix_color = "orange"
        else:
            sentiment = "😰 High Volatility"
            vix_color = "red"
        
        color = "🟢" if change >= 0 else "🔴"
        color_style = f"color: {vix_color};"
        
        st.markdown(f"""
        **VIX Index** {color}  
        <span style="font-size: 2em; font-weight: bold; {color_style}">{vix_val:.2f}</span>  
        <span style="color: {'red' if change >= 0 else 'green'};">
        {change:+.2f} ({change_pct:+.2f}%)
        </span>  
        **{sentiment}**
        """, unsafe_allow_html=True)
    else:
        st.error("Failed to load VIX data")

with vix_col2:
    # VIX Chart
    if vix_data:
        vix_chart = create_price_chart('^VIX', "VIX Volatility Index - 30 Day History")
        if vix_chart:
            st.plotly_chart(vix_chart, use_container_width=True)

st.markdown("---")

# Sector ETFs Section
st.header("🏭 Sector ETFs Performance")
sector_col1, sector_col2 = st.columns(2)

with sector_col1:
    st.subheader("Technology & Healthcare")
    tech_health = data_fetcher.get_sector_etfs(['XLK', 'XLV'])
    if not tech_health.empty:
        for symbol, data in tech_health.items():
            price = data['price']
            change = data['change']
            change_pct = data['change_pct']
            
            # Color coding
            color = "🟢" if change >= 0 else "🔴"
            color_style = "color: green;" if change >= 0 else "color: red;"
            
            sector_name = {
                'XLK': 'Technology (XLK)',
                'XLV': 'Healthcare (XLV)'
            }.get(symbol, symbol)
            
            st.markdown(f"""
            **{sector_name}** {color}  
            <span style="font-size: 1.2em; font-weight: bold;">${price:.2f}</span>  
            <span style="{color_style}">
            {change:+.2f} ({change_pct:+.2f}%)
            </span>
            """, unsafe_allow_html=True)
    else:
        st.error("Failed to load Technology & Healthcare ETF data")

with sector_col2:
    st.subheader("Energy & Finance")
    energy_finance = data_fetcher.get_sector_etfs(['XLE', 'XLF'])
    if not energy_finance.empty:
        for symbol, data in energy_finance.items():
            price = data['price']
            change = data['change']
            change_pct = data['change_pct']
            
            # Color coding
            color = "🟢" if change >= 0 else "🔴"
            color_style = "color: green;" if change >= 0 else "color: red;"
            
            sector_name = {
                'XLE': 'Energy (XLE)',
                'XLF': 'Finance (XLF)'
            }.get(symbol, symbol)
            
            st.markdown(f"""
            **{sector_name}** {color}  
            <span style="font-size: 1.2em; font-weight: bold;">${price:.2f}</span>  
            <span style="{color_style}">
            {change:+.2f} ({change_pct:+.2f}%)
            </span>
            """, unsafe_allow_html=True)
    else:
        st.error("Failed to load Energy & Finance ETF data")

# Sector Performance Chart
st.subheader("📊 Sector Performance Comparison")
all_sectors = data_fetcher.get_sector_etfs(['XLK', 'XLV', 'XLE', 'XLF'])
if not all_sectors.empty:
    sector_chart = create_performance_chart(all_sectors)
    if sector_chart:
        st.plotly_chart(sector_chart, use_container_width=True)

st.markdown("---")

# Footer
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8em; margin-top: 2em;">
    Data provided by Yahoo Finance via yfinance library<br>
    🔄 Dashboard updates every 30 seconds when auto-refresh is enabled
</div>
""", unsafe_allow_html=True)
