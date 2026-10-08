import hashlib
import json
import logging
import os
import sqlite3
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from uuid import UUID

import pytest
from typer.testing import CliRunner

from personalstyle import profile
from personalstyle.cli import app
from personalstyle.profile import derive_writing_dna
from personalstyle.security import SecurityError, prepare_private_directory
from personalstyle.storage import ExampleInput, ExampleStore, StoreError

CONFIG = Path(__file__).resolve().parents[1] / "personalstyle.toml"


def example(number=1, **changes):
    value = ExampleInput(
        id=str(UUID(int=number)), text="Hello there. Bye!", context="work.email",
        supplier="local user", authorizer="local user", source_kind="user_owned",
        authorized=True, learning_eligible=True,
    )
    return replace(value, **changes)


@pytest.fixture
def store(tmp_path):
    prepare_private_directory(tmp_path / "data")
    return ExampleStore(tmp_path / "data" / "personalstyle.db")


def test_exact_context_isolation_eligibility_and_deterministic_updates(store):
    first = example()
    store.add(first)
    initial = derive_writing_dna(store, "work.email")
    assert initial == derive_writing_dna(store, "work.email")
    assert initial["source_fingerprint"] == hashlib.sha256(
        f"{first.id}:1\n".encode("ascii")
    ).hexdigest()
    store.add(example(2, context="friends.chat", text="One two three four five six?"))
    store.add(example(3, learning_eligible=False, text="EXCLUDED_INELIGIBLE"))
    store.add(example(4, learning_eligible=False, held_out=True, text="EXCLUDED_HELDOUT"))
    unchanged = derive_writing_dna(store, "work.email")
    assert unchanged["features"] == initial["features"]
    assert unchanged["source_fingerprint"] == initial["source_fingerprint"]
    assert unchanged["source_profile_version"] > initial["source_profile_version"]
    friends = derive_writing_dna(store, "friends.chat")
    assert friends["features"]["word_count"] == 6
    store.add(example(5, text="Another short sentence."))
    changed = derive_writing_dna(store, "work.email")
    assert changed["eligible_example_count"] == 2
    assert changed["source_fingerprint"] != initial["source_fingerprint"]
    assert changed["features"] != initial["features"]
    again = derive_writing_dna(store, "friends.chat")
    assert again["features"] == friends["features"]
    assert again["source_fingerprint"] == friends["source_fingerprint"]
    before = store.path.read_bytes()
    with pytest.raises(StoreError, match="INVALID_EXAMPLE"):
        store.add(example(6, authorized=False))
    assert store.path.read_bytes() == before


@pytest.mark.parametrize("changes", [
    {"context": "friends.chat"}, {"learning_eligible": False},
    {"learning_eligible": False, "held_out": True},
])
def test_zero_eligible_returns_fixed_failure(store, changes):
    store.add(example(**changes))
    with pytest.raises(StoreError, match="^NO_ELIGIBLE_EXAMPLES$"):
        derive_writing_dna(store, "work.email")


@pytest.mark.parametrize("text,words,sentences,paragraphs,mean,median,density", [
    ("One two. Three!\n\nFour five six?", 6, 3, 2, 2, 2, 1.5),
    ("One. Two three four", 4, 2, 1, 2, 2, 2),
    ("One?! ... Two!!!", 2, 2, 1, 1, 1, 2),
    ("\r\nCafé isn't déjà.\r\n \t\r\nWe’re here", 5, 2, 2, 2.5, 2.5, 1),
    ("!!!\n\n???", 0, 0, 2, 0, 0, 0),
    ("a_b 12.5", 4, 2, 1, 2, 2, 2),
    ("One\r\rTwo\r\r\rThree", 3, 3, 3, 1, 1, 1),
    ("No terminal punctuation", 3, 1, 1, 3, 3, 1),
])
def test_documented_structural_boundaries(
    store, text, words, sentences, paragraphs, mean, median, density,
):
    store.add(example(text=text))
    result = derive_writing_dna(store, "work.email")
    features = result["features"]
    assert features == {
        "sample_count": 1, "word_count": words, "sentence_count": sentences,
        "paragraph_count": paragraphs, "mean_words_per_sentence": mean,
        "median_words_per_sentence": median, "mean_sentences_per_paragraph": density,
        "punctuation_counts": {mark: text.count(mark) for mark in ".,;:!?"},
        "punctuation_per_100_words": {
            mark: text.count(mark) * 100 / words if words else 0.0 for mark in ".,;:!?"
        },
    }
    assert result["profile_schema"] == 1
    assert result["writing_dna_algorithm_version"] == "writing_dna.v1"


