"""
logging module

Provides centralized logging configuration and utilities.

Features:
- Centralized logging configuration using `logging.config.dictConfig`.
- Utilities for application-wide loggers.

Submodules:
- config: Defines logging configuration.
- custom_logger: Provides a `get_logger` function for accessing loggers.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

from .custom_logger import get_logger

__all__ = ["get_logger"]
