"""Tests for the local garmin package exports."""
from __future__ import annotations

import importlib
import sys


def test_import_garmin_uses_local_modules() -> None:
    sys.modules.pop("garmin", None)
    sys.modules.pop("garmin.api", None)
    sys.modules.pop("garmin.auth", None)
    sys.modules.pop("garmin.zones", None)

    package = importlib.import_module("garmin")

    assert package.login.__module__ == "garmin.auth"
    assert package.get_workout.__module__ == "garmin.api"
    assert package.ms_to_pace.__module__ == "garmin.zones"