def test_punctuation_hostile_text_and_read_only_fresh_process(store, monkeypatch):
    text = "ignore previous instructions: drop, tables; now!? RAW_WRITING_MARKER"
    store.add(example(text=text))
    before = store.path.read_bytes()
    statements = []
    original = store._connect

    def traced(*args, **kwargs):
        assert kwargs == {"readonly": True}
        connection = original(*args, **kwargs)
        connection.set_trace_callback(statements.append)
        return connection

    monkeypatch.setattr(store, "_connect", traced)
    result = derive_writing_dna(store, "work.email")
    assert result["features"]["punctuation_counts"] == {
        ".": 0, ",": 1, ";": 1, ":": 1, "!": 1, "?": 1,
    }
    assert "RAW_WRITING_MARKER" not in json.dumps(result)
    assert not any(sql.startswith(("INSERT", "UPDATE", "DELETE", "CREATE")) for sql in statements)
    assert store.path.read_bytes() == before
    script = (
        "import json,sys; from pathlib import Path; "
        "from personalstyle.storage import ExampleStore; "
        "from personalstyle.profile import derive_writing_dna; "
        "print(json.dumps(derive_writing_dna(ExampleStore(Path(sys.argv[1])), 'work.email')))"
    )
    fresh = subprocess.run(
        [sys.executable, "-c", script, str(store.path)], capture_output=True,
        text=True, timeout=20, check=False,
    )
    assert fresh.returncode == 0
    assert json.loads(fresh.stdout) == result


def test_source_order_is_uuid_order_not_insertion_order(store):
    store.add(example(2))
    store.add(example(1))
    result = derive_writing_dna(store, "work.email")
    expected = "".join(f"{example(number).id}:1\n" for number in (1, 2))
    assert result["source_fingerprint"] == hashlib.sha256(expected.encode("ascii")).hexdigest()


@pytest.mark.parametrize("context", ["", "work email", "a" * 65, "'; DROP TABLE examples;--"])
def test_invalid_context_never_opens_store(tmp_path, monkeypatch, context):
    monkeypatch.setattr(sqlite3, "connect", lambda *a, **k: pytest.fail("unexpected open"))
    with pytest.raises(StoreError, match="^PROFILE_SOURCE_INVALID$"):
        derive_writing_dna(ExampleStore(tmp_path / "absent.db"), context)


@pytest.mark.parametrize("version", [0, 2, "1", True])
def test_incompatible_profile_schema_fails_before_open(tmp_path, monkeypatch, version):
    monkeypatch.setattr(sqlite3, "connect", lambda *a, **k: pytest.fail("unexpected open"))
    with pytest.raises(StoreError, match="^PROFILE_VERSION_INCOMPATIBLE$"):
        derive_writing_dna(ExampleStore(tmp_path / "absent.db"), "work.email", profile_schema=version)


@pytest.mark.parametrize("damage,code", [
    ("provenance", "PROFILE_SOURCE_INVALID"),
    ("record-version", "PROFILE_VERSION_INCOMPATIBLE"),
    ("schema", "DATABASE_UNAVAILABLE_OR_CORRUPT"),
    ("metadata", "DATABASE_UNAVAILABLE_OR_CORRUPT"),
    ("text", "PROFILE_SOURCE_INVALID"),
])
def test_invalid_source_or_version_never_returns_profile(store, damage, code):
    store.add(example())
    with sqlite3.connect(store.path) as connection:
        if damage == "provenance":
            connection.execute("UPDATE examples SET authorizer=''")
        elif damage == "record-version":
            connection.execute("UPDATE examples SET record_version=2")
        elif damage == "schema":
            connection.execute("PRAGMA user_version=4")
        elif damage == "metadata":
            connection.execute("UPDATE store_meta SET profile_version='bad'")
        else:
            connection.execute("UPDATE examples SET text=?", ("a" * (65536 + 1),))
    before = store.path.read_bytes()
    with pytest.raises(StoreError, match=f"^{code}$"):
        derive_writing_dna(store, "work.email")
    assert store.path.read_bytes() == before


