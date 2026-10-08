import copy
import json
from dataclasses import replace
from pathlib import Path
from uuid import UUID

import pytest
import test_feedback
from test_feedback import EDIT, REQUEST, TEXT, event

from personalstyle.config import load_config
from personalstyle.feedback import record_feedback
from personalstyle.learning import POLICY, derive_learning_evidence, evaluate_context_preferences
from personalstyle.provider import Candidate
from personalstyle.storage import ExampleInput, StoreError
from personalstyle.verification import CHECKS, verified_source, verify_pair


receipt = test_feedback.receipt
store = test_feedback.store


def test_scoped_evidence_exclusions_determinism_and_explicit_evaluation(store, receipt):
    first = record_feedback(store, receipt, event())
    initial = derive_learning_evidence(store, "work.email")
    assert initial["eligible_observation_count"] == 1
    assert initial["hypotheses"] and initial["promotion_state"] == "NOT_EVALUATED"
    assert initial["policy_version"] == POLICY and initial["active_preferences"] == []
    assert first["source"]["run_id"] == receipt["run_id"]
    for number, changes in enumerate((
        {"held_out": True}, {"learning_authorized": False},
        {"event_type": "accept", "edited_text": None, "classification_hint": None},
        {"edited_text": TEXT.replace("12", "13")},
        {"classification_hint": "constraint"},
        {"corrected_context": "friends.chat"},
        {"classification_hint": "mixed_unknown"},
    ), 2):
        record_feedback(store, receipt, event(number, **changes))
    filtered = derive_learning_evidence(store, "work.email")
    assert filtered["source_fingerprint"] == initial["source_fingerprint"]
    assert filtered["hypotheses"] == initial["hypotheses"]

    from pathlib import Path

    class Adapter:
        def generate(self, prepared, messages, **options):
            return Candidate(json.dumps(dict.fromkeys(CHECKS, True)), 1, 40, 40)

    other_pair = copy.deepcopy(verified_source(receipt)["result"])
    other_pair.update(context="friends.chat", model_calls=3)
    other_receipt = verify_pair(replace(REQUEST, context="friends.chat"), other_pair,
        load_config(Path(__file__).resolve().parents[1] / "personalstyle.toml"),
        store, provider=Adapter())
    assert other_receipt["state"] == "SUCCEEDED"
    record_feedback(store, other_receipt, event(9))
    isolated = derive_learning_evidence(store, "work.email")
    assert isolated["hypotheses"] == initial["hypotheses"]
    assert isolated["source_fingerprint"] == initial["source_fingerprint"]
    assert derive_learning_evidence(store, "friends.chat")["eligible_observation_count"] == 1

    record_feedback(store, receipt, event(10, edited_text=EDIT + " "))
    before = store.path.read_bytes()
    accumulated = derive_learning_evidence(store, "work.email")
    assert accumulated == derive_learning_evidence(store, "work.email")
    assert accumulated["eligible_observation_count"] == 2
    assert accumulated["source_fingerprint"] != initial["source_fingerprint"]
    assert accumulated["source_profile_version"] > initial["source_profile_version"]
    assert accumulated["active_preferences"] == [] and accumulated["policy_version"] == POLICY
    assert store.path.read_bytes() == before
    assert TEXT not in json.dumps(accumulated) and EDIT not in json.dumps(accumulated)


def test_invalid_context_and_resource_bound_fail_explicitly(store):
    with pytest.raises(StoreError, match="^FEEDBACK_SOURCE_INVALID$"):
        derive_learning_evidence(store, "inferred context")
    with pytest.raises(StoreError, match="^PROFILE_RESOURCE_LIMIT$"):
        derive_learning_evidence(store, "work.email", timeout_seconds=0)


