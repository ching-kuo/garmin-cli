"""Health data commands."""
from __future__ import annotations

from datetime import datetime

import click

from garmin_cli.auth import ensure_authenticated
from garmin_cli.date_utils import resolve_date_range
from garmin_cli.endpoints.health import get_hrv, get_sleep, get_weight
from garmin_cli.output import render_output
from garmin_cli.serializers import (
    COLUMNS_HRV,
    COLUMNS_SLEEP,
    COLUMNS_WEIGHT,
    serialize_hrv,
    serialize_sleep,
    serialize_weight,
)

_DATE_TYPE = click.DateTime(formats=["%Y-%m-%d"])


@click.group()
def health() -> None:
    """Health data commands."""


@health.command()
@click.option("--date", "value_date", type=_DATE_TYPE, default=None)
@click.option("--days", type=int)
@click.option("--ahead", type=int)
@click.option("--from", "date_from", type=_DATE_TYPE, default=None)
@click.option("--to", "date_to", type=_DATE_TYPE, default=None)
@click.pass_context
def sleep(
    ctx: click.Context,
    value_date: datetime | None,
    days: int | None,
    ahead: int | None,
    date_from: datetime | None,
    date_to: datetime | None,
) -> None:
    """Get sleep data."""
    start, end = resolve_date_range(
        date_=value_date.date() if value_date else None,
        from_date=date_from.date() if date_from else None,
        to_date=date_to.date() if date_to else None,
        days=days,
        ahead=ahead,
    )
    ensure_authenticated(ctx.obj["config"])
    data = serialize_sleep(get_sleep(start, end))
    render_output(
        ctx.obj["config"].output_format,
        "health sleep",
        data,
        COLUMNS_SLEEP,
        date_range=(start, end),
    )


@health.command()
@click.option("--date", "value_date", type=_DATE_TYPE, default=None)
@click.option("--days", type=int)
@click.option("--from", "date_from", type=_DATE_TYPE, default=None)
@click.option("--to", "date_to", type=_DATE_TYPE, default=None)
@click.pass_context
def hrv(
    ctx: click.Context,
    value_date: datetime | None,
    days: int | None,
    date_from: datetime | None,
    date_to: datetime | None,
) -> None:
    """Get HRV data."""
    start, end = resolve_date_range(
        date_=value_date.date() if value_date else None,
        from_date=date_from.date() if date_from else None,
        to_date=date_to.date() if date_to else None,
        days=days,
        ahead=None,
    )
    ensure_authenticated(ctx.obj["config"])
    data = serialize_hrv(get_hrv(start, end))
    render_output(
        ctx.obj["config"].output_format,
        "health hrv",
        data,
        COLUMNS_HRV,
        date_range=(start, end),
    )


@health.command()
@click.option("--date", "value_date", type=_DATE_TYPE, default=None)
@click.option("--days", type=int)
@click.option("--from", "date_from", type=_DATE_TYPE, default=None)
@click.option("--to", "date_to", type=_DATE_TYPE, default=None)
@click.pass_context
def weight(
    ctx: click.Context,
    value_date: datetime | None,
    days: int | None,
    date_from: datetime | None,
    date_to: datetime | None,
) -> None:
    """Get weight data."""
    start, end = resolve_date_range(
        date_=value_date.date() if value_date else None,
        from_date=date_from.date() if date_from else None,
        to_date=date_to.date() if date_to else None,
        days=days,
        ahead=None,
    )
    ensure_authenticated(ctx.obj["config"])
    data = serialize_weight(get_weight(start, end))
    render_output(
        ctx.obj["config"].output_format,
        "health weight",
        data,
        COLUMNS_WEIGHT,
        date_range=(start, end),
    )