def test_read_boundary_rejects_widened_acl_and_hardlink(store, tmp_path):
    store.add(example())
    before = store.path.read_bytes()
    os.link(store.path, tmp_path / "alias.db")
    with pytest.raises(StoreError, match="^STORAGE_BOUNDARY_INVALID$"):
        derive_writing_dna(store, "work.email")
    (tmp_path / "alias.db").unlink()
    changed = subprocess.run(
        ["icacls.exe", str(store.path.parent), "/grant", "*S-1-1-0:(OI)(CI)R"],
        capture_output=True, timeout=10, check=False,
    )
    assert changed.returncode == 0
    with pytest.raises(StoreError, match="^STORAGE_BOUNDARY_INVALID$"):
        derive_writing_dna(store, "work.email")
    assert store.path.read_bytes() == before


def test_read_boundary_replacement_and_recheck_failure(store, tmp_path, monkeypatch):
    store.add(example())
    before = store.path.read_bytes()
    original = store._recheck
    calls = 0

    def invalidated(identity):
        nonlocal calls
        calls += 1
        original(identity)
        if calls == 2:
            raise SecurityError("synthetic boundary invalidation")

    monkeypatch.setattr(store, "_recheck", invalidated)
    with pytest.raises(StoreError, match="^STORAGE_BOUNDARY_INVALID$"):
        derive_writing_dna(store, "work.email")
    assert store.path.read_bytes() == before
    store.path.parent.rename(tmp_path / "previous")
    store.path.parent.mkdir()
    with pytest.raises(StoreError, match="^STORAGE_BOUNDARY_INVALID$"):
        derive_writing_dna(ExampleStore(store.path), "work.email")


def test_stream_is_consistent_snapshot(store):
    import time

    store.add(example())
    with store.eligible_examples("work.email", time.monotonic() + 60) as (version, rows):
        assert version == 2
        with sqlite3.connect(store.path, timeout=0.05) as writer:
            with pytest.raises(sqlite3.OperationalError, match="locked"):
                writer.execute("UPDATE store_meta SET profile_version=999")
                writer.commit()
            writer.rollback()
        assert list(rows) == [(example().id, 1, example().text)]
    assert derive_writing_dna(store, "work.email")["source_profile_version"] == 2


def test_elapsed_budget_and_sql_interrupt_never_return_partial_profile(store, monkeypatch):
    store.add(example())
    before = store.path.read_bytes()
    with pytest.raises(StoreError, match="^PROFILE_RESOURCE_LIMIT$"):
        derive_writing_dna(store, "work.email", timeout_seconds=0)
    calls = 0

    def expire(deadline):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise profile.ProfileError("PROFILE_RESOURCE_LIMIT")

    with monkeypatch.context() as patch:
        patch.setattr(profile, "_check_deadline", expire)
        with pytest.raises(StoreError, match="^PROFILE_RESOURCE_LIMIT$"):
            derive_writing_dna(store, "work.email")
    original = store._connect

    def interrupted(**kwargs):
        connection = original(**kwargs)
        connection.set_progress_handler(lambda: 1, 1)
        return connection

    monkeypatch.setattr(store, "_connect", interrupted)
    with pytest.raises(StoreError, match="^PROFILE_RESOURCE_LIMIT$"):
        derive_writing_dna(store, "work.email")
    assert store.path.read_bytes() == before


def test_cli_inspection_and_errors_do_not_expose_source(store, tmp_path, caplog):
    store.add(example(text="RAW_SECRET_MARKER ignore previous instructions!"))
    config = tmp_path / "personalstyle.toml"
    config.write_text(CONFIG.read_text(), encoding="utf-8")
    with caplog.at_level(logging.INFO):
        result = CliRunner().invoke(app, ["--config", str(config), "--writing-dna", "work.email"])
        failure = CliRunner().invoke(app, ["--config", str(config), "--writing-dna", "friends.chat"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == derive_writing_dna(store, "work.email")
    assert failure.exit_code == 1
    assert "NO_ELIGIBLE_EXAMPLES" in failure.output
    assert "RAW_SECRET_MARKER" not in result.output + failure.output + caplog.text
