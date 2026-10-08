import re
import tomllib
from pathlib import Path

import pytest
from typer.testing import CliRunner

from personalstyle.cli import app
from personalstyle.config import ConfigError, load_config

CONFIG = Path(__file__).resolve().parents[1] / "personalstyle.toml"


def test_current_configuration_preserved():
    with CONFIG.open("rb") as stream:
        expected = tomllib.load(stream)
    assert load_config(CONFIG) == expected
    assert expected["versions"] == {
        "protocol": "1.0", "config_schema": 1, "storage_schema": 1,
        "profile_schema": 1, "prompt_contract": 1,
        "compatibility_policy": "same-major-capability-negotiated",
    }
    assert expected["harness"] == {
        "max_generation_attempts": 3, "max_total_model_calls": 8, "timeout_seconds": 60,
    }
    assert expected["security"]["companion_mode_enabled"] is False
    assert expected["logging"]["store_prompts"] is False
    assert expected["logging"]["store_outputs"] is False


def test_cli_help_and_startup_without_model(tmp_path, monkeypatch):
    path = tmp_path / "config.toml"
    path.write_text(re.sub(r'(?m)^model = .*$', 'model = "TODO"', CONFIG.read_text()))
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    assert runner.invoke(app, ["--help"]).exit_code == 0
    result = runner.invoke(app, ["--config", str(path)])
    assert result.exit_code == 0, result.output
    assert "model is TODO" in result.output
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize("old,new", [
    ("config_schema = 1", "config_schema = 2"),
    ("storage_schema = 1", "storage_schema = 2"),
    ("profile_schema = 1", "profile_schema = 2"),
    ("prompt_contract = 1", "prompt_contract = 2"),
    ('protocol = "1.0"', 'protocol = "2.0"'),
    ("max_generation_attempts = 3", "max_generation_attempts = 0"),
    ("max_total_model_calls = 8", "max_total_model_calls = true"),
    ("timeout_seconds = 60", "timeout_seconds = 0"),
    ("explicit_context_required = true", 'explicit_context_required = "true"'),
    ("max_examples = 5", ""),
])
def test_invalid_configuration_rejected(tmp_path, old, new):
    path = tmp_path / "invalid.toml"
    path.write_text(CONFIG.read_text().replace(old, new), encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(path)
    assert CliRunner().invoke(app, ["--config", str(path)]).exit_code == 1


def test_missing_and_malformed_configuration(tmp_path):
    path = tmp_path / "config.toml"
    with pytest.raises(ConfigError):
        load_config(path)
    path.write_text('secret-content = [', encoding="utf-8")
    result = CliRunner().invoke(app, ["--config", str(path)])
    assert result.exit_code == 1
    assert "secret-content" not in result.output
