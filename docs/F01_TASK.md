# F01 — Persist authorized writing examples and explicit context metadata

## Activation checkpoint

```text
CONTRACT_ID: PS-V1-001 / F01 bounded task, owner selected after SEC01 merge
TASK: F01
STATE: passing
VERIFICATION_STATUS: valid for current Windows persistence artifact
PRODUCT / PROTOCOL: 0.1.0 / 1.0
CONFIG / STORAGE / PROFILE / PROMPT: 1 / 1 / 1 / 1
REPOSITORY_REVISION / MERGE_BASE / CHECKPOINT: ae563ac9656cee0c84bd13465b3459f979ca9ad4
VERIFIED_IMPLEMENTATION_REVISION: 34dd524133e6c684c69bc8aecb7f3e8604277a6b
BRANCH: task/f01-writing-examples
ENTRY_GUARD_RESULT: pass; I01 and SEC01 merged, GitHub gate enforced, clean synchronized main, Windows/Python isolated environment verified, owner selected F01, WIP 1
DECLARED_WRITE_SET: docs/F01_TASK.md; src/personalstyle/storage.py; src/personalstyle/cli.py; tests/test_storage.py; tests/test_initialization.py only for additive CLI coverage; src/personalstyle/security.py only if file ACL verification requires a minimal extension
ATTEMPTS_USED: 3 of 3
DIAGNOSIS_USED: 1 of 2
RECOVERY_USED: 0 of 1
PASSING_EVIDENCE: attempt 3 local 73 tests, Ruff/mypy and required remote CI passed at verified revision
FAILED_EVIDENCE: attempt 1 permission-test fixture, Ruff and mypy defects; history below
BLOCKERS: none at activation
NEXT_ACTION: review F01 PR #4 after final evidence-only head passes required CI; no F02 activation
```

SEC01 PR #3 merged without further code changes as the checkpoint above. Local main was
fast-forwarded and verified clean and identical to origin/main before this task branch.
The merged initialization/security suite passed locally (Windows/Python 3.14.6); pip
reported no broken dependencies. SEC01 counters remain 3/3 attempts, 2/2 diagnosis, 0/1
recovery; this activation does not extend or reset them. This document records activation,
not a persistence implementation or acceptance pass.

## Objective and scope

Implement the smallest local engine-owned SQLite path to add and inspect user-authorized
writing examples with explicit context tags and provenance. The CLI is a thin adapter.

Each example retains an ID, content, explicit bounded context, supplying/owning or
authorizing party, learning eligibility, held-out reservation, record version and timestamp.
Third-party text without explicit learning authorization is not user-style evidence.
Held-out writing must never be marked eligible for learning. No inferred durable context.

Use the current storage schema version 1 with explicit schema initialization and checked
version metadata. Existing unsupported/unknown stores fail before writes; do not invent
a migration. Transactions preserve the last trustworthy state on failure. Do not accept
SQL identifiers, filesystem paths or execution instructions from example content.

## Mandatory protected-write boundary

Real writing may be persisted only through the SEC01-protected profile directory.
Verify that directory's OS ownership and ACL **before opening the canonical profile store
for mutation**, and again after any condition that could invalidate the trust boundary.
If verification fails, perform **no persistence write**, including database creation,
schema initialization or metadata mutations. Re-verify immediately before every write;
an earlier successful check is not permanent authorization. Refuse insecure or reparse targets and verify
that the database file does not bypass the boundary through a link or permissive ACL.
Do not silently reset existing permissions or take over unrelated files.

Invalidation examples: process restart, profile-path change, migration/recovery, detected
filesystem replacement/reparse change, and reopening after a previous security failure.
Do not cache successful boundary checks across operations; recheck before open/transaction
and commit, and compare filesystem identities within an operation.

Use SEC01's explicit preparation path for a new empty profile directory. Generation/imported
text cannot select a storage path. Host OS account/admin trust and encryption limitations
carry forward; same-account malicious processes are not isolated by this application.

This verified persistence path is Windows-specific. Unsupported platforms must refuse
sensitive persistence until a separate bounded task implements and verifies their secure
storage mechanism. This is not a claim that PersonalStyle is a Windows-only product.

## Acceptance criteria

- F01-AC1: engine API and CLI add a valid authorized example, then a fresh connection/process
  can inspect it with unchanged text, context, provenance and version metadata.
