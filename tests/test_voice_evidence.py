"""V01 consent, persistence, migration and exact-context voice eligibility."""

import json
import sqlite3
from pathlib import Path
from uuid import UUID

import pytest

from personalstyle.feedback import CLASSIFIER, FeedbackInput, classify_edit, presentation_changes
from personalstyle.generation import RewriteRequest
from personalstyle.security import prepare_private_directory, prepare_private_file
from personalstyle.storage import (
    APPLICATION_ID,
    SCHEMA_V3,
    ExampleInput,
    ExampleStore,
    StoreError,
)


def sample(number: int, *, context: str = "casual.chat", learning: bool = True,
           source_kind: str = "user_owned") -> ExampleInput:
    return ExampleInput(
        str(UUID(int=number)), f"Synthetic sample {number}.", context, "local owner", "local owner",
        source_kind, True, learning, False,
    )


@pytest.fixture
def store(tmp_path: Path) -> ExampleStore:
    directory = tmp_path / "profile"
    prepare_private_directory(directory)
    return ExampleStore(directory / "profile.db")


def test_separate_consents_survive_restart_and_contexts_do_not_mix(store):
    casual = sample(201)
    academic = sample(202, context="academic.essay", learning=False)
    store.add(casual)
    store.add(academic)

    reopened = ExampleStore(store.path)
    assert reopened.voice_status("casual.chat")["state"] == "AVAILABLE"
    assert reopened.voice_status("academic.essay")["state"] == "PERSONALIZATION_OFF"
    with reopened.eligible_examples("casual.chat", 10**12) as (_, rows):
        assert [row[0] for row in rows] == [casual.id]
    with reopened.eligible_examples("academic.essay", 10**12) as (_, rows):
        assert list(rows) == []

    reopened.set_personalization(casual.id, False, authorized=True)
    assert ExampleStore(store.path).voice_status("casual.chat")["eligible_sources"] == 0
    assert ExampleStore(store.path).get(casual.id)["text"] == casual.text
    reopened.set_personalization(casual.id, True, authorized=True)
    assert ExampleStore(store.path).voice_status("casual.chat")["state"] == "AVAILABLE"


def test_missing_storage_authorization_and_non_user_sources_never_become_voice(store):
    request = sample(203)
    store.add(request)
    with pytest.raises(StoreError, match="^VOICE_AUTHORIZATION_REQUIRED$"):
        store.authorize_legacy_example(
            request.id, storage_authorized=False,
            personalization_authorized=True, authorized=True,
        )
    reference = sample(204, source_kind="authorized_reference", learning=False)
    store.add(reference)
    with pytest.raises(StoreError, match="^VOICE_SOURCE_INELIGIBLE$"):
        store.set_personalization(reference.id, True, authorized=True)
    with pytest.raises(StoreError, match="^INVALID_EXAMPLE$"):
        sample(205, source_kind="ai_generated").validate()
    assert store.voice_status("casual.chat")["eligible_sources"] == 1


def legacy_schema3_store(path: Path) -> ExampleStore:
    directory = path.parent
    prepare_private_directory(directory)
    store = ExampleStore(path)
    prepare_private_file(path)
    with sqlite3.connect(path) as connection:
        for statement in SCHEMA_V3.values():
            connection.execute(statement)
        connection.execute(f"PRAGMA application_id={APPLICATION_ID}")
        connection.execute("PRAGMA user_version=3")
        connection.execute("INSERT INTO store_meta VALUES (3, 17)")
        connection.execute(
            "INSERT INTO examples VALUES (?, ?, 'casual.chat', 'owner', 'owner', "
            "'user_owned', 0, 0, 1, '2026-10-16', 2)",
            (str(UUID(int=206)), "Synthetic sample 206."),
        )
        connection.execute(
            "INSERT INTO feedback VALUES (?, 'casual.chat', '{}', 1, 17, '2026-10-16', ?, '[]')",
            (str(UUID(int=207)), str(UUID(int=208))),
        )
        connection.execute(
            "INSERT INTO preferences VALUES (?, 1, 'casual.chat', 'line_count', '{}')",
            (str(UUID(int=209)),),
        )
        connection.execute("INSERT INTO documents VALUES ('doc', 1, '{}')")
        connection.execute("INSERT INTO document_segments VALUES ('doc', 'seg', 0, '{}')")
    return store


