# G01 — Generic humanization without voice enrollment

```text
TASK: G01
STATE: locally verified — implementation attempt 1 complete; publication checkpoint next
BASE: 0ffd5844bc4c26a172bcda43472bee2722c82c53
BRANCH: task/g01-generic-humanization
WIP: 1
IMPLEMENTATION: 1/2
DIAGNOSIS: 0/2
RECOVERY: 0/1
DEPENDENCIES: F03 generation; F04 hard verification; P01 protocol 1.1; V01 consent boundary
```

## Objective

Enable a user to request a clearly identified generic rewrite without supplying or
authorizing voice samples. Reuse the existing authoritative generation and hard-verification
policy. This implements the approved `Paste → Humanize → Review → Copy` path without
pretending generic output is personalized.

Current observed gap: `generate_pair` generates a generic candidate and a personalized
candidate together, but it first reads eligible exact-context voice evidence. `verify_pair`
also requires both candidates and re-reads personalization evidence. With no eligible
examples, the engine returns `NO_ELIGIBLE_EXAMPLES` before the generic candidate can be
returned. This is a missing standalone operation, not a failure of the previously verified
F03 paired-generation contract.

## Write set

- `docs/G01_TASK.md`
- `src/personalstyle/generation.py`
- `src/personalstyle/verification.py`
- `src/personalstyle/protocol.py`
- focused generation, verification and protocol tests
- `personalstyle.toml` only if an existing version/capability declaration requires a
  compatible additive update; no speculative version bump

No Flutter, F08, UX-C, consent, schema, profile, storage, ACL, or user-data changes.

## Contract

- Add an explicit protocol 1.1 capability for generic-only rewrite; never silently fall back
  from personalized rewrite.
- Validate the same bounded request envelope and explicit context before provider work.
- Do not read, create, initialize, or mutate the profile database for a generic rewrite.
- Use the configured authoritative provider and existing model identity, prompt, timeout,
  output, attempt and shared model-call ceilings.
- Apply the existing deterministic fact/constraint checks and semantic second-pass verifier.
  A generated candidate is never returned as a verified result until all required checks pass.
- Reuse shared generation/verification logic; do not create a parallel verifier or retry loop.
- Return provenance that identifies generic mode and accurately represents no examples,
  Writing DNA, preferences, or personalized profile dependency.
- Do not store feedback, examples, consent or profile state as part of this operation.
- Capability negotiation must reject clients requesting an unsupported capability and keep
  same-major minor-version behavior additive. The existing P01 protocol version is 1.1.

## Acceptance

1. A generic rewrite succeeds through authenticated P01 without any eligible example and
   without creating or reading a profile database.
2. Wrong/missing protocol capability, malformed input and oversized input reject before any
   model call.
3. No example, preference, Writing DNA, consent, feedback or database content enters the
   generic prompt or response provenance.
4. Deterministic required-information and constraint failures reject the candidate.
5. Semantic verification is performed through the existing hard-verification behavior;
   verifier failure, repeated identical failure, and exhausted budgets remain failures.
6. Generation and verification share the existing bounded operation/model-call budget; no
   hidden retry is introduced.
7. Existing paired generic+personalized F03 behavior and F04 verification tests remain
   compatible.
8. Logs/errors contain no raw request text, provider prompt, credential or profile data.
9. A deterministic synthetic-provider protocol acceptance passes; one configured local
   `ollama / qwen3:8b` synthetic-content acceptance proves a real verified generic-only path.

## Verification

- During implementation: focused generation, verification, and protocol tests only.
- Final local: focused G01 tests; relevant F03/F04/P01/V01 compatibility tests; Ruff,
  mypy, pip check, `git diff --check`; one configured-provider acceptance.
- Complete regression: required exact-head GitHub CI with all test modules assigned exactly
  once. Do not duplicate a full local regression without a specific documented need.
- Do not use a real user profile or live user writing. Do not call the model before the
  deterministic and protocol tests pass.

## Budgets and stop rules

- Implementation attempts: 2. Attempt 1 is the primary standalone generic operation.
- Diagnosis attempts: 2, non-modifying and evidence-led.
- Recovery attempts: 1, only for one materially different repair after classification.
- Preserve all historical F03/F04/V01 failures and counters. These are new G01 counters.
- Same material failure twice means stop and diagnose. No repeat-until-green runs.
- Stop if the existing verifier cannot safely accept a generic-only receipt without a
  broader state/schema change; present the exact required change rather than bypassing F04.

## Explicit exclusions

No UI mode selector, onboarding, generic/personalized automatic switching, learning,
feedback retention, example entry, context inference, provider/model routing, schema change,
long-document changes, file import/export, or profile initialization. UX-C may expose this
capability only after G01 is verified and reconciled into its own checkpoint.

## Checkpoint

The existing UX-C branch and checkpoint `2712ca9c341ea20143719bb71d3db3db24f7c11f` are
preserved unchanged. V01 gate evidence is PR #18 merge `8cf61458d407eb3ba14ecf7fd11fee74ca371aa5`
and post-merge CI run `39728117199` (all six jobs passed). H01 is PR #19 merge
`0ffd5844bc4c26a172bcda43472bee2722c82c53`; post-merge CI run `39729222067` passed all six
jobs. F08 remains incomplete and its untracked local artifacts are preserved.

## G01 evidence — implementation attempt 1

- Added explicit protocol 1.1 `rewrite.generic`; existing `rewrite` remains paired and does
  not fall back silently. The generic capability uses the authenticated envelope, explicit
  context and existing request limits.
- Generic generation skips personalization derivation and emits only a generic candidate.
  Generic verification skips profile reads and retains deterministic checks, semantic
  second-pass verification, hard failures, repair policy and shared call ceiling.
- Focused G01 plus F03/F04 compatibility tests: **6 passed in 47.38s**. The paired
  provenance compatibility case took 40.894s; the generic cases passed in the same run.
- Protocol pre-dispatch matrix after the explicit 1.1 test correction: **15 passed in
  2.77s**, including a malformed `rewrite.generic` request and oversized-body rejection;
  each case was repeated 20 times and rejected before engine dispatch.
- The affected generation, verification and protocol modules completed through the H01
  runner with exit 0 before the protocol test was tightened to explicitly send protocol
  1.1. The runner removes successful reports; the six-test result above is the retained
  exact-count evidence on the final test revision.
- Configured-provider acceptance: **PASSED** with `ollama / qwen3:8b`, synthetic text,
  generic mode, 3 model calls, 47.016 seconds, final `SUCCEEDED / verified`; no profile
  database was created. The run used a temporary isolated path and did not access the
  owner's profile or writing.
- Ruff `src tests`: passed. Mypy `src`: passed after an explicit paired-mode DNA invariant
  check. `pip check`: passed. `git diff --check`: passed. Static checks were rerun once on
  the corrected source revision.
- The protocol test now explicitly declares protocol `1.1`. This was a test-precision
  correction; it did not alter production behavior. The earlier fixture-only verification
  failure and isolated corrected pass are preserved in conversation history.
- No full local regression was run. Exact-head GitHub CI is the complete regression gate.

Current counters: implementation **1/2 used**, diagnosis **0/2**, recovery **0/1**.
Remaining limitation: the generic-only capability is engine/protocol-only and has not been
exposed through Flutter. No user-profile or UI behavior is claimed. Next permitted action:
commit and publish this bounded G01 implementation for exact-head CI; do not merge until the
owner reviews it.