- F01-AC2: absent/invalid context, absent provenance/authorization, invalid learning/held-out
  combinations and oversized inputs are deterministically rejected before mutation. Freeze
  concrete limits before coding and test boundaries; no unbounded read/import path.
- F01-AC3: verify the protected directory and database target before opening for mutation,
  immediately before writes, and after any trust-boundary invalidation. Failed verification
  performs no persistence write, including database creation/schema initialization.
  Real OS tests show
  insecure ACLs, link/reparse targets and unsupported platforms fail without storing writing.
  Demonstrate rejection after permissions are changed following successful initialization.
- F01-AC4: explicit schema/version checks, parameterized SQL, transaction failure rollback,
  hostile writing kept as data and normal diagnostics free of synthetic writing/secret
  markers have executable evidence. No learning, preference or profile contamination path.
  A caller-supplied example UUID is the idempotency key: identical retry returns the original
  record without another row/version increment; different payload for that UUID is a conflict.
- F01-AC5: I01/SEC01 regressions, Ruff, mypy and the required GitHub check pass on the committed
  artifact. Handoff records revision/base, checks, failures, persistent budgets, limitations
  and next permitted task. No F02 activation without a separate explicit task selection.

## Exclusions and execution controls

No Writing DNA, retrieval, generation/model/Ollama integration, prompts, feedback/learning,
network API, pairing/client protocol, agents, scheduler, UI, mobile storage, encryption,
release security gate, unrelated refactors or cosmetic document edits.

Frozen initial limits: text 64 KiB UTF-8, context 64 ASCII characters (lowercase identifier),
provenance 256 UTF-8 bytes each for supplier/owner-or-authorizer and source kind (user_owned
or authorized_reference), 1000 examples per profile, SQLite file 128 MiB, database wait and
query budget 2 seconds each, existing SEC01 ACL subprocess ceiling 10 seconds.
Owner authorization is explicit local user attestation, not proof of third-party ownership.

Failures are explicit fixed codes: STORAGE_BOUNDARY_INVALID, INVALID_EXAMPLE (including
context/provenance), DATABASE_UNAVAILABLE_OR_CORRUPT, TRANSACTION_FAILED,
IDEMPOTENCY_CONFLICT, PERSISTENCE_VERIFICATION_FAILED. Unexpected sensitive logging,
required scope expansion and exhausted budget block the task. Fail/rollback/block, never
best-effort persistence. Schema/version mismatch and hot journal/recovery state require an
explicit recovery/migration decision; no automatic recovery is introduced in F01.

Conservative task ceiling: 3 implementation attempts, 2 non-modifying diagnosis cycles,
1 recovery action; first material implementation counts as attempt 1. Counters persist
across sessions and interruptions. Classify failures and state changed information before
repair. Do not weaken criteria/tests. Stop on budget exhaustion or required scope/permission
expansion; only the owner may extend the budget. Use bounded input/database waits and the
existing 10-minute CI ceiling; specify concrete resource limits before implementing.

Recovery preserves unrelated work: repair F01-local changes, revert only F01-local changes,
then restore the task-start checkpoint. Refresh main before final verification and resolve
semantic conflicts against source authority. No SEC01 reopen or additional SEC01 budget is
authorized. New security features beyond necessary persistence integration need a new task.

## Failure history

Attempt 1 observed: 69 tests passed; real permission-change fixture could not apply its
Set-Acl change (PrivilegeNotHeldException); five Ruff findings and one mypy optional-value
assignment error. Expected: real broadened ACL rejected, tests/lint/types all pass.
Classification: verifier fixture uses an unavailable OS privilege; implementation typing/
lint defects. New information: native icacls DACL grant changes permissions without requesting
ownership/audit privileges. Attempt 2 uses an Everyone read grant on synthetic test data,
preserves rejection/no-write assertions, corrects imports/explicit subprocess check flags and
optional result typing. Adds initialization rollback and bounded database-lock tests.
Remaining: 1 implementation attempt / 2 diagnosis / 1 recovery. No criteria weakened.

Final review diagnosis cycle 1: synthetic store with a nonnumeric profile_version produced
TypeError rather than DATABASE_UNAVAILABLE_OR_CORRUPT; database bytes unchanged.
Class: implementation_defect against the frozen corrupt-store failure requirement.
Attempt 3 explicitly checks metadata integer type and adds the unchanged-store regression.
Remaining: 0 implementation attempts / 1 diagnosis / 1 recovery. Stop on further failure.
Diagnostic fixture cleanup initially failed because its direct SQLite connection was still
open; process exit closed it. This affected only synthetic temporary data, not the candidate.

