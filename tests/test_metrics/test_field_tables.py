"""Tests for the domain-agnostic flat field-table core and its adoption.

The existing ``tests/test_serializers.py`` is the byte-identical regression net
for serializer *output*; these tests exercise the new
:mod:`garmin_cli.metrics.field_table` primitives directly and assert the
import-time consistency guards that protect the migrated health / performance /
device serializers from COLUMNS_*-vs-table drift.
"""
from __future__ import annotations

from typing import Any

import pytest

from garmin_cli.metrics import (
    FieldEntry,
    FieldTable,
    project_row,
    resolve_field,
    validate_table_coverage,
)


# ---------------------------------------------------------------------------
# FieldEntry / resolve_field
# ---------------------------------------------------------------------------


class TestResolveField:

    def test_single_path_resolves(self) -> None:
        entry = FieldEntry("k", (("a",),))
        assert resolve_field(entry, {"a": 5}) == 5

    def test_missing_returns_none(self) -> None:
        entry = FieldEntry("k", (("a",),))
        assert resolve_field(entry, {}) is None

    def test_precedence_first_non_none_wins(self) -> None:
        entry = FieldEntry("k", (("a",), ("b",)))
        assert resolve_field(entry, {"a": 1, "b": 2}) == 1

    def test_precedence_falls_through_on_none(self) -> None:
        entry = FieldEntry("k", (("a",), ("b",)))
        assert resolve_field(entry, {"a": None, "b": 2}) == 2

    def test_explicit_none_is_treated_as_absent(self) -> None:
        entry = FieldEntry("k", (("a",),))
        assert resolve_field(entry, {"a": None}) is None

    def test_nested_path_walk(self) -> None:
        entry = FieldEntry("k", (("a", "b", "c"),))
        assert resolve_field(entry, {"a": {"b": {"c": 9}}}) == 9

    def test_nested_path_missing_intermediate(self) -> None:
        entry = FieldEntry("k", (("a", "b", "c"),))
        assert resolve_field(entry, {"a": {}}) is None

    def test_converter_applied_to_non_none(self) -> None:
        entry = FieldEntry("k", (("a",),), lambda v: v / 1000)
        assert resolve_field(entry, {"a": 75000}) == pytest.approx(75.0)

    def test_converter_not_called_on_none(self) -> None:
        called: list[Any] = []

        def conv(value: Any) -> Any:
            called.append(value)
            return value

        entry = FieldEntry("k", (("a",),), conv)
        assert resolve_field(entry, {}) is None
        assert called == []

    def test_zero_is_not_treated_as_absent(self) -> None:
        entry = FieldEntry("k", (("a",), ("b",)), lambda v: v * 2)
        assert resolve_field(entry, {"a": 0, "b": 99}) == 0


# ---------------------------------------------------------------------------
# project_row / FieldTable projection
# ---------------------------------------------------------------------------


class TestProjectRow:

    def test_key_order_matches_declaration(self) -> None:
        entries = (
            FieldEntry("z", (("z",),)),
            FieldEntry("a", (("a",),)),
            FieldEntry("m", (("m",),)),
        )
        row = project_row({"a": 1, "m": 2, "z": 3}, entries)
        assert list(row.keys()) == ["z", "a", "m"]

    def test_row_has_exactly_one_key_per_entry(self) -> None:
        entries = (FieldEntry("a", (("a",),)), FieldEntry("b", (("b",),)))
        row = project_row({"a": 1, "b": 2, "extra": 3}, entries)
        assert set(row) == {"a", "b"}

    def test_table_project_and_project_all(self) -> None:
        table = FieldTable(
            name="t",
            columns=("date", "v"),
            entries=(
                FieldEntry("date", (("calendarDate",),)),
                FieldEntry("v", (("value",),)),
            ),
        )
        assert table.project({"calendarDate": "d", "value": 1}) == {"date": "d", "v": 1}
        assert table.project_all(
            [{"calendarDate": "d1", "value": 1}, {"calendarDate": "d2", "value": 2}]
        ) == [{"date": "d1", "v": 1}, {"date": "d2", "v": 2}]

    def test_empty_item_yields_all_none_row(self) -> None:
        table = FieldTable(
            name="t",
            columns=("a", "b"),
            entries=(FieldEntry("a", (("a",),)), FieldEntry("b", (("b",),))),
        )
        assert table.project({}) == {"a": None, "b": None}


# ---------------------------------------------------------------------------
# FieldTable construction invariants
# ---------------------------------------------------------------------------


