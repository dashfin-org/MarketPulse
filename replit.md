# Global Finance Dashboard

## Overview

This is a Streamlit-based financial dashboard that provides real-time market data visualization and analysis. The application fetches financial data from Yahoo Finance and displays interactive charts and metrics for various financial instruments including stocks, indices, and other market data.

## System Architecture

The application follows a modular architecture built on Streamlit for the web framework:

**Frontend**: Streamlit web application with interactive widgets and real-time data visualization
- Single-page application with sidebar controls
- Plotly charts for interactive financial data visualization
- Auto-refresh capability for real-time updates

**Backend**: Python-based data processing and fetching layer
- Yahoo Finance API integration for market data
- Caching layer for performance optimization
- Error handling and logging for robustness

**Data Source**: Yahoo Finance API via yfinance library
- Real-time and historical market data
- No local database storage (stateless architecture)

## Key Components

### 1. Main Application (`app.py`)
- Streamlit web interface configuration
- Dashboard layout and controls
- Auto-refresh functionality
- Column-based responsive layout

### 2. Data Fetcher (`utils/data_fetcher.py`)
- Centralized data retrieval from Yahoo Finance
- Caching mechanism with 5-minute TTL
- Error handling and logging
- Price calculation and change percentage logic

### 3. Chart Generator (`utils/charts.py`)
- Plotly-based interactive chart creation
- Candlestick charts for price visualization
- Customizable time periods and styling
- Error handling for chart generation

## Data Flow

1. **User Interaction**: User interacts with sidebar controls (refresh, auto-refresh)
2. **Data Fetching**: DataFetcher queries Yahoo Finance API for market data
3. **Data Processing**: Raw data is processed to calculate changes and percentages
4. **Caching**: Processed data is cached for 5 minutes to reduce API calls
5. **Visualization**: Charts are generated using Plotly and displayed in Streamlit
6. **Auto-refresh**: Optional 30-second auto-refresh cycle for real-time updates

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework
- **yfinance**: Yahoo Finance API client
- **Plotly**: Interactive charting library
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing

### Data Sources
- **Yahoo Finance API**: Primary source for all financial data
- No authentication required for basic market data

## Deployment Strategy

The application is designed for cloud deployment on platforms like:
- Streamlit Cloud (recommended)
- Heroku
- AWS/GCP/Azure container services

**Deployment considerations**:
- Stateless architecture (no database required)
- Environment variables for configuration
- Caching for performance optimization
- Error handling for API rate limits

## Changelog

- July 05, 2025. Initial setup
- July 05, 2025. Added PostgreSQL database integration with financial data storage, historical analysis, market alerts, and database statistics pages

## User Preferences

Preferred communication style: Simple, everyday language.