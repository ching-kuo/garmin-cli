"""Tests for garmin_cli.serializers — all serialize_* functions and COLUMNS."""
from __future__ import annotations

from typing import Any

import pytest

from garmin_cli.serializers import (
    COLUMNS_ACTIVITY_SUMMARY,
    COLUMNS_BODY_BATTERY,
    COLUMNS_CALENDAR_WORKOUT,
    COLUMNS_HRV,
    COLUMNS_MULTISPORT_CHILDREN,
    COLUMNS_READINESS,
    COLUMNS_RESTING_HR,
    COLUMNS_SLEEP,
    COLUMNS_SPO2,
    COLUMNS_STATUS,
    COLUMNS_STRESS,
    COLUMNS_THRESHOLDS,
    COLUMNS_VO2MAX,
    COLUMNS_WEIGHT,
    COLUMNS_ZONES,
    serialize_activity_summary,
    serialize_body_battery,
    serialize_calendar_workout,
    serialize_hrv,
    serialize_multisport_children,
    serialize_resting_hr,
    serialize_sleep,
    serialize_spo2,
    serialize_stress,
    serialize_thresholds,
    serialize_training_readiness,
    serialize_training_status,
    serialize_vo2max,
    serialize_weight,
    serialize_workout_detail,
    serialize_workout_summary,
    select_latest_dated_rows,
    serialize_zones,
)


# ---------------------------------------------------------------------------
# select_latest_dated_rows
# ---------------------------------------------------------------------------


class TestSelectLatestDatedRows:

    def test_returns_only_latest_date_rows(self) -> None:
        rows: list[dict[str, object]] = [
            {"date": "2026-03-10", "vo2max": 54.0, "sport": "generic"},
            {"date": "2026-03-10", "vo2max": 55.0, "sport": "cycling"},
            {"date": "2026-03-08", "vo2max": 52.0, "sport": "generic"},
        ]
        assert select_latest_dated_rows(rows) == rows[:2]

    def test_empty_input_returns_empty(self) -> None:
        assert select_latest_dated_rows([]) == []

    def test_no_dated_rows_returns_first(self) -> None:
        rows: list[dict[str, object]] = [{"vo2max": 52.0}, {"vo2max": 50.0}]
        assert select_latest_dated_rows(rows) == [rows[0]]

    def test_single_row_returned(self) -> None:
        rows: list[dict[str, object]] = [{"date": "2026-03-11", "vo2max": 52.0}]
        assert select_latest_dated_rows(rows) == rows


# ---------------------------------------------------------------------------
# serialize_sleep
# ---------------------------------------------------------------------------

class TestSerializeSleep:

    def test_returns_list(self, sample_sleep_raw: Any) -> None:
        result = serialize_sleep(sample_sleep_raw)
        assert isinstance(result, list)

    def test_single_day_returns_one_item(self, sample_sleep_raw: Any) -> None:
        result = serialize_sleep(sample_sleep_raw)
        assert len(result) == 1

    def test_contains_date_key(self, sample_sleep_raw: Any) -> None:
        result = serialize_sleep(sample_sleep_raw)
        assert "date" in result[0]

    def test_date_value_correct(self, sample_sleep_raw: Any) -> None:
        result = serialize_sleep(sample_sleep_raw)
        assert result[0]["date"] == "2026-03-11"

    def test_duration_hours_present(self, sample_sleep_raw: Any) -> None:
        result = serialize_sleep(sample_sleep_raw)
        assert "duration_hours" in result[0]

    def test_duration_hours_correct(self, sample_sleep_raw: Any) -> None:
        result = serialize_sleep(sample_sleep_raw)
        # 27000 seconds / 3600 = 7.5 hours
        assert result[0]["duration_hours"] == pytest.approx(7.5, rel=0.01)

    def test_deep_min_present(self, sample_sleep_raw: Any) -> None:
        result = serialize_sleep(sample_sleep_raw)
        assert "deep_min" in result[0]

    def test_deep_min_correct(self, sample_sleep_raw: Any) -> None:
        result = serialize_sleep(sample_sleep_raw)
        # 5400 seconds / 60 = 90 minutes
        assert result[0]["deep_min"] == pytest.approx(90, rel=0.01)

    def test_light_min_present(self, sample_sleep_raw: Any) -> None:
        result = serialize_sleep(sample_sleep_raw)
        assert "light_min" in result[0]

    def test_rem_min_present(self, sample_sleep_raw: Any) -> None:
        result = serialize_sleep(sample_sleep_raw)
        assert "rem_min" in result[0]

    def test_awake_min_present(self, sample_sleep_raw: Any) -> None:
        result = serialize_sleep(sample_sleep_raw)
        assert "awake_min" in result[0]

    def test_score_present(self, sample_sleep_raw: Any) -> None:
        result = serialize_sleep(sample_sleep_raw)
        assert "score" in result[0]

    def test_score_value(self, sample_sleep_raw: Any) -> None:
        result = serialize_sleep(sample_sleep_raw)
        assert result[0]["score"] == 82

    def test_missing_score_returns_none(self) -> None:
        raw = {"dailySleepDTO": {"calendarDate": "2026-03-11", "sleepTimeSeconds": 3600}}
        result = serialize_sleep(raw)
        assert result[0]["score"] is None

    def test_missing_keys_return_none_not_crash(self) -> None:
        result = serialize_sleep({})
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["date"] is None or result[0].get("date") is None

    def test_multi_day_returns_multiple_items(self, sample_sleep_multi_raw: Any) -> None:
        result = serialize_sleep(sample_sleep_multi_raw)
        assert len(result) == 2

    def test_multi_day_each_item_has_required_keys(self, sample_sleep_multi_raw: Any) -> None:
        result = serialize_sleep(sample_sleep_multi_raw)
        for item in result:
            for key in ("date", "duration_hours", "deep_min", "light_min", "rem_min", "awake_min", "score"):
                assert key in item

    def test_columns_contains_required_fields(self) -> None:
        for col in ("date", "duration_hours", "deep_min", "light_min", "rem_min", "awake_min", "score"):
            assert col in COLUMNS_SLEEP



