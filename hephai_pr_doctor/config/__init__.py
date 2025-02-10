"""
config module

Centralized configuration management.

Features:
- Loads and validates environment variables.
- Provides access to critical application configurations.

Submodules:
- config: Defines the `Config` class for managing configurations.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

from .config import PRScoringConfig

# Expose the PRScoringConfig class for external use.
__all__ = ["PRScoringConfig"]
