"""Explicit, deterministic exact-context preference evaluation; no background mutation."""

import hashlib
import json
import re
import time
from collections import Counter
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from personalstyle.feedback import _decode, feedback_snapshot, presentation_changes
from personalstyle.storage import ExampleStore, StoreError

ALGORITHM = "learning_evidence.v1"
POLICY = "context_preference_promotion.v1"
FEATURES = ("paragraph_count", "line_count", "separator_characters")


def derive_learning_evidence(
    store: ExampleStore, context: str, *, timeout_seconds: int = 60,
) -> dict[str, Any]:
    if type(timeout_seconds) is not int or not 0 < timeout_seconds <= 60:
        raise StoreError("PROFILE_RESOURCE_LIMIT")
    deadline = time.monotonic() + timeout_seconds
    counts: Counter[tuple[str, str]] = Counter()
    eligible = 0
    fingerprint = hashlib.sha256()
    with feedback_snapshot(store, context, deadline) as (version, rows):
        for record in rows:
            event = record["event"]
            if (
                event["event_type"] != "edit" or not event["learning_authorized"]
                or event["held_out"] or record["classification"] != "style_expression"
            ):
                continue
            eligible += 1
            fingerprint.update(f"{event['id']}:{record['record_version']}\n".encode("ascii"))
            for feature, direction in presentation_changes(
                record["accepted_text"], event["edited_text"],
            ).items():
                counts[feature, direction] += 1
    return {
        "context": context, "profile_schema": 1, "algorithm_version": ALGORITHM,
        "source_profile_version": version, "source_fingerprint": fingerprint.hexdigest(),
        "eligible_observation_count": eligible,
        "hypotheses": [
            {"context": context, "feature": feature, "observed_change": change,
             "observation_count": count, "state": "unpromoted"}
            for (feature, change), count in sorted(counts.items())
        ],
        "promotion_state": "NOT_EVALUATED", "policy_version": POLICY,
        "active_preferences": [],
    }


# Three fixed feature queries, not one query per feedback record. GROUP BY streams
# indexed run IDs; SQLite's LIMIT keeps only the latest three metadata units.
UNIT_QUERY = (
    "SELECT run_id, MIN(id), MIN(profile_version), MIN(json_extract(observations, ?)) "
    "FROM feedback WHERE context=? AND json_extract(observations, ?) IS NOT NULL "
    "GROUP BY run_id HAVING MIN(json_extract(observations, ?))=MAX(json_extract(observations, ?)) "
    "ORDER BY MIN(profile_version) DESC, MIN(id) DESC LIMIT 3"
)


def evaluate_context_preferences(
    store: ExampleStore, context: str, *, timeout_seconds: int = 60,
) -> list[dict[str, Any]]:
    """Explicit user-triggered evaluation, atomically append any changed preference states."""
    if type(context) is not str or re.fullmatch(r"[a-z][a-z0-9_.-]{0,63}", context) is None:
        raise StoreError("FEEDBACK_SOURCE_INVALID")
    if type(timeout_seconds) is not int or not 0 < timeout_seconds <= 60:
        raise StoreError("PROFILE_RESOURCE_LIMIT")
    deadline = time.monotonic() + timeout_seconds
    with store.feedback_connection(write=True) as connection:
        # Validate cached structural observations against accepted, authorized feedback.
        # One streamed query; retain no source writing or corpus-sized Python collection.
        for row in connection.execute(
            "SELECT * FROM feedback WHERE context=? ORDER BY id COLLATE BINARY", (context,),
        ):
            if time.monotonic() >= deadline:
                raise StoreError("PROFILE_RESOURCE_LIMIT")
            _decode(row)
        previous = {p["feature"]: p for p in store.preference_records(connection, context)}
        source_version = connection.execute("SELECT profile_version FROM store_meta").fetchone()[0]
        changes = []
        for feature in FEATURES:
            if time.monotonic() >= deadline:
                raise StoreError("PROFILE_RESOURCE_LIMIT")
            path = "$." + feature
            rows = connection.execute(UNIT_QUERY, (path, context, path, path, path)).fetchall()
            units = [{"run_id": row[0], "feedback_id": row[1], "direction": row[3]}
                     for row in reversed(rows)]
            old = previous.get(feature)
            direction = old["direction"] if old else None
            state = "unpromoted"
            if len(units) == 3:
                if len({u["direction"] for u in units}) == 1:
                    state, direction = "active", units[0]["direction"]
                else:
                    state = "contested"
            value = {
                "id": str(uuid5(NAMESPACE_URL, f"personalstyle/{POLICY}/{context}/{feature}")),
                "version": old["version"] + 1 if old else 1,
                "context": context, "feature": feature, "direction": direction, "state": state,
                "policy_version": POLICY, "supporting_units": units,
                "supporting_feedback_ids": [u["feedback_id"] for u in units],
                "supporting_run_ids": [u["run_id"] for u in units],
                "source_profile_version": source_version,
            }
            if old is not None and all(value[k] == old[k] for k in value
                                       if k not in {"version", "source_profile_version"}):
                continue
            if old is None and not units:
                continue
            changes.append(value)
        if changes:
            connection.executemany("INSERT INTO preferences VALUES (?, ?, ?, ?, ?)", [
                (p["id"], p["version"], context, p["feature"], json.dumps(p, sort_keys=True))
                for p in changes
            ])
            connection.execute("UPDATE store_meta SET profile_version=profile_version+1")
        result = store.preference_records(connection, context)
        if any(p not in result for p in changes):
            raise StoreError("PERSISTENCE_VERIFICATION_FAILED")
        if time.monotonic() >= deadline:
            raise StoreError("PROFILE_RESOURCE_LIMIT")
    return result
