"""Input validation functions."""

import argparse
from datetime import datetime

# Valid provider choices
VALID_PROVIDERS = ("gitlab", "github")


def validate_provider(value: str) -> str:
    """
    Validate provider argument.

    Args:
        value: Provider name

    Returns:
        Lowercase provider name

    Raises:
        argparse.ArgumentTypeError: If provider is invalid
    """
    value_lower = value.lower()
    if value_lower not in VALID_PROVIDERS:
        raise argparse.ArgumentTypeError(f"Invalid provider '{value}'. Must be one of: {', '.join(VALID_PROVIDERS)}")
    return value_lower


def validate_project_id(value: str) -> str:
    """
    Validate project ID format.

    Args:
        value: Project ID string

    Returns:
        Project ID string

    Raises:
        argparse.ArgumentTypeError: If format is invalid
    """
    if not value or "/" not in value:
        raise argparse.ArgumentTypeError(
            f"Invalid project ID '{value}'. Expected format: 'owner/repo' or 'group/project'"
        )
    return value


def validate_date(value: str) -> str:
    """
    Validate date format.

    Args:
        value: Date string

    Returns:
        Date string

    Raises:
        argparse.ArgumentTypeError: If format is invalid
    """
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return value
    except ValueError as err:
        raise argparse.ArgumentTypeError(f"Invalid date '{value}'. Expected format: YYYY-MM-DD") from err


def validate_workers(value: str) -> int:
    """
    Validate workers argument.

    Args:
        value: Workers count as string

    Returns:
        Workers count as integer

    Raises:
        argparse.ArgumentTypeError: If value is invalid
    """
    try:
        workers = int(value)
        if workers < 1:
            raise argparse.ArgumentTypeError("Workers must be at least 1")
        if workers > 50:
            raise argparse.ArgumentTypeError("Workers cannot exceed 50 (API rate limits)")
        return workers
    except ValueError as err:
        raise argparse.ArgumentTypeError(f"Invalid workers value '{value}'. Must be an integer.") from err
