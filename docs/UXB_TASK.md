# UX-B — Humanize workspace and result review

```text
STATE: blocked — original protected-storage failure not reproduced; awaiting bounded owner decision
BASE: 9a7a2049ca9d19f5d5d9d163b54a174d073d27a8
BRANCH: task/ux-b-humanize-workspace
WRITE_SET: desktop/lib/main.dart, desktop/lib/engine.dart, desktop/test/ui_test.dart,
           src/personalstyle/security.py, src/personalstyle/storage.py,
           src/personalstyle/protocol.py, tests/test_security.py, tests/test_storage.py,
           tests/test_protocol.py, docs/UXB_TASK.md
IMPLEMENTATION: 2/2
DIAGNOSIS: 1/2
RECOVERY: 0/1
```

## Objective

Replace the engineering-form Flutter screen with the first user-facing writing
workspace based on the existing Academic workspace direction in Figma node 13:2.
The normal path uses friendly context and refinement choices, sends the existing
validated P01 rewrite request, and presents the engine-verified original/result
for review. The engine remains authoritative for context isolation, personalization,
constraint validation, generation, verification and persistence.

The old “Add your writing example” form is not part of this workspace acceptance.
It belongs to UX-C voice onboarding/management. Historical testing of that control
in the engineering prototype is not evidence that the new workspace is usable.

## Bounded scope

- Friendly Writing context selector: Academic, Professional, Everyday.
- Friendly optional refinement selector mapped to the existing `intent` field.
- Context-specific voice selection is implicit in the selected context. The UI must
  not show engine context IDs or claim readiness before the engine reports it.
- Requirements controls only for currently supported constraints: maximum words and
  exact text to preserve. No rubric import/extraction or unsupported compliance claims.
- Primary “Humanize in My Voice” action and an original/result review layout.
- Truthful verification state and existing accept/edit feedback flow.
- Remove example enrollment from this workspace; do not change its engine capability.
- Preserve safe error and uncertain-mutation handling from UX-A.

The UX-B workspace itself adds no profile behavior or schema change. The later bounded
diagnostics correction adds stage-specific protected-storage failure codes in Python/P01;
it does not alter permissions, profile contents, generation policy or storage schema.
No generic-only generation fallback: the current engine requires eligible exact-context
examples before it can generate a pair. No profile readiness or Writing DNA is invented
by Flutter.

## Context mapping

The engine accepts exact context identifiers but does not expose a context registry.
This surface maps the three user labels to the established product namespaces:

| User label | Engine context |
|---|---|
| Academic | `academic.writing` |
| Professional | `work.email` |
| Everyday | `casual.chat` |

The identifiers are transport values only and must not appear in normal UI. The UI must
not borrow evidence from another context. If a selected context has no eligible evidence,
the engine error is shown with a clear explanation and the draft remains available.

## Acceptance

1. Workspace presents a writing-first heading and friendly selectors; no raw context,
   intent-schema or constraint syntax is requested from the user.
2. Selector values map deterministically to the exact engine request. Refinements affect
   only the requested intent; they do not claim a hard verification guarantee.
3. Supported word-count and exact-term requirements map to existing engine constraints.
4. The engine receives original text, selected context, intent and constraints through P01.
5. Only engine-verified candidates render as results. Verification is not represented as
   proof of voice resemblance.
6. Original and result can be reviewed together; the existing accept/edit feedback path
   remains engine-owned and learning remains explicitly opt-in.
7. Example enrollment is absent from the UX-B workspace and remains deferred to UX-C.
8. Engine unavailable, no eligible examples, invalid input and verification failure remain
   clear, sanitized states; no raw writing, secret, path or exception is shown.
9. Focused Flutter tests cover friendly mapping, requirements mapping, result verification,
   feedback delegation, pending mutation safety, and absence of raw IDs/example enrollment.
10. `flutter analyze` and `flutter test` pass. Windows release build is not part of this
    slice unless a native integration defect is introduced.

## Failure and recovery

First implementation attempt is the primary UI slice. A second material attempt is allowed
only for one concrete defect exposed by acceptance. After the same implementation failure
twice, stop and diagnose. Preserve the existing F08 branch/checkpoint and untracked manual
test artifacts. Do not touch PR #14.

## Evidence

The old prototype's example-save failure and F08 native import observations remain historical
evidence only; neither is UX-B workspace acceptance.

