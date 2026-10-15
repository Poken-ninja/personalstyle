# UX-B — Humanize workspace and result review

```text
STATE: implementation complete — awaiting owner visual acceptance
BASE: 9a7a2049ca9d19f5d5d9d163b54a174d073d27a8
BRANCH: task/ux-b-humanize-workspace
WRITE_SET: desktop/lib/main.dart, desktop/test/ui_test.dart, docs/UXB_TASK.md
IMPLEMENTATION: 1/2
DIAGNOSIS: 0/2
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

No Python, protocol, schema, storage, profile, F08 or Figma-file changes. No generic-only
generation fallback: the current engine requires eligible exact-context examples before
it can generate a pair. No profile readiness or Writing DNA is invented by Flutter.

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
