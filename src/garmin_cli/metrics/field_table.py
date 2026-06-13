"""Domain-agnostic declarative field tables for flat per-row serializers.

This is the generalization of the activity :class:`~garmin_cli.metrics.registry.MetricEntry`
pattern to domains whose rows are *flat* projections of a single wire dict
(health, performance, devices). Those rows have no sport applicability and no
``summaryDTO`` split, so they need a slimmer primitive than ``MetricEntry``:

* :class:`FieldEntry` -- one output column: its ``key``, the precedence-ordered
  ``source_paths`` to try on the wire item, and an optional ``converter``
  applied only to a non-None resolved value (mirrors ``MetricEntry.formatter``).
* :func:`project_row` -- resolve every entry against one wire item, producing a
  row dict whose key set is exactly the table's keys (insertion order matches
  declaration order, so JSON-envelope key order is preserved).
* :class:`FieldTable` -- bundles a ``columns`` tuple with its entries and
  validates at construction that the two never drift apart (the per-domain
  analogue of ``_validate_registry_coverage``).

``MetricEntry`` deliberately stays separate: it carries activity-only state
(``sports``) and is resolved by the summaryDTO-aware
:func:`~garmin_cli.metrics.registry.resolve`. Sharing this slim base with it
would force one of those two concerns onto the other domain. The precedence
walk semantics are identical, however, so behaviour stays consistent.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Mapping


@dataclass(frozen=True)
class FieldEntry:
    """Declarative definition of a single flat output field.

    ``key`` is the serializer output key (e.g. ``resting_hr``); Garmin wire
    names live only inside ``source_paths``, each a tuple of nested dict keys
    tried in declared precedence. ``converter`` is applied only when the
    resolved value is not None (None-in/None-out unit transforms).
    """

    key: str
    source_paths: tuple[tuple[str, ...], ...]
    converter: Callable[[Any], Any] | None = None


def _walk(value: Any, path: tuple[str, ...]) -> Any:
    current: Any = value
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def resolve_field(entry: FieldEntry, item: dict[str, Any]) -> Any:
    """Resolve one :class:`FieldEntry` against a wire ``item``.

    Walks ``entry.source_paths`` in declared precedence and returns the first
    non-None value, applying ``entry.converter`` to it when present. Returns
    None when no path resolves (the converter is never called with None, so a
    field that is simply absent stays None rather than a converted-None).
    """
    for path in entry.source_paths:
        value = _walk(item, path)
        if value is not None:
            return entry.converter(value) if entry.converter else value
    return None


def project_row(
    item: dict[str, Any],
    entries: tuple[FieldEntry, ...],
) -> dict[str, Any]:
    """Project one wire ``item`` into a row dict over ``entries``.

    The resulting dict has exactly one key per entry, inserted in declaration
    order so that JSON-envelope key ordering matches the legacy hand-written
    serializers byte-for-byte.
    """
    return {entry.key: resolve_field(entry, item) for entry in entries}


@dataclass(frozen=True)
class FieldTable:
    """A named bundle of :class:`FieldEntry` rows plus its column order.

    ``columns`` is the published CSV/table header order; ``entries`` declares
    how each column is resolved. The two are validated to be in lockstep at
    construction (see :meth:`__post_init__`) so a column can never be added to
    the header without a resolver, nor a resolver emit a key absent from the
    header. This is the per-domain analogue of ``_validate_registry_coverage``.
    """

    name: str
    columns: tuple[str, ...]
    entries: tuple[FieldEntry, ...]

    _by_key: dict[str, FieldEntry] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        entry_keys = tuple(entry.key for entry in self.entries)
        if entry_keys != self.columns:
            raise RuntimeError(
                f"FieldTable {self.name!r} columns/entries drift: "
                f"columns={self.columns!r} entry_keys={entry_keys!r}"
            )
        # ``frozen=True`` blocks normal attribute assignment.
        object.__setattr__(
            self, "_by_key", {entry.key: entry for entry in self.entries}
        )

    def project(self, item: dict[str, Any]) -> dict[str, Any]:
        """Project a single wire ``item`` into a row over this table's entries."""
        return project_row(item, self.entries)

    def project_all(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Project a list of wire items into one row each (order preserved)."""
        return [self.project(item) for item in items]


def validate_table_coverage(
    domain: str,
    column_constants: Mapping[str, tuple[str, ...]],
    tables: Iterable[FieldTable],
    *,
    exempt: frozenset[str] = frozenset(),
) -> None:
    """Assert a domain's ``COLUMNS_*`` constants stay in lockstep with its tables.

    The cross-domain analogue of ``_validate_registry_coverage``. Each
    :class:`FieldTable` already guarantees ``entries`` match ``columns`` at
    construction; this guards the *other* drift direction: a published column
    constant that no table backs (e.g. a ``COLUMNS_FOO`` added with a bespoke
    hand-written serializer that silently bypasses the declarative path).

    ``column_constants`` maps a constant's name to its tuple value (typically
    every module global named ``COLUMNS_*``); ``tables`` is the module's declared
    tables. ``exempt`` lists constant names that intentionally have no table
    because their serializer is structural (e.g. fan-out / cross-item merge).
    Raises :class:`RuntimeError` on the first inconsistency found.
    """
    covered: dict[tuple[str, ...], FieldTable] = {}
    for table in tables:
        covered[table.columns] = table
    for const_name, columns in column_constants.items():
        if const_name in exempt:
            continue
        if columns not in covered:
            raise RuntimeError(
                f"{domain} column constant {const_name!r} has no backing "
                f"FieldTable (columns={columns!r}); declare a table or add it "
                f"to the structural exemption set"
            )