@pytest.fixture
def memory_store(tmp_path):
    """SQLite policy fixture; protected OS persistence is covered by integration tests."""
    import sqlite3
    from contextlib import contextmanager

    from personalstyle.storage import APPLICATION_ID, SCHEMA, ExampleStore

    class MemoryStore(ExampleStore):
        @contextmanager
        def feedback_connection(self, *, write=False):
            self.connection.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            try:
                self._schema(self.connection)
                yield self.connection
                self.connection.commit()
            finally:
                self.connection.rollback()

    value = MemoryStore(Path("unused-policy-fixture.db"))
    value.connection = sqlite3.connect(tmp_path / "policy-fixture.db")
    for sql in SCHEMA.values():
        value.connection.execute(sql)
    value.connection.execute(f"PRAGMA application_id={APPLICATION_ID}")
    value.connection.execute("PRAGMA user_version=2")
    value.connection.execute("INSERT INTO store_meta VALUES (2,1)")
    value.connection.commit()
    yield value
    value.connection.close()


def source_receipt(receipt, number, *, text=TEXT, context="work.email"):
    from pathlib import Path
    from uuid import UUID

    class Adapter:
        def generate(self, prepared, messages, **options):
            return Candidate(json.dumps(dict.fromkeys(CHECKS, True)), 1, 40, 40)

    pair = copy.deepcopy(verified_source(receipt)["result"])
    pair.update(run_id=str(UUID(int=number)), context=context, model_calls=3)
    for candidate in pair["candidates"].values():
        candidate.update(text=text, verification_status="not_verified")
    request = replace(REQUEST, original=text, context=context)
    result = verify_pair(request, pair, load_config(
        Path(__file__).resolve().parents[1] / "personalstyle.toml"), None, provider=Adapter())
    assert result["state"] == "SUCCEEDED"
    return result


def test_independence_contestation_reactivation_history_and_no_logs(memory_store, receipt, caplog):
    target = memory_store
    first = source_receipt(receipt, 101)
    record_feedback(target, first, event(30))
    record_feedback(target, source_receipt(receipt, 102), event(20))
    two = evaluate_context_preferences(target, "work.email")
    assert len(two) == 3 and all(p["state"] == "unpromoted" for p in two)
    record_feedback(target, first, event(31, edited_text=EDIT + " "))
    assert all(p["state"] != "active" for p in evaluate_context_preferences(target, "work.email"))
    record_feedback(target, source_receipt(receipt, 103), event(10))
    active = evaluate_context_preferences(target, "work.email")
    assert all(p["state"] == "active" and p["direction"] == "increase" for p in active)
    assert all(len(set(p["supporting_run_ids"])) == 3 for p in active)
    version = target.connection.execute("SELECT profile_version FROM store_meta").fetchone()[0]
    assert evaluate_context_preferences(target, "work.email") == active
    assert target.connection.execute("SELECT profile_version FROM store_meta").fetchone() == (version,)
    # Later creation wins despite a smaller ID; one opposite unit deactivates, never flips.
    opposite = source_receipt(receipt, 104, text=EDIT)
    record_feedback(target, opposite, event(1, edited_text=TEXT))
    contested = evaluate_context_preferences(target, "work.email")
    assert all(p["state"] == "contested" and p["direction"] == "increase" for p in contested)
    assert all(p["supporting_feedback_ids"] == [event(20).id, event(10).id, event(1).id]
               for p in contested)
    for n in range(105, 108):
        record_feedback(target, source_receipt(receipt, n), event(n))
        current = evaluate_context_preferences(target, "work.email")
        assert all(p["state"] == ("active" if n == 107 else "contested") for p in current)
    assert all(p["version"] > a["version"] for p, a in zip(current, active))
    assert all(p["policy_version"] == POLICY for p in current)
    assert target.connection.execute("SELECT COUNT(*) FROM preferences").fetchone()[0] > 3
    assert not caplog.text and TEXT not in json.dumps(current) and EDIT not in json.dumps(current)