# ---------------------------------------------------------------------------
# serialize_hrv
# ---------------------------------------------------------------------------

class TestSerializeHrv:

    def test_contains_date(self, sample_hrv_raw: Any) -> None:
        result = serialize_hrv(sample_hrv_raw)
        assert result[0]["date"] == "2026-03-11"

    def test_weekly_avg_present(self, sample_hrv_raw: Any) -> None:
        result = serialize_hrv(sample_hrv_raw)
        assert "weekly_avg" in result[0]
        assert result[0]["weekly_avg"] == 52

    def test_last_night_present(self, sample_hrv_raw: Any) -> None:
        result = serialize_hrv(sample_hrv_raw)
        assert "last_night" in result[0]
        assert result[0]["last_night"] == 48

    def test_status_present(self, sample_hrv_raw: Any) -> None:
        result = serialize_hrv(sample_hrv_raw)
        assert "status" in result[0]
        assert result[0]["status"] == "BALANCED"

    def test_missing_keys_return_none(self) -> None:
        result = serialize_hrv({})
        assert result == []

    def test_missing_hrv_summary_returns_empty_list(self) -> None:
        result = serialize_hrv({"foo": "bar"})
        assert result == []

    def test_range_payload_returns_multiple_rows(self) -> None:
        result = serialize_hrv(
            {
                "hrvSummaries": [
                    {
                        "calendarDate": "2026-03-10",
                        "weeklyAvg": 50,
                        "lastNight": 48,
                        "status": "BALANCED",
                    },
                    {
                        "calendarDate": "2026-03-11",
                        "weeklyAvg": 51,
                        "lastNight": 49,
                        "status": "BALANCED",
                    },
                ]
            }
        )
        assert result == [
            {
                "date": "2026-03-10",
                "weekly_avg": 50,
                "last_night": 48,
                "status": "BALANCED",
            },
            {
                "date": "2026-03-11",
                "weekly_avg": 51,
                "last_night": 49,
                "status": "BALANCED",
            },
        ]

    def test_range_payload_prefers_last_night_avg_when_available(self) -> None:
        result = serialize_hrv(
            {
                "hrvSummaries": [
                    {
                        "calendarDate": "2026-03-10",
                        "weeklyAvg": 50,
                        "lastNightAvg": 47,
                        "status": "BALANCED",
                    }
                ]
            }
        )
        assert result == [
            {
                "date": "2026-03-10",
                "weekly_avg": 50,
                "last_night": 47,
                "status": "BALANCED",
            }
        ]

    def test_columns_contains_required_fields(self) -> None:
        for col in ("date", "weekly_avg", "last_night", "status"):
            assert col in COLUMNS_HRV


# ---------------------------------------------------------------------------
# serialize_weight
# ---------------------------------------------------------------------------

class TestSerializeWeight:

    def test_contains_date(self, sample_weight_raw: Any) -> None:
        result = serialize_weight(sample_weight_raw)
        assert result[0]["date"] == "2026-03-11"

    def test_weight_kg_converted_from_grams(self, sample_weight_raw: Any) -> None:
        result = serialize_weight(sample_weight_raw)
        # 75000g -> 75.0 kg
        assert result[0]["weight_kg"] == pytest.approx(75.0, rel=0.01)

    def test_bmi_present(self, sample_weight_raw: Any) -> None:
        result = serialize_weight(sample_weight_raw)
        assert "bmi" in result[0]
        assert result[0]["bmi"] == pytest.approx(23.5, rel=0.01)

    def test_body_fat_pct_present(self, sample_weight_raw: Any) -> None:
        result = serialize_weight(sample_weight_raw)
        assert "body_fat_pct" in result[0]
        assert result[0]["body_fat_pct"] == pytest.approx(18.2, rel=0.01)

    def test_missing_weight_list_returns_empty(self) -> None:
        result = serialize_weight({})
        assert isinstance(result, list)

    def test_columns_contains_required_fields(self) -> None:
        for col in ("date", "weight_kg", "bmi", "body_fat_pct"):
            assert col in COLUMNS_WEIGHT



