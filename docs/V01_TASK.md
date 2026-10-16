# V01 — Voice evidence, consent and context isolation

```text
TASK: V01
BRANCH: task/v01-voice-evidence
BASE: 9a7a2049ca9d19f5d5d9d163b54a174d073d27a8
STATE: blocked before implementation — consent/revocation policy decision required
WIP: 1
IMPLEMENTATION: 0/2 used
DIAGNOSIS: 0/2 used
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
transfer, and future inspect/delete/revoke behavior. It explicitly leaves the consent and
revocation lifecycle unresolved. This contract records that open policy gate; it does not
resolve it by implementation assumption.

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
- Resolve the owner policy questions below before implementation attempt 1.
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
- Protocol is 1.0, storage schema 3, profile schema 1, prompt contract 1. No version is
  changed by this contract. A durable consent/revocation representation likely needs an
  explicit storage migration; implementation must prove the minimum schema change and
  compatibility before selecting a version. Protocol changes must be additive and
  capability-negotiated. A profile or prompt version changes only if the actual serialized
  profile or selection behavior changes.
- Existing explicit migrations are guarded, transactional transitions 1→2 and 2→3;
  normal operations do not silently migrate older stores. V01 must preserve this rule and
  existing examples, feedback, preferences, and F07 document state.

No migration or compatibility behavior is claimed as verified for V01 until executable
upgrade, rollback/failure, reopen, and protected-boundary tests pass.

## Required policy decision — implementation stop gate

ADR-004 leaves source deletion/revocation and retention unresolved. Before implementation,
the owner must decide:

1. **Existing schema-3 examples:** should they remain usable under their existing
   `learning_eligible` flag, or become unavailable for personalization until the owner
   explicitly reauthorizes them under the new durable consent contract? Recommended safe
   default: preserve all records and mark authorization unconfirmed/ineligible; never infer
   new consent from a legacy boolean.
2. **Consent scopes and lifetime:** approve separate durable choices for (a) storing a
   source and (b) using that source for exact-context personalization, with the latter
   requiring the former; confirm that the authorization persists across sessions until
   revoked. Learning OFF must not be represented as storage OFF.
3. **Revocation semantics:** when storage authorization is revoked, choose whether the
   source is deleted immediately (with dependent derived evidence invalidated) or retained
   but quarantined and unusable pending explicit deletion. When personalization is turned
   off while storage remains authorized, confirm whether the source stays stored but is
   excluded from retrieval and derived learning.
4. **Feedback:** confirm that explicit accept/edit submission stores a local feedback record
   regardless of the learning toggle, while learning authorization only controls whether it
   can create eligible learning evidence. This matches the current engine and UX-C
   disclosure; changing feedback retention needs a separate explicit policy.

Do not implement consent rows, migration defaults, deletion, retention, or UI consent copy
until these choices are resolved. No owner/profile data may be inspected or changed to
answer them.

## Planned minimal write set after policy resolution

- `docs/V01_TASK.md`
- authoritative Python storage/provenance/eligibility code and explicit migration only if
  required by the approved policy;
- P01 protocol capability/version declarations only if a client-visible readiness,
  authorization, or revocation operation is needed;
- targeted Python tests and migration fixtures;
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

## Current stop condition and next permitted action

No V01 feature code has been changed. The task is blocked before attempt 1 because ADR-004's
source revocation/retention lifecycle and legacy-example authorization treatment are
unresolved. The next permitted action is for the owner to answer the four policy points in
“Required policy decision”; after that, reassess the minimum migration and begin attempt 1
only if the resolved policy fits this contract.
