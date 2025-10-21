"""
Unified structured logging configuration for nagatha_core.

Provides consistent logging across all modules with optional file output
and structured logging support.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from .config import get_config


class LoggerFactory:
    """Factory for creating configured loggers."""
    
    _configured = False
    _config = None
    
    @classmethod
    def configure(cls, log_level: str = "INFO", log_file: Optional[str] = None):
        """
        Configure the root logger.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional file path for log output
        """
        if cls._configured:
            return
        
        cls._config = {
            "level": log_level,
            "file": log_file,
        }
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create formatters
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
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get a configured logger instance.
        
        Args:
            name: Logger name (typically __name__)
            
        Returns:
            logging.Logger instance
        """
        if not cls._configured:
            config = get_config()
            cls.configure(
                log_level=config.logging.level,
                log_file=config.logging.log_file,
            )
        
        return logging.getLogger(name)


# Global logger factory
_factory = LoggerFactory()


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        logging.Logger instance
    """
    return _factory.get_logger(name)


def configure_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """
    Configure the logging system.
    
    Args:
        log_level: Logging level
        log_file: Optional log file path
    """
    _factory.configure(log_level, log_file)
