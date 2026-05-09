"""Declarative catalog of metric definitions.

The registry is the single source of truth for metric keys, source paths,
sport applicability, formatting, and detail level. CLI columns, MCP response
fields, and capability manifests all derive from registry entries.
"""
from __future__ import annotations

from garmin_cli.metrics.registry import (
    CYCLING_TYPE_KEYS,
    LAP_SWIM_TYPE_KEYS,
    OW_SWIM_TYPE_KEYS,
    REGISTRY,
    RUNNING_TYPE_KEYS,
    SWIM_TYPE_KEYS,
    MetricEntry,
    at_detail,
    for_sport,
    lookup,
    project,
    resolve,
)

__all__ = (
    "CYCLING_TYPE_KEYS",
    "LAP_SWIM_TYPE_KEYS",
    "OW_SWIM_TYPE_KEYS",
    "REGISTRY",
    "RUNNING_TYPE_KEYS",
    "SWIM_TYPE_KEYS",
    "MetricEntry",
    "at_detail",
    "for_sport",
    "lookup",
    "project",
    "resolve",
)
