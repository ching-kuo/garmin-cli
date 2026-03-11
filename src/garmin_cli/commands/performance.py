"""Performance commands."""
from __future__ import annotations

from datetime import date

import click

from garmin_cli.auth import ensure_authenticated
from garmin_cli.endpoints.performance import (
    get_all_thresholds,
    get_lactate_threshold,
    get_vo2max,
)
from garmin_cli.output import render_output
from garmin_cli.serializers import (
    COLUMNS_LACTATE,
    COLUMNS_THRESHOLDS,
    COLUMNS_VO2MAX,
    serialize_thresholds,
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
    selected_date = value_date.date() if value_date else date.today()
    raw = get_vo2max(selected_date)
    data = [raw] if isinstance(raw, dict) else (raw or [])
    render_output(ctx.obj["config"].output_format, "performance vo2max", data, COLUMNS_VO2MAX)


@performance.command("zones")
@click.pass_context
def zones_cmd(ctx: click.Context) -> None:
    """Get lactate-threshold-derived zone inputs."""
    ensure_authenticated(ctx.obj["config"])
    raw = get_lactate_threshold()
    data = [raw] if isinstance(raw, dict) else (raw or [])
    render_output(ctx.obj["config"].output_format, "performance zones", data, COLUMNS_LACTATE)
