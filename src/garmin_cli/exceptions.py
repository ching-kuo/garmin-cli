"""Custom exceptions for garmin-cli."""
from __future__ import annotations


class GarminCliError(Exception):
    """Raised for all expected garmin-cli failures.

    Attributes:
        error: Human-readable error message.
        error_code: Machine-readable error code (e.g. AUTH_FAILED, NOT_FOUND).
    """

    def __init__(self, error: str, error_code: str) -> None:
        self.error = error
        self.error_code = error_code
        super().__init__(error)
