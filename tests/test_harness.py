"""Focused checks for coverage, safe temp roots, and sanitized pytest diagnostics."""

import io
import json
import subprocess
from types import SimpleNamespace

import pytest

from personalstyle.security import SecurityError
from personalstyle.storage import StoreError
from scripts import pytest_diagnostics
from scripts import run_pytest_shard as runner


def test_shard_map_assigns_every_test_module_once():
    discovered = set(runner.validate_shards())
    assigned = [name for files in runner.SHARDS.values() for name in files]
    assert len(assigned) == len(set(assigned))
    assert set(assigned) == discovered
    assert "test_harness.py" in runner.SHARDS["protocol-storage"]


def test_runner_allocates_unique_verified_writable_temp_roots(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "RUN_ROOT", tmp_path / ".pytest-harness")

    first = runner._allocate_run()
    second = runner._allocate_run()

    assert first[0] != second[0]
    for _, run_dir, temp_dir, report in (first, second):
        assert run_dir.parent == tmp_path / ".pytest-harness"
        assert temp_dir.is_dir()
        assert not (temp_dir / ".write-check").exists()
        assert report.parent == run_dir
        assert temp_dir.resolve().is_relative_to(tmp_path.resolve())


def test_runner_rejects_unwritable_temp_root_without_exposing_path(tmp_path, monkeypatch):
    root_file = tmp_path / ".pytest-harness"
    root_file.write_text("not a directory", encoding="utf-8")
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "RUN_ROOT", root_file)

    with pytest.raises(OSError):
        runner._allocate_run()


def test_focus_is_limited_to_test_tree_and_fail_fast_is_diagnostic_only(tmp_path):
    assert runner._valid_focus("tests/test_storage.py::test_boundary")
    assert not runner._valid_focus("--pyargs personalstyle")
    assert not runner._valid_focus("tests/../personalstyle/config.py")

    command = runner._pytest_command(["tests/test_harness.py"], tmp_path / "tmp", True)
    assert "--maxfail=1" in command
    acceptance_command = runner._pytest_command(["tests/test_harness.py"], tmp_path / "tmp", False)
    assert "--maxfail=1" not in acceptance_command


def test_safe_test_identity_drops_parameter_values():
    assert pytest_diagnostics._safe_identity(
        "tests/test_profile.py::test_example[PRIVATE_WRITING_MARKER]"
    ) == ("test_profile", "test_example")


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (subprocess.TimeoutExpired("powershell.exe", 10), "acl_subprocess_timeout"),
        (FileNotFoundError("PRIVATE_PATH"), "acl_subprocess_launch_failure"),
        (None, "acl_protection_mismatch"),
    ],
)
def test_acl_failure_categories_are_distinct_and_sanitized(error, expected):
    if error is None:
        boundary_error = SecurityError("Private profile permissions could not be verified")
    else:
        try:
            raise SecurityError("OS permission verification unavailable") from error
        except SecurityError as caught:
            boundary_error = caught
    try:
        raise boundary_error
    except SecurityError:
        try:
            raise StoreError("STORAGE_BOUNDARY_INVALID") from None
        except StoreError as wrapped:
            failure = wrapped
    assert pytest_diagnostics._failure_category(failure) == expected


def test_progress_record_is_machine_readable_and_omits_parameters_and_exception_text(
    tmp_path, monkeypatch
):
    report_path = tmp_path / "outcomes.jsonl"
    monkeypatch.setenv("PERSONALSTYLE_TEST_REPORT_FILE", str(report_path))
    monkeypatch.setenv("PERSONALSTYLE_TEST_SHARD", "protocol-storage")
    monkeypatch.setenv("PERSONALSTYLE_TEST_REVISION", "0123456789ab")
    monkeypatch.setenv("PERSONALSTYLE_TEST_WORKTREE", "dirty")
    monkeypatch.setenv("PERSONALSTYLE_TEST_RUN_ID", "a" * 32)
    plugin = pytest_diagnostics.SanitizedPytestDiagnostics()
    output = io.StringIO()
    monkeypatch.setattr(pytest_diagnostics.sys, "__stdout__", output)
    report = SimpleNamespace(
        nodeid="tests/test_harness.py::test_secret[PRIVATE_WRITING_MARKER]",
        when="call",
        outcome="failed",
        duration=0.125,
    )

    plugin.record_report(report, ValueError("PRIVATE_EXCEPTION_TEXT"))

    encoded = report_path.read_text(encoding="utf-8")
    event = json.loads(encoded)
    assert event == {
        "duration_ms": 125,
        "failure_category": "test_failure",
        "module": "test_harness",
        "outcome": "failed",
        "phase": "call",
        "revision": "0123456789ab",
        "run_id": "a" * 32,
        "shard": "protocol-storage",
        "test": "test_secret",
        "worktree": "dirty",
    }
    assert "PRIVATE_" not in encoded
    assert "PRIVATE_" not in output.getvalue()
    assert output.getvalue().startswith("H01_TEST {")