def test_conflicting_run_is_excluded_and_ineligible_never_promotes(memory_store, receipt):
    target = memory_store
    for n in (1, 2):
        record_feedback(target, source_receipt(receipt, 200+n), event(n))
    source = source_receipt(receipt, 203, text=EDIT)
    record_feedback(target, source, event(3, edited_text=EDIT.replace("\n\n", "\n\n\n")))
    record_feedback(target, source, event(4, edited_text=TEXT))
    # Line/separator evidence conflicts from one run; paragraph only decreases in that run.
    states = {p["feature"]: p for p in evaluate_context_preferences(target, "work.email")}
    assert states["line_count"]["state"] == "unpromoted"
    assert len(states["line_count"]["supporting_run_ids"]) == 2
    assert states["separator_characters"]["state"] == "unpromoted"
    assert states["paragraph_count"]["state"] == "contested"
    for n, changes in enumerate((
        {"held_out": True}, {"learning_authorized": False},
        {"event_type": "accept", "edited_text": None, "classification_hint": None},
        {"edited_text": TEXT.replace("12", "13")}, {"classification_hint": "constraint"},
        {"corrected_context": "friends.chat"}, {"classification_hint": "mixed_unknown"},
    ), 10):
        record_feedback(target, source_receipt(receipt, 300+n), event(n, **changes))
    for n in range(3):
        record_feedback(target, source_receipt(receipt, 400+n, context="friends.chat"), event(30+n))
    assert {p["feature"]: p for p in evaluate_context_preferences(target, "work.email")} == states
    assert all(p["state"] == "active" for p in evaluate_context_preferences(target, "friends.chat"))


def test_protected_promotion_consumption_exact_provenance_and_f04_integrity(store, receipt, monkeypatch, caplog):
    from pathlib import Path

    from personalstyle import verification
    from personalstyle.generation import generate_pair
    from personalstyle.profile import derive_personalization
    from personalstyle.provider import PreparedModel

    for n in range(3):
        record_feedback(store, source_receipt(receipt, 700+n), event(n+1))
    from personalstyle.security import SecurityError

    before_promotion = store.path.read_bytes()
    original_recheck = store._recheck
    calls = 0

    def reject_commit(identity):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise SecurityError("synthetic")
        original_recheck(identity)

    with monkeypatch.context() as patch:
        patch.setattr(store, "_recheck", reject_commit)
        with pytest.raises(StoreError, match="^STORAGE_BOUNDARY_INVALID$"):
            evaluate_context_preferences(store, "work.email")
    assert store.path.read_bytes() == before_promotion
    preferences = evaluate_context_preferences(store, "work.email")
    ids = [{"id": p["id"], "version": p["version"]} for p in preferences]
    monkeypatch.setattr(verification, "derive_personalization", derive_personalization)

    class Adapter:
        def __init__(self):
            self.messages = []

        def prepare(self, context_tokens):
            return PreparedModel("ollama", "qwen3:8b", "a"*64, "0.40.0", context_tokens, 1472, 1)

        def generate(self, prepared, messages, **options):
            self.messages.append(messages)
            output = json.dumps(dict.fromkeys(CHECKS, True)) if "Compare the original" in messages[0]["content"] else TEXT
            return Candidate(output, 1, 40, 40)

    settings = load_config(Path(__file__).resolve().parents[1] / "personalstyle.toml")
    before = store.path.read_bytes()
    adapter = Adapter()
    pair = generate_pair(REQUEST, settings, store, provider=adapter)
    assert pair["candidates"]["generic"]["selected_preferences"] == []
    assert pair["candidates"]["personalized"]["selected_preferences"] == ids
    evidence = json.loads(adapter.messages[1][1]["content"])["personalization"]
    assert [{"id": p["id"], "version": p["version"]} for p in evidence["preferences"]] == ids
    assert all(p["context"] == "work.email" for p in evidence["preferences"])
    assert evidence["examples"] and evidence["writing_dna"]
    verified = verify_pair(REQUEST, pair, settings, store, provider=adapter)
    assert verified["state"] == "SUCCEEDED"
    assert store.path.read_bytes() == before and not caplog.text
    forged = copy.deepcopy(pair)
    forged["candidates"]["personalized"]["selected_preferences"][0]["version"] += 1
    assert verify_pair(REQUEST, forged, settings, store, provider=adapter)["failure_code"] == "PERSONALIZATION_SOURCE_CHANGED"
    store.add(ExampleInput(str(UUID(int=99)), "Hello.", "friends.chat", "owner", "owner",
                           "user_owned", True, True, False))
    other = generate_pair(replace(REQUEST, context="friends.chat"), settings, store, provider=Adapter())
    assert other["candidates"]["personalized"]["selected_preferences"] == []
    # A new opposite unit invalidates old provenance and removes contested state from prompts.
    monkeypatch.setattr(verification, "derive_personalization", lambda *a, **k: (
        verified_source(receipt)["result"]["candidates"]["personalized"]["writing_dna_source"],
        [{"id": str(UUID(int=90)), "record_version": 1, "text": "Synthetic writing."}]))
    record_feedback(store, source_receipt(receipt, 800, text=EDIT), event(10, edited_text=TEXT))
    assert all(p["state"] == "contested" for p in evaluate_context_preferences(store, "work.email"))
    monkeypatch.setattr(verification, "derive_personalization", derive_personalization)
    pair = generate_pair(REQUEST, settings, store, provider=Adapter())
    assert pair["candidates"]["personalized"]["selected_preferences"] == []


