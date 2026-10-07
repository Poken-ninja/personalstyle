"""Read-derived structural Writing DNA; source prose never appears in the result."""

import hashlib
import re
import time
from collections import Counter

from personalstyle.storage import ExampleStore, StoreError

ALGORITHM_VERSION = "writing_dna.v1"
WORDS = re.compile(r"[^\W_]+(?:['’][^\W_]+)*", re.UNICODE)
PARAGRAPHS = re.compile(r"\n[ \t]*\n(?:[ \t]*\n)*")
SENTENCES = re.compile(r"[.!?]+")
PUNCTUATION = ".,;:!?"


class ProfileError(StoreError):
    """Fixed profile failure code without source content."""


def _check_deadline(deadline: float) -> None:
    if time.monotonic() >= deadline:
        raise ProfileError("PROFILE_RESOURCE_LIMIT")


def derive_writing_dna(
    store: ExampleStore, context: str, *, profile_schema: int = 1, timeout_seconds: int = 60,
) -> dict[str, object]:
    """Derive all eligible sources; fail rather than return a partial snapshot."""
    if type(profile_schema) is not int or profile_schema != 1:
        raise ProfileError("PROFILE_VERSION_INCOMPATIBLE")
    if type(timeout_seconds) is not int or not 0 < timeout_seconds <= 60:
        raise ProfileError("PROFILE_RESOURCE_LIMIT")
    deadline = time.monotonic() + timeout_seconds
    samples = words = paragraphs = sentences = 0
    lengths: Counter[int] = Counter()
    punctuation = {mark: 0 for mark in PUNCTUATION}
    fingerprint = hashlib.sha256()
    with store.eligible_examples(context, deadline) as (source_version, rows):
        for example_id, record_version, text in rows:
            _check_deadline(deadline)
            samples += 1
            fingerprint.update(f"{example_id}:{record_version}\n".encode("ascii"))
            normalized = text.replace("\r\n", "\n").replace("\r", "\n")
            for paragraph in PARAGRAPHS.split(normalized):
                _check_deadline(deadline)
                if not paragraph.strip():
                    continue
                paragraphs += 1
                for span in SENTENCES.split(paragraph):
                    size = sum(1 for _ in WORDS.finditer(span))
                    if size:
                        lengths[size] += 1
                        words += size
                        sentences += 1
            for mark in punctuation:
                punctuation[mark] += text.count(mark)
        if not samples:
            raise ProfileError("NO_ELIGIBLE_EXAMPLES")
        _check_deadline(deadline)
        # Histogram size is bounded by per-example input length, not corpus count.
        middle = [(sentences + 1) // 2, sentences // 2 + 1]
        cumulative = 0
        medians: list[int] = []
        for length, count in sorted(lengths.items()):
            previous, cumulative = cumulative, cumulative + count
            medians.extend(length for rank in middle if previous < rank <= cumulative)
        features = {
            "sample_count": samples, "word_count": words, "sentence_count": sentences,
            "paragraph_count": paragraphs,
            "mean_words_per_sentence": words / sentences if sentences else 0.0,
            "median_words_per_sentence": sum(medians) / 2 if sentences else 0.0,
            "mean_sentences_per_paragraph": sentences / paragraphs if paragraphs else 0.0,
            "punctuation_counts": punctuation,
            "punctuation_per_100_words": {
                mark: count * 100 / words if words else 0.0 for mark, count in punctuation.items()
            },
        }
    _check_deadline(deadline)
    return {
        "profile_schema": profile_schema, "writing_dna_algorithm_version": ALGORITHM_VERSION,
        "context": context, "source_profile_version": source_version,
        "eligible_example_count": samples, "source_fingerprint": fingerprint.hexdigest(),
        "features": features,
    }
