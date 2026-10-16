# V01 — Voice evidence, consent and context isolation

```text
TASK: V01
BRANCH: task/v01-voice-evidence
BASE: 9a7a2049ca9d19f5d5d9d163b54a174d073d27a8
STATE: revocation-safety repair — focused checks pass; final regression pending
WIP: 1
IMPLEMENTATION: 2/2 used (attempt 1; authorized revocation repair attempt 2)
DIAGNOSIS: 1/2 used
RECOVERY: 0/1 used
```

This contract activates the engine layer that must precede UX-C/V02. It does not mark
voice onboarding, generic-only generation, F08, or the Windows alpha complete. PR #14
remains open/draft and is not modified by this task.

## Checkpoint and authority

The UX-C checkpoint `2712ca9c341ea20143719bb71d3db3db24f7c11f` is pushed to
`task/ux-c-voice-onboarding`. It remains at implementation 1/2, diagnosis 2/2,
recovery 0/1, blocked on V01. Its Copy result behavior does not submit feedback or mutate
profile/learning state; its disclosure says a submitted feedback record is stored even
when learning is unchecked. UX-C source and tests are not part of this branch's write set.

The authoritative product decision is ADR-004 at PR #14 head
`cd9dfa5384c689ef6e4d6d7116bd51cf9b2e4f0c`. It requires exact-context source eligibility,
typed provenance, separate storage and learning authorization, default-deny context
transfer, and future inspect/delete/revoke behavior. The owner resolved ADR-004's consent
and revocation questions on 2026-10-16; the approved policy is recorded below.

## Objective

Provide engine-owned, persistent, context-scoped voice evidence whose authorization and
eligibility survive process restarts and can be revoked without cross-context leakage.
Authorized evidence should be reusable across sessions after the user's explicit
authorization, without asking for consent on every rewrite. Saving a source, using it for
personalization, and storing a feedback event are separate operations and must be described
truthfully. Generic-only generation remains unavailable until a separate authoritative
engine path is implemented and verified; the client must not simulate it.

## Entry dependencies

- UX-C checkpoint pushed; no UX-C screen changes in V01.
- PR #14 ADR-004 remains draft; use its recorded decisions without changing its branch.
- One authoritative Python writer and the existing SEC01 protected SQLite boundary.
- Owner policy approval received 2026-10-16; no further consent decision blocks attempt 1.
- Confirm current remote main and branch/worktree state before feature edits. Preserve the
  unrelated F08 artifacts and the stashed `tests/test_storage.py` change from UX-C work.

## Observed implementation and compatibility assessment

At base `9a7a2049ca9d19f5d5d9d163b54a174d073d27a8`:

- Storage schema is 3. `examples` stores context, supplier/authorizer, source kind,
  `learning_eligible`, held-out flag, record/profile versions, and creation time. It has no
  explicit consent record, authorization version, revocation/tombstone state, or AI-draft
  source type. `ExampleInput.authorized` is a write-time boolean and is not durable evidence
  of what the user authorized.
- Retrieval filters exact context, `learning_eligible=1`, and `held_out=0`; context transfer
  is not implemented.
- Feedback is a separate durable record. `learning_authorized=false` suppresses learning
  observations, but does not suppress storage of a submitted accept/edit feedback event.
- The current source kinds are `user_owned` and `authorized_reference`; the engine cannot
  distinguish an AI-generated draft from an original user-authored source by typed input.
- `generate_pair` requires eligible examples before generating candidates. There is no
  generic-only fallback or read-only voice-readiness capability.
- Protocol is 1.0, storage schema 3, profile schema 1, prompt contract 1. The minimal
  proposed storage change is an explicit schema 3→4 table keyed to example ID, recording
  storage authorization, personalization authorization, authorization version and times.
  Missing rows mean legacy/unconfirmed and are ineligible; migration preserves their source
  bytes and does not infer consent. New protocol operations are additive/capability
  negotiated under protocol 1.1. Profile schema stays 1 unless the serialized DNA changes;
  prompt contract changes only if selection behavior changes. Verify all dependent provenance
  validators and F07 checkpoint invalidation through profile-version change.
- Existing explicit migrations are guarded, transactional transitions 1→2 and 2→3;
  normal operations do not silently migrate older stores. V01 must preserve this rule and
  existing examples, feedback, preferences, and F07 document state.

