"""Inspectable scoped evidence; promotion stays blocked until the owner defines policy."""

import hashlib
import re
import time
from collections import Counter
from typing import Any

from personalstyle.feedback import feedback_snapshot
from personalstyle.storage import ExampleStore, StoreError

ALGORITHM = "learning_evidence.v1"
POLICY_BLOCKER = "F06_PROMOTION_POLICY_UNRESOLVED"


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
            texts = [record["accepted_text"], event["edited_text"]]
            normalized = [text.replace("\r\n", "\n").replace("\r", "\n") for text in texts]
            # These describe observed presentation changes, never desired active rules.
            measurements = {
                "paragraph_count": [len(re.split(r"\n[ \t]*\n+", s.strip())) for s in normalized],
                "line_count": [len(s.splitlines()) for s in normalized],
                "separator_characters": [sum(c.isspace() for c in s) for s in normalized],
            }
            for feature, (before, after) in measurements.items():
                if before != after:
                    counts[feature, "increase" if after > before else "decrease"] += 1
    return {
        "context": context, "profile_schema": 1, "algorithm_version": ALGORITHM,
        "source_profile_version": version, "source_fingerprint": fingerprint.hexdigest(),
        "eligible_observation_count": eligible,
        "hypotheses": [
            {"context": context, "feature": feature, "observed_change": change,
             "observation_count": count, "state": "unpromoted"}
            for (feature, change), count in sorted(counts.items())
        ],
        "promotion_state": "BLOCKED", "failure_code": POLICY_BLOCKER,
        "active_preferences": [],
    }
