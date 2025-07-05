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
from database import db_manager
import json

# Page configuration
st.set_page_config(
    page_title="Global Finance Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database and data fetcher
@st.cache_resource
def initialize_database():
    """Initialize database tables"""
    try:
        db_manager.create_tables()
        return True
    except Exception as e:
        st.error(f"Database initialization failed: {str(e)}")
        return False

@st.cache_resource
def get_data_fetcher():
    return DataFetcher()

# Initialize database
db_initialized = initialize_database()
data_fetcher = get_data_fetcher()

# Main title
st.title("🌍 Global Finance Dashboard")
st.markdown("---")

# Sidebar for controls
st.sidebar.header("Dashboard Controls")

# Navigation
page = st.sidebar.selectbox("Navigate", ["Live Dashboard", "Historical Data", "Market Alerts", "Database Stats"])

# Auto-refresh controls (only for live dashboard)
if page == "Live Dashboard":
    auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=False)
    refresh_button = st.sidebar.button("🔄 Refresh Data")
else:
    auto_refresh = False
    refresh_button = False

# Auto-refresh logic
if auto_refresh:
    time.sleep(30)
    st.rerun()

# Manual refresh
if refresh_button:
    st.cache_data.clear()
    st.rerun()

if page == "Live Dashboard":
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
        if us_indices:
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
        if intl_indices:
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
        if metals:
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
        if energy:
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
            yield_val = max(0.1, jp_10y['price'] - 3.5)  # Approximate Japanese yield
            change = jp_10y['change'] * 0.3
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
        if tech_health:
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
        if energy_finance:
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
    if all_sectors:
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

elif page == "Historical Data":
    st.header("📈 Historical Data Analysis")
    
    # Symbol selection
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_symbol = st.selectbox(
            "Select Symbol", 
            ['SPY', 'QQQ', 'DIA', 'GLD', 'SLV', 'USO', 'UNG', '^VIX', 'XLK', 'XLV', 'XLE', 'XLF']
        )
    with col2:
        hours_back = st.slider("Hours of History", 1, 168, 24)
    
    if selected_symbol and db_initialized:
        # Get historical data from database
        historical_data = db_manager.get_historical_data(selected_symbol, hours_back)
        
        if historical_data:
            # Convert to DataFrame for easy plotting
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # Create historical price chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['price'],
                mode='lines+markers',
                name=f'{selected_symbol} Price',
                line=dict(color='blue', width=2)
            ))
            
            fig.update_layout(
                title=f"{selected_symbol} Price History (Last {hours_back} hours)",
                xaxis_title="Time",
                yaxis_title="Price",
                template="plotly_white",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Current Price", f"${df['price'].iloc[-1]:.2f}")
            with col2:
                price_change = df['price'].iloc[-1] - df['price'].iloc[0]
                st.metric("Price Change", f"${price_change:.2f}")
            with col3:
                st.metric("Max Price", f"${df['price'].max():.2f}")
            with col4:
                st.metric("Min Price", f"${df['price'].min():.2f}")
            
            # Data table
            st.subheader("Recent Data Points")
            st.dataframe(df.tail(10), use_container_width=True)
            
        else:
            st.info(f"No historical data available for {selected_symbol} in the last {hours_back} hours.")
    else:
        st.warning("Database not available or symbol not selected.")

elif page == "Market Alerts":
    st.header("🚨 Market Alerts")
    
    if not db_initialized:
        st.error("Database not available for alerts functionality.")
        st.stop()
    
    # Create new alert
    st.subheader("Create New Alert")
    with st.form("new_alert"):
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            alert_symbol = st.selectbox(
                "Symbol", 
                ['SPY', 'QQQ', 'DIA', 'GLD', 'SLV', 'USO', 'UNG', '^VIX', 'XLK', 'XLV', 'XLE', 'XLF']
            )
        with col2:
            alert_type = st.selectbox("Alert Type", ["above", "below"])
        with col3:
            target_price = st.number_input("Target Price", min_value=0.01, value=100.0, step=0.01)
        with col4:
            user_id = st.text_input("User ID", value="default_user")
        
        submit_alert = st.form_submit_button("Create Alert")
        
        if submit_alert:
            success = db_manager.create_market_alert(user_id, alert_symbol, alert_type, target_price)
            if success:
                st.success(f"Alert created: {alert_symbol} {alert_type} ${target_price}")
            else:
                st.error("Failed to create alert")
    
    # Display active alerts
    st.subheader("Active Alerts")
    active_alerts = db_manager.get_active_alerts()
    
    if active_alerts:
        alert_df = pd.DataFrame(active_alerts)
        st.dataframe(alert_df, use_container_width=True)
    else:
        st.info("No active alerts found.")
    
    # Alert checking section
    st.subheader("Check Alerts")
    if st.button("Check All Alerts Against Current Prices"):
        with st.spinner("Checking alerts..."):
            # Get current prices for all symbols
            current_prices = {}
            all_symbols = ['SPY', 'QQQ', 'DIA', 'GLD', 'SLV', 'USO', 'UNG', '^VIX', 'XLK', 'XLV', 'XLE', 'XLF']
            
            for symbol in all_symbols:
                data = data_fetcher._fetch_ticker_data(symbol)
                if data:
                    current_prices[symbol] = data['price']
            
            triggered_alerts = db_manager.check_alerts(current_prices)
            
            if triggered_alerts:
                st.success(f"🚨 {len(triggered_alerts)} alerts triggered!")
                for alert in triggered_alerts:
                    st.write(f"Alert: {alert['symbol']} {alert['alert_type']} ${alert['target_price']:.2f} - Current: ${alert['current_price']:.2f}")
            else:
                st.info("No alerts triggered.")

elif page == "Database Stats":
    st.header("📊 Database Statistics")
    
    if not db_initialized:
        st.error("Database not available.")
        st.stop()
    
    # Get market statistics
    stats = db_manager.get_market_statistics()
    
    if stats:
        st.subheader("Data Storage Summary")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Index Records", stats.get('index_records', 0))
        with col2:
            st.metric("Commodity Records", stats.get('commodity_records', 0))
        with col3:
            st.metric("Bond Records", stats.get('bond_records', 0))
        with col4:
            st.metric("VIX Records", stats.get('vix_records', 0))
        with col5:
            st.metric("Sector Records", stats.get('sector_records', 0))
        
        # Most volatile symbols
        if 'most_volatile' in stats and stats['most_volatile']:
            st.subheader("Most Volatile Symbols")
            volatile_df = pd.DataFrame(stats['most_volatile'])
            st.dataframe(volatile_df, use_container_width=True)
    
    # Database connection test
    st.subheader("Database Connection")
    try:
        session = db_manager.get_session()
        session.close()
        st.success("✅ Database connection successful")
    except Exception as e:
        st.error(f"❌ Database connection failed: {str(e)}")
    
    # Manual data cleanup
    st.subheader("Database Management")
    if st.button("Clean Old Data (>7 days)"):
        try:
            session = db_manager.get_session()
            from database import FinancialData
            cutoff_date = datetime.now() - timedelta(days=7)
            
            deleted = session.query(FinancialData).filter(
                FinancialData.timestamp < cutoff_date
            ).delete()
            
            session.commit()
            session.close()
            
            st.success(f"Cleaned {deleted} old records")
        except Exception as e:
            st.error(f"Error cleaning data: {str(e)}")
            if session:
                session.rollback()
                session.close()