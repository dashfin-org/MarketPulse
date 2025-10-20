"""
Logging configuration and utilities for MarketPulse application.
"""
import logging
import sys
from typing import Optional
from functools import wraps
import time

from config import config


class StructuredLogger:
    """Structured logger with context support."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context = {}
    
    def with_context(self, **kwargs):
        """Add context to logger."""
        new_logger = StructuredLogger(self.logger.name)
        new_logger.context = {**self.context, **kwargs}
        return new_logger
    
    def _log(self, level: int, message: str, **kwargs):
        """Internal logging method with context."""
        context = {**self.context, **kwargs}
        if context:
            context_str = " | ".join(f"{k}={v}" for k, v in context.items())
            message = f"{message} | {context_str}"
        self.logger.log(level, message)
    
    def debug(self, message: str, **kwargs):
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log(logging.CRITICAL, message, **kwargs)


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name)


def log_execution_time(logger: Optional[StructuredLogger] = None):
    """Decorator to log function execution time."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            func_logger = logger or get_logger(func.__module__)
            
            try:
                func_logger.debug(f"Starting {func.__name__}")
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                func_logger.debug(
                    f"Completed {func.__name__}",
                    execution_time=f"{execution_time:.3f}s"
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                func_logger.error(
                    f"Failed {func.__name__}",
                    error=str(e),
                    execution_time=f"{execution_time:.3f}s"
                )
                raise
        return wrapper
    return decorator


def log_api_call(api_name: str, logger: Optional[StructuredLogger] = None):
    """Decorator to log API calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_logger = logger or get_logger(func.__module__)
            
            try:
                func_logger.info(f"API call started", api=api_name, function=func.__name__)
                result = func(*args, **kwargs)
                func_logger.info(f"API call successful", api=api_name, function=func.__name__)
                return result
            except Exception as e:
                func_logger.error(
                    f"API call failed",
                    api=api_name,
                    function=func.__name__,
                    error=str(e)
                )
                raise
        return wrapper
    return decorator


class StreamlitLogHandler(logging.Handler):
    """Custom log handler for Streamlit applications."""
    
    def emit(self, record):
        """Emit log record to Streamlit."""
        try:
            import streamlit as st
            log_entry = self.format(record)
            
            if record.levelno >= logging.ERROR:
                st.error(f"🚨 {log_entry}")
            elif record.levelno >= logging.WARNING:
                st.warning(f"⚠️ {log_entry}")
            elif record.levelno >= logging.INFO and config.app.debug:
                st.info(f"ℹ️ {log_entry}")
        except Exception:
            # Fallback to console if Streamlit is not available
            print(f"LOG: {self.format(record)}", file=sys.stderr)


def setup_logging():
    """Setup application logging with custom configuration."""
    # Clear existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Set log level
    root_logger.setLevel(getattr(logging, config.app.log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (only in production)
    if not config.app.debug:
        file_handler = logging.FileHandler('marketpulse.log')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Streamlit handler (for UI feedback)
    if config.app.debug:
        streamlit_handler = StreamlitLogHandler()
        streamlit_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        root_logger.addHandler(streamlit_handler)
    
    # Set specific logger levels
    logging.getLogger('yfinance').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.INFO)
    
    # Log startup
    logger = get_logger(__name__)
    logger.info("Logging system initialized", environment=config.app.environment)