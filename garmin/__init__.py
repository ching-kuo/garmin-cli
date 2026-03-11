"""Garmin Connect integration sub-package."""

from .auth import login
from .api import (
    get_workout,
    get_calendar,
    get_all_user_thresholds,
    update_workout_description,
)
from .zones import (
    ms_to_pace,
    calculate_running_zones,
    calculate_cycling_zones,
    classify_running_step,
)

__all__ = [
    "login",
    "get_workout",
    "get_calendar",
    "get_all_user_thresholds",
    "update_workout_description",
    "ms_to_pace",
    "calculate_running_zones",
    "calculate_cycling_zones",
    "classify_running_step",
]
