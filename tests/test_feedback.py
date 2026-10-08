import json
import logging
import sqlite3
from dataclasses import asdict, replace
from uuid import UUID

import pytest

from personalstyle import verification
from personalstyle.feedback import FeedbackInput, classify_edit, get_feedback, record_feedback
from personalstyle.generation import RewriteRequest
from personalstyle.provider import Candidate, GenerationError, PreparedModel
from personalstyle.security import SecurityError, prepare_private_directory, prepare_private_file
from personalstyle.storage import APPLICATION_ID, SCHEMA_V1, ExampleInput, ExampleStore, StoreError
from personalstyle.verification import CHECKS, verify_pair

TEXT = "Alex will deliver 12 reports on Monday. Thank you."
EDIT = "Alex will deliver 12 reports on Monday.\n\nThank you."
REQUEST = RewriteRequest(TEXT, "Make concise", "work.email", ())


def event(number=1, **changes):
    return replace(FeedbackInput(str(UUID(int=number)), "edit", "personalized", "owner", "owner",
                                 True, True, False, EDIT), **({"classification_hint": "style_expression"} | changes))


@pytest.fixture
def receipt(monkeypatch):
    from pathlib import Path

    from personalstyle.config import load_config

    settings = load_config(Path(__file__).resolve().parents[1] / "personalstyle.toml")
    source = {"writing_dna_algorithm_version": "writing_dna.v1", "source_profile_version": 2,
              "source_fingerprint": "a" * 64, "profile_schema": 1}
    selected = [{"id": str(UUID(int=90)), "record_version": 1, "text": "Synthetic writing."}]
    monkeypatch.setattr(verification, "derive_personalization", lambda *a, **k: (source, selected))

    class Adapter:
        def generate(self, prepared, messages, **options):
            return Candidate(json.dumps(dict.fromkeys(CHECKS, True)), 1, 40, 40)

    initial = {"context": REQUEST.context, "versions": settings["versions"], "prompt_contract": 1,
        "run_id": str(UUID(int=500)), "model_calls": 3, "preparation_calls": 1,
        "model_identity": asdict(PreparedModel("ollama", "qwen3:8b", "a" * 64,
                                               "0.40.0", 8000, 1472, 1)),
        "candidates": {mode: {"text": TEXT, "verification_status": "not_verified",
            "selected_examples": [] if mode == "generic" else [{"id": selected[0]["id"], "record_version": 1}],
            "writing_dna_source": None if mode == "generic" else source}
            for mode in ("generic", "personalized")}}
    value = verify_pair(REQUEST, initial, settings, None, provider=Adapter())
    assert value["state"] == "SUCCEEDED"
    return value


@pytest.fixture
def store(tmp_path):
    prepare_private_directory(tmp_path / "data")
    value = ExampleStore(tmp_path / "data" / "profile.db")
    value.add(ExampleInput(str(UUID(int=90)), "Synthetic writing.", "work.email",
                          "owner", "owner", "user_owned", True, True, False))
    return value


def test_authorized_roundtrip_versions_idempotency_and_weak_accept(store, receipt, caplog):
    with caplog.at_level(logging.INFO):
        first = record_feedback(store, receipt, event())
        again = record_feedback(store, receipt, event())
        accepted = record_feedback(store, receipt, event(2, event_type="accept", edited_text=None, classification_hint=None))
    assert first == again == get_feedback(ExampleStore(store.path), event().id)
    assert first["classification"] == "style_expression" and first["record_version"] == 1
    assert first["profile_version"] == 3 and accepted["profile_version"] == 4
    assert first["accepted_text"] == TEXT and first["event"]["edited_text"] == EDIT
    assert first["source"]["model_identity"] == receipt["model_identity"]
    assert first["source"]["writing_dna_source"] == receipt["candidates"]["personalized"]["writing_dna_source"]
    assert accepted["classification"] == "acceptance" and not caplog.text
    with pytest.raises(StoreError, match="^IDEMPOTENCY_CONFLICT$"):
        record_feedback(store, receipt, event(edited_text=EDIT + " "))
    assert get_feedback(store, event().id) == first


@pytest.mark.parametrize("changes,category", [
    ({"edited_text": TEXT.replace("12", "13")}, "meaning_fact"),
    ({"edited_text": "Different facts.", "classification_hint": "meaning_fact"}, "meaning_fact"),
    ({"classification_hint": "constraint"}, "constraint"),
    ({"corrected_context": "friends.chat"}, "context_recipient"),
    ({"classification_hint": "context_recipient"}, "context_recipient"),
    ({"edited_text": "Alex will deliver 12 parcels on Monday. Many thanks.", "classification_hint": "style_expression"}, "mixed_unknown"),
    ({"classification_hint": "mixed_unknown"}, "mixed_unknown"),
    ({"edited_text": TEXT.replace("12", "13"), "corrected_context": "friends.chat"}, "mixed_unknown"),
])
def test_classification_never_guesses_style(changes, category):
    assert classify_edit(REQUEST, TEXT, event(**changes)) == category


