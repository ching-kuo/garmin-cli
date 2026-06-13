"""Tests for packaging metadata."""
from __future__ import annotations

from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    import tomli as tomllib


def test_pyproject_package_discovery_src_only() -> None:
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    config = tomllib.loads(pyproject.read_text())

    find_config = config["tool"]["setuptools"]["packages"]["find"]
    where = set(find_config.get("where", []))
    include = set(find_config.get("include", []))

    assert where == {"src"}, f"Expected where={{'src'}}, got {where!r}"
    assert "." not in where, "Root '.' must not be in 'where' (shadow package removed)"
    assert "garmin_cli*" in include, "'garmin_cli*' must be in include"
    assert "garmin*" not in include, "'garmin*' must not be in include (shadow package removed)"


def test_runtime_version_matches_pyproject() -> None:
    """__version__ derives from installed metadata, so it must equal the
    single source of truth in pyproject.toml -- guards against the drift that
    left it pinned at 1.2.0 through several releases."""
    from garmin_cli import __version__

    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    declared = tomllib.loads(pyproject.read_text())["project"]["version"]
    assert __version__ == declared, (
        f"garmin_cli.__version__={__version__!r} != pyproject version={declared!r}; "
        "reinstall the package (pip install -e .) to refresh metadata"
    )
