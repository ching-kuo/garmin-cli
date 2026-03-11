"""Configuration dataclass and environment variable loading."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class CliConfig:
    """Immutable CLI configuration."""

    email: str | None = None
    password: str | None = None
    garth_home: str = "~/.garth"
    output_format: str = "table"


def load_config() -> CliConfig:
    """Load configuration from environment variables."""
    email_raw = os.environ.get("GARMIN_EMAIL")
    password_raw = os.environ.get("GARMIN_PASSWORD")
    garth_home = os.environ.get("GARTH_HOME", "~/.garth")

    return CliConfig(
        email=email_raw if email_raw != "" else None,
        password=password_raw if password_raw != "" else None,
        garth_home=garth_home,
    )
