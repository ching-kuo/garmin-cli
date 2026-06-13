"""Serializers for device-domain Garmin Connect payloads."""
from __future__ import annotations

from typing import Any

from garmin_cli.metrics import FieldEntry, FieldTable, validate_table_coverage
from garmin_cli.serializers._common import _listify

COLUMNS_DEVICE = ("device_id", "display_name", "device_type", "last_sync_time")


_DEVICE_TABLE = FieldTable(
    name="device",
    columns=COLUMNS_DEVICE,
    entries=(
        FieldEntry("device_id", (("deviceId",),)),
        FieldEntry("display_name", (("displayName",),)),
        FieldEntry("device_type", (("deviceTypeName",),)),
        FieldEntry("last_sync_time", (("lastSyncTime",),)),
    ),
)


def serialize_device(raw: Any) -> list[dict[str, Any]]:
    return _DEVICE_TABLE.project_all(_listify(raw))


validate_table_coverage(
    "device",
    {"COLUMNS_DEVICE": COLUMNS_DEVICE},
    (_DEVICE_TABLE,),
)
