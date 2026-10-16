# UX-C — Discover and manage a context-specific writing voice

```text
STATE: blocked — V02 voice onboarding awaits V01; Copy result/disclosure slice checkpointed
BASE: 266aad9700b1bed6e1966d4a26f86d5eba69bde3 (UX-B checkpoint)
BRANCH: task/ux-c-voice-onboarding
WIP: 1
IMPLEMENTATION: 1/2 (attempt 1 consumed by the Copy result/disclosure Flutter edit)
DIAGNOSIS: 2/2 (prior synthetic diagnosis plus this bounded protected-storage diagnosis)
RECOVERY: 0/1
```

## Product objective

Voice setup should feel like a short conversation that helps the user discover how they
naturally write. Do not make the primary onboarding experience a blank “paste examples so we
can remember your voice” form. Ask a few optional, context-specific original-writing
questions, then show the user what the system can actually infer and let them correct,
remove, or explicitly add preferences. The user decides what represents them.

The workflow is:

```text
choose Academic / Professional / Everyday
→ answer a short natural prompt (or skip / provide genuine existing writing)
→ optionally opt into a persistent local voice profile for this context
→ explicitly authorize source storage and personalization use under the engine's consent policy
→ engine derives a transparent context-scoped profile
→ user reviews evidence and proposed interpretation
→ user confirms, edits, removes, or adds explicit preferences
→ later generation uses only confirmed, eligible information for that context
```

No cross-context voice mixing. Never imply that a few answers establish a statistically
validated personality or voice. Do not use synthetic, third-party, rubric, or unchanged
AI-generated writing as the user's authentic voice.

For users who opt in, profile authorization should persist per context so they do not have to
re-explain their style or reconfirm the same choice on every rewrite. Make profile state
visible and revocable; define whether disabling learning affects only future evidence or also
removes prior evidence before implementation. “Training” here means building a local profile
from authorized examples and preferences, not fine-tuning/retraining the Ollama model. Generic
use must remain available without opting into personalization once the engine supports that
path.

## Repository-grounded capability boundary

Current implementation evidence from `src/personalstyle/profile.py` and
`tests/test_profile.py`:

- `writing_dna.v1` reads eligible examples for one exact context and returns a source
  profile version/fingerprint plus structural measurements: sample/word/sentence/paragraph
  counts, mean/median sentence length, sentences per paragraph, and punctuation counts/rates.
- It does **not** infer semantic traits such as directness, warmth, confidence, vocabulary
  sophistication, or technical expertise. It does not store a user-editable voice profile.
- Existing F06 preferences are narrow deterministic structural preferences, not a general
  personality editor. The engine currently has no read-only voice-status protocol capability.
- Existing examples require explicit authorization; `learning_eligible` is separate. The
  engine owns eligibility, exact-context selection, derivation, and persistence.

Therefore the UI must not label structural measurements as a complete analysis of how the
person speaks. Any human-readable semantic profile must be a proposal the user can inspect
and correct, backed by an engine-owned, versioned representation and tests before Flutter
uses it. Observed measurements, machine-proposed interpretations, and user-confirmed
preferences must remain visibly and durably distinct. A user correction must not rewrite the
source evidence or masquerade as an observed fact.

The engine contract must define what generates any semantic suggestions, how untrusted model
suggestions are validated, what is persisted, how edits/deletions work, and how confirmed
preferences affect generation. If the smallest safe implementation requires a new persisted
profile entity or migration beyond the existing schema-3 contract, stop at that boundary and
record the proposed minimal change for owner review; do not add schema or pretend Flutter can
own it.

## Simplification review — recommended delivery split

The simplest useful first slice does not need a new model-based personality analyzer or a
new profile schema:

1. Ask one optional, natural prompt for each context the user wants to set up. Send each
   explicitly authorized response through existing `example.write`; it remains an ordinary
   exact-context example, not a special questionnaire record.
2. Add one additive, read-only engine operation that returns the existing `writing_dna.v1`
   summary and eligible-example count for the selected context. It must not initialize a
   missing database or expose sample text.
3. Show only truthful measured observations from that snapshot. Do not turn counts into
   semantic labels such as “direct” or “warm.” Existing source examples and DNA already feed
   personalized generation, so this gives a real end-to-end improvement without a second
   profile representation or migration.