def test_corrupt_evidence_fails_closed(memory_store, receipt):
    target = memory_store
    for n in range(3):
        record_feedback(target, source_receipt(receipt, 900+n), event(n+1))
    target.connection.execute("UPDATE feedback SET observations='{}' WHERE id=?", (event(1).id,))
    target.connection.commit()
    with pytest.raises(StoreError, match="^FEEDBACK_SOURCE_INVALID$"):
        evaluate_context_preferences(target, "work.email")
    assert target.connection.execute("SELECT COUNT(*) FROM preferences").fetchone() == (0,)



def test_actual_query_plans_and_fixed_query_count(memory_store, receipt):
    target = memory_store
    record_feedback(target, source_receipt(receipt, 1001), event(1))
    trace = []
    target.connection.set_trace_callback(trace.append)
    evaluate_context_preferences(target, "work.email")
    first_count = sum("FROM feedback" in q for q in trace if q.startswith("SELECT"))
    assert first_count == 4  # One validation stream, three feature aggregates.
    for n in range(1002, 1012):
        record_feedback(target, source_receipt(receipt, n), event(n))
    trace.clear()
    evaluate_context_preferences(target, "work.email")
    target.connection.set_trace_callback(None)
    assert sum("FROM feedback" in q for q in trace if q.startswith("SELECT")) == first_count
    for query in (q for q in trace if q.startswith("SELECT") and "FROM feedback" in q):
        details = [row[3] for row in target.connection.execute("EXPLAIN QUERY PLAN " + query)]
        assert any("SEARCH feedback USING INDEX feedback_" in d for d in details)
        assert not any("TEMP B-TREE FOR GROUP BY" in d for d in details)
    query = next(q for q in trace if q.startswith("SELECT p.id"))
    details = [row[3] for row in target.connection.execute("EXPLAIN QUERY PLAN " + query)]
    assert any("preferences_context" in d and "SEARCH" in d for d in details)
    assert not any("TEMP B-TREE" in d for d in details)
    details = [row[3] for row in target.connection.execute(
        "EXPLAIN QUERY PLAN SELECT * FROM examples WHERE context=? AND learning_eligible=1 "
        "AND held_out=0 ORDER BY id COLLATE BINARY", ("work.email",))]
    assert any("SEARCH examples USING INDEX examples_eligible" in d for d in details)
    assert not any("TEMP B-TREE" in d for d in details)



@pytest.mark.parametrize("defect", ["authorization", "source_version", "not_verified", "run_id"])
def test_invalid_feedback_cannot_activate_preferences(memory_store, receipt, defect):
    target = memory_store
    for n in range(3):
        record_feedback(target, source_receipt(receipt, 2000+n), event(n+1))
    payload = json.loads(target.connection.execute("SELECT payload FROM feedback WHERE id=?",
                                                 (event(1).id,)).fetchone()[0])
    if defect == "authorization":
        payload["event"]["authorized"] = False
    elif defect == "source_version":
        payload["source"]["versions"]["profile_schema"] = 2
    elif defect == "not_verified":
        payload["source"]["verification_status"] = "not_verified"
    else:
        payload["source"]["run_id"] = str(UUID(int=9999))
    target.connection.execute("UPDATE feedback SET payload=? WHERE id=?",
                              (json.dumps(payload), event(1).id))
    target.connection.commit()
    with pytest.raises(StoreError, match="^(FEEDBACK_SOURCE_INVALID|INVALID_FEEDBACK)$"):
        evaluate_context_preferences(target, "work.email")
    assert target.connection.execute("SELECT COUNT(*) FROM preferences").fetchone() == (0,)
