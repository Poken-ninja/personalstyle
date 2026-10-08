"""Authorized feedback on engine-verified rewrites, inside the canonical SQLite store."""

import json
import re
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from personalstyle.generation import RewriteRequest
from personalstyle.storage import MAX_TEXT_BYTES, ExampleStore, StoreError
from personalstyle.verification import CALENDAR, NUMBERS, deterministic_failures, verified_source

CLASSIFICATIONS = {
    "style_expression", "meaning_fact", "constraint", "context_recipient", "mixed_unknown",
}
CLASSIFIER = "feedback_classification.v1"


@dataclass(frozen=True, repr=False)
class FeedbackInput:
    id: str
    event_type: str
    candidate_mode: str
    supplier: str
    authorizer: str
    authorized: bool
    learning_authorized: bool
    held_out: bool
    edited_text: str | None = None
    corrected_context: str | None = None
    classification_hint: str | None = None

    def validate(self) -> None:
        try:
            valid = (
                type(self.id) is str and str(UUID(self.id)) == self.id
                and self.event_type in {"accept", "edit"}
                and self.candidate_mode in {"generic", "personalized"}
                and all(type(s) is str and s.strip() and len(s.encode()) <= 256
                        for s in (self.supplier, self.authorizer))
                and self.authorized is True
                and type(self.learning_authorized) is bool and type(self.held_out) is bool
                and (self.corrected_context is None or (
                    type(self.corrected_context) is str
                    and re.fullmatch(r"[a-z][a-z0-9_.-]{0,63}", self.corrected_context) is not None
                ))
                and (self.classification_hint is None or self.classification_hint in CLASSIFICATIONS)
            )
            if self.event_type == "accept":
                valid = valid and all(v is None for v in (
                    self.edited_text, self.corrected_context, self.classification_hint))
            else:
                valid = (valid and isinstance(self.edited_text, str)
                         and bool(self.edited_text.strip())
                         and len(self.edited_text.encode()) <= MAX_TEXT_BYTES)
        except (ValueError, TypeError, AttributeError, UnicodeError):
            valid = False
        if not valid:
            raise StoreError("INVALID_FEEDBACK")


def classify_edit(request: RewriteRequest, accepted: str, event: FeedbackInput) -> str:
    """Conclusive presentation edits only; unestablished semantic edits stay unknown."""
    if event.event_type == "accept":
        return "acceptance"
    edited = event.edited_text or ""
    categories = set()
    if (
        set(NUMBERS.findall(accepted)) != set(NUMBERS.findall(edited))
        or {s.casefold() for s in CALENDAR.findall(accepted)}
        != {s.casefold() for s in CALENDAR.findall(edited)}
    ):
        categories.add("meaning_fact")
    if event.corrected_context is not None and event.corrected_context != request.context:
        categories.add("context_recipient")
    if set(deterministic_failures(request, edited)) - {"REQUIRED_INFORMATION_MISSING"}:
        categories.add("constraint")
    hint = event.classification_hint
    if hint is not None and hint != "style_expression":
        categories.add(hint)
    if categories:
        return next(iter(categories)) if len(categories) == 1 else "mixed_unknown"
    # Exact lexical/punctuation tokens, only separator formatting changed. No semantic guess.
    if hint == "style_expression" and accepted != edited and accepted.split() == edited.split():
        return "style_expression"
    return "mixed_unknown"


def _decode(row: tuple[Any, ...]) -> dict[str, Any]:
    try:
        if type(row[3]) is not int or row[3] != 1 or type(row[4]) is not int or row[4] < 1:
            raise ValueError
        payload = json.loads(row[2])
        if len(row[2].encode()) > MAX_TEXT_BYTES:
            raise ValueError
        event = FeedbackInput(**payload["event"])
        event.validate()
        raw_request = payload["request"]
        request = RewriteRequest(**{**raw_request, "constraints": tuple(raw_request["constraints"])})
        request.validate()
        if (
            row[0] != event.id or row[1] != request.context or payload["context"] != request.context
            or payload["classification_version"] != CLASSIFIER
            or type(payload["accepted_text"]) is not str
            or not payload["accepted_text"].strip()
            or len(payload["accepted_text"].encode()) > MAX_TEXT_BYTES
            or payload["classification"] != classify_edit(request, payload["accepted_text"], event)
            or payload["source"]["context"] != request.context
            or payload["source"]["candidate_mode"] != event.candidate_mode
            or payload["source"]["verification_status"] != "verified"
        ):
            raise ValueError
    except (KeyError, TypeError, ValueError, AttributeError):
        raise StoreError("FEEDBACK_SOURCE_INVALID") from None
    return {**payload, "record_version": row[3], "profile_version": row[4], "created_at": row[5]}


