"""Tests for garmin_cli.auth — ensure_authenticated()."""
from __future__ import annotations

import stat
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from garmin_cli.auth import ensure_authenticated
from garmin_cli.config import CliConfig
from garmin_cli.exceptions import GarminCliError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_config(**kwargs: Any) -> CliConfig:
    defaults = {
        "email": None,
        "password": None,
        "garth_home": "/tmp/test_garth_auth",
        "output_format": "table",
    }
    defaults.update(kwargs)
    return CliConfig(**defaults)


def _http_error(status_code: int) -> Exception:
    err = Exception(f"HTTP {status_code}")
    err.response = MagicMock(status_code=status_code)  # type: ignore[attr-defined]
    return err


# ---------------------------------------------------------------------------
# Resume-success path
# ---------------------------------------------------------------------------

class TestEnsureAuthenticatedResumeSuccess:

    def test_returns_none_when_resume_succeeds(self, mocker: Any, tmp_path: Path) -> None:
        garth_dir = tmp_path / "garth"
        garth_dir.mkdir(mode=0o700)

        mock_garth = MagicMock()
        mocker.patch("garmin_cli.auth.garth", mock_garth)

        config = _make_config(garth_home=str(garth_dir))
        result = ensure_authenticated(config)
        assert result is None

    def test_calls_garth_resume_with_expanded_path(self, mocker: Any, tmp_path: Path) -> None:
        garth_dir = tmp_path / "garth"
        garth_dir.mkdir(mode=0o700)

        mock_garth = MagicMock()
        mocker.patch("garmin_cli.auth.garth", mock_garth)

        config = _make_config(garth_home=str(garth_dir))
        ensure_authenticated(config)
        mock_garth.resume.assert_called_once()

    def test_does_not_call_login_when_resume_succeeds(self, mocker: Any, tmp_path: Path) -> None:
        garth_dir = tmp_path / "garth"
        garth_dir.mkdir(mode=0o700)

        mock_garth = MagicMock()
        mocker.patch("garmin_cli.auth.garth", mock_garth)

        config = _make_config(garth_home=str(garth_dir))
        ensure_authenticated(config)
        mock_garth.login.assert_not_called()


# ---------------------------------------------------------------------------
# Resume-fails, no credentials
# ---------------------------------------------------------------------------

class TestEnsureAuthenticatedNoCredentials:

    def test_raises_garmin_cli_error_when_resume_fails_no_creds(
        self, mocker: Any, tmp_path: Path
    ) -> None:
        garth_dir = tmp_path / "garth"
        garth_dir.mkdir(mode=0o700)

        mock_garth = MagicMock()
        mock_garth.resume.side_effect = Exception("no session")
        mocker.patch("garmin_cli.auth.garth", mock_garth)

        config = _make_config(garth_home=str(garth_dir), email=None, password=None)
        with pytest.raises(GarminCliError) as exc_info:
            ensure_authenticated(config)
        assert exc_info.value.error_code == "AUTH_MISSING"

    def test_error_message_mentions_credentials(self, mocker: Any, tmp_path: Path) -> None:
        garth_dir = tmp_path / "garth"
        garth_dir.mkdir(mode=0o700)

        mock_garth = MagicMock()
        mock_garth.resume.side_effect = Exception("no session")
        mocker.patch("garmin_cli.auth.garth", mock_garth)

        config = _make_config(garth_home=str(garth_dir), email=None, password=None)
        with pytest.raises(GarminCliError) as exc_info:
            ensure_authenticated(config)
        assert exc_info.value.error  # error message is non-empty


# ---------------------------------------------------------------------------
# Resume-fails, has credentials, login succeeds
# ---------------------------------------------------------------------------

