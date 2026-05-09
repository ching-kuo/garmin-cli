"""Tests for the metric registry foundation (U1)."""
from __future__ import annotations

from typing import Any

import pytest

from garmin_cli.metrics import (
    CYCLING_TYPE_KEYS,
    LAP_SWIM_TYPE_KEYS,
    REGISTRY,
    RUNNING_TYPE_KEYS,
    MetricEntry,
    at_detail,
    for_sport,
    lookup,
    project,
    resolve,
)
from garmin_cli.serializers import COLUMNS_ACTIVITY_DETAIL, serialize_activity_detail


# ---------------------------------------------------------------------------
# MetricEntry shape
# ---------------------------------------------------------------------------


class TestMetricEntry:

    def test_entry_is_frozen(self) -> None:
        entry = lookup("avg_power_w")
        with pytest.raises((AttributeError, Exception)):
            entry.key = "other"  # type: ignore[misc]

    def test_every_entry_has_at_least_one_source_path(self) -> None:
        for entry in REGISTRY.values():
            assert entry.source_paths, f"{entry.key} has no source paths"
            for path in entry.source_paths:
                assert isinstance(path, tuple)
                assert len(path) >= 1
                for segment in path:
                    assert isinstance(segment, str) and segment


# ---------------------------------------------------------------------------
# lookup
# ---------------------------------------------------------------------------


class TestLookup:

    def test_returns_metric_entry(self) -> None:
        entry = lookup("avg_power_w")
        assert isinstance(entry, MetricEntry)
        assert entry.key == "avg_power_w"

    def test_norm_power_w_source_paths_match_existing_serializer(self) -> None:
        entry = lookup("norm_power_w")
        assert ("normPower",) in entry.source_paths
        assert ("summaryDTO", "normPower") in entry.source_paths
        assert ("summaryDTO", "normalizedPower") in entry.source_paths
        # precedence: top-level normPower must come before summaryDTO entries
        idx_top = entry.source_paths.index(("normPower",))
        idx_sum = entry.source_paths.index(("summaryDTO", "normPower"))
        assert idx_top < idx_sum

    def test_avg_power_source_paths_match_existing_serializer(self) -> None:
        entry = lookup("avg_power_w")
        assert ("averagePower",) in entry.source_paths
        assert ("summaryDTO", "averagePower") in entry.source_paths
        assert entry.source_paths.index(("averagePower",)) < entry.source_paths.index(
            ("summaryDTO", "averagePower")
        )

    def test_unknown_key_raises_keyerror(self) -> None:
        with pytest.raises(KeyError):
            lookup("not_a_real_metric")


# ---------------------------------------------------------------------------
# for_sport
# ---------------------------------------------------------------------------


