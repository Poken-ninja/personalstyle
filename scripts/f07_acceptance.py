"""One bounded real-provider qualification using synthetic writing and protected state."""

import json
import logging
import tempfile
import time
from pathlib import Path
from uuid import uuid4

from personalstyle.config import load_config
from personalstyle.document import DOCUMENT_SECONDS, OPERATION_SECONDS, rewrite_document
from personalstyle.generation import RewriteRequest
from personalstyle.provider import GenerationError, OllamaProvider
from personalstyle.security import prepare_private_directory
from personalstyle.storage import ExampleInput, ExampleStore, StoreError


def synthetic_document(words: int) -> str:
    sentences = [
        "The team reviews the draft and records the decisions before sharing the update with colleagues.",
        "Each reviewer checks the details carefully and explains any concern in a separate short note.",
        "The coordinator collects these notes and keeps the document organized for the next discussion.",
        "Clear descriptions help the group understand the proposal and decide which action should follow.",
        "The final summary preserves the agreed facts and gives everyone a consistent account of the discussion.",
    ]
    # Fixed synthetic paragraphs, exactly 100 words each, no held-out/user content.
    closing = (
        "After the review, everyone receives the approved summary, understands the next action, "
        "and can ask the coordinator for clarification before work begins on the proposal."
    )
    vocabulary = " ".join([*sentences, closing]).split()
    assert len(vocabulary) == 99
    paragraphs = []
    for ordinal in range(words // 100):
        paragraphs.append(" ".join([f"Section{ordinal}.", *vocabulary]))
    return "\n\n".join(paragraphs)


class Capture(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(record.getMessage())


class ProgressStore(ExampleStore):
    """Acceptance-only metadata observer; all canonical writes stay in ExampleStore."""

    def save_document_checkpoint(self, manifest, segments, *, expected_revision, replace=False):
        super().save_document_checkpoint(manifest, segments, expected_revision=expected_revision,
                                         replace=replace)
        if replace:
            self.states = {s["id"]: s["state"] for s in segments}
        else:
            self.states.update({s["id"]: s["state"] for s in segments})
        if any(s["state"] in {"VERIFIED", "BLOCKED"} for s in segments) or not segments:
            print(json.dumps({"event": "checkpoint", "document_id": manifest["id"],
                              "state": manifest["state"], "model_calls": manifest["calls"],
                              "verified_segments": sum(s == "VERIFIED" for s in self.states.values()),
                              "total_segments": manifest["segment_count"],
                              "failure_code": manifest["failure_code"]}), flush=True)


def main() -> int:
    settings = load_config(Path(__file__).resolve().parents[1] / "personalstyle.toml")
    root = Path(tempfile.mkdtemp(prefix="personalstyle-f07-"))
    prepare_private_directory(root / "profile")
    store = ProgressStore(root / "profile" / "profile.db")
    example = "Please review the update. Thank you for your careful attention."
    store.add(ExampleInput(str(uuid4()), example, "work.email", "synthetic-owner",
                           "synthetic-owner", "user_owned", True, True))
    provider = OllamaProvider(settings["model"]["model"])
    capture = Capture()
    logging.getLogger().addHandler(capture)
    print(json.dumps({"event": "acceptance_started", "provider": settings["model"]["provider"],
                      "model": settings["model"]["model"], "per_document_seconds": DOCUMENT_SECONDS,
                      "synthetic_checkpoint_directory": str(root)}), flush=True)
    for words in (2000, 5000):
        text = synthetic_document(words)
        assert len(text.split()) == words
        document_id = str(uuid4())
        with store.feedback_connection() as connection:
            canonical_before = {name: connection.execute(f"SELECT * FROM {name}").fetchall()
                                for name in ("store_meta", "examples", "feedback", "preferences")}
        start = time.monotonic()
        result = rewrite_document(
            store, document_id, RewriteRequest(text, "Improve clarity while preserving every fact, "
                "request and section. Return a faithful rewrite, without commentary.", "work.email", ()),
            settings, provider=provider,
        )
        elapsed = time.monotonic() - start
        manifest, segments = store.document_checkpoint(document_id)
        with store.feedback_connection() as connection:
            canonical_after = {name: connection.execute(f"SELECT * FROM {name}").fetchall()
                               for name in canonical_before}
        no_leak = all(text not in message and example not in message
                      and all(s["source"] not in message for s in segments)
                      and all(not s["output"] or s["output"] not in message for s in segments)
                      for message in capture.messages)
        identities = [s["evidence"]["result"]["model_identity"] for s in segments if s["evidence"]]
        repairs = sum(max(0, n - 1) for s in segments for n in s["attempts"].values())
        summary = {"event": "acceptance_result", "document_id": document_id, "source_words": words,
                   "segments": len(segments), "calls": result["model_calls"], "repairs": repairs,
                   "document_contract": manifest["contract"],
                   "input_upper_bound": max((c["input_token_upper_bound"] for s in segments
                       if s["evidence"] for c in s["evidence"]["result"]["candidates"].values()), default=0),
                   "seconds": round(elapsed, 3), "ceiling_seconds": DOCUMENT_SECONDS, "operation_seconds": OPERATION_SECONDS,
                   "state": result["state"], "failure_code": result["failure_code"],
                   "whole_document_verification": result["whole_document_verification"],
                   "provider": settings["model"]["provider"], "model": settings["model"]["model"],
                   "digest": manifest["dependencies"]["digest"],
                   "runtime_versions": sorted({i["runtime_version"] for i in identities}),
                   "learning_state_unchanged": canonical_before == canonical_after,
                   "normal_logs_sensitive_free": no_leak}
        print(json.dumps(summary), flush=True)
        if (result["state"] != "VERIFIED" or elapsed > DOCUMENT_SECONDS
                or canonical_before != canonical_after or not no_leak):
            return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (StoreError, GenerationError) as error:
        print(json.dumps({"state": "BLOCKED", "failure_code": str(error)}), flush=True)
        raise SystemExit(1) from None
