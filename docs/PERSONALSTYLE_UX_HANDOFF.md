# PersonalStyle product and UX handoff

This document separates current capabilities from future product/UX direction. Proposed
ADR-004 is in the open draft documentation-only
[PR #14](https://github.com/Poken-ninja/personalstyle/pull/14); it is not an accepted file on
main. Preserve that PR and its branch. Current execution authority is the
[execution contract](../EXECUTION_CONTRACT.md#current-status); designs and roadmap order do
not activate implementation.

## Current capabilities

At verified main `05dfea97ccc3ad97c0dbe1b0d68073cf0e2f63fb`:

- G01's authoritative `rewrite.generic` is merged in
  [PR #20](https://github.com/Poken-ninja/personalstyle/pull/20). Generic humanization requires
  no voice enrollment and does not silently fall back from a personalized request.
- V01 is merged in [PR #18](https://github.com/Poken-ninja/personalstyle/pull/18). The engine
  supports read-only aggregate exact-context `voice.status`, separate storage and
  personalization authorization (`example.authorize`), personalization enable/disable
  (`example.personalization.set`) and source revocation (`example.revoke`). It enforces
  exact-context evidence isolation. `voice.status` is not a raw profile/DNA inspection API
  and is **not exposed in Flutter**. Voice onboarding/management UI remains future work.
- UX-I02 is merged in [PR #22](https://github.com/Poken-ninja/personalstyle/pull/22):
  **Paste → choose context → Humanize → Review/Edit → Copy**. Friendly contexts map to
  Academic (`academic.essay`), Professional (`work.email`) and Everyday (`casual.chat`).
  The ordinary generic desktop flow uses engine verification, labels generic results honestly,
  permits local editing and copies without another engine call or generic feedback controls.
  Existing stored-voice rewriting remains separate; this is not an onboarding UI.

Feedback receipt-contract work remains deferred. Do not claim that positive feedback has an
authoritative persistence receipt merely because an operation returned successfully.

## Product promise

PersonalStyle is a local-first writing assistant whose primary job is to help a user make a
draft sound like their authentic voice in its specific context while preserving meaning,
important facts, legitimate citations and confirmed requirements. It is not an AI-detector
bypass tool and must not promise undetectability or guaranteed human authorship.

The future personalized journey is: discover or provide genuine writing evidence → choose a friendly writing
context → add or import a draft → humanize in the user's voice → review the source, result and
actual checks → edit or accept → optionally authorize learning from qualifying edits.
Ordinary users should not need engine IDs, protocol terms, SQLite knowledge or structured
constraint syntax.

## Product invariants

- Academic, professional and everyday/casual voice evidence remains context-isolated by
  default. The UI presents friendly labels; the engine remains authoritative for context IDs,
  eligibility and validation.
- Voice discovery is optional. Only genuine user-authored writing with the required explicit
  storage/learning authorization can become eligible voice evidence. Synthetic, third-party,
  rubric and unchanged AI-generated text are not personal-style evidence.
- Accepting a result is not consent to learn. Meaning, fact, constraint and context corrections
  are not silently converted into style preferences.
- Copy does not authorize learning or submit feedback. Generic output must never be called
  personalized, and generic use does not require enrollment.
- Verification and voice resemblance are distinct. A result is called verified only when the
  engine says its required checks passed; style quality is not represented as a hard proof.
- The Python engine owns validation, personalization, generation, verification, budgets,
  consent and canonical persistence. Flutter owns presentation, native interactions and
  user-friendly mapping to existing engine contracts.
- Errors must state the safe failure category, the affected operation and whether a durable
  mutation's outcome is known. Never expose writing, credentials, private paths or exception
  dumps. Never automatically replay an uncertain mutation.
- Handshake readiness proves neither protected profile-storage nor model readiness. The old
  protected-storage failure remains unresolved/not reproduced; no cause or fix is established.

## Screen direction

The product should be a small, polished, writing-first desktop app: neutral light surfaces,
readable typography, restrained teal accents, clear spacing, accessible focus/navigation and
responsive desktop resizing. Avoid dashboard sprawl and fake controls. The approved Figma
file is [PersonalStyle](https://www.figma.com/design/689pIZn92H8dv10nkeLmmM); the original
workspace [node 2-11](https://www.figma.com/design/689pIZn92H8dv10nkeLmmM?node-id=2-11) is an
outdated concept. Newer references are [voice discovery, node 12-2](https://www.figma.com/design/689pIZn92H8dv10nkeLmmM?node-id=12-2)
and [academic workspace, node 13-2](https://www.figma.com/design/689pIZn92H8dv10nkeLmmM?node-id=13-2);
neither has completed visual QA. The result comparison, edit/accept, voice-management and
requirements-confirmation screens still need design work. Never claim a missing frame exists.

## Future delivery direction

This is product direction, not a queue of authorized tasks. UX-A's error/recovery slice is
merged ([PR #16](https://github.com/Poken-ninja/personalstyle/pull/16)); UX-I02 supplies the
current generic writing/review/edit/copy path. The broader design and onboarding work below
is not claimed complete or activated.

1. **UX-A — actionable errors and recovery:** explain startup/runtime failures, typed engine
   errors and uncertain pending mutations; prevent accidental duplicate writes.
2. **UX-B — humanize workspace and result review:** writing-first layout, friendly context,
   original/result comparison and honest check status.
3. **UX-C — voice onboarding and management:** optional discovery and inspectable, authorized,
   context-scoped evidence only where the engine supports it.
4. **UX-D — requirements/rubric interface:** only capabilities implemented by the authoritative
   requirements/verifier engine; rubric extraction is not assumed.
5. **UX-E — usability/design acceptance:** visual, keyboard, accessibility and real Windows
   workflow evaluation.

Each future slice needs explicit owner selection and its own bounded task contract. If it needs a new engine capability, create a
separate dependency task instead of simulating that behavior in Flutter.

## Context, voice and refinement controls

The Academic workspace in the existing Figma file already proposes three friendly selectors:
**Writing context**, **Use my writing voice**, and **Optional refinement**. Keep these as
dropdowns; users should not enter engine context IDs, voice names or structured constraint
syntax. These are future design controls; the current ordinary generic action is **Humanize**.

- Selecting Academic, Professional or Everyday selects only that exact context. Default the
  voice selector to that context's own profile when eligible evidence exists. Offer an explicit
  generic mode; never borrow another context's examples or preferences.
- When the selected context has no eligible examples, say so and offer “Add writing for this
  context” or “Continue with generic writing.” Do not call generic output personalized.
- The authoritative generic path now exists as `rewrite.generic` and is exposed by UX-I02's
  ordinary Humanize action. Personalized paired `rewrite` still requires eligible evidence;
  it must not silently fall back or borrow another context. Read-only aggregate readiness
  exists as `voice.status`; future UI may use that capability after separate activation.
  Flutter does not currently expose it, and it does not provide a Writing DNA summary.
- Keep optional refinements predefined and user-controlled. Start with “Humanize only,” then
  offer a small set such as simpler wording, more concise, or more formal/conversational. A
  complexity choice describes the user's desired output, not their knowledge or expertise.
  Never infer that a user knows or does not know a subject.
- Make “preserve exact terms” a clear requirement when users select terms to protect. The
  existing verifier can enforce exact `required_literal` values; Flutter can present readable
  term chips/fields and translate them to that engine syntax. Do not claim that the engine
  automatically identifies every technical term. General technicality/style refinements remain
  quality requests, not hard verification guarantees.

## Future voice-profile inspection and adjustment

Users should be able to inspect context-scoped evidence and the derived Writing DNA without
seeing raw SQLite or needing a confidence score. The current DNA contains structural measures
such as sample count, sentence/paragraph counts, sentence-length statistics and punctuation
counts; it does not establish semantic traits such as “direct,” “advanced,” or “expert.” Present
only measurements or summaries the engine actually returns, with source context and profile
version.

Do not let users edit derived measurements in place. Separate observed evidence from explicit
user preferences: a user may choose desired wording complexity or terminology handling, while
the engine retains its reproducible derived snapshot. Persisted preference editing requires an
engine-owned, context-scoped, versioned capability and explicit acceptance tests before Flutter
exposes it. “Use simpler wording” must never imply the user lacks expertise.

## Future progressive personalization depth

PersonalStyle should work for people who want one clear action and for power users who want
fine control over how each context sounds. This is depth of user control, not a universal
“humanization strength” score. Do not promise that a higher level is more human, more authentic,
or less detectable.

- **Simple:** choose a friendly context; use that context's eligible voice by default; humanize.
- **Guided:** optionally choose wording complexity, formality/warmth, concision/detail, and
  terminology handling through clear presets. “Match my voice” is the default; users can ask
  for simpler or more technical wording without the product guessing their expertise.
- **Advanced:** inspect context-scoped source and measured Writing DNA; adjust explicit
  context-specific preferences; manage protected terms and formatting/structure requirements;
  and review which authorized evidence is used. Advanced controls remain engine-validated and
  cannot bypass fact, meaning, consent, context-isolation, verification, or resource limits.

Advanced controls must be progressive disclosure rather than a second engineering console.
Provide clear defaults and explain the effect of each control. Distinguish measured traits from
user-chosen preferences, soft style requests from hard verifiable requirements, and generic
output from personalized output. Do not expose prompt text, raw profile data or internal IDs as
the way to achieve power-user control. Each advanced feature is exposed only after the engine
has an authoritative, versioned contract and tests for it.

## Contexts with incomplete voice evidence

Profiles are independent per context. If a user has Academic evidence but no Professional or
Everyday evidence, those latter contexts remain unavailable for personalized mode. The UI may
offer the authoritative generic path with an honest label, or guide the user to add genuine
writing for that exact context. It must not synthesize a missing voice, silently switch context,
or treat an AI draft, rubric or synthetic fixture as personal evidence. The read-only engine
`voice.status` capability now supports aggregate readiness for the exact context; its Flutter
integration remains future, separately authorized work. Do not misuse `preference.evaluate`,
which is a state-changing operation.

## Current checkpoint

ST01 inspected main `05dfea97ccc3ad97c0dbe1b0d68073cf0e2f63fb` and verified PRs #18–#22
merged. F07, F08 Phase A, V01, H01, G01 and UX-I02 are completed bounded slices. F08 Phase A
TXT/Markdown native export/save cancellation and exact saved-file read-back are verified in
[PR #21](https://github.com/Poken-ninja/personalstyle/pull/21); the former blocked snapshot
is historical. F08 overall is incomplete; DOCX Phase B and PDF Phase C remain frozen/unstarted.

Voice onboarding/management UI is optional future work and not activated. Feedback receipt
semantics remain deferred. Windows alpha, S03 model setup Phase B, cross-platform protected
storage and overall V1 remain incomplete. No product success or release readiness is claimed.

The original owner-store failure remains unresolved/not reproduced. Do not repeat the owner
profile submission for this handoff or infer a storage fix from Phase A acceptance. Preserve
the [issue #17 history](https://github.com/Poken-ninja/personalstyle/issues/17) and historical
task records, including their failures, counters and pre-merge checkpoints. Current status
supersedes their old pending/dependency/next-action instructions; it does not rewrite evidence.

Preserve the dirty legacy `task/f08-document-import-export` worktree, unfinished merge and
F08 artifacts, the UX-C branch/stash and draft PR #14. Fresh work must start from current main
in a clean worktree. **No product implementation task is selected after ST01.** The next owner
decision may select a separately bounded voice onboarding/readiness task; nothing starts here.
