"""Activity commands."""
from __future__ import annotations

import click

from garmin_cli.auth import ensure_authenticated
from garmin_cli.endpoints.activities import (
    get_activity,
    get_activity_weather,
    list_activities,
)
from garmin_cli.output import render_output
from garmin_cli.serializers import (
    COLUMNS_ACTIVITY_SUMMARY,
    COLUMNS_ACTIVITY_WEATHER,
    serialize_activity_summary,
)


@click.group()
def activity() -> None:
    """Activity commands."""


@activity.command("list")
@click.option("--limit", type=int, default=20)
@click.option("--type", "activity_type", type=str, default=None)
@click.option("--search", type=str, default=None)
@click.pass_context
def list_cmd(
    ctx: click.Context,
    limit: int,
    activity_type: str | None,
    search: str | None,
) -> None:
    """List recent activities."""
    ensure_authenticated(ctx.obj["config"])
    raw = list_activities(limit=limit, start=0, activity_type=activity_type, search=search)
    data = serialize_activity_summary(raw)
    render_output(ctx.obj["config"].output_format, "activity list", data, COLUMNS_ACTIVITY_SUMMARY)


@activity.command("get")
@click.argument("activity_id")
@click.pass_context
def get_cmd(ctx: click.Context, activity_id: str) -> None:
    """Get a single activity by ID."""
    ensure_authenticated(ctx.obj["config"])
    raw = get_activity(activity_id)
    data = serialize_activity_summary(raw)
    render_output(ctx.obj["config"].output_format, "activity get", data, COLUMNS_ACTIVITY_SUMMARY)


@activity.command("weather")
@click.argument("activity_id")
@click.pass_context
def weather_cmd(ctx: click.Context, activity_id: str) -> None:
    """Get weather data for an activity."""
    ensure_authenticated(ctx.obj["config"])
    raw = get_activity_weather(activity_id)
    data = [raw] if isinstance(raw, dict) else (raw or [])
    render_output(ctx.obj["config"].output_format, "activity weather", data, COLUMNS_ACTIVITY_WEATHER)