class TestForSport:

    def test_running_includes_running_metrics(self) -> None:
        keys = {entry.key for entry in for_sport("running")}
        assert "avg_cadence_spm" in keys
        assert "avg_ground_contact_time" in keys
        assert "avg_vertical_oscillation" in keys
        assert "avg_vertical_ratio" in keys
        assert "avg_stride_length" in keys
        assert "aerobic_training_effect" in keys
        assert "anaerobic_training_effect" in keys

    def test_running_excludes_cycling_only_metrics(self) -> None:
        keys = {entry.key for entry in for_sport("running")}
        assert "norm_power_w" not in keys
        assert "tss" not in keys
        assert "intensity_factor" not in keys
        assert "avg_cadence_rpm" not in keys

    def test_cycling_includes_cycling_metrics(self) -> None:
        keys = {entry.key for entry in for_sport("cycling")}
        assert "avg_power_w" in keys
        assert "max_power_w" in keys
        assert "norm_power_w" in keys
        assert "tss" in keys
        assert "intensity_factor" in keys
        assert "avg_cadence_rpm" in keys
        assert "aerobic_training_effect" in keys

    def test_cycling_excludes_running_only_metrics(self) -> None:
        keys = {entry.key for entry in for_sport("cycling")}
        assert "avg_cadence_spm" not in keys
        assert "avg_ground_contact_time" not in keys
        assert "avg_stride_length" not in keys

    def test_lap_swimming_includes_swim_metrics(self) -> None:
        keys = {entry.key for entry in for_sport("lap_swimming")}
        assert "swolf" in keys
        assert "total_strokes" in keys
        assert "avg_stroke_rate" in keys
        assert "distance_per_stroke" in keys

    def test_lap_swimming_excludes_running_and_cycling_only(self) -> None:
        keys = {entry.key for entry in for_sport("lap_swimming")}
        assert "avg_cadence_spm" not in keys
        assert "avg_cadence_rpm" not in keys
        assert "norm_power_w" not in keys
        assert "tss" not in keys
        assert "avg_ground_contact_time" not in keys

    def test_open_water_swimming_excludes_swolf(self) -> None:
        keys = {entry.key for entry in for_sport("open_water_swimming")}
        assert "swolf" not in keys

    def test_unknown_sport_returns_only_universal_entries(self) -> None:
        entries = list(for_sport("unknown_typekey"))
        for entry in entries:
            assert entry.sports is None

    def test_none_sport_returns_only_universal_entries(self) -> None:
        entries = list(for_sport(None))
        for entry in entries:
            assert entry.sports is None

    def test_universal_entries_present_for_every_sport(self) -> None:
        # universal entries (sports=None) are always yielded
        universal_keys = {e.key for e in REGISTRY.values() if e.sports is None}
        for sport in ("running", "cycling", "lap_swimming", "open_water_swimming", None, "unknown"):
            keys = {entry.key for entry in for_sport(sport)}
            assert universal_keys.issubset(keys)


# ---------------------------------------------------------------------------
# at_detail
# ---------------------------------------------------------------------------


class TestAtDetail:

    def test_summary_returns_seven_base_fields(self) -> None:
        keys = {entry.key for entry in at_detail("summary")}
        assert keys == {"id", "date", "name", "type", "distance_km", "duration_min", "avg_hr"}

    def test_standard_includes_extended_metrics(self) -> None:
        keys = {entry.key for entry in at_detail("standard")}
        # at minimum, these legacy detail keys must be at standard level
        for key in (
            "max_hr",
            "calories",
            "elevation_gain_m",
            "avg_speed_kmh",
            "avg_power_w",
            "norm_power_w",
            "tss",
            "intensity_factor",
            "avg_cadence_spm",
            "avg_cadence_rpm",
        ):
            assert key in keys, f"{key} missing from standard"

    def test_standard_includes_new_sport_specific_metrics(self) -> None:
        keys = {entry.key for entry in at_detail("standard")}
        for key in (
            "avg_ground_contact_time",
            "avg_vertical_oscillation",
            "avg_vertical_ratio",
            "avg_stride_length",
            "aerobic_training_effect",
            "anaerobic_training_effect",
            "vo2max",
            "swolf",
        ):
            assert key in keys, f"{key} missing from standard"

    def test_summary_and_standard_are_disjoint(self) -> None:
        summary_keys = {e.key for e in at_detail("summary")}
        standard_keys = {e.key for e in at_detail("standard")}
        assert not summary_keys & standard_keys


# ---------------------------------------------------------------------------
# resolve
# ---------------------------------------------------------------------------