# ---------------------------------------------------------------------------
# serialize_activity_summary
# ---------------------------------------------------------------------------

class TestSerializeActivitySummary:

    def test_singleton_wraps_in_list(self, sample_activity_raw: Any) -> None:
        result = serialize_activity_summary(sample_activity_raw)
        assert len(result) == 1

    def test_list_input_returns_multiple(self, sample_activities_list_raw: Any) -> None:
        result = serialize_activity_summary(sample_activities_list_raw)
        assert len(result) == 2

    def test_id_present(self, sample_activity_raw: Any) -> None:
        result = serialize_activity_summary(sample_activity_raw)
        assert result[0]["id"] == 12345678

    def test_date_present(self, sample_activity_raw: Any) -> None:
        result = serialize_activity_summary(sample_activity_raw)
        assert "date" in result[0]

    def test_name_present(self, sample_activity_raw: Any) -> None:
        result = serialize_activity_summary(sample_activity_raw)
        assert result[0]["name"] == "Morning Run"

    def test_type_present(self, sample_activity_raw: Any) -> None:
        result = serialize_activity_summary(sample_activity_raw)
        assert result[0]["type"] == "running"

    def test_distance_km_converted(self, sample_activity_raw: Any) -> None:
        result = serialize_activity_summary(sample_activity_raw)
        # 10000m -> 10.0 km
        assert result[0]["distance_km"] == pytest.approx(10.0, rel=0.01)

    def test_duration_min_converted(self, sample_activity_raw: Any) -> None:
        result = serialize_activity_summary(sample_activity_raw)
        # 3600s -> 60.0 min
        assert result[0]["duration_min"] == pytest.approx(60.0, rel=0.01)

    def test_avg_hr_present(self, sample_activity_raw: Any) -> None:
        result = serialize_activity_summary(sample_activity_raw)
        assert result[0]["avg_hr"] == 155

    def test_missing_keys_return_none(self) -> None:
        result = serialize_activity_summary({})
        assert isinstance(result, list)
        assert result[0].get("id") is None

    def test_columns_contains_required_fields(self) -> None:
        for col in ("id", "date", "name", "type", "distance_km", "duration_min", "avg_hr"):
            assert col in COLUMNS_ACTIVITY_SUMMARY

    def test_summary_dto_fallback(self) -> None:
        """Child activities fetched directly should use summaryDTO fallback."""
        raw = {
            "activityId": 18878956185,
            "activityName": "Running",
            "activityType": {"typeKey": "running"},
            "summaryDTO": {
                "startTimeLocal": "2026-04-06T14:30:00",
                "distance": 35049.1,
                "duration": 11888.1,
                "averageHR": 160,
            },
        }
        result = serialize_activity_summary(raw)
        assert result[0]["id"] == 18878956185
        assert result[0]["date"] == "2026-04-06T14:30:00"
        assert result[0]["distance_km"] == pytest.approx(35.0491, rel=0.01)
        assert result[0]["duration_min"] == pytest.approx(198.135, rel=0.01)
        assert result[0]["avg_hr"] == 160

    def test_top_level_fields_preferred_over_summary_dto(self) -> None:
        """Top-level fields take precedence over summaryDTO."""
        raw = {
            "activityId": 1,
            "startTimeLocal": "2026-04-06T06:00:00",
            "distance": 10000.0,
            "duration": 3600.0,
            "averageHR": 150,
            "summaryDTO": {
                "startTimeLocal": "2026-04-06T06:00:01",
                "distance": 9999.0,
                "duration": 3599.0,
                "averageHR": 149,
            },
        }
        result = serialize_activity_summary(raw)
        assert result[0]["date"] == "2026-04-06T06:00:00"
        assert result[0]["distance_km"] == pytest.approx(10.0, rel=0.01)
        assert result[0]["duration_min"] == pytest.approx(60.0, rel=0.01)
        assert result[0]["avg_hr"] == 150

    def test_hybrid_top_level_and_summary_dto(self) -> None:
        """Per-field coalescing uses top-level when present, summaryDTO otherwise."""
        raw = {
            "activityId": 2,
            "startTimeLocal": "2026-04-06T14:00:00",
            "averageHR": 162,
            "activityType": {"typeKey": "running"},
            "summaryDTO": {
                "distance": 35049.1,
                "duration": 11888.1,
                "averageHR": 999,
            },
        }
        result = serialize_activity_summary(raw)
        assert result[0]["date"] == "2026-04-06T14:00:00"
        assert result[0]["distance_km"] == pytest.approx(35.0491, rel=0.01)
        assert result[0]["duration_min"] == pytest.approx(198.135, rel=0.01)
        assert result[0]["avg_hr"] == 162


