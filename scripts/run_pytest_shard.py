"""Run a deterministic, coverage-checked subset of the Python test modules."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
SHARDS: dict[str, tuple[str, ...]] = {
    "documents-profile": ("test_document.py", "test_profile.py"),
    "provider-learning": ("test_provider.py", "test_initialization.py", "test_learning.py"),
    "protocol-storage": ("test_protocol.py", "test_storage.py"),
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate and print shard coverage")
    parser.add_argument("--shard", choices=tuple(SHARDS), help="run one complete test-module shard")
    args = parser.parse_args()

    try:
        discovered = validate_shards()
    except ValueError as error:
        parser.error(str(error))

    if args.check:
        for name, files in SHARDS.items():
            print(f"{name}: {len(files)} modules: {', '.join(files)}")
        print(f"Coverage: {len(discovered)} of {len(discovered)} test modules assigned exactly once")
        return 0
    if args.shard is None:
        parser.error("provide --check or --shard")

    paths = [str(TESTS / filename) for filename in SHARDS[args.shard]]
    print(f"Running complete pytest shard: {args.shard}", flush=True)
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *paths], cwd=ROOT, check=False
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