class TestResolve:

    def test_top_level_value_takes_precedence_over_summary(self) -> None:
        entry = lookup("norm_power_w")
        activity = {"normPower": 250, "summaryDTO": {"normPower": 200, "normalizedPower": 180}}
        assert resolve(entry, activity) == 250

    def test_summary_dto_used_when_top_level_missing(self) -> None:
        entry = lookup("norm_power_w")
        activity = {"summaryDTO": {"normPower": 200}}
        assert resolve(entry, activity) == 200

    def test_normalized_power_alias_used_as_last_resort(self) -> None:
        entry = lookup("norm_power_w")
        activity = {"summaryDTO": {"normalizedPower": 180}}
        assert resolve(entry, activity) == 180

    def test_normalized_power_at_top_level_resolves(self) -> None:
        """Top-level ``normalizedPower`` is a valid alias for ``normPower``."""
        entry = lookup("norm_power_w")
        activity = {"normalizedPower": 250, "summaryDTO": {}}
        assert resolve(entry, activity) == 250

    def test_norm_power_top_level_takes_precedence_over_normalized_power_top_level(self) -> None:
        entry = lookup("norm_power_w")
        activity = {"normPower": 240, "normalizedPower": 250}
        assert resolve(entry, activity) == 240

    def test_returns_none_when_no_path_resolves(self) -> None:
        entry = lookup("norm_power_w")
        assert resolve(entry, {}) is None
        assert resolve(entry, {"summaryDTO": {}}) is None

    def test_explicit_none_falls_through_to_next_path(self) -> None:
        entry = lookup("norm_power_w")
        activity = {"normPower": None, "summaryDTO": {"normPower": 195}}
        assert resolve(entry, activity) == 195

    def test_formatter_applied(self) -> None:
        entry = lookup("avg_speed_kmh")
        # raw is m/s; formatter multiplies by 3.6
        activity = {"averageSpeed": 10.0}
        assert resolve(entry, activity) == pytest.approx(36.0, rel=0.01)

    def test_formatter_not_applied_to_none(self) -> None:
        entry = lookup("avg_speed_kmh")
        assert resolve(entry, {}) is None

    def test_summary_dto_arg_used_for_summary_paths(self) -> None:
        entry = lookup("max_hr")
        activity = {"otherStuff": True}
        summary = {"maxHR": 180}
        assert resolve(entry, activity, summary) == 180

    def test_distance_km_division(self) -> None:
        entry = lookup("distance_km")
        activity = {"distance": 12500.0}
        assert resolve(entry, activity) == pytest.approx(12.5, rel=0.01)

    def test_duration_min_division(self) -> None:
        entry = lookup("duration_min")
        activity = {"duration": 1800.0}
        assert resolve(entry, activity) == pytest.approx(30.0, rel=0.01)

    def test_recovery_time_h_division(self) -> None:
        # raw is minutes; formatter divides by 60
        entry = lookup("recovery_time_h")
        activity = {"recoveryTime": 1440}
        assert resolve(entry, activity) == pytest.approx(24.0, rel=0.01)

    def test_nested_type_key_resolved(self) -> None:
        entry = lookup("type")
        activity = {"activityType": {"typeKey": "cycling"}}
        assert resolve(entry, activity) == "cycling"

    def test_nested_path_returns_none_when_intermediate_missing(self) -> None:
        entry = lookup("type")
        # activityType missing
        assert resolve(entry, {}) is None
        # activityType present but typeKey missing
        assert resolve(entry, {"activityType": {}}) is None


# ---------------------------------------------------------------------------
# project
# ---------------------------------------------------------------------------


class TestProject:

    def test_projects_to_dict_keyed_by_entry_key(self) -> None:
        entries = [lookup("id"), lookup("type"), lookup("avg_power_w")]
        activity = {
            "activityId": 42,
            "activityType": {"typeKey": "cycling"},
            "averagePower": 200,
        }
        out = project(entries, activity)
        assert out == {"id": 42, "type": "cycling", "avg_power_w": 200}

    def test_projects_none_for_missing_values(self) -> None:
        entries = [lookup("id"), lookup("norm_power_w")]
        out = project(entries, {"activityId": 1})
        assert out == {"id": 1, "norm_power_w": None}


# ---------------------------------------------------------------------------
# Load-bearing back-compat fixture
# ---------------------------------------------------------------------------

# Every legacy COLUMNS_ACTIVITY_DETAIL key must be projected by the registry
# with the same value as today's serialize_activity_detail. This is the
# acceptance gate for U1 — Phase 2 cannot land without this passing.

