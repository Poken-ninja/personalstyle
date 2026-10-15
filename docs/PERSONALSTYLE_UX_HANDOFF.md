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