No migration or compatibility behavior is claimed as verified for V01 until executable
upgrade, rollback/failure, reopen, and protected-boundary tests pass.

## Existing-store migration instructions and risks

Migration is explicit; ordinary engine startup/read/write does not upgrade a profile. After
installing this engine, close all PersonalStyle engine/client processes so an old-schema
writer cannot overlap the migration, then run `personalstyle --migrate-storage` from the
directory containing the active `personalstyle.toml` (or supply its path with `--config`).
The verified CLI exposes this exact root command. It performs ordered migrations to schema
4 inside the existing protected-store boundary. Schema 3 examples and other canonical rows
are retained; missing V01 authorization rows mean legacy examples remain excluded until the
owner explicitly reauthorizes each source. The migration increments profile version to
invalidate dependent snapshots. The migration is transactional and its rollback/reopen
behavior is covered by the passing storage tests. Do not reset the store or run concurrent
old/new engine writers. This task did not run migration on the owner's real profile.

## Approved consent and revocation policy

1. Legacy schema-3 examples remain intact but are not used until explicitly reauthorized
   under V01. Migration must not delete or infer consent from `learning_eligible`.
2. Storage authorization and exact-context personalization authorization are separate,
   durable choices. Personalization requires storage authorization. Once authorized, the
   choice persists across sessions until revoked; no repeated per-rewrite prompt.
3. Revoking storage authorization deletes that source and invalidates dependent voice
   evidence/derived preferences while preserving unrelated data. Turning personalization
   off disables retrieval and future learning; the original sample may remain only while
   storage authorization remains active.
4. If learning is disabled, accept/edit feedback is not submitted or retained. Feedback
   storage associated with opted-in learning is not a general feedback archive. Copy,
   accept, edit, save and export remain available without training. Explicit file export is
   not profile/feedback consent.
5. Sources declared AI-generated, model output, held-out, or unauthorized cannot enter
   eligible voice evidence. No client-supplied claim can prove authorship; the engine
   enforces declared provenance and the authorization boundary, and the UI must not label
   synthetic/AI drafts as authentic samples.

Physical secure erasure is not promised. Deletion means removal from the canonical SQLite
records and invalidation of dependent derived state through the verified protected-store
transaction; filesystem/media remanence is outside the claim.

## Planned minimal write set after policy resolution

- `docs/V01_TASK.md`
- `src/personalstyle/storage.py`, `src/personalstyle/feedback.py`, and `src/personalstyle/config.py`
  for consent state, eligibility, revocation, feedback persistence, and ordered migration;
- `src/personalstyle/protocol.py` and `personalstyle.toml` for additive P01 capabilities and
  protocol/storage declarations;
- `src/personalstyle/cli.py` for an explicit, never-implicit protected-store migration command;
- focused tests for storage, feedback, profile, protocol, and F07 migration/checkpoint
  compatibility;
- no Flutter onboarding/profile screens, F08 files, PR #14 files, or unrelated shared docs.

Refine this write set after the owner resolves policy and before attempt 1. Keep canonical
SQLite writes in the Python engine and preserve SEC01 protections.

## Acceptance criteria

1. Saving a source requires explicit, durable storage authorization and records provenance,
   owner/source type, exact context, authorization version/time, and eligibility state.
2. Personalization use requires separately explicit authorization; authorization persists
   across engine sessions and can be revoked according to the approved lifecycle.
3. AI-generated drafts, model output, third-party/reference material without proper
   authorization, held-out data, unknown source types, and unauthorized sources are rejected
   or excluded deterministically at write and read time.
4. Only exact-context authorized evidence is selected. Cross-context retrieval remains
   default-deny. Tampering with stored context/consent/provenance fails closed.
5. Revocation prevents future retrieval and deterministically invalidates all dependent
   derived evidence required by the approved policy; unrelated contexts/sources remain
   intact.
6. A process restart reconstructs consent, source eligibility, revocation, and version state
   from protected durable storage, without session-memory authorization.
7. Storage authorization, personalization authorization, and feedback-record persistence
   have distinct machine-readable outcomes and user-facing safe classifications. Learning
   OFF is never reported as storage OFF.