# ---------------------------------------------------------------------------
# serialize_multisport_children
# ---------------------------------------------------------------------------

class TestSerializeMultisportChildren:

    def test_returns_child_rows(self, sample_multisport_children_raw: Any) -> None:
        result = serialize_multisport_children(sample_multisport_children_raw)
        assert len(result) == 3

    def test_sport_field_present(self, sample_multisport_children_raw: Any) -> None:
        result = serialize_multisport_children(sample_multisport_children_raw)
        assert result[0]["sport"] == "open_water_swimming"
        assert result[1]["sport"] == "cycling"
        assert result[2]["sport"] == "running"

    def test_distance_converted_to_km(self, sample_multisport_children_raw: Any) -> None:
        result = serialize_multisport_children(sample_multisport_children_raw)
        assert result[0]["distance_km"] == pytest.approx(1.5, rel=0.01)
        assert result[1]["distance_km"] == pytest.approx(40.0, rel=0.01)

    def test_duration_converted_to_minutes(self, sample_multisport_children_raw: Any) -> None:
        result = serialize_multisport_children(sample_multisport_children_raw)
        assert result[0]["duration_min"] == pytest.approx(30.0, rel=0.01)
        assert result[1]["duration_min"] == pytest.approx(70.0, rel=0.01)

    def test_avg_hr_present(self, sample_multisport_children_raw: Any) -> None:
        result = serialize_multisport_children(sample_multisport_children_raw)
        assert result[0]["avg_hr"] == 145

    def test_calories_present(self, sample_multisport_children_raw: Any) -> None:
        result = serialize_multisport_children(sample_multisport_children_raw)
        assert result[0]["calories"] == 350

    def test_empty_list(self) -> None:
        assert serialize_multisport_children([]) == []

    def test_skips_non_dict_items(self) -> None:
        result = serialize_multisport_children([None, "bad", 123])
        assert result == []

    def test_summary_dto_fallback(self) -> None:
        children = [
            {
                "activityId": 1,
                "activityName": "Swim",
                "activityType": {"typeKey": "swimming"},
                "summaryDTO": {
                    "distance": 1500.0,
                    "duration": 1800.0,
                    "averageHR": 140,
                    "averageSpeed": 0.833,
                    "calories": 300,
                },
            }
        ]
        result = serialize_multisport_children(children)
        assert result[0]["distance_km"] == pytest.approx(1.5, rel=0.01)
        assert result[0]["avg_hr"] == 140

    def test_columns_contains_required_fields(self) -> None:
        for col in ("id", "sport", "name", "distance_km", "duration_min", "avg_hr", "avg_pace", "calories"):
            assert col in COLUMNS_MULTISPORT_CHILDREN


# ---------------------------------------------------------------------------
# serialize_calendar_workout
# ---------------------------------------------------------------------------

class TestSerializeCalendarWorkout:

    def test_returns_multiple_items(self, sample_calendar_raw: Any) -> None:
        result = serialize_calendar_workout(sample_calendar_raw)
        assert len(result) == 2

    def test_date_present(self, sample_calendar_raw: Any) -> None:
        result = serialize_calendar_workout(sample_calendar_raw)
        assert result[0]["date"] == "2026-03-12"

    def test_id_present(self, sample_calendar_raw: Any) -> None:
        result = serialize_calendar_workout(sample_calendar_raw)
        assert result[0]["id"] == 987654

    def test_name_present(self, sample_calendar_raw: Any) -> None:
        result = serialize_calendar_workout(sample_calendar_raw)
        assert result[0]["name"] == "Tempo Run"

    def test_type_present(self, sample_calendar_raw: Any) -> None:
        result = serialize_calendar_workout(sample_calendar_raw)
        assert result[0]["type"] == "running"

    def test_duration_min_converted(self, sample_calendar_raw: Any) -> None:
        result = serialize_calendar_workout(sample_calendar_raw)
        # 3600s -> 60 min
        assert result[0]["duration_min"] == pytest.approx(60.0, rel=0.01)

    def test_description_present(self, sample_calendar_raw: Any) -> None:
        result = serialize_calendar_workout(sample_calendar_raw)
        assert result[0]["description"] == "Hard effort"

    def test_empty_calendar_items_returns_empty_list(self) -> None:
        result = serialize_calendar_workout({"calendarItems": []})
        assert result == []

    def test_missing_raw_returns_empty_list(self) -> None:
        result = serialize_calendar_workout({})
        assert isinstance(result, list)

    def test_columns_contains_required_fields(self) -> None:
        for col in ("date", "id", "name", "type", "duration_min", "description"):
            assert col in COLUMNS_CALENDAR_WORKOUT



