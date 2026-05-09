"""Metric registry: declarative source-of-truth for all activity metrics."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Literal, Mapping


DetailLevel = Literal["summary", "standard", "deep"]


# Sport typeKey families. These mirror the values Garmin Connect emits in
# ``activityType.typeKey`` and are reused by sport profiles in U4.
RUNNING_TYPE_KEYS: frozenset[str] = frozenset({
    "running",
    "trail_running",
    "treadmill_running",
    "track_running",
    "indoor_running",
})
CYCLING_TYPE_KEYS: frozenset[str] = frozenset({
    "cycling",
    "road_biking",
    "mountain_biking",
    "gravel_cycling",
    "virtual_ride",
    "indoor_cycling",
    "ebike_mountain_biking",
    "cyclocross",
})
LAP_SWIM_TYPE_KEYS: frozenset[str] = frozenset({"lap_swimming"})
OW_SWIM_TYPE_KEYS: frozenset[str] = frozenset({"open_water_swimming", "swimming"})
SWIM_TYPE_KEYS: frozenset[str] = LAP_SWIM_TYPE_KEYS | OW_SWIM_TYPE_KEYS


@dataclass(frozen=True)
class MetricEntry:
    """Declarative definition of a single metric.

    ``key`` is the existing serializer output key (e.g. ``avg_power_w``); Garmin
    wire names live only inside ``source_paths``. ``sports=None`` marks a
    universal metric. ``formatter`` is applied only when the resolved value is
    not None.
    """

    key: str
    label: str
    unit: str | None
    source_paths: tuple[tuple[str, ...], ...]
    sports: frozenset[str] | None
    detail_level: DetailLevel
    available_in: frozenset[str]
    formatter: Callable[[Any], Any] | None = None


# --- Resolver helpers --------------------------------------------------------


def _walk(value: Any, path: tuple[str, ...]) -> Any:
    current: Any = value
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _apply_formatter(entry: MetricEntry, value: Any) -> Any:
    if entry.formatter is None:
        return value
    return entry.formatter(value)


def resolve(
    entry: MetricEntry,
    activity: dict[str, Any],
    summary_dto: dict[str, Any] | None = None,
) -> Any:
    """Resolve a metric value from an activity payload.

    Walks ``entry.source_paths`` in declared precedence and returns the first
    non-None value (after applying ``entry.formatter``). When ``summary_dto`` is
    passed separately, paths beginning with ``"summaryDTO"`` are tried against
    it first so callers that have already unpacked ``summaryDTO`` need not
    re-nest it.
    """
    for path in entry.source_paths:
        if summary_dto is not None and path and path[0] == "summaryDTO":
            value = _walk(summary_dto, path[1:])
            if value is not None:
                return _apply_formatter(entry, value)
        value = _walk(activity, path)
        if value is not None:
            return _apply_formatter(entry, value)
    return None


def project(
    entries: Iterable[MetricEntry],
    activity: dict[str, Any],
    summary_dto: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Project a set of registry entries onto an activity payload."""
    return {entry.key: resolve(entry, activity, summary_dto) for entry in entries}


# --- Value transforms (preserve existing serializer semantics) ---------------


def _to_km(value: Any) -> float | None:
    return None if value is None else value / 1000


def _to_kmh(value: Any) -> float | None:
    return None if value is None else value * 3.6


def _to_minutes(value: Any) -> float | None:
    return None if value is None else value / 60


# --- Registry entries --------------------------------------------------------

_JSON_ONLY: frozenset[str] = frozenset({"json"})


def _entry(
    key: str,
    *,
    label: str,
    unit: str | None,
    source_paths: tuple[tuple[str, ...], ...],
    sports: frozenset[str] | None,
    detail_level: DetailLevel,
    formatter: Callable[[Any], Any] | None = None,
    available_in: frozenset[str] = _JSON_ONLY,
) -> MetricEntry:
    return MetricEntry(
        key=key,
        label=label,
        unit=unit,
        source_paths=source_paths,
        sports=sports,
        detail_level=detail_level,
        available_in=available_in,
        formatter=formatter,
    )


