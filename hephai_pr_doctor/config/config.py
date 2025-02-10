"""
config.py

Configuration module for HEPHAI-PR-Doctor's PR scoring system.

This module loads PR scoring parameters from environment variables, with default values.
Users can override these settings via a `.env` file or by exporting variables in their shell.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env if available
load_dotenv()


def get_env_variable(var_name: str, default: int | float) -> int | float:
    """
    Retrieves an environment variable, falling back to a default if not set.

    Args:
        var_name (str): Name of the environment variable.
        default (int | float): Default value if the environment variable is not set.

    Returns:
        int | float: Parsed environment variable value.
    """
    try:
        return type(default)(os.getenv(var_name, default))
    except ValueError:
        return default


class PRScoringConfig:
    """
    PR Scoring Configuration class.

    - Loads PR scoring settings from environment variables.
    - Provides defaults if no environment variables are found.
    - Can be instantiated for flexible configurations.
    """

    def __init__(self):
        self.BASE_SCORE = get_env_variable("BASE_SCORE", 100)
        self.PR_SCORE_THRESHOLD = get_env_variable("PR_SCORE_THRESHOLD", 70)

        self.CHANGE_FILE_WEIGHT = get_env_variable("CHANGE_FILE_WEIGHT", 3)
        self.ADDITION_WEIGHT = get_env_variable("ADDITION_WEIGHT", 0.2)
        self.DELETION_WEIGHT = get_env_variable("DELETION_WEIGHT", 0.1)
        self.SMALL_PR_BONUS = get_env_variable("SMALL_PR_BONUS", 5)
        self.LARGE_PR_PENALTY = get_env_variable("LARGE_PR_PENALTY", 10)
        self.MASSIVE_PR_PENALTY = get_env_variable("MASSIVE_PR_PENALTY", 20)
        self.MISSING_TESTS_PENALTY = get_env_variable("MISSING_TESTS_PENALTY", 10)
        self.FLAKE8_PENALTY = get_env_variable("FLAKE8_PENALTY", 5)
        self.MYPY_PENALTY = get_env_variable("MYPY_PENALTY", 3)

    def __repr__(self) -> str:
        """
        Returns a string representation of the PR scoring configuration.
        """
        return (
            f"PRScoringConfig(BASE_SCORE={self.BASE_SCORE}, "
            f"CHANGE_FILE_WEIGHT={self.CHANGE_FILE_WEIGHT}, "
            f"ADDITION_WEIGHT={self.ADDITION_WEIGHT}, "
            f"DELETION_WEIGHT={self.DELETION_WEIGHT}, "
            f"SMALL_PR_BONUS={self.SMALL_PR_BONUS}, "
            f"LARGE_PR_PENALTY={self.LARGE_PR_PENALTY}, "
            f"MASSIVE_PR_PENALTY={self.MASSIVE_PR_PENALTY}, "
            f"MISSING_TESTS_PENALTY={self.MISSING_TESTS_PENALTY}, "
            f"FLAKE8_PENALTY={self.FLAKE8_PENALTY}, "
            f"MYPY_PENALTY={self.MYPY_PENALTY})"
        )


# Load global configuration
CONFIG = PRScoringConfig()