## Local acceptance evidence and operating limits

Attempt 2 on Windows/Python 3.14.6: 72 tests passed in 49.98s; Ruff passed; mypy passed
for 5 source files. This includes all 41 I01/SEC01 tests. Existing startup syntax is retained.

F01-AC1: engine add/read returns unchanged content/context/provenance with timestamp and
record version; fresh-process readback and CLI inspection pass. UUID idempotency retries
return the original record; a conflicting payload is rejected without another row or
profile-version increment. Authorization is an explicit local user's attestation.
F01-AC2: invalid authorization/context/provenance/held-out flags/oversized input are rejected
before database creation. CLI JSON request is bounded to 64 KiB + 4096 bytes; input contents
are not interpolated into SQL, OS code or policy. Exact Unicode text is preserved.
F01-AC3: verify directory and explicitly protected database file before opening; verify again
before transaction and commit; compare directory/file device/inode identity. No long-lived
connections/check cache. Real ACL widening blocks existing store mutation and reopening;
insecure initial roots never reach sqlite.connect; hardlinks and replaced roots are rejected.
SQLite sidecars present before open require explicit recovery, not automatic recovery.
The active transaction's rollback journal inherits the already-verified protected directory
ACL. Its canonical mutation unit is one guarded atomic transaction; dirty-page spilling is
disabled before transaction, then the boundary is rechecked before commit.
F01-AC4: initial schema + example + profile-version update roll back together on injected
precommit failure; existing-store rollback leaves no partial row/version update. Corrupt,
future-version, foreign-schema, recovery-journal and locked stores fail without partial data.
Normal CLI add/failure output and logs omit synthetic writing markers; explicit user-requested
inspection prints the record. SQL schema/version are checked, statements parameterized.
F01-AC5: required remote CI passed on verified implementation revision; this committed
handoff records exact evidence, budgets, failures, base and next action.

Final local verification after attempt 3: 73 tests passed in 56.21s; Ruff passed; mypy
passed for 5 source files. Corrupt metadata now raises the fixed failure code and preserves
database bytes. Synthetic diagnostic directory was removed after its process exited.

Only Windows persistence is verified. Same-account hostile processes and host administrators
retain OS privileges; no application encryption, forensic erase or cross-platform storage
claim. A committed write whose subsequent readback cannot be verified reports failure;
retry with the same UUID reconciles deterministically rather than inserting duplicates.
Failed first initialization may leave an empty protected database file with no schema/records;
reopening requires an explicit recovery decision, never guessed migration. No automatic
recovery, migration, deletion or learning is implemented. Do not start F02.

## Committed-revision completion evidence

Required GitHub Actions run on `34dd524133e6c684c69bc8aecb7f3e8604277a6b` succeeded:
https://github.com/Poken-ninja/personalstyle/actions/runs/37544337398/job/112544594453
Package install/import, existing help/startup, complete 73-test suite (including I01/SEC01),
Ruff, mypy, dependency consistency and patch checks all passed. Gate was observed pending/
BLOCKED before completion; no bypass. Earlier committed attempt-2 CI also passed, but the
current evidence is the corrected attempt-3 artifact. No real user writing used in tests.

PR: https://github.com/Poken-ninja/personalstyle/pull/4
Five changed files, all declared F01 scope; main base remains the SEC01 merge checkpoint.
No conflicts/unrelated changes. Final handoff-only commit preserves all tested source and
tests; its own required check must pass before merge. Branch is pushed; working tree was
clean before this record update. Budgets: 3/3 attempts, 1/2 diagnosis, 0/1 recovery. Any
further implementation repair requires explicit owner extension; merge/review is next.

CLI usage from the project root: `personalstyle --prepare-storage`, then
`personalstyle --add-example REQUEST.json`, and explicit inspection using
`personalstyle --get-example UUID`. An example request contains exactly these keys:
id (canonical UUID), text, context, supplier, authorizer, source_kind (user_owned or
authorized_reference), authorized (true), learning_eligible (boolean), held_out (boolean).
Use the same id/payload for a retry; held_out and learning_eligible cannot both be true.
`--config PATH` selects an explicitly supplied local project configuration; writing cannot
choose the profile path. Add output is metadata only; explicit inspection prints writing.