8. Missing eligible evidence is reported as unavailable/provisional. No generic-only output
   is claimed or exposed until the engine has its own verified generic-only path.
9. Approved migrations are explicit, deterministic, atomic/rollback-safe, idempotent where
   applicable, and preserve representative schema-3 examples, feedback, preferences, and
   document checkpoints. No normal open/write performs an implicit migration.
10. Existing SEC01 boundary, F03/F04 verification, F05/F06 learning policy, F07 checkpoint
    behavior, idempotency, and sensitive-log protections remain intact.
11. Positive and negative tests cover missing/denied authorization, AI-generated and
    unauthorized source declarations, held-out/revoked sources, context isolation,
    restart persistence, migration preservation/rollback, and no sensitive logging.

## Verification and budget

After policy resolution, run targeted V01 storage/provenance/protocol tests while editing.
Only after targeted acceptance passes, perform the task's single final full Python
regression and required static checks. A real model call is unnecessary unless the approved
contract changes actual generation consumption in a way deterministic/provider fixtures
cannot prove. Do not run owner-profile operations as acceptance.

- Implementation: 0/2 used; attempt 1 is the primary engine contract.
- Diagnosis: 0/2 used.
- Recovery: 0/1 used.
- A materially different repair may use attempt 2 only after concrete failed acceptance.
- A repeated same failure stops implementation and enters bounded diagnosis; no retries
  without changed evidence.
- Any need to widen scope, change consent semantics beyond the owner's answer, bypass
  protected storage, or introduce generic fallback stops for owner decision.

## Current checkpoint — 2026-10-16

Owner policy was resolved on 2026-10-16. Implementation attempt 1 is used (1/2); one
bounded diagnosis cycle is used (1/2); recovery remains 0/1.
The current implementation uses schema 4's per-example authorization table; migration
preserves old rows without manufacturing authorization and advances profile version to
invalidate dependent snapshots. The `example_authorizations` primary key supports source
mutation and the existing examples context index supports exact-context retrieval; no
unmeasured secondary consent index is added. Protocol 1.1 exposes aggregate `voice.status`,
legacy reauthorization, personalization toggle, and source revocation. Feedback with
learning disabled returns `recorded=false` without opening SQLite. No Flutter/UX-C screens
or generic-only generation were changed.

Initial targeted runs exposed four fixture/implementation failures: an idempotent example
write used an uninitialized timestamp; a consent-version CHECK prevented a legitimate
version increment; a revocation query compared JSON objects as strings; and several fixtures
still treated schema 4 as future or omitted explicit legacy authorization. These have been
corrected. Focused V01/storage/feedback/protocol/F07 checks subsequently passed 35 tests;
profile/generation/learning compatibility passed 56 tests after correcting the stale
future-schema fixture (its corrected five-case test passed). The secondary consent index was
removed before final verification because the actual join uses example ID and the existing
examples context index; no query-plan evidence justified the additional index.

Targeted evidence after the final schema design:

- V01 evidence/migration/revocation tests plus affected F07 schema/checkpoint tests: 9 passed.
- V01 + feedback + P01 voice-consent protocol + F07 migration/restart integration: 35 passed.
- Profile/generation/learning compatibility: 56 passed; the one schema-version fixture was
  corrected from treating schema 4 as future, and its five-case affected test passed.
- The full suite first completed at 300 passed, 2 failed in 845.86s. Both failures were stale
  F07 fixtures that assumed schema-3 examples remained eligible and profile version stayed
  unchanged. The fixtures were corrected to add explicit exact-context authorization and
  expect the deliberate migration profile-version increment.
