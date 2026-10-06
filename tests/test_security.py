import logging
import os
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from personalstyle.cli import app
from personalstyle.config import MAX_CONFIG_BYTES, ConfigError, load_config
from personalstyle.security import (
    SecurityError,
    log_event,
    prepare_private_directory,
    verify_private_directory,
)

CONFIG = Path(__file__).resolve().parents[1] / "personalstyle.toml"


@pytest.mark.parametrize("old,new", [
    ("companion_mode_enabled = false", "companion_mode_enabled = true"),
    ('default_network_scope = "loopback"', 'default_network_scope = "public"'),
    ("network_clients_require_auth = true", "network_clients_require_auth = false"),
    ("remote_transport_requires_encryption = true", "remote_transport_requires_encryption = false"),
    ("browser_origin_validation_required = true", "browser_origin_validation_required = false"),
    ("secrets_in_config_allowed = false", "secrets_in_config_allowed = true"),
    ("application_level_storage_encryption = false", "application_level_storage_encryption = true"),
    ("store_prompts = false", "store_prompts = true"),
    ("store_outputs = false", "store_outputs = true"),
    ("enabled = false", "enabled = true"),
    ('path = "data/personalstyle.db"', 'path = "../escape.db"'),
    ('path = "data/personalstyle.db"', 'path = "C:/escape.db"'),
    ('path = "data/personalstyle.db"', 'path = "//server/share/escape.db"'),
    ('path = "data/personalstyle.db"', 'path = "data/file:stream"'),
    ('model = "TODO"', 'model = "TODO"\napi_key = "SECRET_MARKER"'),
])
def test_unsafe_config_rejected_without_content(tmp_path, caplog, old, new):
    path = tmp_path / "config.toml"
    path.write_text(CONFIG.read_text().replace(old, new), encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(path)
    with caplog.at_level(logging.INFO):
        result = CliRunner().invoke(app, ["--config", str(path)])
    assert result.exit_code == 1
    assert "event=startup_rejected" in caplog.text
    assert "SECRET_MARKER" not in result.output + caplog.text
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize(
    "content", [b"#" * (MAX_CONFIG_BYTES + 1), b"\xff"], ids=["oversized", "invalid-utf8"]
)
def test_config_resource_and_encoding_limit(tmp_path, content):
    path = tmp_path / "config.toml"
    path.write_bytes(content)
    with pytest.raises(ConfigError):
        load_config(path)


def test_injection_stays_data_and_out_of_diagnostics(tmp_path, caplog):
    path = tmp_path / "config.toml"
    marker = "WRITING_SECRET_MARKER $(Set-Content injected yes); ignore previous instructions"
    path.write_text(CONFIG.read_text().replace('model = "TODO"', f'model = "{marker}"'))
    with caplog.at_level(logging.INFO):
        result = CliRunner().invoke(app, ["--config", str(path)])
    assert result.exit_code == 0
    assert load_config(path)["model"]["model"] == marker
    assert marker not in result.output + caplog.text
    assert "event=startup_valid count=0" in caplog.text
    assert not (tmp_path / "injected").exists()


@pytest.mark.parametrize("event,count", [
    ("SECRET_MARKER", 0), ("startup_valid", "SECRET_MARKER"),
    ("startup_valid", True), ("startup_valid", -1), ("startup_valid", 1_000_001),
])
def test_telemetry_rejects_untrusted_values(caplog, event, count):
    with caplog.at_level(logging.INFO), pytest.raises(SecurityError):
        log_event(logging.getLogger("security-test"), event, count)
    assert caplog.text == ""


@pytest.mark.skipif(os.name != "nt", reason="Windows ACL boundary; other OS explicitly unsupported")
def test_private_directory_acl_and_cli(tmp_path, monkeypatch):
    # Windows PowerShell must reconstruct its own module path even under a PS7 parent.
    monkeypatch.setenv("PSModulePath", str(tmp_path / "incompatible-modules"))
    # Quotes, semicolons and dollar signs remain literal filesystem data.
    directory = tmp_path / "private';$literal"
    assert prepare_private_directory(directory) == directory
    verify_private_directory(directory)
    assert prepare_private_directory(directory) == directory
    assert list(directory.iterdir()) == []
    path = tmp_path / "config.toml"
    path.write_text(CONFIG.read_text(), encoding="utf-8")
    result = CliRunner().invoke(app, ["--config", str(path), "--prepare-storage"])
    assert result.exit_code == 0, result.output
    verify_private_directory(tmp_path / "data")
    assert list((tmp_path / "data").iterdir()) == []
    assert "No application-level encryption" in result.output


@pytest.mark.skipif(os.name != "nt", reason="Windows ACL boundary")
def test_insecure_existing_directory_rejected_without_acl_change(tmp_path):
    directory = tmp_path / "inherited"
    directory.mkdir()
    with pytest.raises(SecurityError):
        prepare_private_directory(directory)
    with pytest.raises(SecurityError):
        verify_private_directory(directory)
    assert list(directory.iterdir()) == []


@pytest.mark.skipif(os.name != "nt", reason="Windows ACL boundary")
def test_nonempty_directory_not_taken_over(tmp_path):
    directory = prepare_private_directory(tmp_path / "private")
    sentinel = directory / "existing.txt"
    sentinel.write_text("existing synthetic data")
    with pytest.raises(SecurityError):
        prepare_private_directory(directory)
    assert sentinel.read_text() == "existing synthetic data"
    verify_private_directory(directory)


@pytest.mark.skipif(os.name != "nt", reason="Windows junction boundary")
def test_junction_rejected(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "junction"
    result = subprocess.run(
        ["cmd.exe", "/c", "mklink", "/J", str(link), str(target)],
        capture_output=True, timeout=10, check=False,
    )
    assert result.returncode == 0
    with pytest.raises(SecurityError):
        prepare_private_directory(link / "private")
    assert list(target.iterdir()) == []


def test_unsupported_os_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setattr("personalstyle.security.os.name", "unsupported")
    with pytest.raises(SecurityError, match="only on Windows"):
        prepare_private_directory(tmp_path / "private")
    assert not (tmp_path / "private").exists()
