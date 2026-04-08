"""Activity commands."""
from __future__ import annotations

import click

from garmin_cli.auth import ensure_authenticated
from garmin_cli.endpoints.activities import (
    get_activity,
    get_activity_weather,
    get_multisport_children,
    is_multisport_parent,
    list_activities,
)
from garmin_cli.output import echo_csv, echo_json, echo_table, make_envelope, render_output
from garmin_cli.serializers import (
    COLUMNS_ACTIVITY_SUMMARY,
    COLUMNS_ACTIVITY_WEATHER,
    COLUMNS_MULTISPORT_CHILDREN,
    serialize_activity_summary,
    serialize_multisport_children,
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
    """Get a single activity by ID. For multisport activities, shows each child sport."""
    ensure_authenticated(ctx.obj["config"])
    raw = get_activity(activity_id)
    fmt = ctx.obj["config"].output_format
    data = serialize_activity_summary(raw)

    child_data: list[dict] = []
    if is_multisport_parent(raw):
        children = get_multisport_children(raw)
        if children:
            child_data = serialize_multisport_children(children)

    if fmt == "json":
        envelope = make_envelope(command="activity get", data=data)
        if child_data:
            envelope["children"] = child_data
        echo_json(envelope)
    elif fmt == "table":
        echo_table(data, COLUMNS_ACTIVITY_SUMMARY)
        if child_data:
            click.echo("")
            click.echo("Child activities:")
            echo_table(child_data, COLUMNS_MULTISPORT_CHILDREN)
    else:
        if child_data:
            echo_csv(child_data, COLUMNS_MULTISPORT_CHILDREN)
        else:
            echo_csv(data, COLUMNS_ACTIVITY_SUMMARY)


@activity.command("weather")
@click.argument("activity_id")
@click.pass_context
def weather_cmd(ctx: click.Context, activity_id: str) -> None:
    """Get weather data for an activity."""
    ensure_authenticated(ctx.obj["config"])
    raw = get_activity_weather(activity_id)
    data = [raw] if isinstance(raw, dict) else (raw or [])
    render_output(ctx.obj["config"].output_format, "activity weather", data, COLUMNS_ACTIVITY_WEATHER)