4. Keep already supported per-request refinement controls separate from the derived profile.
   Do not pretend a refinement choice is saved as a profile preference.

The requested editable semantic voice card is a distinct engine capability, not a Flutter
shortcut. The existing `preferences` table is reserved by `context_preference_promotion.v1`
for three narrowly validated feedback-derived structural features; it cannot safely hold
arbitrary user traits. Supporting durable add/remove/correct operations that affect future
generation needs an explicit profile-state contract, migration/rollback tests if storage
changes, provenance, and deterministic consumption rules. Keep that as the next bounded
engine task if it cannot fit the existing schema safely. Do not mix an AI analyzer, flexible
trait framework, and onboarding UI into the first simple onboarding slice.

## Prior diagnosis — preserve history

- UX-B is checkpointed but blocked; its two implementation attempts are exhausted. Do not
  change its history or counters.
- The preview app uses an isolated synthetic configuration. Its protected `data` directory
  passed the ACL verifier and had zero eligible Academic examples.
- The repository-configured profile directory passed the read-only ACL check; its SQLite
  database was absent at inspection. No user database was opened or created in that check.
- The original `PROFILE_DIRECTORY_PROTECTION_FAILED` report was not reproduced; its cause
  remains unknown. Synthetic authenticated `example.write`, storage round-trip/idempotency,
  and first-database rollback tests passed. One old expected generic boundary code was
  corrected to the existing specific safe code and passed in isolation.
- No model call, owner-profile write, consent grant, ACL change, or profile initialization
  occurred during that diagnosis.

## Consent UI audit — verified current implementation

- The current Flutter workspace has a checkbox for **learning from feedback** only
  (`desktop/lib/main.dart`, `feedbackLearning`). It is not consent to store an original
  writing sample.
- The current Flutter UI has no writing-example submission flow or storage-consent checkbox;
  `desktop/test/ui_test.dart` explicitly asserts that “Save authorized example” is absent.
- The Python protocol exposes `example.write`, and `ExampleInput` requires
  `authorized=True`, with `learning_eligible` separately represented. Those engine fields
  are not evidence that a user saw or accepted a consent choice.
- The current result checkbox is only learning authorization. `feedback.write` is sent for
  accepted/edited feedback whether it is checked or not, and `record_feedback` durably stores
  the source candidate and edited text in either case. `learning_authorized=false` excludes
  eligible learning; it does not mean “do not store this feedback.” The current UI therefore
  lacks an explicit explanation/choice for that durable feedback write too.
- Therefore no onboarding/sample save may be wired by silently hard-coding authorization.
  The consent controls and their meaning must be visible and explicit before submission.
  This confirms the V01 gate is real; it is not just a missing profile-status API.

The ordinary humanize → review → copy path must not require onboarding or learning consent.
Copy must not trigger `feedback.write`. Voice discovery, example storage, feedback retention,
and learning authorization are separate actions with truthful explanations. Resolve the
current feedback-retention semantics in the V01 engine contract before presenting the existing
checkbox as sufficient user consent. Do not reprompt the user on every rewrite: implement a
clear persistent per-context opt-in/revocation policy, with per-event provenance derived and
validated by the engine. The exact revocation effect on previously stored examples is an
engine-policy decision that must be settled before code.

## Attempt 1 — result copy and accurate feedback disclosure

Bounded write set: `desktop/lib/main.dart`, `desktop/test/ui_test.dart`, this task record, and
the UX handoff. Add a direct copy action that copies the current result/edit locally without
calling the engine. Keep the learning checkbox optional; state plainly that submitting
feedback stores the event locally regardless of that checkbox, while the checkbox controls
eligibility for future learning. No Python behavior, protocol, consent policy, storage schema,
or model behavior changes in this UI correction. The separate V01 gate remains required before
adding voice onboarding, persistent profile consent, or example submission UI.

Verification checkpoint (2026-10-16): the earlier sandboxed Flutter/Dart launches stalled with
no diagnostics; a direct analyzer process was stopped. This was not a code failure. Re-running
with the installed Flutter SDK outside the sandbox completed: focused `test/ui_test.dart` passed
18/18 in about 8 seconds, and `flutter analyze --no-pub` passed with no issues in 9.5 seconds.
The evidence supports an SDK/tool-launch restriction in the earlier environment, not a Dart
source defect. `git diff --check` also passed. No version/config/protocol/storage declarations
changed.

