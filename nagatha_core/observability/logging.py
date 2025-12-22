"""
Structured logging utilities.

Provides enhanced logging with JSON-like structured output
and correlation ID integration.
"""

import logging
import sys
import json
from pathlib import Path
from typing import Any, Dict, Optional

from .tracing import get_correlation_id


class StructuredFormatter(logging.Formatter):
    """
    Formatter that outputs structured (JSON-ish) log records.
    
    Includes correlation IDs automatically when available.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as structured output.
        
        Args:
            record: Log record to format
            
        Returns:
            Formatted log string
        """
        # Build structured log entry
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add correlation ID if available
        correlation_id = get_correlation_id()
        if correlation_id:
            log_entry["correlation_id"] = correlation_id
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName",
                "relativeCreated", "thread", "threadName", "exc_info",
                "exc_text", "stack_info",
            ]:
                log_entry[key] = value
        
        return json.dumps(log_entry)


class StructuredLogger:
    """
    Enhanced logger with structured output and correlation tracking.
    
    Example:
        >>> from nagatha_core.observability import StructuredLogger
        >>> logger = StructuredLogger("my_module")
        >>> logger.info("Processing request", extra={"user_id": "123"})
    """
    
    def __init__(self, name: str, use_json: bool = False):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name
            use_json: Whether to use JSON formatting
        """
        self._logger = logging.getLogger(name)
        self._use_json = use_json
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional extra fields."""
        self._log(logging.DEBUG, message, kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional extra fields."""
        self._log(logging.INFO, message, kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional extra fields."""
        self._log(logging.WARNING, message, kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with optional extra fields."""
        self._log(logging.ERROR, message, kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with optional extra fields."""
        self._log(logging.CRITICAL, message, kwargs)
    
    def _log(self, level: int, message: str, extra: Dict[str, Any]):
        """
        Internal log method.
        
        Args:
            level: Log level
            message: Log message
            extra: Extra fields to include
        """
        # Add correlation ID if available
        correlation_id = get_correlation_id()
        if correlation_id:
            extra["correlation_id"] = correlation_id
        
        self._logger.log(level, message, extra=extra)


class LoggerFactory:
    """Factory for creating configured loggers."""
    
    _configured = False
    _config = None
    
    @classmethod
    def configure(
        cls,
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        use_json: bool = False,
    ):
        """
        Configure the root logger.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional file path for log output
            use_json: Whether to use JSON formatting
        """
        if cls._configured:
            return
        
        cls._config = {
            "level": log_level,
            "file": log_file,
            "json": use_json,
        }
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create formatter
        if use_json:
            formatter = StructuredFormatter()
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler (if specified)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        cls._configured = True
    
    @classmethod
    def get_logger(cls, name: str, use_json: bool = False) -> logging.Logger:
        """
        Get a configured logger instance.
        
        Args:
            name: Logger name (typically __name__)
            use_json: Whether to return StructuredLogger
            
        Returns:
            logging.Logger or StructuredLogger instance
        """
        if not cls._configured:
            cls.configure()
        
        if use_json or (cls._config and cls._config.get("json")):
            return StructuredLogger(name, use_json=True)
        
        return logging.getLogger(name)


# Global logger factory
_factory = LoggerFactory()


def get_logger(name: str, use_json: bool = False) -> logging.Logger:
    """
    Get a configured logger.
    
    Args:
        name: Logger name (typically __name__)
        use_json: Whether to use structured JSON logging
        
    Returns:
        logging.Logger or StructuredLogger instance
        
    Example:
        >>> from nagatha_core.observability import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Hello, World!")
    """
    return _factory.get_logger(name, use_json)


def configure_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    use_json: bool = False,
):
    """
    Configure the logging system.
    
    Args:
        log_level: Logging level
        log_file: Optional log file path
        use_json: Whether to use JSON formatting
        
    Example:
        >>> from nagatha_core.observability import configure_logging
        >>> configure_logging(log_level="DEBUG", use_json=True)
    """
    _factory.configure(log_level, log_file, use_json)
