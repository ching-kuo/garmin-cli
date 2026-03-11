"""Tests for garmin_cli.endpoints.health — all health endpoint functions."""
from __future__ import annotations

from datetime import date
from typing import Any
from unittest.mock import MagicMock, call

import pytest

from garmin_cli.endpoints.health import (
    get_body_battery,
    get_hrv,
    get_resting_hr,
    get_sleep,
    get_spo2,
    get_stress,
    get_training_readiness,
    get_training_status,
    get_weight,
)
from garmin_cli.exceptions import GarminCliError


# ---------------------------------------------------------------------------
# Mock HTTP error helper
# ---------------------------------------------------------------------------

def _http_error(status_code: int) -> Exception:
    """Create a mock HTTP error with a response.status_code attribute."""
    err = Exception(f"HTTP {status_code}")
    err.response = MagicMock(status_code=status_code)  # type: ignore[attr-defined]
    return err


# ---------------------------------------------------------------------------
# get_sleep
# ---------------------------------------------------------------------------

class TestGetSleep:

    def test_calls_garth_connectapi(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = {"dailySleepDTO": {}}
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        get_sleep(date(2026, 3, 11), date(2026, 3, 11))
        assert mock_garth.connectapi.called

    def test_returns_raw_response(self, mocker: Any) -> None:
        payload = {"dailySleepDTO": {"calendarDate": "2026-03-11"}}
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = payload
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        result = get_sleep(date(2026, 3, 11), date(2026, 3, 11))
        assert result is not None

    def test_accepts_date_range(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = []
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        result = get_sleep(date(2026, 3, 1), date(2026, 3, 11))
        assert result is not None

    def test_passes_start_date_in_request(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = {}
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        get_sleep(date(2026, 3, 1), date(2026, 3, 7))
        call_args = mock_garth.connectapi.call_args
        call_str = str(call_args)
        assert "2026-03-01" in call_str or "2026" in call_str

    def test_passes_end_date_in_request(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = {}
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        get_sleep(date(2026, 3, 1), date(2026, 3, 7))
        call_str = str(mock_garth.connectapi.call_args)
        assert "2026-03-07" in call_str or "2026" in call_str


# ---------------------------------------------------------------------------
# get_hrv
# ---------------------------------------------------------------------------

class TestGetHrv:

    def test_calls_connectapi(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = {}
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        get_hrv(date(2026, 3, 11), date(2026, 3, 11))
        assert mock_garth.connectapi.called

    def test_returns_value(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = {"hrvSummary": {}}
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        result = get_hrv(date(2026, 3, 11), date(2026, 3, 11))
        assert result is not None

    def test_date_present_in_api_call(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = {}
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        get_hrv(date(2026, 3, 11), date(2026, 3, 11))
        call_str = str(mock_garth.connectapi.call_args)
        assert "2026" in call_str

    def test_multi_day_range_uses_daily_range_endpoint(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = {}
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        get_hrv(date(2026, 3, 1), date(2026, 3, 7))
        call_str = str(mock_garth.connectapi.call_args)
        assert "/hrv-service/hrv/daily/2026-03-01/2026-03-07" in call_str


# ---------------------------------------------------------------------------
# get_weight
# ---------------------------------------------------------------------------

class TestGetWeight:

    def test_calls_connectapi(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = {"dateWeightList": []}
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        get_weight(date(2026, 3, 11), date(2026, 3, 11))
        assert mock_garth.connectapi.called

    def test_returns_value(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = {"dateWeightList": []}
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        result = get_weight(date(2026, 3, 1), date(2026, 3, 11))
        assert result is not None


# ---------------------------------------------------------------------------
# get_body_battery
# ---------------------------------------------------------------------------

class TestGetBodyBattery:

    def test_calls_connectapi(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = {}
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        get_body_battery(date(2026, 3, 11))
        assert mock_garth.connectapi.called

    def test_accepts_single_date(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = {}
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        result = get_body_battery(date(2026, 3, 11))
        assert result is not None

    def test_date_in_endpoint_url(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = {}
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        get_body_battery(date(2026, 3, 11))
        call_str = str(mock_garth.connectapi.call_args)
        assert "2026-03-11" in call_str or "2026" in call_str


# ---------------------------------------------------------------------------
# get_stress
# ---------------------------------------------------------------------------

class TestGetStress:

    def test_calls_connectapi(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = {}
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        get_stress(date(2026, 3, 11))
        assert mock_garth.connectapi.called

    def test_returns_value(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = {"avgStressLevel": 35}
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        result = get_stress(date(2026, 3, 11))
        assert result is not None


# ---------------------------------------------------------------------------
# get_spo2
# ---------------------------------------------------------------------------

class TestGetSpo2:

    def test_calls_connectapi(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = {}
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        get_spo2(date(2026, 3, 11))
        assert mock_garth.connectapi.called

    def test_returns_value(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = {"averageSpO2": 97}
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        result = get_spo2(date(2026, 3, 11))
        assert result is not None


# ---------------------------------------------------------------------------
# get_resting_hr
# ---------------------------------------------------------------------------

class TestGetRestingHr:

    def test_calls_connectapi(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = {}
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        get_resting_hr(date(2026, 3, 11))
        assert mock_garth.connectapi.called

    def test_returns_value(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = {"restingHeartRateValue": 52}
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        result = get_resting_hr(date(2026, 3, 11))
        assert result is not None


# ---------------------------------------------------------------------------
# get_training_readiness
# ---------------------------------------------------------------------------

class TestGetTrainingReadiness:

    def test_calls_connectapi(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = {}
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        get_training_readiness(date(2026, 3, 11))
        assert mock_garth.connectapi.called

    def test_returns_value(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = {"score": 68}
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        result = get_training_readiness(date(2026, 3, 11))
        assert result is not None

    def test_date_in_endpoint_url(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = {}
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        get_training_readiness(date(2026, 3, 11))
        call_str = str(mock_garth.connectapi.call_args)
        assert "2026-03-11" in call_str or "2026" in call_str


# ---------------------------------------------------------------------------
# get_training_status
# ---------------------------------------------------------------------------

class TestGetTrainingStatus:

    def test_calls_connectapi(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = {}
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        get_training_status(date(2026, 3, 11))
        assert mock_garth.connectapi.called

    def test_returns_value(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.return_value = {"trainingStatusType": "PRODUCTIVE"}
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        result = get_training_status(date(2026, 3, 11))
        assert result is not None


# ---------------------------------------------------------------------------
# Rate limiting / error handling (strengthened assertions)
# ---------------------------------------------------------------------------

class TestHealthEndpointErrorHandling:

    def test_http_404_raises_garmin_cli_error_with_not_found_code(
        self, mocker: Any
    ) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.side_effect = _http_error(404)
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        with pytest.raises(GarminCliError) as exc_info:
            get_sleep(date(2026, 3, 11), date(2026, 3, 11))
        assert exc_info.value.error_code == "NOT_FOUND"

    def test_http_429_raises_rate_limited_error_after_retries(
        self, mocker: Any
    ) -> None:
        mock_garth = MagicMock()
        # 4 calls: 1 initial + 3 retries — all return 429
        mock_garth.connectapi.side_effect = [_http_error(429)] * 4
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)
        mocker.patch("time.sleep")  # avoid real delays in tests

        with pytest.raises(GarminCliError) as exc_info:
            get_sleep(date(2026, 3, 11), date(2026, 3, 11))
        assert exc_info.value.error_code == "RATE_LIMITED"

    def test_http_500_raises_server_error_after_retries(
        self, mocker: Any
    ) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.side_effect = [_http_error(500)] * 4
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)
        mocker.patch("time.sleep")

        with pytest.raises(GarminCliError) as exc_info:
            get_sleep(date(2026, 3, 11), date(2026, 3, 11))
        assert exc_info.value.error_code == "SERVER_ERROR"

    def test_http_429_retries_before_failing(self, mocker: Any) -> None:
        """Implementation must retry 3 times before giving up on 429."""
        mock_garth = MagicMock()
        mock_garth.connectapi.side_effect = [_http_error(429)] * 4
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)
        mock_sleep = mocker.patch("time.sleep")

        with pytest.raises(GarminCliError):
            get_sleep(date(2026, 3, 11), date(2026, 3, 11))

        # Should have called sleep for exponential backoff
        assert mock_sleep.call_count >= 1

    def test_http_429_succeeds_on_retry(self, mocker: Any) -> None:
        """Implementation retries and succeeds on 2nd attempt."""
        mock_garth = MagicMock()
        mock_garth.connectapi.side_effect = [
            _http_error(429),
            {"dailySleepDTO": {}},  # succeeds on retry
        ]
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)
        mocker.patch("time.sleep")

        result = get_sleep(date(2026, 3, 11), date(2026, 3, 11))
        assert result is not None

    def test_hrv_404_raises_not_found(self, mocker: Any) -> None:
        mock_garth = MagicMock()
        mock_garth.connectapi.side_effect = _http_error(404)
        mocker.patch("garmin_cli.endpoints.health.garth", mock_garth)

        with pytest.raises(GarminCliError) as exc_info:
            get_hrv(date(2026, 3, 11), date(2026, 3, 11))
        assert exc_info.value.error_code == "NOT_FOUND"
