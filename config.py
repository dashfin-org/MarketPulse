"""
Configuration management for MarketPulse application.
Handles environment variables, database settings, and application configuration.
"""
import os
import logging
from typing import Optional
from dataclasses import dataclass
from pathlib import Path

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # dotenv not available, continue without it
    pass


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    url: Optional[str] = None
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False

    def __post_init__(self):
        if not self.url:
            self.url = os.getenv('DATABASE_URL')
        
        # Set echo to True in development
        if os.getenv('ENVIRONMENT', 'development').lower() == 'development':
            self.echo = True


@dataclass
class APIConfig:
    """External API configuration."""
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    openai_max_tokens: int = 2000
    openai_temperature: float = 0.1
    
    # Yahoo Finance settings
    yfinance_timeout: int = 10
    yfinance_retry_attempts: int = 3
    
    # News API settings
    news_sources_timeout: int = 15
    max_news_articles: int = 50

    def __post_init__(self):
        if not self.openai_api_key:
            self.openai_api_key = os.getenv('OPENAI_API_KEY')


@dataclass
class CacheConfig:
    """Caching configuration."""
    default_ttl: int = 300  # 5 minutes
    market_data_ttl: int = 60  # 1 minute for market data
    news_ttl: int = 900  # 15 minutes for news
    fundamental_data_ttl: int = 3600  # 1 hour for fundamental data
    
    # Redis settings (if using Redis)
    redis_url: Optional[str] = None
    redis_db: int = 0

    def __post_init__(self):
        if not self.redis_url:
            self.redis_url = os.getenv('REDIS_URL')


@dataclass
class AppConfig:
    """Main application configuration."""
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    
    # Streamlit settings
    streamlit_host: str = "0.0.0.0"
    streamlit_port: int = 5000
    
    # Security settings
    secret_key: Optional[str] = None
    
    # Feature flags
    enable_ai_analysis: bool = True
    enable_news_fetching: bool = True
    enable_real_time_updates: bool = False

    def __post_init__(self):
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.debug = self.environment.lower() == 'development'
        self.log_level = os.getenv('LOG_LEVEL', 'DEBUG' if self.debug else 'INFO')
        
        if not self.secret_key:
            self.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
        
        # Disable AI features if no API key is provided
        if not os.getenv('OPENAI_API_KEY'):
            self.enable_ai_analysis = False


class Config:
    """Main configuration class that combines all config sections."""
    
    def __init__(self):
        self.database = DatabaseConfig()
        self.api = APIConfig()
        self.cache = CacheConfig()
        self.app = AppConfig()
        
        # Validate critical configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate critical configuration settings."""
        errors = []
        
        if not self.database.url:
            errors.append("DATABASE_URL environment variable is required")
        
        if self.app.enable_ai_analysis and not self.api.openai_api_key:
            errors.append("OPENAI_API_KEY is required when AI analysis is enabled")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors)
            raise ValueError(error_msg)
    
    def setup_logging(self):
        """Setup application logging."""
        logging.basicConfig(
            level=getattr(logging, self.app.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('marketpulse.log') if not self.app.debug else logging.NullHandler()
            ]
        )
        
        # Set specific loggers
        logging.getLogger('yfinance').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)


# Global configuration instance
config = Config()