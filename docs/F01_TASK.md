# F01 — Persist authorized writing examples and explicit context metadata

## Activation checkpoint

```text
CONTRACT_ID: PS-V1-001 / F01 bounded task, owner selected after SEC01 merge
TASK: F01
STATE: active
VERIFICATION_STATUS: not_verified (F01 behavior not implemented)
PRODUCT / PROTOCOL: 0.1.0 / 1.0
CONFIG / STORAGE / PROFILE / PROMPT: 1 / 1 / 1 / 1
REPOSITORY_REVISION / MERGE_BASE / CHECKPOINT: ae563ac9656cee0c84bd13465b3459f979ca9ad4
BRANCH: task/f01-writing-examples
ENTRY_GUARD_RESULT: pass; I01 and SEC01 merged, GitHub gate enforced, clean synchronized main, Windows/Python isolated environment verified, owner selected F01, WIP 1
DECLARED_WRITE_SET: docs/F01_TASK.md; src/personalstyle/storage.py; src/personalstyle/cli.py; tests/test_storage.py; tests/test_initialization.py only for additive CLI coverage; src/personalstyle/security.py only if file ACL verification requires a minimal extension
ATTEMPTS_USED: 0 of 3
DIAGNOSIS_USED: 0 of 2
RECOVERY_USED: 0 of 1
PASSING_EVIDENCE: prerequisites only; 41 tests passed on merged SEC01 checkpoint
FAILED_EVIDENCE: none for F01
BLOCKERS: none at activation
NEXT_ACTION: F01 implementation attempt 1 within the scope below
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
Re-verify that directory's OS ownership and ACL immediately before **every write**, including
schema initialization and metadata mutations. Refuse insecure or reparse targets and verify
that the database file does not bypass the boundary through a link or permissive ACL.
Do not silently reset existing permissions or take over unrelated files.

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
- F01-AC3: writes re-verify the protected directory and database target. Real OS tests show
  insecure ACLs, link/reparse targets and unsupported platforms fail without storing writing.
  Demonstrate rejection after permissions are changed following successful initialization.
- F01-AC4: explicit schema/version checks, parameterized SQL, transaction failure rollback,
  hostile writing kept as data and normal diagnostics free of synthetic writing/secret
  markers have executable evidence. No learning, preference or profile contamination path.
- F01-AC5: I01/SEC01 regressions, Ruff, mypy and the required GitHub check pass on the committed
  artifact. Handoff records revision/base, checks, failures, persistent budgets, limitations
  and next permitted task. No F02 activation without a separate explicit task selection.

## Exclusions and execution controls

No Writing DNA, retrieval, generation/model/Ollama integration, prompts, feedback/learning,
network API, pairing/client protocol, agents, scheduler, UI, mobile storage, encryption,
release security gate, unrelated refactors or cosmetic document edits.

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
