"""
Application initialization module for MarketPulse.
Handles startup tasks, configuration validation, and system health checks.
"""
import sys
from typing import Dict, Any

from config import config
from database import DatabaseManager, get_db_session
from utils.logging_config import setup_logging, get_logger
from utils.exceptions import ConfigurationError, DatabaseError
from utils.cache import cache

logger = get_logger(__name__)


class AppInitializer:
    """Handles application initialization and health checks."""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.initialization_status = {}
    
    def initialize(self) -> Dict[str, Any]:
        """
        Initialize the application with comprehensive checks.
        Returns initialization status.
        """
        logger.info("Starting MarketPulse application initialization")
        
        try:
            # Setup logging first
            self._setup_logging()
            
            # Validate configuration
            self._validate_configuration()
            
            # Initialize database
            self._initialize_database()
            
            # Setup cache
            self._setup_cache()
            
            # Health checks
            self._perform_health_checks()
            
            logger.info("Application initialization completed successfully")
            self.initialization_status['status'] = 'success'
            
        except Exception as e:
            logger.critical("Application initialization failed", error=str(e))
            self.initialization_status['status'] = 'failed'
            self.initialization_status['error'] = str(e)
            raise
        
        return self.initialization_status
    
    def _setup_logging(self):
        """Setup application logging."""
        try:
            setup_logging()
            self.initialization_status['logging'] = 'configured'
            logger.info("Logging system configured")
        except Exception as e:
            print(f"Failed to setup logging: {e}")
            self.initialization_status['logging'] = 'failed'
            raise ConfigurationError(f"Logging setup failed: {e}")
    
    def _validate_configuration(self):
        """Validate application configuration."""
        try:
            # Configuration is already validated in config.py
            self.initialization_status['configuration'] = {
                'environment': config.app.environment,
                'debug': config.app.debug,
                'database_configured': bool(config.database.url),
                'ai_enabled': config.app.enable_ai_analysis,
                'news_enabled': config.app.enable_news_fetching
            }
            logger.info("Configuration validated", **self.initialization_status['configuration'])
        except Exception as e:
            self.initialization_status['configuration'] = 'failed'
            raise ConfigurationError(f"Configuration validation failed: {e}")
    
    def _initialize_database(self):
        """Initialize database connection and tables."""
        try:
            # Test database connection
            if not self.db_manager.health_check():
                raise DatabaseError("Database health check failed")
            
            # Create tables if they don't exist
            self.db_manager.create_tables()
            
            self.initialization_status['database'] = 'initialized'
            logger.info("Database initialized successfully")
            
        except Exception as e:
            self.initialization_status['database'] = 'failed'
            raise DatabaseError(f"Database initialization failed: {e}")
    
    def _setup_cache(self):
        """Setup caching system."""
        try:
            # Clear any existing cache on startup
            cache.clear()
            
            self.initialization_status['cache'] = {
                'type': 'memory',
                'default_ttl': config.cache.default_ttl,
                'status': 'initialized'
            }
            logger.info("Cache system initialized")
            
        except Exception as e:
            self.initialization_status['cache'] = 'failed'
            logger.warning("Cache setup failed, continuing without cache", error=str(e))
    
    def _perform_health_checks(self):
        """Perform system health checks."""
        health_status = {}
        
        try:
            # Database health check
            health_status['database'] = self.db_manager.health_check()
            
            # Cache health check
            try:
                cache.set('health_check', 'ok', 10)
                health_status['cache'] = cache.get('health_check') == 'ok'
                cache.delete('health_check')
            except Exception:
                health_status['cache'] = False
            
            # API availability checks (basic)
            health_status['yfinance'] = True  # Will be tested on first use
            health_status['openai'] = config.app.enable_ai_analysis
            
            self.initialization_status['health_checks'] = health_status
            
            # Log health status
            failed_checks = [k for k, v in health_status.items() if not v]
            if failed_checks:
                logger.warning("Some health checks failed", failed_checks=failed_checks)
            else:
                logger.info("All health checks passed")
                
        except Exception as e:
            logger.error("Health checks failed", error=str(e))
            self.initialization_status['health_checks'] = 'failed'
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        return {
            'app_version': '1.0.0',
            'environment': config.app.environment,
            'python_version': sys.version,
            'initialization_status': self.initialization_status,
            'features': {
                'ai_analysis': config.app.enable_ai_analysis,
                'news_fetching': config.app.enable_news_fetching,
                'real_time_updates': config.app.enable_real_time_updates
            },
            'cache_stats': cache.stats() if 'cache' in self.initialization_status else None
        }


# Global initializer instance
app_initializer = AppInitializer()


def initialize_app() -> Dict[str, Any]:
    """Initialize the application and return status."""
    return app_initializer.initialize()


def get_app_status() -> Dict[str, Any]:
    """Get current application status."""
    return app_initializer.get_system_info()