# ---------------------------------------------------------------------------
# serialize_thresholds
# ---------------------------------------------------------------------------

class TestSerializeThresholds:

    def test_returns_two_items(self, sample_all_thresholds_raw: Any) -> None:
        result = serialize_thresholds(sample_all_thresholds_raw)
        assert len(result) == 2

    def test_sport_present(self, sample_all_thresholds_raw: Any) -> None:
        result = serialize_thresholds(sample_all_thresholds_raw)
        assert result[0]["sport"] == "running"

    def test_lt_hr_bpm_present(self, sample_all_thresholds_raw: Any) -> None:
        result = serialize_thresholds(sample_all_thresholds_raw)
        assert result[0]["lt_hr_bpm"] == 168

    def test_lt_pace_present(self, sample_all_thresholds_raw: Any) -> None:
        result = serialize_thresholds(sample_all_thresholds_raw)
        assert result[0]["lt_pace"] == "5:12"

    def test_ftp_watts_present_cycling(self, sample_all_thresholds_raw: Any) -> None:
        result = serialize_thresholds(sample_all_thresholds_raw)
        cycling = next(r for r in result if r["sport"] == "cycling")
        assert cycling["ftp_watts"] == 280

    def test_ftp_watts_none_for_running(self, sample_all_thresholds_raw: Any) -> None:
        result = serialize_thresholds(sample_all_thresholds_raw)
        running = next(r for r in result if r["sport"] == "running")
        assert running["ftp_watts"] is None

    def test_weight_kg_present(self, sample_all_thresholds_raw: Any) -> None:
        result = serialize_thresholds(sample_all_thresholds_raw)
        assert result[0]["weight_kg"] == 75.0

    def test_missing_keys_return_none(self) -> None:
        result = serialize_thresholds({"thresholds": [{}]})
        assert isinstance(result, list)
        assert result[0].get("sport") is None

    def test_numeric_lt_pace_is_formatted(self) -> None:
        result = serialize_thresholds(
            {
                "thresholds": [
                    {
                        "sport": "running",
                        "lactateThresholdHeartRate": 168,
                        "lactateThresholdPace": 250,
                        "functionalThresholdPower": None,
                        "weight": 75.0,
                    }
                ]
            }
        )
        assert result[0]["lt_pace"] == "4:10"

    def test_columns_contains_required_fields(self) -> None:
        for col in ("sport", "lt_hr_bpm", "lt_pace", "ftp_watts", "weight_kg"):
            assert col in COLUMNS_THRESHOLDS


class TestWorkoutSerializers:

    def test_workout_summary_uses_display_name_and_estimated_duration(
        self,
        sample_workout_alt_raw: Any,
    ) -> None:
        result = serialize_workout_summary(sample_workout_alt_raw)
        assert result == [
            {
                "id": 987654,
                "name": "Tempo Run",
                "sport": "Running",
                "duration_min": 60.0,
                "description": "4x10min at threshold pace",
            }
        ]

    def test_workout_detail_includes_steps_and_summary(
        self,
        sample_workout_detail_raw: Any,
    ) -> None:
        result = serialize_workout_detail(sample_workout_detail_raw)
        assert result[0]["steps_summary"] == "warmup > interval > cooldown"
        assert result[0]["steps"] == [
            {
                "step_order": 1,
                "step_type": "warmup",
                "duration_type": "time",
                "duration_value": 600,
                "target_type": None,
                "target_value_low": None,
                "target_value_high": None,
            },
            {
                "step_order": 2,
                "step_type": "interval",
                "duration_type": "time",
                "duration_value": 300,
                "target_type": "heart.rate.zone",
                "target_value_low": 160,
                "target_value_high": 170,
            },
            {
                "step_order": 3,
                "step_type": "cooldown",
                "duration_type": "time",
                "duration_value": 600,
                "target_type": None,
                "target_value_low": None,
                "target_value_high": None,
            },
        ]

    def test_workout_detail_handles_missing_segments(self, sample_workout_raw: Any) -> None:
        result = serialize_workout_detail(sample_workout_raw)
        assert result[0]["steps"] == []
        assert result[0]["steps_summary"] == ""


