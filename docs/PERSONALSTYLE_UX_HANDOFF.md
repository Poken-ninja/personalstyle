# PersonalStyle product and UX handoff

This document routes product/UX work to the accepted product decisions in
[ADR-004](decisions/ADR-004-voice-and-constraint-humanization.md) and the open
[PR #14](https://github.com/Poken-ninja/personalstyle/pull/14). It does not claim that
proposed product behavior is implemented. Do not edit PR #14's branch or merge it as part of
an unrelated task.

## Product promise

PersonalStyle is a local-first writing assistant whose primary job is to help a user make a
draft sound like their authentic voice in its specific context while preserving meaning,
important facts, legitimate citations and confirmed requirements. It is not an AI-detector
bypass tool and must not promise undetectability or guaranteed human authorship.

The main journey is: discover or provide genuine writing evidence → choose a friendly writing
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
- A user who opts in should be able to build a persistent, local, context-specific voice
  profile and use it across future rewrites without re-explaining their style or being asked
  for the same consent every time. Consent state must be visible and revocable. This is
  personalization from authorized examples/preferences, not fine-tuning or retraining the
  Ollama model.
- Accepting a result is not consent to learn. Meaning, fact, constraint and context corrections
  are not silently converted into style preferences.
- Verification and voice resemblance are distinct. A result is called verified only when the
  engine says its required checks passed; style quality is not represented as a hard proof.
- The Python engine owns validation, personalization, generation, verification, budgets,
  consent and canonical persistence. Flutter owns presentation, native interactions and
  user-friendly mapping to existing engine contracts.
- Errors must state the safe failure category, the affected operation and whether a durable
  mutation's outcome is known. Never expose writing, credentials, private paths or exception
  dumps. Never automatically replay an uncertain mutation.

## Ordinary humanize and result flow

The normal path is usable without voice onboarding: paste or import a draft, choose a friendly
context, humanize, review the result, and copy or export it. Voice discovery is optional, not a
prerequisite imposed on every user. If no eligible context voice exists, the UI must explain
that state and offer generic generation only when the engine has an authoritative generic-only
path; the current `generate_pair` implementation still requires eligible examples, so this
fallback is not yet available.

The result view shows the original beside the accepted result and gives the user a direct
**Copy result** action. It should also make textual changes easy to inspect (for example, a
deterministic highlighted comparison or a clear side-by-side view); this is presentation, not
a claim that the engine semantically classified every change. Copying must not submit feedback,
save a profile example, or authorize learning.

An opt-in voice profile should persist by context, so users do not repeat setup or consent on
every rewrite. Turning profile learning off must stop future learning while preserving an
honest explanation of what already-stored examples/preferences remain and how to remove them.
This consent lifetime and revocation behavior belongs to the engine contract.

Learning from edits must never be required to use the core humanize/copy flow. Example storage,
feedback retention, and learning authorization are distinct durable behaviors and must each be
explained accurately. In the current implementation, `feedback.write` stores the
source/candidate and edited text even when `learning_authorized=false`; that flag only controls
whether eligible style evidence may contribute to learning. Therefore, the existing learning
checkbox alone is not consent to storage and cannot be described as “nothing saved” when
unchecked. Resolve that data-retention/consent contract in the engine task before exposing the
flow as an ordinary user choice.

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

## Delivery order

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

Each slice needs its own bounded task contract. If it needs a new engine capability, create a
separate dependency task instead of simulating that behavior in Flutter.

## Context, voice and refinement controls

The Academic workspace in the existing Figma file already proposes three friendly selectors:
**Writing context**, **Use my writing voice**, and **Optional refinement**. Keep these as
dropdowns; users should not enter engine context IDs, voice names or structured constraint
syntax. The primary action remains Humanize in My Voice.

- Selecting Academic, Professional or Everyday selects only that exact context. Default the
  voice selector to that context's own profile when eligible evidence exists. Offer an explicit
  generic mode; never borrow another context's examples or preferences.
- When the selected context has no eligible examples, say so and offer “Add writing for this
  context” or “Continue with generic writing.” Do not call generic output personalized.
- This fallback is a product requirement, not current behavior: `generate_pair` derives
  personalization before generating either candidate, so it currently fails with
  `NO_ELIGIBLE_EXAMPLES` when the selected context is empty. A bounded engine task must add a
  generic-only execution path before the UI offers that fallback. P01 also has no read-only
  context/profile inspection capability, so the UI cannot currently show per-context readiness
  or a Writing DNA summary before generation.
- Keep optional refinements predefined and user-controlled. Start with “Humanize only,” then
  offer a small set such as simpler wording, more concise, or more formal/conversational. A
  complexity choice describes the user's desired output, not their knowledge or expertise.
  Never infer that a user knows or does not know a subject.
- Make “preserve exact terms” a clear requirement when users select terms to protect. The
  existing verifier can enforce exact `required_literal` values; Flutter can present readable
  term chips/fields and translate them to that engine syntax. Do not claim that the engine
  automatically identifies every technical term. General technicality/style refinements remain
  quality requests, not hard verification guarantees.

## Inspecting and adjusting a voice profile

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

## Progressive personalization depth

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
or treat an AI draft, rubric or synthetic fixture as personal evidence. A read-only engine
readiness capability is needed to show these states before a rewrite; do not misuse
`preference.evaluate`, which is a state-changing operation.

## Current checkpoint

F08 has a local incomplete checkpoint on `task/f08-document-import-export` at
`52d4ca57d64df20f0a668e0db6dd40b50eda387e`. Its Phase A remains blocked: the native TXT
export/save and read-back acceptance is outstanding; the historical owner-store example-save
failure was not reproduced in a synthetic child-process test and remains unexplained. No
profile submission should be repeated for this handoff. F08 work and temporary files remain on
that branch/worktree and must not be overwritten by UX work.

Current UX-A is based on `main` at `4c5e9d26d57c05c9fa2e7ae8021fd7c78870f06a`. PR #14 is
open, draft and documentation-only. The Windows alpha remains incomplete; S03 Phase B and
F08's DOCX/PDF phases are not activated by this handoff.
