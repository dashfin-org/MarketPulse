"""
Custom exceptions for MarketPulse application.
Provides specific exception types for different error scenarios.
"""


class MarketPulseException(Exception):
    """Base exception for MarketPulse application."""

    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ConfigurationError(MarketPulseException):
    """Raised when there's a configuration error."""
    pass


class DataFetchError(MarketPulseException):
    """Raised when data fetching fails."""
    pass


class DatabaseError(MarketPulseException):
    """Raised when database operations fail."""
    pass


class APIError(MarketPulseException):
    """Raised when external API calls fail."""
    pass


class ValidationError(MarketPulseException):
    """Raised when data validation fails."""
    pass


class CacheError(MarketPulseException):
    """Raised when cache operations fail."""
    pass


class ChartError(MarketPulseException):
    """Raised when chart creation fails."""
    pass


class NewsError(MarketPulseException):
    """Raised when news fetching fails."""
    pass


class AIAnalysisError(MarketPulseException):
    """Raised when AI analysis fails."""
    pass
