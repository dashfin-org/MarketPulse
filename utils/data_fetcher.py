import yfinance as yf
import streamlit as st
from typing import Dict, List, Optional
import time

from config import config
from database import db_manager
from utils.exceptions import DataFetchError, ValidationError
from utils.logging_config import get_logger, log_execution_time, log_api_call

logger = get_logger(__name__)


class DataFetcher:
    """
    Handles fetching financial data from Yahoo Finance with caching and error handling
    """

    def __init__(self):
        self.cache_duration = config.cache.market_data_ttl
        self.timeout = config.api.yfinance_timeout
        self.retry_attempts = config.api.yfinance_retry_attempts

    def _validate_symbol(self, symbol: str) -> str:
        """Validate and normalize stock symbol."""
        if not symbol or not isinstance(symbol, str):
            raise ValidationError("Symbol must be a non-empty string")

        symbol = symbol.strip().upper()

        # Allow common financial symbol formats
        # Remove allowed special characters for validation
        clean_symbol = symbol.replace('.', '').replace('-', '').replace('^', '').replace('=', '')

        if not clean_symbol.isalnum():
            raise ValidationError(f"Invalid symbol format: {symbol}")

        return symbol

    @st.cache_data(ttl=60)  # Use config value
    @log_api_call("Yahoo Finance")
    @log_execution_time()
    def _fetch_ticker_data(_self, symbol: str) -> Optional[Dict]:
        """
        Fetch ticker data with caching and retry logic
        """
        symbol = _self._validate_symbol(symbol)

        for attempt in range(_self.retry_attempts):
            try:
                logger.debug("Fetching ticker data", symbol=symbol, attempt=attempt + 1)

                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="2d")

                if hist.empty:
                    logger.warning("No historical data available", symbol=symbol)
                    return None

                current_price = float(hist['Close'].iloc[-1])
                prev_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price

                change = current_price - prev_close
                change_pct = (change / prev_close) * 100 if prev_close != 0 else 0
                volume = float(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0

                return {
                    'symbol': symbol,
                    'price': current_price,
                    'change': change,
                    'change_pct': change_pct,
                    'volume': volume,
                    'info': info
                }

            except Exception as e:
                logger.warning(
                    "Failed to fetch ticker data",
                    symbol=symbol,
                    attempt=attempt + 1,
                    error=str(e)
                )
                if attempt < _self.retry_attempts - 1:
                    time.sleep(1)  # Wait before retry
                else:
                    logger.error("All retry attempts failed", symbol=symbol)
                    raise DataFetchError(
                        f"Failed to fetch data for {symbol} after {
                            _self.retry_attempts} attempts: {
                            str(e)}")

        return None

    @log_execution_time()
    def get_indices_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Fetch data for stock indices with error handling
        """
        if not symbols:
            raise ValidationError("Symbols list cannot be empty")

        indices_data = {}
        failed_symbols = []

        for symbol in symbols:
            try:
                data = self._fetch_ticker_data(symbol)
                if data:
                    indices_data[symbol] = data
                    # Store in database
                    try:
                        db_manager.store_financial_data(symbol, data, 'index')
                    except Exception as e:
                        logger.warning("Failed to store index data", symbol=symbol, error=str(e))
                else:
                    failed_symbols.append(symbol)
            except Exception as e:
                logger.error("Failed to fetch index data", symbol=symbol, error=str(e))
                failed_symbols.append(symbol)

        if failed_symbols:
            logger.warning("Some symbols failed to fetch", failed_symbols=failed_symbols)

        return indices_data

    @log_execution_time()
    def get_commodities_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Fetch data for commodities with error handling
        """
        if not symbols:
            raise ValidationError("Symbols list cannot be empty")

        commodities_data = {}
        failed_symbols = []

        for symbol in symbols:
            try:
                data = self._fetch_ticker_data(symbol)
                if data:
                    commodities_data[symbol] = data
                    # Store in database
                    try:
                        db_manager.store_financial_data(symbol, data, 'commodity')
                    except Exception as e:
                        logger.warning("Failed to store commodity data", symbol=symbol, error=str(e))
                else:
                    failed_symbols.append(symbol)
            except Exception as e:
                logger.error("Failed to fetch commodity data", symbol=symbol, error=str(e))
                failed_symbols.append(symbol)

        if failed_symbols:
            logger.warning("Some commodity symbols failed to fetch", failed_symbols=failed_symbols)

        return commodities_data

    def get_bond_data(self, symbol):
        """
        Fetch bond yield data
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")

            if hist.empty:
                logger.warning(f"No bond data for {symbol}")
                return None

            current_yield = hist['Close'].iloc[-1]
            prev_yield = hist['Close'].iloc[-2] if len(hist) > 1 else current_yield

            change = current_yield - prev_yield

            return {
                'symbol': symbol,
                'price': current_yield,
                'change': change
            }
        except Exception as e:
            logger.error(f"Error fetching bond data for {symbol}: {str(e)}")
            return None

    def get_vix_data(self):
        """
        Fetch VIX volatility index data
        """
        data = self._fetch_ticker_data('^VIX')
        if data:
            # Store in database
            try:
                db_manager.store_financial_data('^VIX', data, 'vix')
            except Exception as e:
                logger.warning(f"Failed to store VIX data: {str(e)}")
        return data

    def get_sector_etfs(self, symbols):
        """
        Fetch data for sector ETFs
        """
        sector_data = {}

        for symbol in symbols:
            data = self._fetch_ticker_data(symbol)
            if data:
                sector_data[symbol] = data
                # Store in database
                try:
                    db_manager.store_financial_data(symbol, data, 'sector')
                except Exception as e:
                    logger.warning(f"Failed to store data for {symbol}: {str(e)}")

        return sector_data

    @st.cache_data(ttl=300)
    def get_historical_data(_self, symbol, period="1mo"):
        """
        Fetch historical data for charting
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)

            if hist.empty:
                logger.warning(f"No historical data for {symbol}")
                return None

            return hist
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return None

    def get_market_summary(self):
        """
        Get a summary of key market indicators
        """
        try:
            # Key symbols to track
            key_symbols = ['^GSPC', '^IXIC', '^DJI', '^VIX', 'GLD', 'USO']

            summary = {}
            for symbol in key_symbols:
                data = self._fetch_ticker_data(symbol)
                if data:
                    summary[symbol] = {
                        'price': data['price'],
                        'change_pct': data['change_pct']
                    }

            return summary
        except Exception as e:
            logger.error(f"Error getting market summary: {str(e)}")
            return {}

    def get_top_movers(self, symbols, limit=5):
        """
        Get top movers from a list of symbols
        """
        try:
            movers = []

            for symbol in symbols:
                data = self._fetch_ticker_data(symbol)
                if data:
                    movers.append({
                        'symbol': symbol,
                        'price': data['price'],
                        'change_pct': data['change_pct']
                    })

            # Sort by absolute change percentage
            movers.sort(key=lambda x: abs(x['change_pct']), reverse=True)

            return movers[:limit]
        except Exception as e:
            logger.error(f"Error getting top movers: {str(e)}")
            return []