def canonical_rows(path: Path) -> dict[str, list[tuple]]:
    with sqlite3.connect(path) as connection:
        return {
            table: connection.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall()
            for table in ("examples", "feedback", "preferences", "documents", "document_segments")
        }


def test_schema3_migration_preserves_data_and_requires_explicit_reauthorization(tmp_path):
    store = legacy_schema3_store(tmp_path / "legacy" / "profile.db")
    before = canonical_rows(store.path)
    assert store.voice_status("casual.chat")["state"] == "MIGRATION_REQUIRED"
    with pytest.raises(StoreError, match="^STORAGE_MIGRATION_REQUIRED$"):
        store.add(sample(216))
    assert canonical_rows(store.path) == before
    store.migrate_to_current_schema()
    after = canonical_rows(store.path)
    assert after == before
    assert store.voice_status("casual.chat")["state"] == "AUTHORIZATION_REQUIRED"
    assert store.get(str(UUID(int=206)))["text"] == "Synthetic sample 206."
    with store.eligible_examples("casual.chat", 10**12) as (_, rows):
        assert list(rows) == []

    store.authorize_legacy_example(
        str(UUID(int=206)), storage_authorized=True,
        personalization_authorized=True, authorized=True,
    )
    assert store.voice_status("casual.chat")["state"] == "AVAILABLE"
    with ExampleStore(store.path).eligible_examples("casual.chat", 10**12) as (_, rows):
        assert [row[0] for row in rows] == [str(UUID(int=206))]
    stable = canonical_rows(store.path)
    store.migrate_to_current_schema()
    assert canonical_rows(store.path) == stable


def test_schema3_migration_failure_rolls_back_without_losing_legacy_data(tmp_path, monkeypatch):
    store = legacy_schema3_store(tmp_path / "rollback" / "profile.db")
    before = canonical_rows(store.path)

    def fail_recheck(_identity):
        from personalstyle.security import SecurityError
        raise SecurityError("synthetic boundary change")

    monkeypatch.setattr(store, "_recheck", fail_recheck)
    with pytest.raises(StoreError, match="^STORAGE_BOUNDARY_INVALID$"):
        store.migrate_voice_schema()
    assert canonical_rows(store.path) == before
    with sqlite3.connect(store.path) as connection:
        assert connection.execute("PRAGMA user_version").fetchone() == (3,)
        assert connection.execute(
            "SELECT name FROM sqlite_master WHERE name='example_authorizations'",
        ).fetchone() is None


def test_revoking_source_deletes_only_dependent_learning_and_source(store):
    source = sample(210)
    unrelated = sample(211, context="work.email")
    store.add(source)
    store.add(unrelated)
    feedback_id = str(UUID(int=212))
    run_id = str(UUID(int=213))
    with store.feedback_connection(write=True) as connection:
        connection.execute(
            "INSERT INTO feedback VALUES (?, 'casual.chat', ?, 1, 3, '2026-10-16', ?, '{}')",
            (feedback_id, '{"source":{"selected_examples":[{"id":"' + source.id + '"}]}}', run_id),
        )
        connection.execute(
            "INSERT INTO preferences VALUES (?, 1, 'casual.chat', 'line_count', ?)" ,
            (str(UUID(int=214)), '{"supporting_feedback_ids":["' + feedback_id + '"]}'),
        )
        connection.execute(
            "INSERT INTO preferences VALUES (?, 1, 'work.email', 'line_count', '{}')",
            (str(UUID(int=215)),),
        )

    assert store.revoke_example(source.id, authorized=True)
    assert store.get(source.id) is None
    with store.feedback_connection() as connection:
        assert connection.execute("SELECT id FROM feedback").fetchall() == []
        assert connection.execute("SELECT id FROM preferences ORDER BY context").fetchall() == [
            (str(UUID(int=215)),),
        ]
    assert store.get(unrelated.id) is not None
    assert store.voice_status("casual.chat")["state"] == "UNAVAILABLE"


