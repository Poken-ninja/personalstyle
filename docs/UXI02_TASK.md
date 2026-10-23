# UX-I02 — Generic Humanize → Review → Copy

```text
STATE: ACTIVE — recovery scope narrowed; verification pending
BASE: b4acde3a8831a2f5f3f83d383a371f0d33f5f2f1 (origin/main)
BRANCH: task/ux-i02-generic-flow
HEAD: b4acde3a8831a2f5f3f83d383a371f0d33f5f2f1
IMPLEMENTATION: 1/1 used
CORRECTION: 1/1 used
DIAGNOSIS: 1/1 used — focused diagnosis identified an authoritative response-contract gap
RECOVERY: 1/1 used — owner-authorized scope reduction only
```

## Objective

Wire the ordinary Flutter desktop journey to the existing authoritative
`rewrite.generic` capability. The UI must label its result as generic, accept
only the engine's verified response, and allow local editing and clipboard copy
without profile, feedback, consent, learning, or other engine mutation.

The paired `rewrite` operation remains available through its existing explicit
path and its behavior is not changed. F08 document behavior and all Python
production behavior are excluded.

## Verified prerequisites

- `origin/main` includes protocol 1.1 and advertises `rewrite.generic`.
- The protocol accepts the same bounded rewrite payload for `rewrite.generic`
  and invokes the engine's generic generation/verification mode.
- Existing repository evidence establishes contexts `academic.essay`,
  `work.email`, and `casual.chat`.
- V01 feedback returns `recorded: false` when learning authorization is false.
- The UX-C checkpoint contains a local clipboard-copy pattern and a test that
  asserts copying does not submit feedback; only that minimal pattern may be
  carried forward.
- F08 Phase A remains merged; DOCX/PDF phases remain frozen.

## Write set

- `desktop/lib/engine.dart`
- `desktop/lib/main.dart`
- `desktop/test/engine_test.dart`
- `desktop/test/ui_test.dart`
- `docs/UXI02_TASK.md`

No other files are authorized without stopping for owner direction.

## Acceptance and verification

1. Startup handshake requires `rewrite.generic` while retaining protocol 1.1
   and all existing advertised capabilities.
2. Friendly context choices map exactly to the three verified engine IDs.
3. The ordinary Humanize action makes one `rewrite.generic` call with explicit
   context and existing bounded intent/constraint inputs.
4. Only `SUCCEEDED` + `verified` generic results are displayed; generic output is
   identified as not using stored writing voice.
5. Result edits are local. Copy sends the current edited text to the system
   clipboard and causes zero engine calls.
6. Generic review/edit/copy exposes no feedback or learning control, causes no
   `feedback.write` or profile mutation, and claims no feedback persistence.
7. Generic Humanize has no learning-consent prerequisite. Paired rewrite and its
   existing feedback behavior remain outside this task and unchanged.
8. Merged F08 document behavior remains unchanged.

Tier 1: focused engine serialization and widget tests for generic routing,
context, verified-result gating, local editing/copy no-call behavior, absence
of generic feedback controls, and preservation of the paired route.

Tier 2: affected Flutter engine/widget tests, `flutter analyze`, and Windows
build. No local full Python suite, model invocation, or native F08 acceptance.

Tier 3: publish one exact revision and inspect required exact-head CI. Do not
merge without owner approval.

## Failure and recovery rules

- One implementation attempt and one materially different correction.
- One focused diagnosis pass; no repeated identical run after a concrete failure.
- Stop if the authoritative context mapping is contradicted, generic mode
  accesses or requires profile evidence, Python behavior must change, consent
  policy is ambiguous, or the write set must materially expand.
- Preserve this worktree and evidence if blocked. Checkpoint only intended files;
  do not touch the dirty F08 root, UX-C branch/stash, PR #14, or owner profile.

## Evidence log

- Initial state: clean isolated worktree created from the verified `origin/main`
  SHA above. The original F08 worktree remains untouched.
- Initial focused run: the engine tests passed; 2 widget tests failed because
  one expected paired output after generic routing and another still interacted
  with the old Accept label/learning-off submission path. Remaining widget tests
  passed. One test-only correction updated those expectations and added an
  explicit paired-route regression test.
- Focused Flutter verification after that correction and subsequent in-scope
  context/default-intent refinements: engine and UI test files passed (37 tests
  total). `flutter analyze` and Windows Release build passed on the preceding
  source revision; later small `main.dart` changes mean those two results do
  not apply to the exact current worktree revision and were not repeated after
  the stop condition was identified. Final `git diff --check` passed on the
  current WIP. No exact-head CI was started.
- Test-harness observations: the initial sandboxed Flutter invocation stalled
  without test output; the elevated invocation exposed a Flutter native-assets
  setup crash because this clean worktree had no generated package config.
  Offline `flutter pub get` created the local config. One invocation from the
  worktree root resolved Flutter's enclosing package and found no tests;
  running from the actual `desktop/` package directory fixed that. These were
  setup/cwd issues, not product test failures.
- Pre-edit source review confirmed generic mode skips `derive_personalization` in
  generation and verification, and the protocol routes `rewrite.generic` to
  `mode="generic"`. Its result has one generic candidate. This supports a
  Flutter-only integration; no Python write is needed.
- Original stop reason (historical): the current Python protocol returns
  `{"recorded": false, "reason": "LEARNING_NOT_AUTHORIZED"}` when learning is
  off, but when learning is authorized its success response contains `id`,
  `classification`, `record_version`, and `profile_version` and omits
  `recorded: true` (`src/personalstyle/protocol.py`, feedback.write handler).
  UX-I02 explicitly permits a persistence acknowledgement only after
  `recorded == true`. Treating the success-shaped response as `true` would
  violate that contract; treating the absent field as `false` would falsely
  tell the user their authorized feedback was not recorded. Python production
  changes are outside this task's write set, so this acceptance point cannot
  be implemented truthfully here.
- Owner scope decision: do not add `recorded: true` in UX-I02. The ordinary
  generic workflow does not need feedback persistence, so its feedback/learning
  controls and requests are removed. Positive feedback persistence is deferred
  to a separate future **Feedback receipt contract** task. That task must decide
  whether persisted `feedback.write` responses expose `recorded: true` and define
  truthful UI semantics for feedback storage versus learning authorization.
- Recovery work retains generic request routing, friendly context mapping,
  verification gating, generic labeling, local result editing and clipboard-only
  copy. Generic results expose no feedback controls. Existing paired rewrite
  and feedback behavior remains unchanged. No Python production code changed.
- Recovery verification on the narrowed revision: `flutter test --no-pub
  test/engine_test.dart test/ui_test.dart` passed all 34 tests. These are all
  test modules in the desktop package. Coverage includes the generic request,
  all three context mappings, verified-result gating, local edit/copy with no
  additional engine call, absence of generic feedback controls, and explicit
  paired rewrite plus its existing uncertain-mutation path.
- `flutter analyze --no-pub`: passed with no issues.
- `flutter build windows --release --no-pub`: passed; produced the Windows
  Release executable.
- `git diff --check`: passed. No Python source, F08 behavior, profile data, or
  unrelated worktree was changed.
- The earlier 37-test, analyzer and Windows build evidence remains historical;
  the recovery verification above is the applicable evidence for the narrowed
  implementation.
- Publication/CI are not yet complete. The precise next action is to verify and
  commit only this task's five authorized files, push this branch, open one
  draft PR, and observe exact-head CI once.
- F08, UX-C, PR #14, owner profile, and the original dirty F08 worktree remain
  untouched.