class TestPerformanceSerializers:

    def test_serialize_vo2max_supports_flat_and_wrapped_payloads(
        self,
        sample_vo2max_raw: Any,
        sample_vo2max_wrapped_raw: Any,
    ) -> None:
        expected = [{"date": "2026-03-11", "vo2max": 52.0, "sport": "running"}]
        assert serialize_vo2max(sample_vo2max_raw) == expected
        assert serialize_vo2max(sample_vo2max_wrapped_raw) == expected

    def test_serialize_vo2max_flattens_live_wrapper_payload(self, sample_vo2max_live_raw: Any) -> None:
        assert serialize_vo2max(sample_vo2max_live_raw) == [
            {"date": "2026-03-10", "vo2max": 54.0, "sport": "generic"},
            {"date": "2026-03-10", "vo2max": 55.0, "sport": "cycling"},
        ]
        assert COLUMNS_VO2MAX == ("date", "vo2max", "sport")

    def test_serialize_zones_normalizes_speed_and_preserves_pace_string(self) -> None:
        assert serialize_zones(
            {
                "sport": "running",
                "lactateThresholdHeartRate": 168,
                "lactateThresholdSpeed": 3.2,
            }
        ) == [{"sport": "running", "lt_hr_bpm": 168, "lt_pace": "5:12"}]
        assert serialize_zones(
            {
                "sport": "running",
                "lactateThresholdHeartRate": 168,
                "lactateThresholdPace": "4:10",
            }
        ) == [{"sport": "running", "lt_hr_bpm": 168, "lt_pace": "4:10"}]
        assert COLUMNS_ZONES == ("sport", "lt_hr_bpm", "lt_pace")

    def test_serialize_zones_merges_live_lactate_payload(
        self,
        sample_lactate_threshold_live_raw: Any,
    ) -> None:
        assert serialize_zones(sample_lactate_threshold_live_raw) == [
            {"sport": "running", "lt_hr_bpm": 177, "lt_pace": "4:26"}
        ]


@pytest.mark.parametrize(
    ("serializer", "payload_fixture", "expected", "columns", "required_columns"),
    [
        (
            serialize_body_battery,
            "sample_body_battery_raw",
            {"date": "2026-03-11", "start_level": 85, "end_level": 60},
            COLUMNS_BODY_BATTERY,
            ("date", "start_level", "end_level"),
        ),
        (
            serialize_stress,
            "sample_stress_raw",
            {"date": "2026-03-11", "avg_stress": 35, "max_stress": 72},
            COLUMNS_STRESS,
            ("date", "avg_stress", "max_stress"),
        ),
        (
            serialize_spo2,
            "sample_spo2_raw",
            {"date": "2026-03-11", "avg_spo2": 97, "lowest_spo2": 93},
            COLUMNS_SPO2,
            ("date", "avg_spo2", "lowest_spo2"),
        ),
        (
            serialize_resting_hr,
            "sample_resting_hr_raw",
            {"date": "2026-03-11", "resting_hr": 52},
            COLUMNS_RESTING_HR,
            ("date", "resting_hr"),
        ),
        (
            serialize_training_readiness,
            "sample_training_readiness_raw",
            {"date": "2026-03-11", "score": 68, "level": "MODERATE"},
            COLUMNS_READINESS,
            ("date", "score", "level"),
        ),
        (
            serialize_training_status,
            "sample_training_status_raw",
            {
                "date": "2026-03-11",
                "training_status": "PRODUCTIVE",
                "load_type": "OPTIMAL",
            },
            COLUMNS_STATUS,
            ("date", "training_status", "load_type"),
        ),
    ],
)
def test_additional_health_serializers(
    request: pytest.FixtureRequest,
    serializer: Any,
    payload_fixture: str,
    expected: dict[str, Any],
    columns: tuple[str, ...],
    required_columns: tuple[str, ...],
) -> None:
    payload = request.getfixturevalue(payload_fixture)
    assert serializer(payload) == [expected]
    assert columns == required_columns


# ---------------------------------------------------------------------------
# serialize_activity_detail
# ---------------------------------------------------------------------------

