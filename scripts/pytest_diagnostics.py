"""Write sanitized pytest phase records and a slow-test summary for the shard runner."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import pytest


def _safe_identity(nodeid: str) -> tuple[str, str]:
    module_path, separator, test_name = nodeid.partition("::")
    module = Path(module_path.replace("\\", "/")).name.removesuffix(".py")
    name = test_name.split("[", 1)[0] if separator else "collection"
    return module[:80], name[:120]


def _exception_chain(error: BaseException | None):
    seen: set[int] = set()
    current = error
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        yield current
        current = current.__cause__ or current.__context__


def _failure_category(error: BaseException | None) -> str:
    """Return fixed labels only; never serialize exception text or paths."""
    for current in _exception_chain(error):
        if type(current).__name__ != "SecurityError":
            continue
        message = str(current)
        cause = current.__cause__ or current.__context__
        if message == "OS permission verification unavailable":
            if isinstance(cause, subprocess.TimeoutExpired):
                return "acl_subprocess_timeout"
            if isinstance(cause, OSError):
                return "acl_subprocess_launch_failure"
            return "acl_subprocess_failure_unknown"
        if message == "Private profile permissions could not be verified":
            return "acl_protection_mismatch"
    return "test_failure"


class SanitizedPytestDiagnostics:
    """Persist safe phase records immediately, including before a bounded interruption."""

    def __init__(self) -> None:
        report_value = os.environ.get("PERSONALSTYLE_TEST_REPORT_FILE", "")
        self.report_file = Path(report_value) if report_value else None
        shard = os.environ.get("PERSONALSTYLE_TEST_SHARD", "unknown")
        revision = os.environ.get("PERSONALSTYLE_TEST_REVISION", "unknown")
        worktree = os.environ.get("PERSONALSTYLE_TEST_WORKTREE", "unknown")
        run_id = os.environ.get("PERSONALSTYLE_TEST_RUN_ID", "unknown")
        self.shard = shard if re.fullmatch(r"[a-z0-9-]{1,40}", shard) else "unknown"
        self.revision = revision if re.fullmatch(r"[0-9a-f]{7,40}", revision) else "unknown"
        self.worktree = worktree if worktree in {"clean", "dirty", "unknown"} else "unknown"
        self.run_id = run_id if re.fullmatch(r"[0-9a-f]{32}", run_id) else "unknown"
        self.durations: dict[tuple[str, str], float] = defaultdict(float)
        self.events_written = 0
        self.report_limit_notified = False

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item: Any, call: Any):
        """Record setup/call/teardown separately so partial runs retain completed work."""
        outcome = yield
        report = outcome.get_result()
        exception = call.excinfo.value if report.failed and call.excinfo is not None else None
        self.record_report(report, exception)

    def record_report(self, report: Any, exception: BaseException | None) -> None:
        module, test = _safe_identity(report.nodeid)
        event: dict[str, str | int] = {
            "module": module,
            "test": test,
            "phase": report.when,
            "outcome": report.outcome,
            "duration_ms": max(0, round(report.duration * 1000)),
            "shard": self.shard,
            "revision": self.revision,
            "worktree": self.worktree,
            "run_id": self.run_id,
        }
        if exception is not None:
            event["failure_category"] = _failure_category(exception)
        self.durations[(module, test)] += report.duration
        self._record(event)

    def _record(self, event: dict[str, str | int]) -> None:
        if self.events_written >= 20_000:
            if not self.report_limit_notified:
                self.report_limit_notified = True
                self._emit("H01_TEST_REPORT_LIMIT reached=20000")
            return
        self.events_written += 1
        line = json.dumps(event, sort_keys=True, separators=(",", ":"))
        if self.report_file is not None:
            with self.report_file.open("a", encoding="utf-8", newline="\n") as stream:
                stream.write(line + "\n")
                stream.flush()
        # Bypass per-test capture so GitHub retains completed outcomes if the job is killed.
        self._emit(f"H01_TEST {line}")

    def _emit(self, line: str) -> None:
        output = getattr(sys, "__stdout__", None)
        if output is not None:
            output.write(f"{line}\n")
            output.flush()
        else:
            terminal = getattr(self, "_terminal", None)
            if terminal is None:
                return
            terminal.write_line(line)
            terminal._tw.flush()

    def pytest_configure(self, config: Any) -> None:
        self._terminal = config.pluginmanager.get_plugin("terminalreporter")

    def pytest_sessionfinish(self, session: Any, exitstatus: int) -> None:
        del session, exitstatus
        slowest = sorted(self.durations.items(), key=lambda pair: pair[1], reverse=True)[:10]
        for (module, test), duration in slowest:
            event = {
                "module": module,
                "test": test,
                "duration_ms": round(duration * 1000),
                "shard": self.shard,
                "revision": self.revision,
                "worktree": self.worktree,
                "run_id": self.run_id,
            }
            self._record({"slowest_test": f"{module}::{test}", **event})


def pytest_configure(config: Any) -> None:
    config.pluginmanager.register(SanitizedPytestDiagnostics(), "personalstyle-sanitized-diagnostics")