- The corrected full suite completed at 300 passed, 2 failed in 1062.62s. The failures were
  `tests/test_feedback.py::test_authorized_roundtrip_versions_idempotency_and_weak_accept`
  (`STORAGE_BOUNDARY_INVALID`) and
  `tests/test_protocol.py::test_early_rejection_with_unread_body_stress[origin-ORIGIN_CALLER_REJECTED]`
  (`WinError 10053`). In one isolated bounded run, the feedback test passed and the Origin
  rejection reproduced with the same connection abort. A separately authorized P01 diagnosis
  compared the exact test and transport path against unchanged `origin/main` at
  `9a7a2049ca9d19f5d5d9d163b54a174d073d27a8`. The failure also passed in isolation on that
  baseline and on the V01 branch. Source inspection found the bounded close path drained at
  most `MAX_BODY_BYTES`, while the stress request is `MAX_BODY_BYTES + 1`; leaving its final
  byte unread can trigger a Windows TCP reset after the structured response. The minimal P01
  repair raises only that fixed byte cap by one, retaining the same fixed close deadline and
  all reject/auth/resource semantics. It was independently verified in P01 commit
  `4519bb03735c4f1ee7ada2b1ebcbaf0a87ffcc68`, then applied to this branch as
  `53139f644a2d3f4f543534c07e8d3bc69fd798d8`. P01 evidence: targeted rejection/security
  cases 9 passed, full `tests/test_protocol.py` 34 passed, Ruff/mypy/pip check/diff check all
  passed. The feedback boundary failure appeared order/environment-dependent and passed in
  isolation; the combined full regression also passed it.

After the P01 correction was applied to the V01 branch, the single combined full regression
passed: `302 passed in 852.83s`. Final checks on that revision passed: Ruff (`src`, `tests`,
and `scripts/f07_acceptance.py`), mypy (`src`), pip check, and `git diff --check`. The
full-suite run includes schema-3→4 migration, rollback/reopen, consent, revocation,
context-isolation, feedback, F07, and P01 protocol coverage. No live owner-profile operation
or model call was used.

V01 is locally verified on the current branch. The WIP implementation checkpoint is
`f35c4738c38b0584241e77b62fd5312d35765538`; the P01 transport correction is included as
`53139f644a2d3f4f543534c07e8d3bc69fd798d8`. Historical regression failures above remain
part of the record. Implementation/diagnosis/recovery counters remain 1/2, 1/2, and 0/1;
no counter was reset. Publication and exact-head CI status are tracked in the review record.
UX-C/V02 onboarding screens remain gated; F08 artifacts and PR #14 were not modified.

## Owner-authorized revocation-safety repair — 2026-10-16

This section supersedes the preceding pre-repair checkpoint summary. Current counters are
implementation 2/2 used, diagnosis 1/2 used, recovery 0/1 used.

The owner authorized one repair to prevent source revocation or personalization OFF from
reactivating an older preference version. The isolated protected-store reproduction created
an active line-count version 1 and a newer contested version 2 whose support included the
source being revoked. Before repair, deleting only version 2 caused the generation-facing
`active_preferences` API to expose the older active version 1. This reproduces the defect.

Implementation attempt 2/2 invalidates every stored version for the affected exact
`(context, feature)` inside the existing revocation/personalization transaction. It leaves
other features, contexts, sources and their evidence untouched. The code uses a single SQL
deletion with JSON validity guards; no schema/protocol/prompt change is required. Subsequent
explicit preference evaluation derives state only from remaining feedback and cannot fall
back to the deleted historical version.

Focused evidence: the selected revocation/personalization/rollback cases passed (5
parameterized test outcomes in 173.69 seconds). The complete V01 evidence and learning modules passed 20
tests in 447.18 seconds. Coverage includes revocation, personalization OFF, preserved
independent feature evidence, protected-store reopen, subsequent deterministic evaluation,
and rollback after a simulated commit-boundary failure. The earlier fixture correction
changed only an assertion: a context with another eligible source correctly remains
`AVAILABLE` after one source is disabled.

Final local regression after the repair was attempted once with a 900-second ceiling and
did not complete before that ceiling. Captured progress showed one failure marker but pytest
did not flush its summary/traceback before termination. The marker maps by collection order
to `tests/test_profile.py::test_invalid_source_or_version_never_returns_profile[provenance-PROFILE_SOURCE_INVALID]`;
that exact case passed once in isolation (1 passed in 10.25s). This is insufficient to call
the full local regression clean or to classify the marker's original cause. No second full
suite run was made. One-time final static checks passed: Ruff (`src`, `tests`, and
`scripts/f07_acceptance.py`), mypy (`src`, 13 files), pip check, and `git diff --check`.
The earlier intermittent local `PREFERENCE_SOURCE_INVALID` observation and its
non-reproduction evidence above remain separate and unresolved. A successful pre-repair
head CI run is not evidence for this correction. PR #18 remains draft; no merge, real-profile
operation, F08 change or PR #14 change is authorized here.