- Friendly controls and exact request mapping: widget test passed.
- Feedback accept/edit, safe pending-mutation behavior, sanitized errors and refusal to render
  unverified results: covered by the Flutter suite.
- `flutter test --no-pub`: 29 passed.
- `flutter analyze --no-pub`: passed, no issues.
- Windows Debug build: passed. It was built with the existing isolated synthetic profile
  configuration and launched as a separate preview process (PID 32152). No rewrite or example
  save was invoked, and no model call was made.
- Windows Release build reached the linker but could not replace the existing Release executable
  because the older owner-open app held that file. The existing process was left untouched.
- Focused visual preview uses the context work area, exact-term/word-count controls and result
  comparison. Example enrollment is intentionally absent; it belongs to UX-C.

## Engine dependency discovered

The existing engine exposes only exact-context personalization and a paired generic/personalized
rewrite. It has no read-only voice-readiness operation and cannot run a generic-only request when
the selected context has no eligible examples. Therefore the workspace truthfully ties the voice
to the selected context and does not offer a pre-run generic opt-out. The result selector can
display the generic candidate after a successful paired run; it does not opt out of using voice
evidence for the run. A real generic-only choice requires a separate engine task and acceptance.

The UX-B screen has no example-save/onboarding control. Any example-writing acceptance belongs to
UX-C after its UI exists; it must not be inferred from attempts in the old prototype.

## Protected-storage diagnostics correction

The owner observed `STORAGE_BOUNDARY_INVALID` during synthetic rewrite acceptance.
Read-only inspection confirmed the isolated preview profile's directory/file ACL checks
and exact-context eligibility query passed, but did not establish which check failed in
the earlier rewrite. The previous engine collapsed path, directory ACL, file ACL, ACL
verifier availability, and filesystem-identity changes into one code. This bounded
correction preserves fixed stage codes through storage and P01 and maps them to distinct
UI guidance. It exposes no OS error text, paths, account identifiers, ACL entries,
profile content, or credentials. No rewrite/model retry is part of this correction.

IMPLEMENTATION ATTEMPT 2/2: owner-authorized error-specificity correction.
Targeted evidence:
- Synthetic ACL-stage tests, storage propagation test, and sanitized P01 error test: 3 passed.
- Ruff on touched Python files: passed.
- mypy src: passed (13 source files).
- Flutter test suite: 30 passed, including distinct storage-stage messaging and legacy fallback.
- Flutter analyze: passed, no issues.
- Windows Debug rebuild: passed after the owner closed the previous preview; Flutter
  launched the rebuilt app as PID 16316. The owner then observed the precise sanitized code
  `PROFILE_DIRECTORY_PROTECTION_FAILED` when attempting Humanize.
- This code identifies the failing stage (Windows protected-directory ACL verification).
  It does not expose the underlying Windows/PowerShell reason, so the ACL itself is not
  established as incorrectly configured. No profile reset, permission change, example
  write, or further model call was performed.
- No full regression, model call, profile write, or permission change was performed.

## Current checkpoint — 2026-10-15

The phrase about pausing for a hackathon was part of the draft submitted in the UI; it was
not a request to pause this task. Do not treat user-authored draft text as task control.

The owner observed `PROFILE_DIRECTORY_PROTECTION_FAILED` during Humanize. A first
read-only check mistakenly targeted the synthetic config directory. The engine resolves
the configured DB to its `data` child; rerunning the exact directory ACL verifier on that
synthetic profile directory passed. The open Debug artifact contains the expected isolated
config path, but no P01 child process remained when inspected after the failure. This does
not establish why the earlier UI operation received the failure. Classify the discrepancy
as **not reproduced on the current synthetic profile; original cause unknown**. No profile
reset, permission change, example write or additional model call occurred.

Preserved validation: 30 Flutter tests passed; Flutter analyze passed; targeted Python
tests, Ruff and mypy passed; Windows Debug build passed and the rebuilt app was launched.
No full regression or additional live model acceptance was run. The two untracked F08
manual artifacts remain untouched and excluded.

```text
TASK STATE: blocked after implementation attempt 2/2 and diagnosis 1/2
NEXT ACTION: owner decision on whether to authorize one bounded no-model reproduction
              that captures only allowlisted ACL verifier failure categories
```
