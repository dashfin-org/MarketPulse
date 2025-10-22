"""
MarketPulse - Professional Financial Dashboard
A comprehensive financial analysis platform with real-time data, AI insights, and portfolio management.
"""
import streamlit as st
import time

# Import our refactored modules
from app_init import initialize_app, get_app_status
from config import config
from utils.data_fetcher import DataFetcher
from utils.logging_config import get_logger
from utils.exceptions import MarketPulseException, DataFetchError
from utils.cache import periodic_cleanup

# Configure Streamlit page
st.set_page_config(
    page_title="MarketPulse - Financial Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/dashfin-org/MarketPulse',
        'Report a bug': 'https://github.com/dashfin-org/MarketPulse/issues',
        'About': "MarketPulse - Professional Financial Dashboard v1.0.0"
    }
)

# Initialize logger
logger = get_logger(__name__)

# Application initialization


@st.cache_resource
def initialize_application():
    """Initialize the MarketPulse application with comprehensive setup."""
    try:
        status = initialize_app()
        logger.info("Application initialized successfully")
        return status
    except Exception as e:
        logger.critical("Application initialization failed", error=str(e))
        st.error(f"🚨 Application initialization failed: {str(e)}")
        st.stop()
        return None


@st.cache_resource
def get_data_fetcher():
    """Get cached DataFetcher instance."""
    return DataFetcher()


def display_system_status():
    """Display system status in sidebar."""
    with st.sidebar:
        with st.expander("🔧 System Status", expanded=False):
            app_status = get_app_status()

            # Environment info
            st.write(f"**Environment:** {app_status['environment']}")
            st.write(f"**Version:** {app_status['app_version']}")

            # Health checks
            health = app_status['initialization_status'].get('health_checks', {})
            for service, status in health.items():
                icon = "✅" if status else "❌"
                st.write(f"{icon} {service.title()}")

            # Cache stats
            cache_stats = app_status.get('cache_stats', {})
            if cache_stats:
                st.write(f"**Cache:** {cache_stats['active_entries']} active entries")


def handle_error(error: Exception, context: str = "Operation"):
    """Centralized error handling."""
    logger.error(f"{context} failed", error=str(error), error_type=type(error).__name__)

    if isinstance(error, DataFetchError):
        st.error(f"📊 Data fetch error: {str(error)}")
    elif isinstance(error, MarketPulseException):
        st.error(f"⚠️ {context} error: {str(error)}")
    else:
        st.error(f"🚨 Unexpected error in {context}: {str(error)}")
        if config.app.debug:
            st.exception(error)


def main():
    """Main application entry point."""
    # Initialize application
    init_status = initialize_application()
    if not init_status:
        return

    # Display system status
    display_system_status()

    # Periodic cache cleanup
    if st.session_state.get('last_cleanup', 0) < time.time() - 300:  # Every 5 minutes
        periodic_cleanup()
        st.session_state.last_cleanup = time.time()

    # Main application header
    st.title("📈 MarketPulse")
    st.markdown("*Professional Financial Dashboard with Real-time Analytics*")

    # Navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Dashboard",
        "📊 Markets",
        "📰 News",
        "💼 Portfolio",
        "🤖 AI Analysis"
    ])

    try:
        data_fetcher = get_data_fetcher()

        with tab1:
            render_dashboard(data_fetcher)

        with tab2:
            render_markets(data_fetcher)

        with tab3:
            render_news()

        with tab4:
            render_portfolio()

        with tab5:
            render_ai_analysis(data_fetcher)

    except Exception as e:
        handle_error(e, "Main application")


def render_dashboard(data_fetcher: DataFetcher):
    """Render the main dashboard."""
    st.header("Market Overview")

    try:
        # Market indices
        col1, col2, col3, col4 = st.columns(4)

        indices = ['^GSPC', '^DJI', '^IXIC', '^RUT']  # S&P 500, Dow, NASDAQ, Russell 2000
        index_names = ['S&P 500', 'Dow Jones', 'NASDAQ', 'Russell 2000']

        indices_data = data_fetcher.get_indices_data(indices)

        for i, (symbol, name) in enumerate(zip(indices, index_names)):
            with [col1, col2, col3, col4][i]:
                if symbol in indices_data:
                    data = indices_data[symbol]
                    price = data['price']
                    change = data['change']
                    change_pct = data['change_pct']

                    arrow = "↗️" if change >= 0 else "↘️"

                    st.metric(
                        label=f"{arrow} {name}",
                        value=f"{price:,.2f}",
                        delta=f"{change:+.2f} ({change_pct:+.2f}%)"
                    )
                else:
                    st.metric(label=name, value="N/A", delta="Data unavailable")

        # Additional dashboard content would go here
        st.info("💡 Dashboard is loading with real-time market data. More features coming soon!")

    except Exception as e:
        handle_error(e, "Dashboard rendering")


def render_markets(data_fetcher: DataFetcher):
    """Render the markets tab."""
    st.header("Market Analysis")
    st.info("🚧 Markets section under development. Advanced charting and analysis coming soon!")


def render_news():
    """Render the news tab."""
    st.header("Financial News")
    st.info("📰 News integration under development. Real-time financial news coming soon!")


def render_portfolio():
    """Render the portfolio tab."""
    st.header("Portfolio Management")
    st.info("💼 Portfolio management features under development. Track your investments soon!")


def render_ai_analysis(data_fetcher: DataFetcher):
    """Render the AI analysis tab."""
    st.header("AI-Powered Analysis")

    if not config.app.enable_ai_analysis:
        st.warning("🤖 AI Analysis is currently disabled. Enable it in configuration to access AI features.")
        return

    st.info("🤖 AI analysis features under development. Get intelligent market insights soon!")


if __name__ == "__main__":
    main()
