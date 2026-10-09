"""F07 protected schema upgrades and durable document behavior."""

import copy
import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from uuid import UUID

import pytest

from personalstyle.config import load_config
from personalstyle.document import (
    CONTRACT,
    DOCUMENT_CALLS,
    MAX_SEGMENTS,
    MAX_WORDS,
    OPERATION_SECONDS,
    SEGMENT_BYTES,
    inspect_document,
    invalidate_document_contract,
    rewrite_document,
    segment_document,
    verify_assembly,
)
from personalstyle.generation import RewriteRequest
from personalstyle.provider import Candidate, GenerationError, PreparedModel
from personalstyle.security import SecurityError, prepare_private_directory, prepare_private_file
from personalstyle.storage import APPLICATION_ID, SCHEMA_V2, ExampleStore, StoreError
from personalstyle.verification import CHECKS

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT_ID = str(UUID(int=99))


@pytest.fixture
def policy_store(tmp_path):
    """Real SQLite/state engine, OS ACL subprocesses covered by protected tests above."""
    from personalstyle.storage import SCHEMA, ExampleInput

    class PolicyStore(ExampleStore):
        def _boundary(self, check_sidecars=True):
            directory, file = self.path.parent.stat(), self.path.stat()
            return (directory.st_dev, directory.st_ino), (file.st_dev, file.st_ino)

        def _recheck(self, identity):
            if identity != self._boundary():
                raise SecurityError("changed")

    value = PolicyStore(tmp_path / "policy.db")
    with sqlite3.connect(value.path) as connection:
        for sql in SCHEMA.values():
            connection.execute(sql)
        connection.execute(f"PRAGMA application_id={APPLICATION_ID}")
        connection.execute("PRAGMA user_version=3")
        connection.execute("INSERT INTO store_meta VALUES (3,1)")
    # Initial add checks the actual OS ACL; seed this intentionally non-OS policy fixture directly.
    example = ExampleInput(str(UUID(int=10)), "Please send the note. Thank you.", "work.email",
                           "owner", "owner", "user_owned", True, True)
    with value.feedback_connection(write=True) as connection:
        connection.execute("INSERT INTO examples VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, '2026-10-08', 2)",
                           example.payload())
    return value


class EchoProvider:
    def __init__(self, fail_prepare=None):
        self.calls = 0
        self.preparations = 0
        self.fail_prepare = fail_prepare
        self.digest = "a" * 64

    def identity(self):
        return self.digest

    def prepare(self, context_tokens):
        self.calls += 1
        self.preparations += 1
        if self.preparations == self.fail_prepare:
            raise GenerationError("MODEL_RUNTIME_UNAVAILABLE")
        return PreparedModel("ollama", "qwen3:8b", self.digest, "0.18.2", context_tokens, 1472, 0.01)

    def generate_document(self, prepared, messages, **options):
        assert 0 < options["timeout_seconds"] <= OPERATION_SECONDS
        return self.generate(prepared, messages, **options)

    def generate(self, prepared, messages, **options):
        self.calls += 1
        data = json.loads(messages[1]["content"])
        if "candidate" in data:
            text = json.dumps(dict.fromkeys(CHECKS, True))
        else:
            original = data["request"]["original"]
            text = json.dumps({"units": original}) if isinstance(original, list) else original
        return Candidate(text, 0.01, 40, 40)


def paragraphs(*texts):
    # Separate meaningful units large enough that adjacent units cannot coalesce.
    return "\n\n".join(text + " Clear details." * 55 for text in texts)


