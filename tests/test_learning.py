import copy
import json
from dataclasses import replace

import pytest

from test_feedback import EDIT, REQUEST, TEXT, event
from test_feedback import receipt as receipt
from test_feedback import store as store

from personalstyle.config import load_config
from personalstyle.feedback import record_feedback
from personalstyle.learning import POLICY_BLOCKER, derive_learning_evidence
from personalstyle.provider import Candidate
from personalstyle.storage import StoreError
from personalstyle.verification import CHECKS, verified_source, verify_pair


def test_scoped_evidence_exclusions_determinism_and_blocked_promotion(store, receipt):
    first = record_feedback(store, receipt, event())
    initial = derive_learning_evidence(store, "work.email")
    assert initial["eligible_observation_count"] == 1
    assert initial["hypotheses"] and initial["promotion_state"] == "BLOCKED"
    assert initial["failure_code"] == POLICY_BLOCKER and initial["active_preferences"] == []
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
    assert accumulated["active_preferences"] == [] and accumulated["failure_code"] == POLICY_BLOCKER
    assert store.path.read_bytes() == before
    assert TEXT not in json.dumps(accumulated) and EDIT not in json.dumps(accumulated)


def test_invalid_context_and_resource_bound_fail_explicitly(store):
    with pytest.raises(StoreError, match="^FEEDBACK_SOURCE_INVALID$"):
        derive_learning_evidence(store, "inferred context")
    with pytest.raises(StoreError, match="^PROFILE_RESOURCE_LIMIT$"):
        derive_learning_evidence(store, "work.email", timeout_seconds=0)
