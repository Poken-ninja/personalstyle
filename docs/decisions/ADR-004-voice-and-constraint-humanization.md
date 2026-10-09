# ADR-004: Personal voice humanization with context and requirements

## Status and authority

**Accepted product direction, 2026-10-08.** This records owner decisions made during product/UX planning, not a claim that new engine features have been implemented or tested. The authoritative roadmap, task states and completion gates remain in [EXECUTION_CONTRACT.md](../../EXECUTION_CONTRACT.md); builder/security rules are in [AGENTS.md](../../AGENTS.md). This ADR owns the new product behavior and its boundaries. A builder must not treat acceptance of this ADR as permission to activate a task or modify code.

## Why this decision exists

PersonalStyle's primary job is **humanizing a user-supplied, often AI-written draft into writing that resembles that user's demonstrably authentic voice**. Generic editing (shorten, polish, clarify) is useful but secondary. The result must preserve source meaning and required information and respect the explicit writing context and any assignment/client requirements. A universal "humanizer" voice, detector-evasion target, or mechanical removal of apparent "AI tells" would contradict user-specific voice fidelity.

## Accepted product decisions

1. **Primary action and promise.** The primary UX action is "Humanize in my voice." Show source and result, and support accept/edit feedback. Never promise undetectability, guaranteed human authorship, plagiarism avoidance, or universal rubric compliance. A rewrite remains subject to the user's applicable academic/workplace AI-use rules.
2. **Explicit context.** The user selects a clear label (initial conceptual categories: academic, professional, casual/personal, custom). The engine resolves it into a versioned, bounded context ID; the UI must not require users to type technical context IDs. Do not infer a durable context silently. Changing context changes eligible evidence; do not treat identical user identity as permission to transfer style.
3. **Academic personal voice with constraints.** An academic rewrite SHOULD reflect the user's authorized academic writing, but academic register, disciplinary conventions, the user-approved rubric and preserved citations/facts override conflicting stylistic suggestions. This is **not** a rule to remove the user's personality from academic prose.
4. **Other contexts retain boundaries.** Professional rewriting uses professional-context evidence and recipient/workplace constraints, not automatically casual slang. Casual rewriting uses eligible casual evidence. Contexts must not be combined simply to reach an example count.
5. **Voice discovery is an optional, low-friction learning path.** Offer short original-writing questions across everyday/casual, professional and academic situations, and optionally accept user-owned writing samples. Propose three quick questions as a UX default, NOT as a proven adequacy threshold. Users may skip; insufficient evidence means provisional/generic output must be labeled accurately.
6. **Local, authorized continuity.** Store eligible answers, samples, feedback observations, preference evidence and versions in the existing authoritative local protected store. The user must explicitly authorize storage and separately authorize learning where policy requires it. Provide future inspect/delete/revoke flows before claiming full profile-control UX exists. No silent background training or cloud sync.
7. **Learning from edits.** Human-edited results are only *candidate* learning evidence; classify style/expression versus fact, constraint, context and unknown. Promotion remains deterministic, versioned and scoped, with evidence thresholds fixed before validation. An accepted result alone does not establish a particular style preference.
8. **Source provenance.** AI draft, rubric, external/reference material, model output, and held-out evaluation writing must NEVER become user-authentic voice examples by default. Only original, owned/authorized writing and appropriately qualified consented style edits can inform style. Keep per-source provenance and exclusion flags enforceable at retrieval/promotion time.
9. **Requirements architecture.** Provide a general "Requirements" capability usable for academic rubrics, client briefs or other explicit constraints. Academic context presents the rubric-specific workflow. Start from user-confirmed requirement records, not unreviewed model guesses. Objective criteria can pass/fail automatically; subjective criteria or source truth that cannot be verified must say "needs review"/"not established."
10. **No rigid AI-tell blacklist.** Em dashes, emojis, Oxford commas, bullet lists, formal words and transitions are not individual proofs of AI authorship. Detect repetition/generic phrasing only as fallible diagnostics relative to authentic user evidence and context. Never transform content solely to improve an unreliable detector score.
11. **Transparency and safety.** If insufficient voice evidence exists, label output as generic/provisional instead of verified "sounds like you." If required content/rubric checks fail, do not return a false all-clear. Cite-only preservation is not source verification. Do not fabricate claims, quotations or citations to satisfy a rubric.
12. **Architecture continuity.** One authoritative Python engine owns all context eligibility, transformations, verification, learning, provenance and persistence. Flutter and future web surfaces remain thin clients. Figma is a proposed visual design only: [PersonalStyle design](https://www.figma.com/design/689pIZn92H8dv10nkeLmmM?node-id=2-11).

## Requirements precedence and scope

For an individual run, resolve conflicts in this order:
1. Security, authorization, provenance, privacy and platform safety invariants.
2. Meaning, facts, quoted passages, required information and verified source fidelity.
3. Explicit hard requirements confirmed by the user (e.g. word-count bounds, section list, citations, required headings).
4. Context-specific hard register/format rules where defined and verifiable.
5. Authorized exact-context voice evidence and preferences.
6. Explicitly permitted shared style traits (when a future contract implements them).
7. Optional stylistic improvement controls / generic pattern diagnostics.

Do not silently override conflicts. Where a rubric asks for content absent from the input and no source supports it, report the gap rather than inventing information. When a user's style conflicts with a hard requirement, preserve the requirement while retaining as much permitted voice as possible.

The **current implementation** uses exact-context writing evidence and a narrow structural preference evaluator. There is currently **no proven baseline voice inheritance** or richer lexical/style promotion. Shared baseline traits, cross-context opt-in semantics, and profile lifecycle UI are **planned, not implemented**. The default for all new cross-context transfer is deny until an explicit compatibility policy is designed, consented to and tested.

## New execution boundaries (proposed implementation contracts)

The following are future bounded tasks. IDs, dependencies and activation are owned by the roadmap:

| Contract | Required behavior | Required evidence before passing |
|---|---|---|
| V01 — Voice evidence and isolation | Engine-owned source types, consent, versioned context eligibility, revocation/invalidation, optional shared-trait policy decision | Prove unauthorized/AI-draft/held-out samples excluded; wrong-context and revoked evidence never selected; restart/version consistency |
| V02 — Voice discovery and controls | Accessible optional contextual questions, user-owned samples, clear profile/provenance UX and engine-backed submission | Fresh-user/skip/consent-denied/restart/error paths with real protected-store and protocol checks |
| V03 — Voice-fidelity humanization | Rewrite using eligible context evidence, diagnosable generic phrasing, richer style evaluation/learning only if evidence justifies | Held-out, multi-writer voice comparison with no semantic or context regression; edits properly classified; no arbitrary dash/emoji ban |
| R01 — Requirements/rubric engine | Parse candidate criteria, user-confirm ambiguous items, evaluate hard/soft rules, present honest status | Per-criterion ground truth for supported checks; invalid/ambiguous/rubric-injection/missing-citation negative cases |
| V04 — Integrated product evaluation | Integrate voice + context + rubrics into A/B/C comparison with fixed budgets and artifact versions | Frozen, held-out cases; voice similarity, user editing effort, correctness and requirement fidelity compared with baseline |

No training new models, vector search, detector-targeted rewrite passes, silent scheduling, or multiple agents in these contracts without a separately authorized evidence-backed design change.

## Consequential rules: requirement / mechanism / evidence / violation

| Requirement and prevented failure | Applies | Enforcement mechanism required | Compliance evidence and response on violation |
|---|---|---|---|
| Isolate contexts; prevent style leakage | Every retrieval and generation | Engine-side eligibility filter default-deny; explicit compatibility records; no client-only guard | Cross-context negative fixtures + selected source IDs/versions; block selection/run and mark evidence invalid |
| Never train on AI drafts/rubrics; prevent voice poisoning | Every sample ingestion, learning evaluation, migration and retrieval | Typed source provenance + authorization + learning-eligible guard at write and read | Tampered/unknown provenance rejection, held-out exclusion and negative tests; quarantine/reject without profile mutation |
| Preserve content and requirements; prevent fabricated compliance | Every humanization run | Deterministic protected-span, rule-specific validators, bounded semantic review and honest unknown status | Criterion-by-criterion outcomes with source/version/trace; fail or surface review-needed and do not present all-pass |
| Avoid false detector claims or destructive style bans | Diagnostic + rewrite decisions | Diagnostic features advisory only; no unconditional token/punctuation blacklist; compare to user's evidence | Test naturally authored samples using dashes/emojis plus no detector-pass promise; rollback violating rule |
| Only promote qualifying feedback; prevent spurious global learning | Every feedback/event evaluation | Versioned deterministic promotion, exact-context scope, classification and separate consent | Profile before/after, source and threshold proof; reject/leave unpromoted and invalidate derived state if revoked |
| Preserve bounded recovery; prevent retry storms | Every new generation/parser/verifier loop | One authoritative call/time/size budget, classified retries, checkpoints and terminal state | Traces for success, retries, exhaustion, cancellation and resume; stop/block/escalate when budget exhausted |

## Definition of done / failures

**Specification complete:** applicable contracts, decisions, non-goals, scope and dependency boundaries are recorded; there is no runtime verification claim. This ADR meets only that documentary criterion once reviewed/merged.

**V01/V02/V03/R01 feature complete:** every task's observable positive and negative acceptance checks pass against an identified engine/protocol/client revision; evidence for consent, source eligibility, context isolation, protected storage/migration, failure paths, resource limits and restart is recorded; required CI passes for the exact head.

**Integrated V04 product evidence:** freeze writer samples, held-out text, contextual prompts/rubrics, generic baseline, exact provider/model, prompt/profile versions, evaluation instructions and pass thresholds *before* scoring. Require (a) no hard meaning/fact/constraint regression, (b) no cross-context leakage, (c) supported rubric checks truthful, (d) improved authentic-voice resemblance and editing effort versus declared baseline. Use independent human judgments where feasible; an LLM judge is not proof of independence. No pass rates or quality claims are pre-filled.

**Failure examples:** a rubric-check false pass, non-consented stored/personalized sample, training on AI draft, unrelated-context selection, unverifiable/counterfeit reference, removed authentic phrasing due to a blacklist, endless retries, stale profile evidence after revocation, or a product comparison that fails the predeclared rule. Fail closed for hard invariant breaches; record counterexample, preserve last trustworthy checkpoint and only perform bounded diagnosis/repair with owner-approved scope.

The existing Windows-alpha definition is **unchanged**; the expanded personalized-humanizer product target and rubric capability are subsequent V1 gates requiring separately activated tasks. A design document does not make a feature available to users.

## Version and migration impact (decision now, implementation later)

**No version bump for this ADR/roadmap change** because no executable wire/config/storage/profile/prompt/client behavior changes. At the observed main revision, current declarations remain: core 0.1.0, protocol 1.0, config schema 1, storage schema 3, profile schema 1 and prompt contract 1.

Before each implementation task, document a compatibility impact matrix:
- A new backward-compatible protocol capability/endpoint likely requires protocol MINOR/capability negotiation; a breaking wire contract requires a separate MAJOR decision, not a silent change.
- New persisted source types, profile relations, consent or rubric evidence may require an ordered storage schema migration (and a profile schema increment if the serialized profile representation changes). Existing sensitive records, Windows protection and rollback/recovery must be preserved. Never assume a number before the schema diff.
- A changed model instruction/envelope/selection behavior requires a new immutable prompt/selection policy identifier recorded with runs.
- New config keys require defaults and compatibility validation; config-schema bump only when the actual schema/compatibility contract changes.
- Flutter/client version changes only on actual client build/release.
- A product/package version follows the actual shipped feature and SemVer policy.

An ADR does not reserve or execute any migration. Old verification evidence becomes stale for behavior whose code, schema, prompt, eligible source scope or model identity materially changes; unrelated verified evidence remains intact.

## Unresolved before builder execution

1. **Cross-context inheritance policy:** exact definition of transferable traits, approval UX, consent lifetime, precedence and conflict handling. Until settled, deny transfer.
2. **Questionnaire sufficiency and measurement:** proposed three example situations are UX defaults, not evidence threshold; define minimum quality, length, user burden, opt-out and held-out evaluation.
3. **Feedback richness:** support for lexical/syntactic style classification is unverified; require empirical error analysis and a non-poisoning policy.
4. **Rubric grammar and authority:** accepted criterion types, specificity, conflict precedence, clarification UX, unsupported items, citations/source validation, and versioning. First source can be pasted text; F08 determines supported file import.
5. **Benchmark and market position:** acquire licensed/reproducible representative comparison tests; commercial implementations are opaque, public repo claims are not independent benchmarks; do not claim "best" without head-to-head evidence.
6. **Consent/revocation lifecycle:** when a user deletes a source, specify cascading invalidation, restart consistency and retention without destroying unrelated history.
7. **Scheduling:** F08 remains the next pre-approved dependency, not automatically activated; new tasks require explicit owner prioritization and bounded task contracts.

## Research evidence policy

Evidence should be a versioned source inventory (vendor docs, public code versions, evaluation papers and reproducible trials) created during V03/V04. Do not silently treat punctuation, emoji use or AI-detector labels as ground truth. Commercial model internals are generally not published; classify observations as documented features, disclosed implementation, vendor claims, user reports or independently tested behavior. Source changes or dataset leakage invalidate relevant conclusions.