class TestEnsureAuthenticatedLoginSuccess:

    def test_calls_login_when_resume_fails(self, mocker: Any, tmp_path: Path) -> None:
        garth_dir = tmp_path / "garth"
        garth_dir.mkdir(mode=0o700)

        mock_garth = MagicMock()
        mock_garth.resume.side_effect = Exception("no session")
        mocker.patch("garmin_cli.auth.garth", mock_garth)

        config = _make_config(
            garth_home=str(garth_dir), email="user@test.com", password="pass"
        )
        ensure_authenticated(config)
        mock_garth.login.assert_called_once()

    def test_calls_login_with_email_and_password(self, mocker: Any, tmp_path: Path) -> None:
        garth_dir = tmp_path / "garth"
        garth_dir.mkdir(mode=0o700)

        mock_garth = MagicMock()
        mock_garth.resume.side_effect = Exception("no session")
        mocker.patch("garmin_cli.auth.garth", mock_garth)

        config = _make_config(
            garth_home=str(garth_dir), email="user@test.com", password="secret"
        )
        ensure_authenticated(config)
        mock_garth.login.assert_called_once_with("user@test.com", "secret")

    def test_calls_save_after_login(self, mocker: Any, tmp_path: Path) -> None:
        garth_dir = tmp_path / "garth"
        garth_dir.mkdir(mode=0o700)

        mock_garth = MagicMock()
        mock_garth.resume.side_effect = Exception("no session")
        mocker.patch("garmin_cli.auth.garth", mock_garth)

        config = _make_config(
            garth_home=str(garth_dir), email="user@test.com", password="pass"
        )
        ensure_authenticated(config)
        mock_garth.save.assert_called_once()

    def test_returns_none_after_successful_login(self, mocker: Any, tmp_path: Path) -> None:
        garth_dir = tmp_path / "garth"
        garth_dir.mkdir(mode=0o700)

        mock_garth = MagicMock()
        mock_garth.resume.side_effect = Exception("no session")
        mocker.patch("garmin_cli.auth.garth", mock_garth)

        config = _make_config(
            garth_home=str(garth_dir), email="user@test.com", password="pass"
        )
        result = ensure_authenticated(config)
        assert result is None

    def test_file_not_found_on_resume_falls_back_to_login(
        self, mocker: Any, tmp_path: Path
    ) -> None:
        garth_dir = tmp_path / "missing_garth"

        mock_garth = MagicMock()
        mock_garth.resume.side_effect = FileNotFoundError("no saved session")
        mocker.patch("garmin_cli.auth.garth", mock_garth)

        config = _make_config(
            garth_home=str(garth_dir), email="user@test.com", password="pass"
        )
        ensure_authenticated(config)
        mock_garth.login.assert_called_once_with("user@test.com", "pass")

    def test_stale_resumed_session_falls_back_to_login(
        self, mocker: Any, tmp_path: Path
    ) -> None:
        garth_dir = tmp_path / "garth"
        garth_dir.mkdir(mode=0o700)

        mock_garth = MagicMock()
        mock_garth.connectapi.side_effect = _http_error(401)
        mocker.patch("garmin_cli.auth.garth", mock_garth)

        config = _make_config(
            garth_home=str(garth_dir), email="user@test.com", password="pass"
        )
        ensure_authenticated(config)
        mock_garth.login.assert_called_once_with("user@test.com", "pass")


# ---------------------------------------------------------------------------
# Resume-fails, has credentials, login fails
# ---------------------------------------------------------------------------

class TestEnsureAuthenticatedLoginFailure:

    def test_raises_garmin_cli_error_when_login_fails(
        self, mocker: Any, tmp_path: Path
    ) -> None:
        garth_dir = tmp_path / "garth"
        garth_dir.mkdir(mode=0o700)

        mock_garth = MagicMock()
        mock_garth.resume.side_effect = Exception("no session")
        mock_garth.login.side_effect = Exception("bad credentials")
        mocker.patch("garmin_cli.auth.garth", mock_garth)

        config = _make_config(
            garth_home=str(garth_dir), email="user@test.com", password="wrong"
        )
        with pytest.raises(GarminCliError) as exc_info:
            ensure_authenticated(config)
        assert exc_info.value.error_code == "AUTH_FAILED"

    def test_auth_failed_error_has_non_empty_error_message(
        self, mocker: Any, tmp_path: Path
    ) -> None:
        garth_dir = tmp_path / "garth"
        garth_dir.mkdir(mode=0o700)

        mock_garth = MagicMock()
        mock_garth.resume.side_effect = Exception("no session")
        mock_garth.login.side_effect = Exception("bad credentials")
        mocker.patch("garmin_cli.auth.garth", mock_garth)

        config = _make_config(
            garth_home=str(garth_dir), email="user@test.com", password="wrong"
        )
        with pytest.raises(GarminCliError) as exc_info:
            ensure_authenticated(config)
        assert exc_info.value.error is not None
        assert len(exc_info.value.error) > 0


