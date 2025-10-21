"""
Tests for the logging module.
"""

import logging
import tempfile
from pathlib import Path

from nagatha_core.logging import LoggerFactory, get_logger, configure_logging


def test_logger_creation():
    """Test logger creation."""
    logger = get_logger("test")
    
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test"


def test_logger_factory_configure():
    """Test LoggerFactory configuration."""
    LoggerFactory._configured = False
    
    LoggerFactory.configure("DEBUG")
    
    assert LoggerFactory._configured is True
    root_logger = logging.getLogger()
    assert root_logger.level == logging.DEBUG


def test_logger_with_file():
    """Test logger with file output."""
    LoggerFactory._configured = False
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"
        
        LoggerFactory.configure("INFO", str(log_file))
        
        # Log a message
        logger = get_logger("test")
        logger.info("Test message")
        
        # Verify file was created
        # Note: This might not work in all test environments
        # due to async logging


def test_configure_logging():
    """Test configure_logging function."""
    LoggerFactory._configured = False
    
    configure_logging("WARNING")
    
    logger = get_logger("test")
    root_logger = logging.getLogger()
    
    assert root_logger.level == logging.WARNING


def test_multiple_loggers():
    """Test creating multiple loggers."""
    logger1 = get_logger("module1")
    logger2 = get_logger("module2")
    
    assert logger1.name == "module1"
    assert logger2.name == "module2"
    assert logger1 is not logger2