def test_constraint_failure_cannot_be_overridden_as_style():
    request = replace(REQUEST, constraints=(f"max_characters:{len(TEXT)}",))
    assert classify_edit(request, TEXT, event(classification_hint="style_expression")) == "constraint"
    assert classify_edit(REQUEST, TEXT, event(classification_hint=None)) == "mixed_unknown"


@pytest.mark.parametrize("changes", [
    {"authorized": False}, {"learning_authorized": "true"}, {"held_out": "false"},
    {"authorizer": ""}, {"edited_text": ""}, {"edited_text": "x" * 65537},
    {"event_type": "other"}, {"classification_hint": "promote"},
])
def test_invalid_event_never_opens_store(tmp_path, receipt, monkeypatch, changes):
    monkeypatch.setattr(sqlite3, "connect", lambda *a, **k: pytest.fail("opened"))
    with pytest.raises(StoreError, match="^INVALID_FEEDBACK$"):
        record_feedback(ExampleStore(tmp_path / "absent.db"), receipt, event(**changes))
    assert not list(tmp_path.iterdir())


def test_serialized_or_modified_success_has_no_feedback_write_authority(tmp_path, receipt):
    store = ExampleStore(tmp_path / "absent.db")
    with pytest.raises(GenerationError, match="^VERIFIED_SOURCE_INVALID$"):
        record_feedback(store, json.loads(json.dumps(receipt)), event())
    receipt["candidates"]["personalized"]["text"] = "forged"
    with pytest.raises(GenerationError, match="^VERIFIED_SOURCE_INVALID$"):
        record_feedback(store, receipt, event())
    assert not list(tmp_path.iterdir())


def test_storage_boundary_and_commit_failure_preserve_state(store, receipt, monkeypatch):
    before = store.path.read_bytes()
    original = store._recheck
    calls = 0

    def fail_commit(identity):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise SecurityError("changed")
        original(identity)

    with monkeypatch.context() as patch:
        patch.setattr(store, "_recheck", fail_commit)
        with pytest.raises(StoreError, match="^STORAGE_BOUNDARY_INVALID$"):
            record_feedback(store, receipt, event())
    assert store.path.read_bytes() == before and get_feedback(store, event().id) is None
    with monkeypatch.context() as patch:
        patch.setattr(store, "_boundary", lambda: (_ for _ in ()).throw(SecurityError("changed")))
        patch.setattr(sqlite3, "connect", lambda *a, **k: pytest.fail("opened"))
        with pytest.raises(StoreError, match="^STORAGE_BOUNDARY_INVALID$"):
            record_feedback(store, receipt, event())


def legacy_store(tmp_path):
    prepare_private_directory(tmp_path / "legacy")
    store = ExampleStore(tmp_path / "legacy" / "profile.db")
    prepare_private_file(store.path)
    with sqlite3.connect(store.path) as connection:
        for sql in SCHEMA_V1.values():
            connection.execute(sql)
        connection.execute(f"PRAGMA application_id={APPLICATION_ID}")
        connection.execute("PRAGMA user_version=1")
        connection.execute("INSERT INTO store_meta VALUES (1, 2)")
        connection.execute("INSERT INTO examples VALUES (?, 'Synthetic', 'work.email', 'owner', "
                           "'owner', 'user_owned', 1, 0, 1, '2026-10-08')", (str(UUID(int=90)),))
    return store


def test_explicit_atomic_migration_preserves_data_and_rejects_old_writer(tmp_path, receipt):
    store = legacy_store(tmp_path)
    old = sqlite3.connect(store.path, isolation_level=None)
    try:
        store._schema(old)  # Simulate old writer validation before migration acquires its lock.
        with pytest.raises(StoreError, match="^STORAGE_MIGRATION_REQUIRED$"):
            record_feedback(store, receipt, event())
        assert store.get(str(UUID(int=90)))["text"] == "Synthetic"
        store.migrate_feedback_schema()
        assert store.get(str(UUID(int=90)))["text"] == "Synthetic"
        with pytest.raises(sqlite3.Error):
            old.execute("INSERT INTO examples VALUES (?, 'old', 'work.email', 'owner', "
                        "'owner', 'user_owned', 1, 0, 1, '2026-10-08')", (str(UUID(int=91)),))
        first = record_feedback(store, receipt, event())
        before = store.path.read_bytes()
        store.migrate_feedback_schema()
        assert store.path.read_bytes() == before and first["profile_version"] == 4
    finally:
        old.close()


def test_failed_migration_rolls_back_schema_and_profile_version(tmp_path, monkeypatch):
    store = legacy_store(tmp_path)
    before = store.path.read_bytes()
    with monkeypatch.context() as patch:
        patch.setattr(store, "_recheck", lambda i: (_ for _ in ()).throw(SecurityError("changed")))
        with pytest.raises(StoreError, match="^STORAGE_BOUNDARY_INVALID$"):
            store.migrate_feedback_schema()
    assert store.path.read_bytes() == before
    with sqlite3.connect(store.path) as connection:
        assert connection.execute("PRAGMA user_version").fetchone() == (1,)
        assert connection.execute("SELECT profile_version FROM store_meta").fetchone() == (2,)