class TestFieldTableConstruction:

    def test_is_frozen(self) -> None:
        table = FieldTable(
            name="t", columns=("a",), entries=(FieldEntry("a", (("a",),)),)
        )
        with pytest.raises((AttributeError, Exception)):
            table.name = "other"  # type: ignore[misc]

    def test_entry_order_must_match_columns(self) -> None:
        with pytest.raises(RuntimeError, match="drift"):
            FieldTable(
                name="t",
                columns=("a", "b"),
                entries=(FieldEntry("b", (("b",),)), FieldEntry("a", (("a",),))),
            )

    def test_missing_entry_for_column_raises(self) -> None:
        with pytest.raises(RuntimeError, match="drift"):
            FieldTable(
                name="t", columns=("a", "b"), entries=(FieldEntry("a", (("a",),)),)
            )

    def test_extra_entry_not_in_columns_raises(self) -> None:
        with pytest.raises(RuntimeError, match="drift"):
            FieldTable(
                name="t",
                columns=("a",),
                entries=(FieldEntry("a", (("a",),)), FieldEntry("b", (("b",),))),
            )


# ---------------------------------------------------------------------------
# validate_table_coverage (cross-domain analogue of _validate_registry_coverage)
# ---------------------------------------------------------------------------


def _table(name: str, columns: tuple[str, ...]) -> FieldTable:
    return FieldTable(
        name=name,
        columns=columns,
        entries=tuple(FieldEntry(c, ((c,),)) for c in columns),
    )


class TestValidateTableCoverage:

    def test_passes_when_every_constant_backed(self) -> None:
        t = _table("x", ("a", "b"))
        validate_table_coverage("demo", {"COLUMNS_X": ("a", "b")}, (t,))

    def test_raises_when_constant_unbacked(self) -> None:
        t = _table("x", ("a", "b"))
        with pytest.raises(RuntimeError, match="no backing"):
            validate_table_coverage(
                "demo", {"COLUMNS_X": ("a", "b"), "COLUMNS_Y": ("z",)}, (t,)
            )

    def test_exempt_constant_is_skipped(self) -> None:
        t = _table("x", ("a", "b"))
        validate_table_coverage(
            "demo",
            {"COLUMNS_X": ("a", "b"), "COLUMNS_STRUCTURAL": ("z",)},
            (t,),
            exempt=frozenset({"COLUMNS_STRUCTURAL"}),
        )

    def test_domain_name_in_error(self) -> None:
        with pytest.raises(RuntimeError, match="mydomain"):
            validate_table_coverage("mydomain", {"COLUMNS_Y": ("z",)}, ())


# ---------------------------------------------------------------------------
# Adoption check: the live serializer modules' tables stay consistent.
# Importing the modules already runs validate_table_coverage at import time;
# this re-asserts each declared table is self-consistent for defence in depth.
# ---------------------------------------------------------------------------


class TestDomainTablesAreConsistent:

    def test_health_tables_match_columns(self) -> None:
        from garmin_cli.serializers import health

        pairs = [
            (health._SLEEP_TABLE, health.COLUMNS_SLEEP),
            (health._HRV_TABLE, health.COLUMNS_HRV),
            (health._WEIGHT_TABLE, health.COLUMNS_WEIGHT),
            (health._SPO2_TABLE, health.COLUMNS_SPO2),
            (health._RESTING_HR_TABLE, health.COLUMNS_RESTING_HR),
            (health._READINESS_TABLE, health.COLUMNS_READINESS),
            (health._STATUS_TABLE, health.COLUMNS_STATUS),
            (health._DAILY_SUMMARY_TABLE, health.COLUMNS_DAILY_SUMMARY),
            (health._STEPS_TABLE, health.COLUMNS_STEPS),
            (health._INTENSITY_MINUTES_TABLE, health.COLUMNS_INTENSITY_MINUTES),
        ]
        for table, columns in pairs:
            assert table.columns == columns
            assert tuple(e.key for e in table.entries) == columns

    def test_performance_tables_match_columns(self) -> None:
        from garmin_cli.serializers import performance

        pairs = [
            (performance._RACE_PREDICTIONS_TABLE, performance.COLUMNS_RACE_PREDICTIONS),
            (performance._ENDURANCE_SCORE_TABLE, performance.COLUMNS_ENDURANCE_SCORE),
            (performance._HILL_SCORE_TABLE, performance.COLUMNS_HILL_SCORE),
            (performance._THRESHOLDS_TABLE, performance.COLUMNS_THRESHOLDS),
        ]
        for table, columns in pairs:
            assert table.columns == columns

    def test_device_table_matches_columns(self) -> None:
        from garmin_cli.serializers import devices

        assert devices._DEVICE_TABLE.columns == devices.COLUMNS_DEVICE
