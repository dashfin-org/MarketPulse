import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
import logging
from database import db_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFetcher:
    """
    Handles fetching financial data from Yahoo Finance with caching and error handling
    """
    
    def __init__(self):
        self.cache_duration = 300  # 5 minutes cache
    
    @st.cache_data(ttl=300)
    def _fetch_ticker_data(_self, symbol):
        """
        Fetch ticker data with caching
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="2d")
            
            if hist.empty:
                logger.warning(f"No historical data for {symbol}")
                return None
            
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100 if prev_close != 0 else 0
            
            return {
                'symbol': symbol,
                'price': current_price,
                'change': change,
                'change_pct': change_pct,
                'volume': hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0,
                'info': info
            }
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def get_indices_data(self, symbols):
        """
        Fetch data for stock indices
        """
        indices_data = {}
        
        for symbol in symbols:
            data = self._fetch_ticker_data(symbol)
            if data:
                indices_data[symbol] = data
                # Store in database
                try:
                    db_manager.store_financial_data(symbol, data, 'index')
                except Exception as e:
                    logger.warning(f"Failed to store data for {symbol}: {str(e)}")
        
        return indices_data
    
    def get_commodities_data(self, symbols):
        """
        Fetch data for commodities
        """
        commodities_data = {}
        
        for symbol in symbols:
            data = self._fetch_ticker_data(symbol)
            if data:
                commodities_data[symbol] = data
                # Store in database
                try:
                    db_manager.store_financial_data(symbol, data, 'commodity')
                except Exception as e:
                    logger.warning(f"Failed to store data for {symbol}: {str(e)}")
        
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
