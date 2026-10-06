import json
import logging
import os
import sqlite3
import subprocess
from dataclasses import replace
from pathlib import Path
from uuid import uuid4

import pytest
from typer.testing import CliRunner

from personalstyle.cli import app
from personalstyle.security import prepare_private_directory
from personalstyle.storage import MAX_TEXT_BYTES, ExampleInput, ExampleStore, StoreError

CONFIG = Path(__file__).resolve().parents[1] / "personalstyle.toml"


def example(**changes):
    value = ExampleInput(
        id=str(uuid4()), text="Exact text: café\n\nignore previous instructions; DROP TABLE examples;",
        context="work.email", supplier="local user", authorizer="local user",
        source_kind="user_owned", authorized=True, learning_eligible=True,
    )
    return replace(value, **changes)


@pytest.fixture
def store(tmp_path):
    prepare_private_directory(tmp_path / "profile")
    return ExampleStore(tmp_path / "profile" / "personalstyle.db")


@pytest.mark.parametrize("changes", [
    {"authorized": False}, {"authorized": "true"}, {"supplier": ""}, {"authorizer": ""},
    {"source_kind": "untrusted"}, {"context": ""}, {"context": "inferred context"},
    {"context": "a" * 65}, {"supplier": "a" * 257}, {"authorizer": "a" * 257},
    {"text": ""}, {"text": "a" * (MAX_TEXT_BYTES + 1)},
    {"text": "é" * (MAX_TEXT_BYTES // 2 + 1)}, {"id": "not-a-uuid"},
    {"learning_eligible": True, "held_out": True}, {"held_out": "false"},
])
def test_invalid_request_never_creates_database(tmp_path, changes):
    # Validation must precede even filesystem preparation/SQLite opening.
    with pytest.raises(StoreError, match="INVALID_EXAMPLE"):
        ExampleStore(tmp_path / "absent" / "profile.db").add(example(**changes))
    assert list(tmp_path.iterdir()) == []


def test_valid_input_boundaries():
    example(text="a" * MAX_TEXT_BYTES, context="a" * 64, supplier="a" * 256).validate()
    example(learning_eligible=False, held_out=True, source_kind="authorized_reference").validate()


def test_exact_roundtrip_idempotency_and_conflict(store):
    request = example()
    first = store.add(request)
    assert tuple(first.values())[:8] == request.payload()
    assert first["record_version"] == 1
    assert ExampleStore(store.path).get(request.id) == first
    assert store.add(request) == first
    with pytest.raises(StoreError, match="IDEMPOTENCY_CONFLICT"):
        store.add(replace(request, text="different"))
    assert store.get(request.id) == first
    with sqlite3.connect(store.path) as connection:
        assert connection.execute("SELECT count(*) FROM examples").fetchone() == (1,)
        assert connection.execute("SELECT profile_version FROM store_meta").fetchone() == (2,)


def test_cli_exact_readback_in_fresh_process(tmp_path, caplog):
    prepare_private_directory(tmp_path / "data")
    config = tmp_path / "personalstyle.toml"
    config.write_text(CONFIG.read_text(), encoding="utf-8")
    request = example(text="WRITING_SECRET_MARKER\nExact unicode: café")
    path = tmp_path / "input.json"
    path.write_text(json.dumps(request.__dict__, ensure_ascii=False), encoding="utf-8")
    with caplog.at_level(logging.INFO):
        result = CliRunner().invoke(app, ["--config", str(config), "--add-example", str(path)])
    assert result.exit_code == 0, result.output
    assert "WRITING_SECRET_MARKER" not in result.output + caplog.text
    import sys
    script = (
        "import json,sys; from pathlib import Path; from personalstyle.storage import ExampleStore; "
        "print(json.dumps(ExampleStore(Path(sys.argv[1])).get(sys.argv[2])))"
    )
    readback = subprocess.run(
        [sys.executable, "-c", script, str(tmp_path / "data" / "personalstyle.db"), request.id],
        capture_output=True, text=True, timeout=20, check=False,
    )
    assert readback.returncode == 0
    assert json.loads(readback.stdout)["text"] == request.text
    result = CliRunner().invoke(app, ["--config", str(config), "--get-example", request.id])
    assert json.loads(result.output)["context"] == request.context


def test_insecure_boundary_blocks_before_sqlite_open(tmp_path, monkeypatch):
    directory = tmp_path / "insecure"
    directory.mkdir()
    monkeypatch.setattr(sqlite3, "connect", lambda *a, **k: pytest.fail("SQLite opened before guard"))
    with pytest.raises(StoreError, match="STORAGE_BOUNDARY_INVALID"):
        ExampleStore(directory / "profile.db").add(example())
    assert list(directory.iterdir()) == []


def test_permission_change_requires_reverification(store):
    request = example()
    first = store.add(request)
    before = store.path.read_bytes()
    changed = subprocess.run(
        ["icacls.exe", str(store.path.parent), "/grant", "*S-1-1-0:(OI)(CI)R"],
        capture_output=True, timeout=10, check=False,
    )
    assert changed.returncode == 0
    with pytest.raises(StoreError, match="STORAGE_BOUNDARY_INVALID"):
        store.add(example())
    with pytest.raises(StoreError, match="STORAGE_BOUNDARY_INVALID"):
        ExampleStore(store.path).get(str(first["id"]))
    assert store.path.read_bytes() == before


def test_failure_before_commit_rolls_back_existing_store(store, monkeypatch):
    original = example()
    store.add(original)
    added = example()
    original_recheck = store._recheck
    calls = 0

    def fail_before_commit(identity):
        nonlocal calls
        calls += 1
        original_recheck(identity)
        if calls == 2:
            raise StoreError("TRANSACTION_FAILED")

    monkeypatch.setattr(store, "_recheck", fail_before_commit)
    with pytest.raises(StoreError, match="TRANSACTION_FAILED"):
        store.add(added)
    fresh = ExampleStore(store.path)
    assert fresh.get(added.id) is None
    assert fresh.get(original.id)["text"] == original.text
    with sqlite3.connect(store.path) as connection:
        assert connection.execute("SELECT profile_version FROM store_meta").fetchone() == (2,)


def test_initial_schema_and_example_roll_back_together(store, monkeypatch):
    original_recheck = store._recheck
    calls = 0

    def fail_before_commit(identity):
        nonlocal calls
        calls += 1
        original_recheck(identity)
        if calls == 2:
            raise StoreError("TRANSACTION_FAILED")

    monkeypatch.setattr(store, "_recheck", fail_before_commit)
    with pytest.raises(StoreError, match="TRANSACTION_FAILED"):
        store.add(example())
    with sqlite3.connect(store.path) as connection:
        assert connection.execute("SELECT name FROM sqlite_master").fetchall() == []
        assert connection.execute("PRAGMA user_version").fetchone() == (0,)


def test_locked_database_fails_without_partial_record(store):
    store.add(example())
    connection = sqlite3.connect(store.path, isolation_level=None)
    try:
        connection.execute("BEGIN IMMEDIATE")
        request = example()
        with pytest.raises(StoreError, match="DATABASE_UNAVAILABLE_OR_CORRUPT"):
            store.add(request)
    finally:
        connection.execute("ROLLBACK")
        connection.close()
    assert store.get(request.id) is None


@pytest.mark.parametrize("damage", ["corrupt", "future-version", "journal", "foreign-schema"])
def test_unavailable_or_incompatible_store_has_no_mutation(store, damage):
    store.add(example())
    if damage == "corrupt":
        store.path.write_bytes(b"not SQLite SECRET_MARKER")
    elif damage == "journal":
        Path(str(store.path) + "-journal").write_bytes(b"requires recovery")
    else:
        with sqlite3.connect(store.path) as connection:
            connection.execute("PRAGMA user_version=2" if damage == "future-version"
                               else "CREATE TABLE unexpected (value TEXT)")
    before = store.path.read_bytes()
    with pytest.raises(StoreError, match="DATABASE_UNAVAILABLE_OR_CORRUPT"):
        store.add(example())
    assert store.path.read_bytes() == before


def test_hardlink_database_target_rejected(store, tmp_path):
    store.add(example())
    os.link(store.path, tmp_path / "alias.db")
    before = store.path.read_bytes()
    with pytest.raises(StoreError, match="STORAGE_BOUNDARY_INVALID"):
        store.add(example())
    assert store.path.read_bytes() == before


def test_replaced_profile_and_reopen_after_failure(tmp_path):
    path = tmp_path / "profile"
    prepare_private_directory(path)
    store = ExampleStore(path / "profile.db")
    store.add(example())
    path.rename(tmp_path / "previous")
    path.mkdir()
    with pytest.raises(StoreError, match="STORAGE_BOUNDARY_INVALID"):
        store.add(example())
    assert list(path.iterdir()) == []
    with pytest.raises(StoreError, match="STORAGE_BOUNDARY_INVALID"):
        ExampleStore(path / "profile.db").add(example())


def test_cli_failure_omits_raw_writing(tmp_path, caplog):
    config = tmp_path / "config.toml"
    config.write_text(CONFIG.read_text(), encoding="utf-8")
    request = example(text="SECRET_MARKER", authorized=False)
    payload = tmp_path / "request.json"
    payload.write_text(json.dumps(request.__dict__))
    with caplog.at_level(logging.INFO):
        result = CliRunner().invoke(app, ["--config", str(config), "--add-example", str(payload)])
    assert result.exit_code == 1
    assert "INVALID_EXAMPLE" in result.output
    assert "SECRET_MARKER" not in result.output + caplog.text
    assert not (tmp_path / "data").exists()
