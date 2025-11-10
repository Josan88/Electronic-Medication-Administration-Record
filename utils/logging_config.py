"""
Logging configuration for Electronic Medication Administration Record (eMAR).

This module sets up structured logging for the application.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
import os


def setup_logging(app_name="eMAR", log_level=logging.INFO, log_to_file=False):
    """
    Configure application logging.

    Args:
        app_name: Name of the application for the logger
        log_level: Logging level (default: INFO)
        log_to_file: Whether to log to file in addition to console
    """
    # Create logger
    logger = logging.getLogger(app_name)
    logger.setLevel(log_level)

    # Clear any existing handlers
    logger.handlers = []

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_to_file:
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        file_handler = RotatingFileHandler(
            'logs/emar.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Create default logger instance
logger = setup_logging()