## Bounded protected-storage diagnosis — 2026-10-16

- Local branch/HEAD: `task/ux-c-voice-onboarding` / `266aad9700b1bed6e1966d4a26f86d5eba69bde3`;
  `origin/main` is `9a7a2049ca9d19f5d5d9d163b54a174d073d27a8` and is an ancestor. Existing
  tracked changes, F08 untracked artifacts, and `tests/test_storage.py` were preserved.
- GitHub read-only check: PR #16 is merged; PR #14 remains open/draft at
  `cd9dfa5384c689ef6e4d6d7116bd51cf9b2e4f0c`. Latest issue #17 comment says F08 is still
  incomplete; no F08 export/read-back evidence was added by this diagnosis.
- The screenshot's `PROFILE_DIRECTORY_PROTECTION_FAILED` maps to `EngineFailure.protectedStorage`.
  In `src/personalstyle/security.py`, that exact code is produced when the bounded Windows
  PowerShell directory ACL verifier returns a nonzero exit code. A subprocess launch/10-second
  timeout instead maps to `PROFILE_ACL_CHECK_UNAVAILABLE`. The verifier suppresses its raw
  output, so the exact ACL predicate (owner, inheritance, identities, or rights) cannot be
  recovered from the safe code.
- Engine startup/readiness only launches P01 and completes the authenticated handshake; it does
  not verify the profile directory. Storage is checked when an operation accesses the store.
  Current UX-C source invokes `rewrite` and `feedback.write`; rewriting reads eligible examples,
  and feedback writes a durable record. The widget stores the safe failure code but does not
  retain the capability name, so the screenshot alone cannot identify which operation triggered
  it. The banner remains in the in-memory UI state until another operation clears it or the app
  restarts. `Local engine ready` therefore means protocol connection only.
- The local configured `data` directory exists. A fresh **read-only** call to the same
  `verify_private_directory` routine passed under the current account/config. This does not
  prove the screenshot's app used the same executable/config/account at failure time or that the
  earlier result was false. No database was opened, no content inspected, no ACL changed, and no
  profile operation was replayed.
- At inspection there was no running desktop process. An earlier process observation pointed to
  the local Debug executable; Debug and Release executables have 2026-10-15 timestamps, while
  `desktop/lib/main.dart` has a later 2026-10-16 modification time. The binaries do not identify
  an embedded source SHA. The screenshot's exact runtime build/revision is therefore unproven.
- Classification: **unresolved / not reproduced**. The observed engine code establishes a
  directory ACL verification rejection at the time of the failed operation; current read-only
  verification passes. No underlying ACL mismatch or application defect was demonstrated. No
  storage/security repair is authorized or justified by current evidence.
- Counter reconciliation: implementation 1/2 (Copy result is the first material edit),
  diagnosis 2/2, recovery 0/1. The previous “Implementation: 0/2” budget line was stale and is
  corrected below; no historical attempt was reset.

## Phase 1 — guided discovery and truthful profile review

Start with a small optional questionnaire, not an empty sample-entry screen. Use one natural
prompt per chosen context, such as:

- Everyday: “A friend asks why your plans changed. What would you say?”
- Professional: “Ask a colleague for an update you are waiting on.”
- Academic: “Explain an opinion you have about technology and learning.”

Let users answer naturally, skip any prompt, or add genuinely authored existing writing.
Explain that responses provide examples for this specific context. Before storing, ask for
explicit storage authorization; separately ask whether the example may be used for
personalization. Both controls default off. Never ask users to imitate a style or claim that
three answers are a validated threshold.

After authorized evidence exists, present an honest review:

- which context the evidence belongs to and how many eligible samples support it;
- measured structural Writing DNA with plain-language explanations;
- any semantic voice interpretation only if an authoritative engine capability actually
  supplies it, clearly marked as a suggestion until the user confirms it;
- controls to correct/remove a proposed interpretation or add an explicit context-scoped
  preference, only after that state is supported by the engine;
- a clear provisional/unavailable state when evidence is absent or insufficient.

Do not let users edit measured counts or source fingerprints. Separate “what the examples
show” from “what I want my writing to sound like.” Advanced controls may later offer choices
such as wording complexity or terminology preservation, but those are explicit preferences,
not claims about the user's knowledge. Only expose a control when generation can consume its
engine-owned state.

