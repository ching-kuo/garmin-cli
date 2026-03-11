"""Health endpoint helpers backed by Garmin Connect APIs."""
from __future__ import annotations

from datetime import date
from typing import Any

import garth

from garmin_cli.endpoints._base import _make_request


def _request(url: str, *, params: dict[str, Any] | None = None) -> Any:
    return _make_request(garth.connectapi, url, params=params)


def get_sleep(start: date, end: date) -> Any:
    return _request(
        "/wellness-service/wellness/dailySleeps",
        params={"startDate": start.isoformat(), "endDate": end.isoformat()},
    )


def get_hrv(start: date, end: date) -> Any:
    if start == end:
        return _request(f"/hrv-service/hrv/{start.isoformat()}")
    return _request(
        f"/hrv-service/hrv/daily/{start.isoformat()}/{end.isoformat()}"
    )


def get_weight(start: date, end: date) -> Any:
    return _request(
        "/weight-service/weight/dateRange",
        params={"startDate": start.isoformat(), "endDate": end.isoformat()},
    )


def get_body_battery(day: date) -> Any:
    return _request(f"/wellness-service/wellness/bodyBattery/{day.isoformat()}")


def get_stress(day: date) -> Any:
    return _request(f"/wellness-service/wellness/dailyStress/{day.isoformat()}")


def get_spo2(day: date) -> Any:
    return _request(f"/wellness-service/wellness/daily/spo2/{day.isoformat()}")


def get_resting_hr(day: date) -> Any:
    return _request(f"/wellness-service/wellness/dailyHeartRate/{day.isoformat()}")


def get_training_readiness(day: date) -> Any:
    return _request(
        f"/training-info-service/training-info/daily-readiness/{day.isoformat()}"
    )


def get_training_status(day: date) -> Any:
    return _request(
        f"/training-info-service/training-info/training-status/{day.isoformat()}"
    )
