# UX-A — Actionable errors and safe recovery

```text
TASK: UX-A
STATE: locally verified; checkpointed for review
BRANCH: task/uxa-actionable-recovery
BASE: 4c5e9d26d57c05c9fa2e7ae8021fd7c78870f06a
WIP: 1
IMPLEMENTATION: 1/1 used; primary UI error/recovery implementation complete
DIAGNOSIS: 0/1 used
RECOVERY: 0 used
CI_PARTITION_REPAIR: 1/1 owner-authorized harness-only correction; exact-head CI pending
```

## Objective

Replace the Flutter development shell's opaque operation failure with a clear, sanitized
failure category and safe next step. Make uncertain example/feedback submissions explicit so
the user can tell what operation may have written and whether a retry could create a durable
mutation. This is a focused usability/safety slice, not a visual redesign.

## Entry facts

- F08 remains blocked and checkpointed separately at `task/f08-document-import-export`,
  WIP commit `52d4ca57d64df20f0a668e0db6dd40b50eda387e`.
- PR #14 remains open/draft; its UX contract is referenced, not edited or merged here.
- Current base is `4c5e9d26d57c05c9fa2e7ae8021fd7c78870f06a`.
- The recent owner-store `STORAGE_BOUNDARY_INVALID` was not reproduced. A separate synthetic
  P01 child-process example write passed. Do not claim the historical root cause is known and
  do not ask the owner to repeat that submission.

## Write set

- `desktop/lib/engine.dart`
- `desktop/lib/main.dart`
- focused Flutter tests under `desktop/test/`
- this task record

Do not modify Python engine/protocol, storage, consent rules, schemas, config, F08 import/export,
Figma, shared roadmap documents edited by PR #14, or model behavior. If an engine code needed by
the UI is not present in P01, stop and record the missing contract; do not invent a client
behavior.

## Behavior

- Map only known engine error codes to stable user-understandable categories. Preserve a safe
  engine code as a reference where useful; discard arbitrary error strings and details.
- Distinguish invalid input, protected-storage failure, profile database failure, no eligible
  context evidence, model unavailable, operation timeout/resource limit, verification
  rejection, unsupported capability/protocol and unknown engine failure.
- Show a fixed safe phase/detail only when the engine supplies a recognized value. Never infer
  a lower-level cause from a broad error code.
- Name pending durable operations (example save or feedback submission), state whether outcome
  is unknown, and explain retry/idempotency. Never auto-retry or replace an uncertain request.
  Never ask the user to replay the historical F08 example.
- Do not show writing, credentials, raw paths, stack traces or internal exception text in UI or
  ordinary logs.

## Acceptance

1. Supported error classes produce stable categories and useful fixed explanations.
2. Unknown codes/details fall back safely without leaking supplied sensitive markers.
3. Pending example and feedback operations are named; known rejection is distinguished from
   uncertain completion; no mutation is automatically replayed.
4. An unverified candidate is visibly rejected as unverified, never labeled verified.
5. Focused tests cover known/unknown errors, operation naming, pending state, sanitization,
   verification rejection and startup/unavailable states.
6. `flutter analyze`, focused `flutter test`, and `flutter build windows` pass.

## Failure and stop rules

Use the one primary pass. One repair is permitted for a concrete defect exposed by targeted
verification. If the same failure repeats, stop and diagnose once; no repeated profile
operations or owner-store writes. Any need to change engine error contracts, persistent state,
or consent requires a separate task decision. Preserve all F08 work and evidence.

## Checkpoint — actionable failure and mutation recovery UI

- Branch `task/uxa-actionable-recovery`; base remains
  `4c5e9d26d57c05c9fa2e7ae8021fd7c78870f06a`.
- Implementation attempt 1/1 used; diagnosis 0/1; recovery 0 used.
- Flutter maps only whitelisted P01 engine codes to stable categories and fixed explanations.
  Unknown error codes/details are discarded. `STORAGE_BOUNDARY_INVALID` is displayed as
  `PROTECTED_STORAGE_ERROR` with its safe reference. P01 does not supply a more specific
  storage phase, and the UI does not guess one.
- Uncertain example and feedback writes remain visibly named and marked outcome-unknown. No
  automatic replay occurs. Structured invalid-input, source-unavailable and idempotency
  conflict rejections clear pending state and say that no change was saved. An explicit
  connected retry resends the identical request ID and payload. Pending state is retained only
  in the current app session if the engine exits; it is not durable across app restarts.
- The historical owner-store failure remains unexplained. No owner profile operation, retry,
  consent change, ACL change or model call was performed in this task.
- Final focused `flutter test --no-pub test/engine_test.dart test/ui_test.dart`: 30 passed.
  `flutter analyze --no-pub`: passed (no issues). `flutter build windows --release --no-pub`:
  passed; produced `desktop/build/windows/x64/runner/Release/personalstyle_desktop.exe`.
- `git diff --check`: passed. Python engine/protocol and storage were unchanged; no live model
  call or protected-profile operation was part of verification.
- The Figma design mismatch is a separate future UX requirement. No redesign or Figma edit is
  part of UX-A. F08 remains incomplete with native export/read-back outstanding.

## Completion

UX-A completes only when focused tests, analysis and Windows build pass and the interface shows
specific safe categories without false claims about the unresolved F08 example write. This does
not complete F08, Windows alpha, voice onboarding, requirements/rubric support or PersonalStyle
V1. Owner-authorized draft PR #16 is open; merge approval remains separate.

## CI ceiling diagnosis and partition correction — 2026-10-15

PR #16 head `aea0cc01b06517b3f5fbbadb69d79ac745cb645a` exact-head run `38757120149` was
cancelled at the existing Windows job ceiling of 15 minutes. The full `python -m pytest -q`
step reported `108 passed in 890.96s` before `KeyboardInterrupt`; no assertion failure was
reported, and all later quality steps were skipped. The previous successful full harness run
`37865805821` completed in about 10m34s. Python source and tests were unchanged in PR #16.
Logs do not establish a particular in-flight test; the demonstrated issue is aggregate runtime
variance against the full-suite job ceiling, not a proven test defect. The timeout was not
increased.

Owner authorized one CI-only partition correction; this does not consume or reset the UX-A
feature implementation counter. The workflow now runs all Python test modules in four
deterministic Windows shards, each still bounded by 15 minutes, and executes startup/static
checks in a separate job. A required aggregator preserves the existing `Python harness checks`
status name and fails unless every shard and quality job succeeds. `scripts/run_pytest_shard.py`
checks that discovered `test_*.py` modules are assigned exactly once before executing a shard.
Local evidence: coverage check passed for all 11 test modules; shard collection counts were
68 + 71 + 66 + 89 = 294, matching the complete suite; Ruff and `git diff --check` passed.
The full tests were not rerun locally. New exact-head GitHub CI is the verification gate for
the partition and all tests; do not call it passed until that run is green.