class TestSerializeActivityDetail:

    def test_import_exists(self) -> None:
        from garmin_cli.serializers import COLUMNS_ACTIVITY_DETAIL, serialize_activity_detail
        assert callable(serialize_activity_detail)
        assert isinstance(COLUMNS_ACTIVITY_DETAIL, tuple)

    def test_cycling_all_power_cadence_elevation(self) -> None:
        from garmin_cli.serializers import serialize_activity_detail
        raw = {
            "activityId": 1,
            "startTimeLocal": "2026-04-01T08:00:00",
            "activityName": "Morning Ride",
            "activityType": {"typeKey": "cycling"},
            "distance": 50000.0,
            "duration": 5400.0,
            "averageHR": 145,
            "maxHR": 178,
            "calories": 850,
            "elevationGain": 600.0,
            "elevationLoss": 580.0,
            "averageSpeed": 9.259,
            "maxSpeed": 15.0,
            "averageBikingCadenceInRevPerMinute": 85.0,
            "averagePower": 210.0,
            "maxPower": 650.0,
            "normPower": 230.0,
            "trainingStressScore": 120.5,
            "intensityFactor": 0.92,
        }
        result = serialize_activity_detail(raw)
        assert len(result) == 1
        row = result[0]
        # base fields
        assert row["id"] == 1
        assert row["name"] == "Morning Ride"
        assert row["type"] == "cycling"
        assert row["distance_km"] == pytest.approx(50.0, rel=0.01)
        assert row["duration_min"] == pytest.approx(90.0, rel=0.01)
        assert row["avg_hr"] == 145
        # extended fields
        assert row["max_hr"] == 178
        assert row["calories"] == 850
        assert row["elevation_gain_m"] == pytest.approx(600.0, rel=0.01)
        assert row["elevation_loss_m"] == pytest.approx(580.0, rel=0.01)
        assert row["avg_speed_kmh"] == pytest.approx(9.259 * 3.6, rel=0.01)
        assert row["max_speed_kmh"] == pytest.approx(15.0 * 3.6, rel=0.01)
        assert row["avg_cadence_rpm"] == pytest.approx(85.0, rel=0.01)
        assert row["avg_cadence_spm"] is None
        assert row["avg_power_w"] == pytest.approx(210.0, rel=0.01)
        assert row["max_power_w"] == pytest.approx(650.0, rel=0.01)
        assert row["norm_power_w"] == pytest.approx(230.0, rel=0.01)
        assert row["tss"] == pytest.approx(120.5, rel=0.01)
        assert row["intensity_factor"] == pytest.approx(0.92, rel=0.01)

    def test_running_cadence_spm_no_power(self) -> None:
        from garmin_cli.serializers import serialize_activity_detail
        raw = {
            "activityId": 2,
            "startTimeLocal": "2026-04-02T06:00:00",
            "activityName": "Easy Run",
            "activityType": {"typeKey": "running"},
            "distance": 10000.0,
            "duration": 3600.0,
            "averageHR": 150,
            "maxHR": 170,
            "calories": 600,
            "averageRunningCadenceInStepsPerMinute": 180.0,
        }
        result = serialize_activity_detail(raw)
        row = result[0]
        assert row["avg_cadence_spm"] == pytest.approx(180.0, rel=0.01)
        assert row["avg_cadence_rpm"] is None
        assert row["avg_power_w"] is None
        assert row["max_power_w"] is None
        assert row["norm_power_w"] is None

    def test_no_extended_fields_returns_nulls(self) -> None:
        from garmin_cli.serializers import serialize_activity_detail
        raw = {
            "activityId": 3,
            "startTimeLocal": "2026-04-03T10:00:00",
            "activityName": "Walk",
            "activityType": {"typeKey": "walking"},
        }
        result = serialize_activity_detail(raw)
        assert len(result) == 1
        row = result[0]
        assert row["max_hr"] is None
        assert row["calories"] is None
        assert row["elevation_gain_m"] is None
        assert row["elevation_loss_m"] is None
        assert row["avg_speed_kmh"] is None
        assert row["max_speed_kmh"] is None
        assert row["avg_cadence_spm"] is None
        assert row["avg_cadence_rpm"] is None
        assert row["avg_power_w"] is None
        assert row["max_power_w"] is None
        assert row["norm_power_w"] is None
        assert row["tss"] is None
        assert row["intensity_factor"] is None

    def test_summary_dto_fallback_for_extended_fields(self) -> None:
        from garmin_cli.serializers import serialize_activity_detail
        raw = {
            "activityId": 4,
            "activityName": "Ride",
            "activityType": {"typeKey": "cycling"},
            "summaryDTO": {
                "startTimeLocal": "2026-04-04T07:00:00",
                "distance": 20000.0,
                "duration": 3600.0,
                "averageHR": 140,
                "maxHR": 175,
                "calories": 500,
                "elevationGain": 200.0,
                "elevationLoss": 190.0,
                "averageSpeed": 5.556,
                "maxSpeed": 12.0,
                "averageBikingCadenceInRevPerMinute": 80.0,
                "averagePower": 180.0,
                "maxPower": 400.0,
                "normPower": 200.0,
                "trainingStressScore": 80.0,
                "intensityFactor": 0.85,
            },
        }
        result = serialize_activity_detail(raw)
        row = result[0]
        assert row["max_hr"] == 175
        assert row["calories"] == 500
        assert row["elevation_gain_m"] == pytest.approx(200.0, rel=0.01)
        assert row["avg_speed_kmh"] == pytest.approx(5.556 * 3.6, rel=0.01)
        assert row["avg_power_w"] == pytest.approx(180.0, rel=0.01)
        assert row["tss"] == pytest.approx(80.0, rel=0.01)

    def test_top_level_preferred_over_summary_dto_for_extended(self) -> None:
        from garmin_cli.serializers import serialize_activity_detail
        raw = {
            "activityId": 10,
            "activityType": {"typeKey": "cycling"},
            "maxHR": 185,
            "calories": 900,
            "elevationGain": 300.0,
            "averageSpeed": 8.0,
            "averagePower": 250.0,
            "summaryDTO": {
                "maxHR": 170,
                "calories": 800,
                "elevationGain": 200.0,
                "averageSpeed": 6.0,
                "averagePower": 200.0,
            },
        }
        result = serialize_activity_detail(raw)
        row = result[0]
        assert row["max_hr"] == 185
        assert row["calories"] == 900
        assert row["elevation_gain_m"] == pytest.approx(300.0, rel=0.01)
        assert row["avg_speed_kmh"] == pytest.approx(8.0 * 3.6, rel=0.01)
        assert row["avg_power_w"] == pytest.approx(250.0, rel=0.01)

    def test_hybrid_top_level_and_summary_dto_for_extended(self) -> None:
        from garmin_cli.serializers import serialize_activity_detail
        raw = {
            "activityId": 11,
            "activityType": {"typeKey": "cycling"},
            "maxHR": 185,
            "averagePower": 250.0,
            "summaryDTO": {
                "calories": 800,
                "elevationGain": 200.0,
                "averageSpeed": 6.0,
            },
        }
        result = serialize_activity_detail(raw)
        row = result[0]
        assert row["max_hr"] == 185
        assert row["calories"] == 800
        assert row["elevation_gain_m"] == pytest.approx(200.0, rel=0.01)
        assert row["avg_speed_kmh"] == pytest.approx(6.0 * 3.6, rel=0.01)
        assert row["avg_power_w"] == pytest.approx(250.0, rel=0.01)

    def test_speed_zero_converts_to_zero(self) -> None:
        from garmin_cli.serializers import serialize_activity_detail
        raw = {
            "activityId": 5,
            "activityType": {"typeKey": "running"},
            "averageSpeed": 0.0,
            "maxSpeed": 0.0,
        }
        result = serialize_activity_detail(raw)
        assert result[0]["avg_speed_kmh"] == pytest.approx(0.0)
        assert result[0]["max_speed_kmh"] == pytest.approx(0.0)

    def test_speed_null_stays_null(self) -> None:
        from garmin_cli.serializers import serialize_activity_detail
        raw = {
            "activityId": 6,
            "activityType": {"typeKey": "running"},
        }
        result = serialize_activity_detail(raw)
        assert result[0]["avg_speed_kmh"] is None
        assert result[0]["max_speed_kmh"] is None

    def test_first_seven_keys_match_summary(self, sample_activity_raw: Any) -> None:
        from garmin_cli.serializers import serialize_activity_detail
        summary_row = serialize_activity_summary(sample_activity_raw)[0]
        detail_row = serialize_activity_detail(sample_activity_raw)[0]
        summary_keys = list(summary_row.keys())
        detail_keys = list(detail_row.keys())
        assert detail_keys[:7] == summary_keys[:7]
        for key in summary_keys:
            assert detail_row[key] == summary_row[key]

    def test_detail_is_strict_superset_of_summary(self, sample_activity_raw: Any) -> None:
        from garmin_cli.serializers import serialize_activity_detail
        summary_row = serialize_activity_summary(sample_activity_raw)[0]
        detail_row = serialize_activity_detail(sample_activity_raw)[0]
        assert set(summary_row.keys()).issubset(set(detail_row.keys()))
        assert len(detail_row) > len(summary_row)

    def test_columns_activity_detail_exists(self) -> None:
        from garmin_cli.serializers import COLUMNS_ACTIVITY_DETAIL
        for col in (
            "id", "date", "name", "type", "distance_km", "duration_min", "avg_hr",
            "max_hr", "calories", "elevation_gain_m", "elevation_loss_m",
            "avg_speed_kmh", "max_speed_kmh",
            "avg_cadence_spm", "avg_cadence_rpm",
            "avg_power_w", "max_power_w", "norm_power_w",
            "tss", "intensity_factor",
        ):
            assert col in COLUMNS_ACTIVITY_DETAIL

    def test_normalize_activity_base_indirectly(self, sample_activity_raw: Any) -> None:
        """_normalize_activity_base is tested indirectly: summary still works after refactor."""
        result = serialize_activity_summary(sample_activity_raw)
        assert result[0]["id"] == 12345678
        assert result[0]["distance_km"] == pytest.approx(10.0, rel=0.01)
        assert result[0]["duration_min"] == pytest.approx(60.0, rel=0.01)
        assert result[0]["avg_hr"] == 155
