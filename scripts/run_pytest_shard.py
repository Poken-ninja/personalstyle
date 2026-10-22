"""Run coverage-checked pytest shards or focused tests with safe diagnostics."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
RUN_ROOT = ROOT / ".pytest-harness"
PROTOCOL_STORAGE = (
    "test_protocol.py", "test_storage.py", "test_harness.py", "test_voice_evidence.py"
)
SHARDS: dict[str, tuple[str, ...]] = {
    "documents-profile": ("test_document.py", "test_documents.py", "test_profile.py"),
    "provider-learning": ("test_provider.py", "test_initialization.py", "test_learning.py"),
    "protocol-storage": tuple(PROTOCOL_STORAGE),
    "feedback-security": (
        "test_feedback.py", "test_security.py", "test_generation.py", "test_verification.py"
    ),
}


def validate_shards() -> list[str]:
    discovered = {path.name for path in TESTS.glob("test_*.py")}
    assigned = [name for files in SHARDS.values() for name in files]
    duplicates = sorted({name for name in assigned if assigned.count(name) > 1})
    missing = sorted(discovered - set(assigned))
    nonexistent = sorted(set(assigned) - discovered)
    if duplicates or missing or nonexistent:
        raise ValueError(
            f"invalid pytest shard map: duplicates={duplicates}, "
            f"missing={missing}, nonexistent={nonexistent}"
        )
    return sorted(discovered)


def _allocate_run() -> tuple[str, Path, Path, Path]:
    """Create and verify a unique workspace-local temp and diagnostics directory."""
    root = ROOT.resolve(strict=True)
    try:
        metadata = RUN_ROOT.lstat()
    except FileNotFoundError:
        metadata = None
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    if metadata is not None and (
        stat.S_ISLNK(metadata.st_mode)
        or bool(getattr(metadata, "st_file_attributes", 0) & reparse_flag)
    ):
        raise OSError("pytest diagnostic root cannot be a link")
    RUN_ROOT.mkdir(exist_ok=True)
    resolved_run_root = RUN_ROOT.resolve(strict=True)
    if resolved_run_root != root / ".pytest-harness":
        raise OSError("pytest diagnostic root escaped the repository")

    run_id = uuid4().hex
    run_dir = resolved_run_root / run_id
    run_dir.mkdir(exist_ok=False)
    temp_dir = run_dir / "tmp"
    temp_dir.mkdir()
    probe = temp_dir / ".write-check"
    with probe.open("x", encoding="ascii") as stream:
        stream.write("writable")
        stream.flush()
        os.fsync(stream.fileno())
    probe.unlink()
    report = run_dir / "outcomes.jsonl"
    return run_id, run_dir, temp_dir, report


def _revision() -> str:
    configured = os.environ.get("GITHUB_SHA", "")
    if re.fullmatch(r"[0-9a-fA-F]{7,40}", configured):
        return configured.lower()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short=12", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    value = result.stdout.strip().lower()
    return value if result.returncode == 0 and re.fullmatch(r"[0-9a-f]{7,40}", value) else "unknown"


def _worktree_state() -> str:
    try:
        result = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--"],
            cwd=ROOT,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    return {0: "clean", 1: "dirty"}.get(result.returncode, "unknown")


def _valid_focus(selector: str) -> bool:
    normalized = selector.replace("\\", "/")
    return (
        normalized.startswith("tests/")
        and not normalized.startswith("-")
        and ".." not in normalized.split("/")
    )


def _pytest_command(selectors: list[str], temp_dir: Path, fail_fast: bool) -> list[str]:
    return [
        sys.executable,
        "-m",
        "pytest",
        "-p",
        "scripts.pytest_diagnostics",
        "-q",
        "--tb=short",
        f"--basetemp={temp_dir}",
        *(["--maxfail=1"] if fail_fast else []),
        *selectors,
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", action="store_true", help="validate and print shard coverage")
    modes.add_argument("--shard", choices=tuple(SHARDS), help="run one complete test-module shard")
    modes.add_argument(
        "--focus", action="append", default=[], metavar="NODEID",
        help="run one focused tests/... nodeid (repeatable)",
    )
    parser.add_argument(
        "--fail-fast", action="store_true",
        help="stop a diagnostic run after its first failed test; never used by CI acceptance",
    )
    args = parser.parse_args()

    try:
        discovered = validate_shards()
    except ValueError as error:
        parser.error(str(error))

    if args.check:
        if args.fail_fast:
            parser.error("--fail-fast applies only to a test run")
        for name, files in SHARDS.items():
            print(f"{name}: {len(files)} modules: {', '.join(files)}")
        print(f"Coverage: {len(discovered)} of {len(discovered)} test modules assigned exactly once")
        return 0
    if args.shard is None and not args.focus:
        parser.error("provide --check, --shard, or at least one --focus")
    if args.focus and not all(_valid_focus(item) for item in args.focus):
        parser.error("focused selectors must be relative tests/... nodeids without parent traversal")

    try:
        run_id, run_dir, temp_dir, report_file = _allocate_run()
    except OSError:
        print("H01_RUN outcome=temp_root_unavailable", flush=True)
        return 2
    shard = args.shard or "focused"
    env = os.environ.copy()
    env.update({
        "PERSONALSTYLE_TEST_REPORT_FILE": str(report_file),
        "PERSONALSTYLE_TEST_SHARD": shard,
        "PERSONALSTYLE_TEST_REVISION": _revision(),
        "PERSONALSTYLE_TEST_WORKTREE": _worktree_state(),
        "PERSONALSTYLE_TEST_RUN_ID": run_id,
    })
    selectors = (
        [str(TESTS / filename) for filename in SHARDS[args.shard]]
        if args.shard is not None else args.focus
    )
    command = _pytest_command(selectors, temp_dir, args.fail_fast)
    print(
        f"H01_RUN id={run_id} shard={shard} revision={env['PERSONALSTYLE_TEST_REVISION']} "
        f"worktree={env['PERSONALSTYLE_TEST_WORKTREE']}",
        flush=True,
    )
    try:
        result = subprocess.run(command, cwd=ROOT, env=env, check=False)
    except (OSError, subprocess.SubprocessError):
        print(f"H01_RUN id={run_id} outcome=runner_launch_failure", flush=True)
        print(f"H01_REPORT id={run_id} file=.pytest-harness/{run_id}/outcomes.jsonl", flush=True)
        return 2

    if result.returncode == 0:
        try:
            shutil.rmtree(run_dir)
        except OSError:
            print(f"H01_CLEANUP id={run_id} outcome=retained", flush=True)
        print(f"H01_RUN id={run_id} outcome=passed", flush=True)
    else:
        print(f"H01_RUN id={run_id} outcome=failed exit={result.returncode}", flush=True)
        print(f"H01_REPORT id={run_id} file=.pytest-harness/{run_id}/outcomes.jsonl", flush=True)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