_LEGACY_DETAIL_KEYS: tuple[str, ...] = (
    "id",
    "date",
    "name",
    "type",
    "distance_km",
    "duration_min",
    "avg_hr",
    "max_hr",
    "calories",
    "elevation_gain_m",
    "elevation_loss_m",
    "avg_speed_kmh",
    "max_speed_kmh",
    "avg_cadence_spm",
    "avg_cadence_rpm",
    "avg_power_w",
    "max_power_w",
    "norm_power_w",
    "tss",
    "intensity_factor",
)


@pytest.fixture()
def cycling_top_level_payload() -> dict[str, Any]:
    """Cycling activity with all detail fields at top level."""
    return {
        "activityId": 90001,
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
        "averageRunningCadenceInStepsPerMinute": None,
        "averagePower": 210.0,
        "maxPower": 650.0,
        "normPower": 230.0,
        "trainingStressScore": 120.5,
        "intensityFactor": 0.92,
    }


@pytest.fixture()
def cycling_summary_dto_payload() -> dict[str, Any]:
    """Cycling activity with all detail fields nested in summaryDTO."""
    return {
        "activityId": 90002,
        "activityName": "Evening Ride",
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


@pytest.fixture()
def cycling_mixed_payload() -> dict[str, Any]:
    """Cycling activity with detail fields split between top level and summaryDTO."""
    return {
        "activityId": 90003,
        "startTimeLocal": "2026-04-05T09:00:00",
        "activityName": "Mixed Ride",
        "activityType": {"typeKey": "cycling"},
        "maxHR": 185,
        "averagePower": 250.0,
        "summaryDTO": {
            "calories": 800,
            "elevationGain": 200.0,
            "averageSpeed": 6.0,
            "averageBikingCadenceInRevPerMinute": 82.0,
            "trainingStressScore": 90.0,
        },
    }


@pytest.mark.parametrize(
    "fixture_name",
    ["cycling_top_level_payload", "cycling_summary_dto_payload", "cycling_mixed_payload"],
)
def test_back_compat_legacy_detail_keys(fixture_name: str, request: pytest.FixtureRequest) -> None:
    """Registry-driven projection produces byte-identical legacy detail keys."""
    raw = request.getfixturevalue(fixture_name)
    legacy_row = serialize_activity_detail(raw)[0]
    summary_dto = raw.get("summaryDTO") or {}

    new_row = {key: resolve(REGISTRY[key], raw, summary_dto) for key in _LEGACY_DETAIL_KEYS}

    for key in _LEGACY_DETAIL_KEYS:
        assert new_row[key] == legacy_row[key], (
            f"Mismatch on {key} for {fixture_name}: "
            f"registry={new_row[key]!r}, legacy={legacy_row[key]!r}"
        )


def test_legacy_detail_keys_are_subset_of_columns_activity_detail() -> None:
    """The legacy detail keys must remain in COLUMNS_ACTIVITY_DETAIL (R8 back-compat)."""
    assert set(_LEGACY_DETAIL_KEYS).issubset(set(COLUMNS_ACTIVITY_DETAIL))


def test_legacy_detail_keys_keep_legacy_positions() -> None:
    """Legacy column positions must be preserved (no reordering, only appending)."""
    detail_index = {key: idx for idx, key in enumerate(COLUMNS_ACTIVITY_DETAIL)}
    # legacy keys appear in the same relative order as before
    legacy_positions = [detail_index[key] for key in _LEGACY_DETAIL_KEYS]
    assert legacy_positions == sorted(legacy_positions), (
        "Legacy COLUMNS_ACTIVITY_DETAIL keys must keep their relative order"
    )
    # the first 20 columns are exactly the legacy keys, in order
    assert COLUMNS_ACTIVITY_DETAIL[: len(_LEGACY_DETAIL_KEYS)] == _LEGACY_DETAIL_KEYS


def test_back_compat_runs_with_no_summary_dto_arg() -> None:
    """resolve() works with summary_dto=None (paths walk activity directly)."""
    raw = {
        "activityId": 1,
        "activityType": {"typeKey": "cycling"},
        "summaryDTO": {"normPower": 220},
    }
    entry = REGISTRY["norm_power_w"]
    assert resolve(entry, raw) == 220
    assert resolve(entry, raw, None) == 220
