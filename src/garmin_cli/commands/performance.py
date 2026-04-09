"""Performance commands."""
from __future__ import annotations

from datetime import date

import click

from garmin_cli.auth import ensure_authenticated
from garmin_cli.endpoints.performance import (
    get_all_thresholds,
    get_latest_vo2max,
    get_lactate_threshold,
    get_vo2max,
)
from garmin_cli.output import render_output
from garmin_cli.serializers import (
    COLUMNS_THRESHOLDS,
    COLUMNS_VO2MAX,
    COLUMNS_ZONES,
    select_latest_dated_rows,
    serialize_thresholds,
    serialize_vo2max,
    serialize_zones,
)


@click.group()
def performance() -> None:
    """Performance commands."""


@performance.command("thresholds")
@click.pass_context
def thresholds_cmd(ctx: click.Context) -> None:
    """Get available threshold metrics."""
    ensure_authenticated(ctx.obj["config"])
    raw = get_all_thresholds()
    data = serialize_thresholds(raw)
    render_output(ctx.obj["config"].output_format, "performance thresholds", data, COLUMNS_THRESHOLDS)


@performance.command("vo2max")
@click.option("--date", "value_date", type=click.DateTime(formats=["%Y-%m-%d"]), default=None)
@click.pass_context
def vo2max_cmd(ctx: click.Context, value_date: date | None) -> None:
    """Get VO2 max for a day."""
    ensure_authenticated(ctx.obj["config"])
    raw = get_vo2max(value_date.date()) if value_date else get_latest_vo2max()
    data = serialize_vo2max(raw)
    if value_date is None:
        data = select_latest_dated_rows(data)
    render_output(ctx.obj["config"].output_format, "performance vo2max", data, COLUMNS_VO2MAX)


@performance.command("zones")
@click.pass_context
def zones_cmd(ctx: click.Context) -> None:
    """Get lactate-threshold-derived zone inputs."""
    ensure_authenticated(ctx.obj["config"])
    raw = get_lactate_threshold()
    data = serialize_zones(raw)
    render_output(ctx.obj["config"].output_format, "performance zones", data, COLUMNS_ZONES)
