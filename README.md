# MarketPulse - Professional Financial Dashboard

A comprehensive financial analysis platform with real-time data, AI insights, and portfolio management.

## Overview

MarketPulse is a Streamlit-based financial dashboard that provides real-time market data visualization and analysis. The application fetches financial data from Yahoo Finance and displays interactive charts and metrics for various financial instruments including stocks, indices, and other market data.

## Features

- **Live Dashboard**: Real-time market data with auto-refresh capability
- **Historical Data**: Comprehensive historical data analysis
- **Fundamental Analysis**: AI-powered valuation analysis using OpenAI GPT-5
- **Market Alerts**: Price trigger notifications and tracking
- **News Aggregation**: RSS feeds from major financial sources
- **Portfolio Management**: Track and manage investment portfolios
- **Database Integration**: PostgreSQL storage for historical data and analytics

## GitHub MCP Server

For AI assistants and automation tools that need to interact with this repository, you can use the GitHub MCP (Model Context Protocol) server:

**GitHub MCP Server URL**: `https://github.com/modelcontextprotocol/servers/tree/main/src/github`

The GitHub MCP server enables programmatic access to GitHub repositories, issues, pull requests, and other GitHub features through a standardized protocol. This is particularly useful for AI-powered development tools and assistants.

### Installing the GitHub MCP Server

```bash
# Using npm
npm install -g @modelcontextprotocol/server-github

# Or using npx
npx @modelcontextprotocol/server-github
```

For more information about the Model Context Protocol and available servers, visit:
- MCP Documentation: `https://modelcontextprotocol.io`
- MCP Servers Repository: `https://github.com/modelcontextprotocol/servers`

## Installation

### Prerequisites

- Python >= 3.11
- PostgreSQL (optional, for database features)
- OpenAI API key (optional, for AI-powered analysis)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/dashfin-org/MarketPulse.git
cd MarketPulse
```

2. Install dependencies:
```bash
pip install -r requirements.txt
# Or using uv
uv pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the application:
```bash
streamlit run app.py
```

## Configuration

The application uses environment variables for configuration. See `.env.example` for available options:

- `OPENAI_API_KEY`: Your OpenAI API key for AI-powered analysis
- `DATABASE_URL`: PostgreSQL connection string (optional)
- Additional configuration in `config.py`

## System Architecture

### Frontend
- Multi-page Streamlit web application with interactive widgets
- Plotly charts for interactive financial data visualization
- Auto-refresh capability for real-time updates
- AI-powered fundamental analysis with multiple valuation frameworks

### Backend
- Yahoo Finance API integration for market data
- OpenAI GPT-5 integration for AI-powered fundamental analysis
- PostgreSQL database for historical data storage
- Caching layer for performance optimization

### Data Sources
- Yahoo Finance API via yfinance library
- RSS feeds from major financial news sources
- Database storage for accumulated historical data

## Usage

1. **Live Dashboard**: View real-time market data for various financial instruments
2. **Historical Data**: Analyze historical price trends and patterns
3. **Fundamental Analysis**: Get AI-powered valuation analysis and investment recommendations
4. **Market Alerts**: Set up price triggers and notifications
5. **News**: Stay updated with financial news from multiple sources
6. **Portfolio**: Track and manage your investment portfolio

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

- **Get Help**: [https://github.com/dashfin-org/MarketPulse](https://github.com/dashfin-org/MarketPulse)
- **Report a Bug**: [https://github.com/dashfin-org/MarketPulse/issues](https://github.com/dashfin-org/MarketPulse/issues)

## License

This project is open source and available under the appropriate license.

## Changelog

- **October 04, 2025**: Added Fundamental Analysis page with AI-powered valuation analysis
- **July 05, 2025**: Added news and portfolio tracking functionality
- **July 05, 2025**: Added PostgreSQL database integration
- **July 05, 2025**: Initial setup

## Acknowledgments

- Yahoo Finance for market data
- OpenAI for AI-powered analysis
- Streamlit for the web framework
- The open-source community for various libraries and tools