_ENTRIES: tuple[MetricEntry, ...] = (
    # --- Summary base fields (level: summary) --------------------------------
    _entry(
        "id",
        label="Activity ID",
        unit=None,
        source_paths=(("activityId",),),
        sports=None,
        detail_level="summary",
    ),
    _entry(
        "date",
        label="Start time",
        unit=None,
        source_paths=(
            ("startTimeLocal",),
            ("summaryDTO", "startTimeLocal"),
        ),
        sports=None,
        detail_level="summary",
    ),
    _entry(
        "name",
        label="Activity name",
        unit=None,
        source_paths=(("activityName",),),
        sports=None,
        detail_level="summary",
    ),
    _entry(
        "type",
        label="Activity type",
        unit=None,
        source_paths=(("activityType", "typeKey"),),
        sports=None,
        detail_level="summary",
    ),
    _entry(
        "distance_km",
        label="Distance",
        unit="km",
        source_paths=(
            ("distance",),
            ("summaryDTO", "distance"),
        ),
        sports=None,
        detail_level="summary",
        formatter=_to_km,
    ),
    _entry(
        "duration_min",
        label="Duration",
        unit="min",
        source_paths=(
            ("duration",),
            ("summaryDTO", "duration"),
        ),
        sports=None,
        detail_level="summary",
        formatter=_to_minutes,
    ),
    _entry(
        "avg_hr",
        label="Average heart rate",
        unit="bpm",
        source_paths=(
            ("averageHR",),
            ("summaryDTO", "averageHR"),
        ),
        sports=None,
        detail_level="summary",
    ),
    # --- Detail fields, universal (level: standard) --------------------------
    _entry(
        "max_hr",
        label="Maximum heart rate",
        unit="bpm",
        source_paths=(
            ("maxHR",),
            ("summaryDTO", "maxHR"),
        ),
        sports=None,
        detail_level="standard",
    ),
    _entry(
        "calories",
        label="Calories",
        unit="kcal",
        source_paths=(
            ("calories",),
            ("summaryDTO", "calories"),
        ),
        sports=None,
        detail_level="standard",
    ),
    _entry(
        "elevation_gain_m",
        label="Elevation gain",
        unit="m",
        source_paths=(
            ("elevationGain",),
            ("summaryDTO", "elevationGain"),
        ),
        sports=None,
        detail_level="standard",
    ),
    _entry(
        "elevation_loss_m",
        label="Elevation loss",
        unit="m",
        source_paths=(
            ("elevationLoss",),
            ("summaryDTO", "elevationLoss"),
        ),
        sports=None,
        detail_level="standard",
    ),
    _entry(
        "avg_speed_kmh",
        label="Average speed",
        unit="km/h",
        source_paths=(
            ("averageSpeed",),
            ("summaryDTO", "averageSpeed"),
        ),
        sports=None,
        detail_level="standard",
        formatter=_to_kmh,
    ),
    _entry(
        "max_speed_kmh",
        label="Maximum speed",
        unit="km/h",
        source_paths=(
            ("maxSpeed",),
            ("summaryDTO", "maxSpeed"),
        ),
        sports=None,
        detail_level="standard",
        formatter=_to_kmh,
    ),
    # --- Running-specific (level: standard) ----------------------------------
    _entry(
        "avg_cadence_spm",
        label="Average cadence",
        unit="spm",
        source_paths=(
            ("averageRunningCadenceInStepsPerMinute",),
            ("summaryDTO", "averageRunningCadenceInStepsPerMinute"),
        ),
        sports=RUNNING_TYPE_KEYS,
        detail_level="standard",
    ),
    _entry(
        "avg_ground_contact_time",
        label="Average ground contact time",
        unit="ms",
        source_paths=(
            ("avgGroundContactTime",),
            ("summaryDTO", "avgGroundContactTime"),
        ),
        sports=RUNNING_TYPE_KEYS,
        detail_level="standard",
    ),
    _entry(
        "avg_vertical_oscillation",
        label="Average vertical oscillation",
        unit="cm",
        source_paths=(
            ("avgVerticalOscillation",),
            ("summaryDTO", "avgVerticalOscillation"),
        ),
        sports=RUNNING_TYPE_KEYS,
        detail_level="standard",
    ),
    _entry(
        "avg_vertical_ratio",
        label="Average vertical ratio",
        unit="%",
        source_paths=(
            ("avgVerticalRatio",),
            ("summaryDTO", "avgVerticalRatio"),
        ),
        sports=RUNNING_TYPE_KEYS,
        detail_level="standard",
    ),
    _entry(
        "avg_stride_length",
        label="Average stride length",
        unit="cm",
        source_paths=(
            ("avgStrideLength",),
            ("summaryDTO", "avgStrideLength"),
        ),
        sports=RUNNING_TYPE_KEYS,
        detail_level="standard",
    ),
    # --- Cycling-specific (level: standard) ----------------------------------
    _entry(
        "avg_cadence_rpm",
        label="Average cadence",
        unit="rpm",
        source_paths=(
            ("averageBikingCadenceInRevPerMinute",),
            ("summaryDTO", "averageBikingCadenceInRevPerMinute"),
        ),
        sports=CYCLING_TYPE_KEYS,
        detail_level="standard",
    ),
    _entry(
        "avg_power_w",
        label="Average power",
        unit="W",
        source_paths=(
            ("averagePower",),
            ("summaryDTO", "averagePower"),
        ),
        sports=CYCLING_TYPE_KEYS,
        detail_level="standard",
    ),
    _entry(
        "max_power_w",
        label="Maximum power",
        unit="W",
        source_paths=(
            ("maxPower",),
            ("summaryDTO", "maxPower"),
        ),
        sports=CYCLING_TYPE_KEYS,
        detail_level="standard",
    ),
    _entry(
        "norm_power_w",
        label="Normalized power",
        unit="W",
        source_paths=(
            ("normPower",),
            ("normalizedPower",),
            ("summaryDTO", "normPower"),
            ("summaryDTO", "normalizedPower"),
        ),
        sports=CYCLING_TYPE_KEYS,
        detail_level="standard",
    ),
    _entry(
        "tss",
        label="Training stress score",
        unit=None,
        source_paths=(
            ("trainingStressScore",),
            ("summaryDTO", "trainingStressScore"),
        ),
        sports=CYCLING_TYPE_KEYS,
        detail_level="standard",
    ),
    _entry(
        "intensity_factor",
        label="Intensity factor",
        unit=None,
        source_paths=(
            ("intensityFactor",),
            ("summaryDTO", "intensityFactor"),
        ),
        sports=CYCLING_TYPE_KEYS,
        detail_level="standard",
    ),
    # --- Run/bike training response (level: standard) ------------------------
    _entry(
        "aerobic_training_effect",
        label="Aerobic training effect",
        unit=None,
        source_paths=(
            ("aerobicTrainingEffect",),
            ("summaryDTO", "aerobicTrainingEffect"),
        ),
        sports=RUNNING_TYPE_KEYS | CYCLING_TYPE_KEYS,
        detail_level="standard",
    ),
    _entry(
        "anaerobic_training_effect",
        label="Anaerobic training effect",
        unit=None,
        source_paths=(
            ("anaerobicTrainingEffect",),
            ("summaryDTO", "anaerobicTrainingEffect"),
        ),
        sports=RUNNING_TYPE_KEYS | CYCLING_TYPE_KEYS,
        detail_level="standard",
    ),
    _entry(
        "vo2max",
        label="VO2 max",
        unit=None,
        source_paths=(
            ("vO2MaxValue",),
            ("summaryDTO", "vO2MaxValue"),
        ),
        sports=RUNNING_TYPE_KEYS | CYCLING_TYPE_KEYS,
        detail_level="standard",
    ),
    _entry(
        "recovery_time_h",
        label="Recovery time",
        unit="h",
        source_paths=(
            ("recoveryTime",),
            ("summaryDTO", "recoveryTime"),
        ),
        sports=RUNNING_TYPE_KEYS | CYCLING_TYPE_KEYS,
        detail_level="standard",
        formatter=lambda minutes: None if minutes is None else minutes / 60,
    ),
    # --- Pool-swim aggregates (level: standard) ------------------------------
    _entry(
        "swolf",
        label="SWOLF",
        unit=None,
        source_paths=(
            ("avgSwolf",),
            ("summaryDTO", "avgSwolf"),
        ),
        sports=LAP_SWIM_TYPE_KEYS,
        detail_level="standard",
    ),
    _entry(
        "total_strokes",
        label="Total strokes",
        unit=None,
        source_paths=(
            ("strokes",),
            ("summaryDTO", "strokes"),
            ("totalNumberOfStrokes",),
            ("summaryDTO", "totalNumberOfStrokes"),
        ),
        sports=LAP_SWIM_TYPE_KEYS,
        detail_level="standard",
    ),
    _entry(
        "avg_stroke_rate",
        label="Average stroke rate",
        unit="strokes/min",
        source_paths=(
            ("averageStrokeRate",),
            ("summaryDTO", "averageStrokeRate"),
            ("avgStrokeRate",),
            ("summaryDTO", "avgStrokeRate"),
        ),
        sports=LAP_SWIM_TYPE_KEYS,
        detail_level="standard",
    ),
    _entry(
        "distance_per_stroke",
        label="Distance per stroke",
        unit="m",
        source_paths=(
            ("avgStrokeDistance",),
            ("summaryDTO", "avgStrokeDistance"),
        ),
        sports=LAP_SWIM_TYPE_KEYS,
        detail_level="standard",
    ),
)


REGISTRY: Mapping[str, MetricEntry] = {entry.key: entry for entry in _ENTRIES}


# --- Helpers ----------------------------------------------------------------


def lookup(key: str) -> MetricEntry:
    """Return the registry entry for ``key`` or raise ``KeyError``."""
    return REGISTRY[key]


def for_sport(type_key: str | None) -> Iterable[MetricEntry]:
    """Yield entries applicable to the given sport ``typeKey``.

    Entries with ``sports=None`` are universal and always yielded. When
    ``type_key`` is None or unknown, only universal entries are yielded.
    """
    for entry in _ENTRIES:
        if entry.sports is None or (type_key is not None and type_key in entry.sports):
            yield entry


def at_detail(level: DetailLevel) -> Iterable[MetricEntry]:
    """Yield entries whose ``detail_level`` matches ``level``."""
    for entry in _ENTRIES:
        if entry.detail_level == level:
            yield entry
