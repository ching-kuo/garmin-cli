"""Activity endpoint helpers backed by Garmin Connect APIs."""
from __future__ import annotations

from typing import Any

import garth

from garmin_cli.endpoints._base import _make_request, _validate_numeric_id
from garmin_cli.exceptions import GarminCliError


def _request(url: str, *, params: dict[str, Any] | None = None) -> Any:
    return _make_request(garth.connectapi, url, params=params)


def list_activities(
    limit: int,
    start: int,
    activity_type: str | None,
    search: str | None,
) -> list:
    if limit <= 0:
        raise GarminCliError(
            error="limit must be greater than 0",
            error_code="INVALID_INPUT",
        )
    params: dict[str, Any] = {"start": start, "limit": limit}
    if activity_type is not None:
        params["activityType"] = activity_type
    if search is not None:
        params["search"] = search
    result = _request(
        "/activitylist-service/activities/search/activities",
        params=params,
    )
    if isinstance(result, dict):
        return [result]
    return result if result is not None else []


def get_activity(activity_id: Any) -> dict:
    validated = _validate_numeric_id(activity_id, "activity_id")
    result = _request(f"/activity-service/activity/{validated}")
    return result if result is not None else {}


def get_activity_weather(activity_id: Any) -> dict:
    validated = _validate_numeric_id(activity_id, "activity_id")
    result = _request(f"/activity-service/activity/{validated}/weather")
    return result if result is not None else {}