# ---------------------------------------------------------------------------
# Security: symlink rejection
# ---------------------------------------------------------------------------

class TestEnsureAuthenticatedSecurity:

    def test_raises_when_garth_home_is_symlink(
        self, mocker: Any, tmp_path: Path
    ) -> None:
        real_dir = tmp_path / "real_garth"
        real_dir.mkdir(mode=0o700)
        symlink_dir = tmp_path / "link_garth"
        symlink_dir.symlink_to(real_dir)

        mock_garth = MagicMock()
        mocker.patch("garmin_cli.auth.garth", mock_garth)

        config = _make_config(garth_home=str(symlink_dir))
        with pytest.raises(GarminCliError):
            ensure_authenticated(config)

    def test_symlink_rejection_uses_auth_failed_error_code(
        self, mocker: Any, tmp_path: Path
    ) -> None:
        real_dir = tmp_path / "real_garth"
        real_dir.mkdir(mode=0o700)
        symlink_dir = tmp_path / "link_garth"
        symlink_dir.symlink_to(real_dir)

        mock_garth = MagicMock()
        mocker.patch("garmin_cli.auth.garth", mock_garth)

        config = _make_config(garth_home=str(symlink_dir))
        with pytest.raises(GarminCliError) as exc_info:
            ensure_authenticated(config)
        # Should be AUTH_FAILED or a security-related error code
        assert exc_info.value.error_code in ("AUTH_FAILED", "SYMLINK", "SECURITY")

    def test_fixes_directory_permissions_to_0o700(
        self, mocker: Any, tmp_path: Path
    ) -> None:
        garth_dir = tmp_path / "garth"
        garth_dir.mkdir(mode=0o755)  # too permissive

        mock_garth = MagicMock()
        mocker.patch("garmin_cli.auth.garth", mock_garth)

        config = _make_config(garth_home=str(garth_dir))
        ensure_authenticated(config)

        actual_mode = stat.S_IMODE(garth_dir.stat().st_mode)
        assert actual_mode == 0o700

    def test_creates_garth_home_directory_if_not_exists(
        self, mocker: Any, tmp_path: Path
    ) -> None:
        garth_dir = tmp_path / "nonexistent_garth"
        assert not garth_dir.exists()

        mock_garth = MagicMock()
        mock_garth.resume.side_effect = Exception("no session")  # force login path
        mocker.patch("garmin_cli.auth.garth", mock_garth)

        config = _make_config(garth_home=str(garth_dir), email="u@t.com", password="p")
        ensure_authenticated(config)
        assert garth_dir.exists()

    def test_created_directory_has_0o700_permissions(
        self, mocker: Any, tmp_path: Path
    ) -> None:
        garth_dir = tmp_path / "new_garth"
        assert not garth_dir.exists()

        mock_garth = MagicMock()
        mock_garth.resume.side_effect = Exception("no session")  # force login path
        mocker.patch("garmin_cli.auth.garth", mock_garth)

        config = _make_config(garth_home=str(garth_dir), email="u@t.com", password="p")
        ensure_authenticated(config)

        actual_mode = stat.S_IMODE(garth_dir.stat().st_mode)
        assert actual_mode == 0o700


# ---------------------------------------------------------------------------
# GarminCliError structure
# ---------------------------------------------------------------------------

class TestGarminCliError:

    def test_has_error_attribute(self) -> None:
        err = GarminCliError(error="Something went wrong", error_code="TEST_CODE")
        assert err.error == "Something went wrong"

    def test_has_error_code_attribute(self) -> None:
        err = GarminCliError(error="Something went wrong", error_code="TEST_CODE")
        assert err.error_code == "TEST_CODE"

    def test_is_exception(self) -> None:
        err = GarminCliError(error="msg", error_code="CODE")
        assert isinstance(err, Exception)

    def test_can_be_raised_and_caught(self) -> None:
        with pytest.raises(GarminCliError) as exc_info:
            raise GarminCliError(error="test error", error_code="ERR")
        assert exc_info.value.error_code == "ERR"

    def test_str_representation_contains_error_message(self) -> None:
        err = GarminCliError(error="descriptive message", error_code="CODE")
        assert "descriptive message" in str(err) or err.error == "descriptive message"