@pytest.mark.parametrize("operation", ["revoke", "disable_personalization"])
def test_revoking_or_disabling_source_does_not_reactivate_older_preferences(store, operation):
    source = sample(230)
    unrelated_source = sample(231)
    store.add(source)
    store.add(unrelated_source)

    # Create six independent, structurally valid evidence units. The newest preference
    # version depends on the revocable source; its predecessor remains active evidence.
    feedback_ids = []
    with store.feedback_connection(write=True) as connection:
        for offset in range(6):
            number = 240 + offset
            feedback_id = str(UUID(int=number))
            run_id = str(UUID(int=340 + offset))
            selected = source if offset == 4 else unrelated_source
            feedback = FeedbackInput(
                feedback_id, "edit", "personalized", "local owner", "local owner",
                True, True, False,
                "Synthetic fact 42." if offset < 3 or offset == 5 else "Synthetic\nfact 42.",
                classification_hint="style_expression",
            )
            accepted = "Synthetic\nfact 42." if offset < 3 or offset == 5 else "Synthetic fact 42."
            request = RewriteRequest(accepted, "clarify", "casual.chat", ())
            source_data = {
                "context": "casual.chat", "candidate_mode": "personalized",
                "verification_status": "verified",
                "versions": {"profile_schema": 1, "storage_schema": 4},
                "prompt_contract": 1, "run_id": run_id,
                "selected_examples": [{"id": selected.id, "record_version": 1}],
            }
            payload_value = {
                "event": feedback.__dict__, "context": "casual.chat",
                "request": request.__dict__, "source": source_data,
                "accepted_text": accepted,
                "classification": classify_edit(request, accepted, feedback),
                "classification_version": CLASSIFIER,
            }
            payload = json.dumps(payload_value, sort_keys=True)
            observations = json.dumps(presentation_changes(accepted, feedback.edited_text), sort_keys=True)
            connection.execute(
                "INSERT INTO feedback VALUES (?, 'casual.chat', ?, 1, ?, ?, ?, ?)",
                (feedback_id, payload, 20 + offset, f"2026-10-16T00:00:0{offset}+00:00",
                 run_id, observations),
            )
            feedback_ids.append((feedback_id, run_id, "increase" if offset < 3 or offset == 5 else "decrease"))

        def preference(feature: str, version: int, selected: list[tuple[str, str, str]],
                       state: str, direction: str) -> None:
            units = [
                {"feedback_id": feedback_id, "run_id": run_id, "direction": unit_direction}
                for feedback_id, run_id, unit_direction in selected
            ]
            feature_id = str(UUID(int=390 + (feature == "separator_characters")))
            value = {
                "id": feature_id, "version": version, "context": "casual.chat",
                "feature": feature, "direction": direction, "state": state,
                "policy_version": "context_preference_promotion.v1",
                "supporting_units": units,
                "supporting_feedback_ids": [unit["feedback_id"] for unit in units],
                "supporting_run_ids": [unit["run_id"] for unit in units],
                "source_profile_version": 30 + version,
            }
            connection.execute(
                "INSERT INTO preferences VALUES (?, ?, 'casual.chat', ?, ?)",
                (feature_id, version, feature, json.dumps(value, sort_keys=True)),
            )

        preference("line_count", 1, feedback_ids[:3], "active", "increase")
        preference("line_count", 2, feedback_ids[3:], "contested", "increase")
        preference("separator_characters", 1, feedback_ids[:3], "active", "increase")

    with store.feedback_connection() as connection:
        before = ExampleStore.active_preferences(connection, "casual.chat")
        assert [item["feature"] for item in before] == ["separator_characters"]

    if operation == "revoke":
        assert store.revoke_example(source.id, authorized=True)
    else:
        store.set_personalization(source.id, False, authorized=True)

    # Generation consumes this API. Deleting only version 2 would expose v1 again.
    with store.feedback_connection() as connection:
        after = ExampleStore.active_preferences(connection, "casual.chat")
        assert [item["feature"] for item in after] == ["separator_characters"]
        assert connection.execute(
            "SELECT COUNT(*) FROM preferences WHERE context='casual.chat' AND feature='line_count'",
        ).fetchone() == (0,)

    reopened = ExampleStore(store.path)
    with reopened.feedback_connection() as connection:
        assert [item["feature"] for item in ExampleStore.active_preferences(connection, "casual.chat")] == [
            "separator_characters",
        ]
    assert reopened.get(unrelated_source.id) is not None
    if operation == "revoke":
        assert reopened.get(source.id) is None
        assert reopened.voice_status("casual.chat")["state"] == "AVAILABLE"
    else:
        assert reopened.get(source.id)["text"] == source.text
        with reopened.feedback_connection() as connection:
            auth = dict(connection.execute(
                "SELECT example_id, personalization_authorized FROM example_authorizations",
            ).fetchall())
        assert auth[source.id] == 0 and auth[unrelated_source.id] == 1
        assert reopened.voice_status("casual.chat")["state"] == "AVAILABLE"

    from personalstyle.learning import evaluate_context_preferences

    evaluated = evaluate_context_preferences(reopened, "casual.chat")
    assert next(item for item in evaluated if item["feature"] == "line_count")["state"] != "active"
    with reopened.feedback_connection() as connection:
        assert "line_count" not in {
            item["feature"] for item in ExampleStore.active_preferences(connection, "casual.chat")
        }