def source(words):
    return "\n\n".join(" ".join([f"Section{n}"] + ["synthetic"] * 98 + ["complete."])
                        for n in range(words // 100))


def run(store, text, adapter=None, *, document_id=DOCUMENT_ID, settings=None, **changes):
    request = RewriteRequest(text, "Improve expression while retaining all information.", "work.email", ())
    from dataclasses import replace
    request = replace(request, **changes)
    return rewrite_document(store, document_id, request, settings or load_config(ROOT / "personalstyle.toml"),
                            provider=adapter or EchoProvider())


@pytest.mark.parametrize("words", [2000, 5000])
def test_multiple_bounded_segments_complete_and_restart_reuses(policy_store, words, caplog):
    adapter = EchoProvider()
    text = source(words)
    result = run(policy_store, text, adapter)
    assert result["state"] == "VERIFIED" and result["output"] == text
    assert result["total_segments"] > 1 and adapter.calls == result["total_segments"] * 5
    assert result["model_calls"] == adapter.calls <= DOCUMENT_CALLS
    assert all(s["calls"] <= 8 and max(s["attempts"].values()) <= 3 for s in result["segments"])
    calls = adapter.calls
    result = run(policy_store, text, adapter)
    assert adapter.calls == calls and result["reused_segments"] == result["total_segments"]
    assert text not in caplog.text


def test_declared_boundaries_and_structure():
    assert len(source(MAX_WORDS).split()) == MAX_WORDS
    assert segment_document(source(MAX_WORDS))
    for text in (source(MAX_WORDS) + " extra", "x" * (64 * 1024 + 1),
                 "\n\n".join(["x" * SEGMENT_BYTES] * (MAX_SEGMENTS + 1))):
        with pytest.raises(GenerationError, match="^DOCUMENT_INPUT_LIMIT$"):
            segment_document(text)
    for text in ("\n\nFirst.\r\n\r\nSecond.\n\n", "x" * (64 * 1024),
                 "界" * 2000, "word " * 300, "Sentence. " * 300):
        segments = segment_document(text)
        assert all(len(s["source"].encode()) <= SEGMENT_BYTES for s in segments)
        assert "".join(s["prefix"] + s["source"] + s["separator"] for s in segments) == text
        assert segment_document(text) == segments


def test_middle_failure_restart_and_local_source_edit(policy_store):
    text = paragraphs("First paragraph.", "Middle paragraph.", "Last paragraph.")
    adapter = EchoProvider(fail_prepare=2)
    first = run(policy_store, text, adapter)
    assert first["state"] == "BLOCKED" and first["verified_segments"] == 1
    assert [s["calls"] for s in first["segments"]] == [5, 1, 0]
    # Reopen the real SQLite state, carrying no in-process document continuation object.
    reopened = type(policy_store)(policy_store.path)
    adapter.fail_prepare = None
    result = run(reopened, text, adapter)
    assert result["state"] == "VERIFIED" and result["reused_segments"] == 1
    before = adapter.calls
    result = run(reopened, text.replace("Middle", "Changed middle"), adapter)
    assert result["state"] == "VERIFIED" and result["reused_segments"] == 2
    assert adapter.calls == before + 5


@pytest.mark.parametrize("change", ["intent", "context", "constraints", "profile", "model", "prompt"])
def test_dependency_invalidation(policy_store, change, monkeypatch):
    from personalstyle import document

    adapter = EchoProvider()
    text = paragraphs("One paragraph.", "Second paragraph.")
    assert run(policy_store, text, adapter)["state"] == "VERIFIED"
    before = adapter.calls
    arguments = {}
    if change == "intent":
        arguments["intent"] = "Make it clearer."
    elif change == "context":
        with policy_store.feedback_connection(write=True) as connection:
            connection.execute("UPDATE examples SET context='friends.chat'")
        arguments["context"] = "friends.chat"
    elif change == "constraints":
        arguments["constraints"] = ("max_words:500",)
    elif change == "profile":
        with policy_store.feedback_connection(write=True) as connection:
            connection.execute("UPDATE examples SET text='Different authorized expression.'")
    elif change == "model":
        adapter.digest = "b" * 64
    else:
        # Dependency identity changes even while F04 executable semantics stay the same.
        original = document.fingerprint
        monkeypatch.setattr(document, "CONTRACT", "long_document.test")
        # An incompatible document contract cannot be guessed on reopen.
        with pytest.raises(StoreError, match="^DOCUMENT_CHECKPOINT_INVALID$"):
            run(policy_store, text, adapter)
        assert adapter.calls == before
        assert original({"version": 1}) != original({"version": 2})
        return
    result = run(policy_store, text, adapter, **arguments)
    assert result["state"] == "VERIFIED" and result["reused_segments"] == 0
    assert adapter.calls == before + 10


def test_unrelated_context_revision_and_structure_only_reuses(policy_store):
    adapter = EchoProvider()
    text = paragraphs("One paragraph.", "Second paragraph.")
    run(policy_store, text, adapter)
    with policy_store.feedback_connection(write=True) as connection:
        connection.execute("UPDATE store_meta SET profile_version=profile_version+1")
        connection.execute("INSERT INTO examples SELECT ?, 'Unrelated.', 'friends.chat', supplier, "
                           "authorizer, source_kind, 1, 0, 1, created_at, 2 FROM examples LIMIT 1",
                           (str(UUID(int=15)),))
    calls = adapter.calls
    result = run(policy_store, text.replace("\n\n", "\r\n\r\n"), adapter)
    assert result["state"] == "VERIFIED" and result["reused_segments"] == 2
    assert adapter.calls == calls


def test_insert_and_reorder_reuse_unchanged_segment_proofs(policy_store):
    adapter = EchoProvider()
    run(policy_store, paragraphs("First paragraph.", "Second paragraph."), adapter)
    calls = adapter.calls
    result = run(policy_store, paragraphs("New paragraph.", "Second paragraph.", "First paragraph."), adapter)
    assert result["state"] == "VERIFIED"
    assert result["reused_segments"] == 2
    assert adapter.calls == calls + 5


def test_assembly_rejects_loss_reorder_global_constraints_and_corruption(policy_store):
    text = paragraphs("Alice has 12 notes on Monday.", "Bob has 34 notes on Tuesday.")
    run(policy_store, text)
    manifest, segments = policy_store.document_checkpoint(str(UUID(int=99)))
    request = RewriteRequest(text, manifest["dependencies"]["intent"], "work.email", ())
    for output in (segments[1]["output"] + "\n\n" + segments[0]["output"], segments[0]["output"]):
        with pytest.raises(GenerationError, match="^DOCUMENT_VERIFICATION_FAILED$"):
            verify_assembly(request, manifest, segments, output)
    assert run(policy_store, text, constraints=("max_words:2",))["state"] == "BLOCKED"
    with policy_store.feedback_connection(write=True) as connection:
        damaged = copy.deepcopy(segments[0])
        damaged["output"] = "Replaced sensitive text"
        connection.execute("UPDATE document_segments SET payload=? WHERE document_id=? AND id=?",
                           (json.dumps(damaged), manifest["id"], damaged["id"]))
    with pytest.raises(StoreError, match="^DOCUMENT_CHECKPOINT_INVALID$"):
        inspect_document(policy_store, manifest["id"])


def test_crash_reservations_and_expired_deadline_do_not_reset(policy_store, monkeypatch):
    class Crash(EchoProvider):
        def prepare(self, context_tokens):
            raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        run(policy_store, "Synthetic paragraph.", Crash())
    first = inspect_document(policy_store, str(UUID(int=99)))
    assert first["model_calls"] == 8 and first["segments"][0]["calls"] == 8
    adapter = EchoProvider()
    result = run(policy_store, "Synthetic paragraph.", adapter)
    assert result["state"] == "BLOCKED" and adapter.calls == 0
    from personalstyle import document
    monkeypatch.setattr(document.time, "time", lambda: first["deadline"] + 1)
    result = run(policy_store, "Changed paragraph.", adapter)
    assert result["state"] == "BLOCKED" and adapter.calls == 0


def test_same_failure_twice_blocks_further_resume(policy_store):
    class Failing(EchoProvider):
        def prepare(self, context_tokens):
            self.calls += 1
            raise GenerationError("MODEL_RUNTIME_UNAVAILABLE")

    adapter = Failing()
    for _ in range(3):
        result = run(policy_store, "Synthetic paragraph.", adapter)
        assert result["state"] == "BLOCKED"
    assert adapter.calls == 2


def test_hard_failure_never_gets_a_fresh_generation_budget(policy_store):
    class Rejecting(EchoProvider):
        def generate(self, prepared, messages, **options):
            self.calls += 1
            data = json.loads(messages[1]["content"])
            if "candidate" in data:
                return Candidate(json.dumps(dict.fromkeys(CHECKS, False)), 0.01, 40, 40)
            # A failed semantic verdict leads to a materially changed repair instruction;
            # unchanged repair output terminates F04 rather than looping.
            original = data["request"]["original"]
            return Candidate(json.dumps({"units": original}) if isinstance(original, list) else original,
                             0.01, 40, 40)

    adapter = Rejecting()
    first = run(policy_store, "Synthetic paragraph.", adapter)
    assert first["state"] == "BLOCKED" and first["failure_code"] == "IDENTICAL_REPAIR"
    calls = adapter.calls
    second = run(policy_store, "Synthetic paragraph.", adapter)
    assert second["state"] == "BLOCKED" and adapter.calls == calls
    assert "output" not in second


def test_valid_schema2_feedback_and_active_preference_survive_upgrade(policy_store):
    from personalstyle.feedback import FeedbackInput, record_feedback
    from personalstyle.generation import generate_pair
    from personalstyle.learning import derive_learning_evidence, evaluate_context_preferences
    from personalstyle.verification import verify_pair

    settings = load_config(ROOT / "personalstyle.toml")
    settings["versions"]["storage_schema"] = 2  # Historical schema-2 run provenance.
    request = RewriteRequest("First sentence. Second sentence.", "Clarify expression.", "work.email", ())
    adapter = EchoProvider()
    for n in range(3):
        pair = generate_pair(request, settings, policy_store, provider=adapter)
        receipt = verify_pair(request, pair, settings, policy_store, provider=adapter)
        record_feedback(policy_store, receipt, FeedbackInput(
            str(UUID(int=200 + n)), "edit", "personalized", "owner", "owner", True, True, False,
            "First sentence.\n\nSecond sentence.", classification_hint="style_expression"))
    evaluate_context_preferences(policy_store, "work.email")
    with policy_store.feedback_connection() as connection:
        active_before = policy_store.active_preferences(connection, "work.email")
        assert active_before
        before = {name: connection.execute(f"SELECT * FROM {name}").fetchall()
                  for name in ("examples", "feedback", "preferences")}
    # Reconstruct exact merged schema 2, including real engine-generated canonical records.
    with sqlite3.connect(policy_store.path) as connection:
        connection.execute("DROP TABLE document_segments")
        connection.execute("DROP TABLE documents")
        connection.execute("UPDATE store_meta SET schema_version=2")
        connection.execute("PRAGMA user_version=2")
    assert derive_learning_evidence(policy_store, "work.email")["eligible_observation_count"] == 3
    policy_store.migrate_document_schema()
    assert derive_learning_evidence(policy_store, "work.email")["eligible_observation_count"] == 3
    with policy_store.feedback_connection() as connection:
        assert policy_store.active_preferences(connection, "work.email") == active_before
        assert before == {name: connection.execute(f"SELECT * FROM {name}").fetchall() for name in before}


def test_protected_document_progress_and_dependencies_in_fresh_process(schema2):
    with sqlite3.connect(schema2.path) as connection:
        connection.execute("DELETE FROM feedback")
        connection.execute("DELETE FROM preferences")
    schema2.migrate_document_schema()
    result = run(schema2, paragraphs("First paragraph.", "Middle paragraph.", "Last paragraph."),
                 EchoProvider(fail_prepare=2))
    assert result["state"] == "BLOCKED" and result["verified_segments"] == 1
    script = ("import json,sys; from pathlib import Path; from personalstyle.storage import ExampleStore; "
              "from personalstyle.document import inspect_document; "
              "print(json.dumps(inspect_document(ExampleStore(Path(sys.argv[1])),sys.argv[2])))")
    child = subprocess.run([sys.executable, "-c", script,
                            str(schema2.path), str(UUID(int=99))], capture_output=True,
                           text=True, timeout=30, check=True)
    persisted = json.loads(child.stdout)
    assert persisted["state"] == "BLOCKED" and persisted["model_calls"] == 6
    assert persisted["verified_segments"] == 1 and len(persisted["segments"][0]["dependency"]) == 64
    assert "First paragraph" not in child.stdout and "First paragraph" not in child.stderr


@pytest.fixture
def schema2(tmp_path):
    prepare_private_directory(tmp_path / "profile")
    store = ExampleStore(tmp_path / "profile" / "profile.db")
    prepare_private_file(store.path)
    with sqlite3.connect(store.path) as connection:
        for sql in SCHEMA_V2.values():
            connection.execute(sql)
        connection.execute(f"PRAGMA application_id={APPLICATION_ID}")
        connection.execute("PRAGMA user_version=2")
        connection.execute("INSERT INTO store_meta VALUES (2,17)")
        connection.execute("INSERT INTO examples VALUES (?, 'Synthetic', 'work.email', 'owner', "
                           "'owner', 'user_owned', 1, 0, 1, '2026-10-08', 2)", (str(UUID(int=1)),))
        # Representative existing canonical payloads are retained byte-for-byte, not reinterpreted.
        connection.execute("INSERT INTO feedback VALUES (?, 'work.email', '{}', 1, 17, '2026-10-08', ?, '[]')",
                           (str(UUID(int=2)), str(UUID(int=3))))
        connection.execute("INSERT INTO preferences VALUES (?, 1, 'work.email', 'line_count', '{}')",
                           (str(UUID(int=4)),))
    return store


def test_schema2_upgrade_preserves_all_canonical_data_and_is_idempotent(schema2):
    with sqlite3.connect(schema2.path) as connection:
        before = {name: connection.execute(f"SELECT * FROM {name}").fetchall()
                  for name in ("examples", "feedback", "preferences")}
    schema2.migrate_document_schema()
    with sqlite3.connect(schema2.path) as connection:
        assert connection.execute("PRAGMA user_version").fetchone() == (3,)
        assert connection.execute("SELECT * FROM store_meta").fetchone() == (3, 17)
        assert before == {name: connection.execute(f"SELECT * FROM {name}").fetchall()
                          for name in before}
    snapshot = schema2.path.read_bytes()
    ExampleStore(schema2.path).migrate_document_schema()
    assert schema2.path.read_bytes() == snapshot
    assert schema2.get(str(UUID(int=1)))["text"] == "Synthetic"


def test_schema3_failed_guard_rolls_back_entire_migration(schema2, monkeypatch):
    before = schema2.path.read_bytes()
    original = schema2._recheck
    calls = 0

    def recheck(identity):
        nonlocal calls
        calls += 1
        if calls == 3:
            raise SecurityError("changed")
        original(identity)

    monkeypatch.setattr(schema2, "_recheck", recheck)
    with pytest.raises(StoreError, match="^STORAGE_BOUNDARY_INVALID$"):
        schema2.migrate_document_schema()
    assert schema2.path.read_bytes() == before


def test_checkpoint_atomic_cas_restart_and_query_plan(schema2):
    schema2.migrate_document_schema()
    manifest = {"id": str(UUID(int=6)), "revision": 1, "state": "BLOCKED", "calls": 2}
    segment = {"id": "0000", "ordinal": 0, "state": "VERIFIED", "dependency": "a" * 64}
    schema2.save_document_checkpoint(manifest, [segment], expected_revision=0)
    assert ExampleStore(schema2.path).document_checkpoint(manifest["id"]) == (manifest, [segment])
    with pytest.raises(StoreError, match="^DOCUMENT_CHECKPOINT_CONFLICT$"):
        schema2.save_document_checkpoint(manifest, [], expected_revision=0)
    with schema2.feedback_connection() as connection:
        plan = connection.execute("EXPLAIN QUERY PLAN SELECT payload FROM document_segments "
                                  "WHERE document_id=? ORDER BY ordinal", (manifest["id"],)).fetchall()
        assert "document_order" in str(plan) and "TEMP B-TREE" not in str(plan)
        assert connection.execute("SELECT profile_version FROM store_meta").fetchone() == (17,)
    script = ("import json,sys; from pathlib import Path; from personalstyle.storage import ExampleStore; "
              "print(json.dumps(ExampleStore(Path(sys.argv[1])).document_checkpoint(sys.argv[2])))")
    result = subprocess.run([sys.executable, "-c", script,
                             str(schema2.path), manifest["id"]], capture_output=True, text=True,
                            timeout=30, check=True)
    assert json.loads(result.stdout) == [manifest, [segment]]


def test_adjacent_coalescing_preserves_internal_boundaries(policy_store):
    from scripts.f07_acceptance import synthetic_document

    for words, count in ((2000, 10), (5000, 25)):
        text = synthetic_document(words)
        segments = segment_document(text)
        assert len(segments) == count
        assert all("\n\n" in s["source"] for s in segments)
        assert segment_document(text) == segments
        result = run(policy_store, text, document_id=str(UUID(int=words)))
        assert result["state"] == "VERIFIED" and result["output"] == text
        assert result["model_calls"] == count * 5


def test_coalesced_paragraph_loss_or_reorder_is_not_verified(policy_store):
    class Reordered(EchoProvider):
        def generate(self, prepared, messages, **options):
            result = super().generate(prepared, messages, **options)
            data = json.loads(messages[1]["content"])
            if "candidate" not in data:
                return Candidate("Bob has 34 notes.\n\nAlice has 12 notes.", 0.01, 40, 40)
            return result

    result = run(policy_store, "Alice has 12 notes.\n\nBob has 34 notes.", Reordered())
    assert result["state"] == "BLOCKED" and "output" not in result
    assert result["failure_code"] == "DOCUMENT_STRUCTURE_INVALID"


def test_superseded_contract_preserves_stale_evidence_and_budgets(policy_store):
    from personalstyle.document import _seal

    text = "Synthetic paragraph."
    run(policy_store, text)
    manifest, segments = policy_store.document_checkpoint(DOCUMENT_ID)
    evidence, deadline, calls = segments[0]["evidence"], manifest["deadline"], manifest["calls"]
    manifest["contract"] = "long_document.v1"
    revision = manifest["revision"]
    manifest["revision"] += 1
    for segment in segments:
        _seal(segment)
    policy_store.save_document_checkpoint(manifest, segments, expected_revision=revision)
    result = invalidate_document_contract(policy_store, DOCUMENT_ID)
    assert result["state"] == "BLOCKED" and result["verified_segments"] == 0
    assert result["segments"][0]["state"] == "STALE"
    persisted, saved = policy_store.document_checkpoint(DOCUMENT_ID)
    assert saved[0]["evidence"] == evidence and saved[0]["output"] == text
    assert persisted["deadline"] == deadline and persisted["calls"] == calls
    adapter = EchoProvider()
    assert run(policy_store, text, adapter)["state"] == "BLOCKED" and adapter.calls == 0


def test_document_operation_is_capped_by_remaining_deadline(monkeypatch):
    from personalstyle.document import _ReservedProvider

    class Observed(EchoProvider):
        def generate_document(self, prepared, messages, **options):
            self.limit = options["timeout_seconds"]
            return Candidate("synthetic", 0.01, 40, 40)

    adapter = Observed()
    from personalstyle import document
    monkeypatch.setattr(document.time, "time", lambda: 100)
    reserved = _ReservedProvider(adapter, {"deadline": 235, "dependencies": {"digest": adapter.digest}}, 0, {"generic": 0, "personalized": 0})
    prepared = reserved.prepare(8000)
    assert prepared.framing_bytes == 1472 + reserved.framing_extra
    reserved.manifest["deadline"] = 135
    reserved.generate(prepared, [{"role": "system", "content": "verify"}],
                      timeout_seconds=60, max_tokens=2000, temperature=0.2)
    assert adapter.limit == 35 and reserved.calls == 2
    assert CONTRACT == "long_document.v3"


@pytest.mark.parametrize("damage", ["missing", "duplicate", "reorder", "merge", "split", "extra", "keys"])
def test_structured_units_reject_invalid_mapping(damage):
    from personalstyle.document import _decode_units, _source_units

    source = "First paragraph.\r\n\r\nSecond paragraph."
    units = _source_units(source)
    if damage == "missing":
        units.pop()
    elif damage == "duplicate":
        units[1] = dict(units[0])
    elif damage == "reorder":
        units.reverse()
    elif damage == "merge":
        units = [{"id": "u0", "text": "First paragraph. Second paragraph."}]
    elif damage == "split":
        units[0]["text"] = "First.\n\nExtra paragraph."
    elif damage == "extra":
        units.append({"id": "u2", "text": "Extra paragraph."})
    else:
        raw = '{"units":[],"units":[]}'
        with pytest.raises(GenerationError, match="^DOCUMENT_STRUCTURE_INVALID$"):
            _decode_units(raw, source)
        return
    with pytest.raises(GenerationError, match="^DOCUMENT_STRUCTURE_INVALID$"):
        _decode_units(json.dumps({"units": units}), source)


def test_source_separators_are_reconstructed_not_generated(policy_store):
    from personalstyle.document import _decode_units, _source_units

    text = "First paragraph.\r\n \r\nSecond paragraph.\n\n\nThird paragraph."
    units = _source_units(text)
    for unit in units:
        unit["text"] = "  \n" + unit["text"] + "\n  "
    assert _decode_units(json.dumps({"units": units}), text) == text
    result = run(policy_store, text)
    assert result["state"] == "VERIFIED" and result["output"] == text
    manifest, saved = policy_store.document_checkpoint(DOCUMENT_ID)
    assert len(saved[0]["structure"]) == 3
    assert [u["id"] for u in saved[0]["structure"]] == ["u0", "u1", "u2"]
    assert manifest["contract"] == "long_document.v3"
    assert result["model_calls"] == 5


def test_structured_generation_still_invokes_f04_semantic_checks(policy_store, caplog):
    class Inspected(EchoProvider):
        def __init__(self):
            super().__init__(); self.semantic_calls = 0

        def generate_document(self, prepared, messages, **options):
            data = json.loads(messages[1]["content"])
            if "candidate" in data:
                self.semantic_calls += 1
                assert isinstance(data["request"]["original"], str)
                assert isinstance(data["candidate"], str)
                assert options["response_schema"] is None
            else:
                assert isinstance(data["request"]["original"], list)
                assert options["response_schema"]["properties"]["units"]["minItems"] == 2
            return super().generate_document(prepared, messages, **options)

    provider = Inspected()
    text = "First source paragraph.\n\nSecond source paragraph."
    result = run(policy_store, text, provider)
    assert result["state"] == "VERIFIED" and provider.semantic_calls == 2
    assert text not in caplog.text


@pytest.mark.parametrize("old_contract", ["long_document.v1", "long_document.v2"])
def test_prior_generated_failures_preserved_as_stale(policy_store, old_contract):
    from personalstyle.document import _seal

    adapter = EchoProvider(fail_prepare=1)
    original = run(policy_store, "Synthetic paragraph.", adapter)
    assert original["state"] == "BLOCKED"
    manifest, segments = policy_store.document_checkpoint(DOCUMENT_ID)
    manifest["contract"] = old_contract
    revision = manifest["revision"]
    manifest["revision"] += 1
    for segment in segments:
        _seal(segment)
    policy_store.save_document_checkpoint(manifest, segments, expected_revision=revision)
    result = invalidate_document_contract(policy_store, DOCUMENT_ID)
    preserved, saved = policy_store.document_checkpoint(DOCUMENT_ID)
    assert result["segments"][0]["state"] == "STALE"
    assert saved[0]["failure_code"] == "MODEL_RUNTIME_UNAVAILABLE"
    assert saved[0]["previous_state"] == "BLOCKED"
    assert result["model_calls"] == original["model_calls"]
    assert preserved["deadline"] == original["deadline"]