def record_feedback(
    store: ExampleStore, verified_pair: dict[str, Any], event: FeedbackInput,
) -> dict[str, Any]:
    event.validate()  # No filesystem/SQL action for unauthorized input.
    source = verified_source(verified_pair)
    raw_request, result = source["request"], source["result"]
    request = RewriteRequest(**{**raw_request, "constraints": tuple(raw_request["constraints"])})
    candidate = result["candidates"][event.candidate_mode]
    if event.event_type == "edit" and event.edited_text == candidate["text"]:
        raise StoreError("INVALID_FEEDBACK")
    classification = classify_edit(request, candidate["text"], event)
    provenance = {key: result[key] for key in (
        "run_id", "context", "versions", "model_identity", "prompt_contract", "verification_prompt",
        "repair_prompt", "verification_method", "model_calls", "generation_attempts",
    )}
    provenance.update({key: candidate[key] for key in (
        "selected_examples", "writing_dna_source", "verification_status",
    )})
    provenance["candidate_mode"] = event.candidate_mode
    provenance["hard_check_history"] = result["history"][event.candidate_mode]
    payload = {
        "event": asdict(event), "context": request.context, "request": raw_request,
        "source": provenance, "accepted_text": candidate["text"],
        "classification": classification, "classification_version": CLASSIFIER,
    }
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if len(serialized.encode()) > MAX_TEXT_BYTES:
        raise StoreError("INVALID_FEEDBACK")
    with store.feedback_connection(write=True) as connection:
        existing = connection.execute("SELECT payload FROM feedback WHERE id=?", (event.id,)).fetchone()
        if existing is not None and existing[0] != serialized:
            raise StoreError("IDEMPOTENCY_CONFLICT")
        if existing is None:
            connection.execute("UPDATE store_meta SET profile_version=profile_version+1")
            version = connection.execute("SELECT profile_version FROM store_meta").fetchone()[0]
            connection.execute("INSERT INTO feedback VALUES (?, ?, ?, 1, ?, ?)", (
                event.id, request.context, serialized, version, datetime.now(UTC).isoformat(),
            ))
        stored = connection.execute("SELECT payload FROM feedback WHERE id=?", (event.id,)).fetchone()
        if stored != (serialized,):
            raise StoreError("PERSISTENCE_VERIFICATION_FAILED")
    inspected = get_feedback(store, event.id)
    if inspected is None or inspected["event"] != asdict(event):
        raise StoreError("PERSISTENCE_VERIFICATION_FAILED")
    return inspected


def get_feedback(store: ExampleStore, event_id: str) -> dict[str, Any] | None:
    try:
        if str(UUID(event_id)) != event_id:
            raise ValueError
    except (ValueError, TypeError, AttributeError):
        raise StoreError("INVALID_FEEDBACK") from None
    with store.feedback_connection() as connection:
        row = connection.execute("SELECT * FROM feedback WHERE id=?", (event_id,)).fetchone()
        return None if row is None else _decode(row)


@contextmanager
def feedback_snapshot(
    store: ExampleStore, context: str, deadline: float,
) -> Iterator[tuple[int, Iterator[dict[str, Any]]]]:
    if type(context) is not str or re.fullmatch(r"[a-z][a-z0-9_.-]{0,63}", context) is None:
        raise StoreError("FEEDBACK_SOURCE_INVALID")
    with store.feedback_connection() as connection:
        version = connection.execute("SELECT profile_version FROM store_meta").fetchone()[0]
        cursor = connection.execute(
            "SELECT * FROM feedback WHERE context=? ORDER BY id COLLATE BINARY", (context,),
        )

        def rows() -> Iterator[dict[str, Any]]:
            for row in cursor:
                if time.monotonic() >= deadline:
                    raise StoreError("PROFILE_RESOURCE_LIMIT")
                yield _decode(row)

        yield version, rows()
    if time.monotonic() >= deadline:
        raise StoreError("PROFILE_RESOURCE_LIMIT")
