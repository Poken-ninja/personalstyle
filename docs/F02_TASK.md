# F02 — Deterministic Writing DNA for one exact context

## Activation and persistent checkpoint

```text
TASK: F02
STATE: active
VERIFICATION_STATUS: not_verified
BASE / MERGE_BASE / CHECKPOINT: 8a2e3bfc2ab70507a1b10c2eca3cb49913886177
BRANCH: task/f02-writing-dna
ENTRY_GUARD_RESULT: pass; verified F01 main, clean tree, owner activation, WIP 1
DECLARED_WRITE_SET: README.md (status only); EXECUTION_CONTRACT.md (status only); docs/F02_TASK.md; src/personalstyle/storage.py (read extension only); src/personalstyle/profile.py; src/personalstyle/cli.py (thin inspection option); tests/test_profile.py
PRODUCT / PROTOCOL: 0.1.0 / 1.0
CONFIG / STORAGE / PROFILE / PROMPT: 1 / 1 / 1 / 1
WRITING_DNA_ALGORITHM_VERSION: writing_dna.v1
PYTHON_VERSION: 3.14.6
SQLITE_RUNTIME_VERSION: 3.50.4 (not a storage schema version)
ATTEMPTS_USED: 0 of 3
DIAGNOSIS_USED: 0 of 2
RECOVERY_USED: 0 of 1
PASSING_EVIDENCE: prerequisites only; F01 merge has 73 passing regressions and main CI
FAILED_EVIDENCE: none
BLOCKERS: none
NEXT_PERMITTED_ACTION: F02 attempt 1; no F03 or automatic merge
```

Review found stale README/contract entry status, classified as historical status presented
as current. Owner authorized status-only reconciliation; historical handoffs are retained.
Harness-Engineering was read as reference only. No architectural conflict blocks F02.
Activation/status reconciliation is not implementation attempt 1.

## Bounded implementation

Compute an ephemeral inspectable snapshot from all examples with exact requested context,
learning_eligible=1 and held_out=0. F01 accepted provenance is revalidated when reading;
malformed source rows fail rather than contribute. No context inference or fallback.
One read-only SQLite transaction couples the source profile revision with streamed rows,
ordered by canonical UUID. Validate the existing schema, ownership/ACL, links/reparse and
filesystem identity before open and recheck before returning a successful result.
No durable derived tables, migration, version bump, dependencies or changes to F01 writes.

Output: profile_schema=1, writing_dna_algorithm_version=writing_dna.v1, exact context,
source_profile_version, eligible_example_count, SHA-256 source fingerprint over ordered
UUID/record-version pairs (not prose), and feature values. No time/random fields or prose.
The global source revision may advance for unrelated writes; semantic features and the
eligible-source fingerprint must remain unchanged in that case.

## Frozen minimal feature definition and use

- Sample, word, sentence and paragraph counts describe evidence volume and structural
  scale; they are diagnostics, not personality labels or quality gates.
- Mean and median words per sentence describe sentence-length tendency for later
  comparison/control. Median uses a frequency histogram, not retained corpus prose.
- Mean sentences per paragraph describes paragraph density for later formatting guidance.
- Counts and per-100-word rates for `. , ; : ! ?` describe punctuation tendencies for
  later comparison. Zero words yields zero rates, with counts still available.

Words are Unicode alphanumeric runs excluding underscore, with internal straight/curly
apostrophes joining runs. Paragraphs are nonempty blocks separated by blank lines;
CRLF/CR normalize to LF. Sentences are word-containing spans split by runs of `. ! ?`
within a paragraph; an unterminated final span counts. Blank/punctuation-only spans do
not count as sentences; nonempty punctuation-only paragraphs do count as paragraphs.
These are documented structural heuristics, not linguistic/semantic analysis: abbreviations
and decimal punctuation split spans. Every example starts fresh; no cross-example joins.

## Resources and failures

Stream one bounded F01 row at a time. Sentence-length histogram memory is bounded by
the existing 64-KiB per-example text limit, independent of lifetime corpus size. No
aggregate count/file-size quota and no silent truncation. Use the existing 60-second
harness ceiling for complete derivation (including boundary checks) and existing
2-second SQLite execution/wait ceilings; SQL interruption or elapsed ceiling returns
PROFILE_RESOURCE_LIMIT, never partial success. SEC01 subprocesses retain 10-second bounds;
CI retains 10 minutes. The CLI passes the configured harness ceiling.

Fixed failures: NO_ELIGIBLE_EXAMPLES, PROFILE_SOURCE_INVALID, PROFILE_DERIVATION_FAILED,
PROFILE_RESOURCE_LIMIT, STORAGE_BOUNDARY_INVALID, DATABASE_UNAVAILABLE_OR_CORRUPT,
PROFILE_VERSION_INCOMPATIBLE. Invalid explicit context is PROFILE_SOURCE_INVALID.
Existing F01 error behavior remains unchanged. Normal errors/logs contain no prose.
No recovery/migration is automatic. Unsupported schema/store/security blocks reads.

## Acceptance and verification

- F02-AC1: engine/CLI derive requested exact-context eligible non-held-out examples only.
- F02-AC2: repeat calls/fresh processes yield identical output; metadata reconstructs
  source state/algorithm; database bytes and versions remain unchanged by derivation.
- F02-AC3: unrelated contexts, ineligible/held-out examples and invalid provenance/version
  cannot influence features; zero eligible sources gives NO_ELIGIBLE_EXAMPLES. Eligible
  additions change count/source identity deterministically; unrelated additions change
  only global revision, not semantic features/source fingerprint.
- F02-AC4: hand-calculated tests cover all documented numeric features, Unicode/apostrophe,
  punctuation clusters, blank lines, no terminator, empty/punctuation-only spans and median.
- F02-AC5: real protected-boundary positive/negative reads, source corruption/version,
  read-only snapshot and time failure evidence; no prose in output/logs/errors. All
  I01/SEC01/F01 tests plus pytest, Ruff, mypy, pip check and required GitHub CI pass.
- F02-AC6: committed/pushed handoff records revision/base, versions/runtime, write set,
  budgets, checks/CI, failures/blockers/limitations and next action. Open bounded PR; stop.

Budget: 3 total modifying implementation attempts, 2 non-modifying diagnosis cycles,
1 recovery action; counters persist through interruptions. First material feature edit
counts as attempt 1. Classify every failure with observed/expected/evidence/next action
and budget remaining before repair; retries require new information. Only owner extends
budget. On exhaustion/security failure/scope expansion, record blocked/controlled stop.
Recovery: smallest F02-local repair/revert/checkpoint; preserve unrelated work and rerun
invalidated checks. Refresh main before final verification; classify/resolve conflicts
against authority and rerun affected checks. No blind ours/theirs.

Excluded: F03 retrieval/ranking, model/prompts/generation, semantics, learning/preferences,
network/protocol/client surfaces, mobile storage, scheduling/agents, vectors/RAG, migrations,
durable DNA tables, unrelated cleanup. Windows protected reads only; host account/admin
and encryption limitations carry forward. F03 is only a candidate after review, merge
and explicit owner selection; never auto-activate or merge F02.