def test_personalization_off_retains_authorized_source_but_removes_its_learning(store):
    source = sample(220)
    store.add(source)
    feedback_id = str(UUID(int=221))
    with store.feedback_connection(write=True) as connection:
        connection.execute(
            "INSERT INTO feedback VALUES (?, 'casual.chat', ?, 1, 2, '2026-10-16', ?, '{}')",
            (feedback_id, '{"source":{"selected_examples":[{"id":"' + source.id + '"}]}}',
             str(UUID(int=222))),
        )
        connection.execute(
            "INSERT INTO preferences VALUES (?, 1, 'casual.chat', 'line_count', ?)",
            (str(UUID(int=223)), '{"supporting_feedback_ids":["' + feedback_id + '"]}'),
        )

    store.set_personalization(source.id, False, authorized=True)
    assert store.get(source.id)["text"] == source.text
    assert store.voice_status("casual.chat")["state"] == "PERSONALIZATION_OFF"
    with store.feedback_connection() as connection:
        assert connection.execute("SELECT COUNT(*) FROM feedback").fetchone() == (0,)
        assert connection.execute("SELECT COUNT(*) FROM preferences").fetchone() == (0,)


def test_revocation_version_chain_invalidation_rolls_back_atomically(store, monkeypatch):
    source = sample(250)
    unrelated = sample(251)
    store.add(source)
    store.add(unrelated)
    feedback_id = str(UUID(int=252))
    run_id = str(UUID(int=253))
    preference_id = str(UUID(int=254))
    source_payload = json.dumps({"source": {"selected_examples": [{"id": source.id}]}})
    with store.feedback_connection(write=True) as connection:
        connection.execute(
            "INSERT INTO feedback VALUES (?, 'casual.chat', ?, 1, 3, '2026-10-16', ?, '{}')",
            (feedback_id, source_payload, run_id),
        )
        for version in (1, 2):
            connection.execute(
                "INSERT INTO preferences VALUES (?, ?, 'casual.chat', 'line_count', ?)",
                (preference_id, version, json.dumps({"supporting_feedback_ids": [feedback_id]})),
            )

    def snapshot() -> dict[str, list[tuple]]:
        with store.feedback_connection() as connection:
            return {
                table: connection.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall()
                for table in ("examples", "example_authorizations", "feedback", "preferences")
            }

    before = snapshot()
    original_recheck = store._recheck
    rechecks = 0

    def reject_commit(identity):
        nonlocal rechecks
        rechecks += 1
        if rechecks == 2:
            from personalstyle.security import SecurityError
            raise SecurityError("synthetic commit-boundary failure")
        original_recheck(identity)

    with monkeypatch.context() as patcher:
        patcher.setattr(store, "_recheck", reject_commit)
        with pytest.raises(StoreError, match="^STORAGE_BOUNDARY_INVALID$"):
            store.revoke_example(source.id, authorized=True)
    assert snapshot() == before