## Phase 0 — finish scope/contract inspection before feature edits

1. Recheck the actual branch/base, worktree, PR #14 and untracked F08 artifacts. Preserve
   them; do not stage or clean them.
2. ADR-004 was read from PR #14 head `cd9dfa5384c689ef6e4d6d7116bd51cf9b2e4f0c`.
   It orders V01 (voice evidence and isolation) before V02 (voice discovery and controls).
   Do not edit that branch or duplicate its contract.
3. Trace actual protocol, profile derivation, schema-3 persistence, preference consumption,
   consent, and Windows protected-storage APIs. Do not infer behavior from architecture prose.
4. Define the smallest engine-owned API and state needed for discovery/profile review. Keep
   Flutter a thin client. Determine whether suggestions can be derived deterministically or
   need bounded model assistance; do not add model calls without a declared prompt, limits,
   provenance, and explicit user confirmation.
5. If new durable semantic traits/preferences require a schema or compatibility change,
   stop and present that exact minimal change before feature implementation.
6. Update this contract and acceptance tests before consuming implementation attempt 1.

**Entry gate:** this UX-C task is V02. It cannot start feature implementation until the
owner activates and verifies the V01 engine contract for typed source provenance, consent,
context eligibility, revocation/invalidation, and protected-store restart behavior. Existing
`example.write` is reusable after that gate; reusing it now would bypass the accepted
sequence. Keep the useful simplification: V02 should then use existing example storage and
`writing_dna.v1` status rather than inventing a second sample store or an AI trait framework.

## Write set (provisional; narrow after Phase 0)

- `docs/UXC_TASK.md`
- Flutter voice-discovery/profile-review UI and its focused tests
- only the minimum authoritative Python protocol/profile/storage files and migration/tests
  justified by the Phase 0 contract
- no shared status/architecture files unless required after a coherent verified slice

Do not edit PR #14's branch or shared unmerged decision documents. Leave the untracked F08
manual artifacts and pytest directories untouched.

## Acceptance (after V01 entry gate)

1. A first-time user can choose a friendly context and answer an optional original-writing
   question without entering technical IDs or a blank generic “voice sample” form.
2. Skip and existing-authored-writing paths are clear; storage authorization and learning
   authorization are separate, explicit, and off by default.
3. Synthetic/third-party/AI-generated text cannot be represented as authentic voice evidence.
4. All evidence and derived information are exact-context scoped; another context is never
   silently borrowed.
5. The user can inspect what the engine actually measured and the source version/fingerprint
   without raw database access or invented confidence scores.
6. Semantic suggestions, if implemented, are visibly provisional until user-confirmed; the
   user can correct/remove them, and confirmed preferences are versioned engine-owned state.
7. The UI distinguishes source observations, machine suggestions, and user choices. It never
   edits derived measurements or claims a semantic capability that the engine lacks.
8. No UI path creates or mutates canonical state outside the authoritative engine; no
   automatic mutation replay; no raw writing, credentials, or sensitive paths in ordinary
   logs/errors.
9. Missing profile/database and protected-storage errors are reported accurately without
   implicit initialization, data reset, or permission changes.
10. Targeted engine/UI tests and static/build gates pass before the task can be called
    verified; real owner-profile or model operations require separate explicit authorization.

## Budgets and stop rules

- Implementation: 1/2 used. Attempt 1 is the Copy result/feedback-disclosure material Flutter
  edit recorded above;
  attempt 2 is one material repair for an evidenced defect.
- Diagnosis: 2/2 used; the prior isolated synthetic diagnosis and the protected-storage
  diagnosis above are both preserved. No further diagnosis cycle is available in this task.
- Recovery: 0/1 used.
- Fixture-only/test-expectation fixes do not count as implementation attempts unless they
  materially change product behavior.
- Same material failure twice → stop and diagnose. No repeat-until-green loops.
- Stop if honest voice review requires an unspecified schema, model policy, or consent rule.

## Exclusions

No F08 export/import changes, profile initialization, owner-data inspection or writes,
consent grants, model runs, Figma edits, rubric UI, S03 Phase B, cross-context sharing,
deletion/revocation controls unsupported by the engine, or general voice-learning expansion.
