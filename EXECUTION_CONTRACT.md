# PersonalStyle V1 Execution Contract

## Current status

```text
CONTRACT_ID: PS-V1-001
CONTRACT_STATUS: contract_ready; new product direction specified, not implemented
IMPLEMENTATION_STATUS: I01 / SEC01 / F01-F07 / P01 merged in their declared scope; V1 incomplete
SELECTED_PRODUCT_TASK: none
ACTIVE_PRODUCT_TASK: none
NEXT_PERMITTED_ACTION: owner selects bounded task; F08 is next existing roadmap candidate; UX01 may remain design-only
SURFACE_STATUS: Windows Phase A merged; overall alpha incomplete; Phase B and SEC02/SEC03 not_started
ACTIVE_IMPLEMENTATION_LIMIT: 1
CURRENT_OBSERVED_MAIN: 4c5e9d26d57c05c9fa2e7ae8021fd7c78870f06a
F07_EXACT_HEAD_CI: run 37865805821 success at 0e4114f0d6fbda03676f49d1ef13ee004ce14773
```

This document owns product scope, roadmap, dependencies and completion definitions.
Status and specifications are not execution evidence. Task-specific scope, acceptance,
budgets and evidence live in the selected bounded task contract; stable builder and
security rules live in [AGENTS.md](AGENTS.md). The accepted new product direction and
version-impact policy are owned by [ADR-004](docs/decisions/ADR-004-voice-and-constraint-humanization.md).

## Completed tasks and evidence

| Task | Verified outcome | Historical record / merge evidence |
|---|---|---|
| I01 | Runnable/testable Python harness | [I01 handoff](docs/I01_HANDOFF.md); [PR #1](https://github.com/Poken-ninja/personalstyle/pull/1) |
| GitHub gate | Required Python harness check and protected main enforced | [Gate handoff](docs/GITHUB_GATE_HANDOFF.md); [PR #2](https://github.com/Poken-ninja/personalstyle/pull/2) |
| SEC01 | Declared Windows local protection boundary | [SEC01 handoff](docs/SEC01_HANDOFF.md); [PR #3](https://github.com/Poken-ninja/personalstyle/pull/3) |
| F01 | Authorized writing persistence through the Windows protected boundary | [F01 task](docs/F01_TASK.md); [PR #4](https://github.com/Poken-ninja/personalstyle/pull/4) |
| F02 | Read-derived deterministic exact-context Writing DNA | [F02 task](docs/F02_TASK.md); [PR #5](https://github.com/Poken-ninja/personalstyle/pull/5) |
| F03 | Exact-model generic/personalized generation; candidates initially unverified | [F03 task](docs/F03_TASK.md); [PR #8](https://github.com/Poken-ninja/personalstyle/pull/8) |
| F04 | Hard second-pass verification and bounded repair | [F04 task](docs/F04_TASK.md); [PR #9](https://github.com/Poken-ninja/personalstyle/pull/9) |
| P01 | Authenticated versioned loopback engine boundary | [Historical task](docs/P01_TASK.md); [PR #11](https://github.com/Poken-ninja/personalstyle/pull/11) owns recovery/final merge evidence |
| S03-WIN-ALPHA Phase A | Windows Flutter foundation and real authenticated engine lifecycle | [Historical task](docs/S03_WIN_ALPHA_TASK.md); [PR #12](https://github.com/Poken-ninja/personalstyle/pull/12) |
| F07 | Bounded, resumable 2k/5k-word long-document rewriting on the scoped Windows environment | [Historical task](docs/F07_TASK.md); [PR #13](https://github.com/Poken-ninja/personalstyle/pull/13), merged `4c5e9d26d57c05c9fa2e7ae8021fd7c78870f06a`; exact-head CI run `37865805821` SUCCESS |

F05/F06 merge: `0ffd79f305044e739815e26fd97bd1798085c717`; [historical task](docs/F05_F06_TASK.md), [PR #10](https://github.com/Poken-ninja/personalstyle/pull/10).
P01 merge: `b811eb1147afe3e2010d69324eb822ed60a0f12a`; exact-head and merged-main CI green,
246-test local recovery and real authenticated transport acceptance passed. PR #11 preserves
the historical 600s timeout/210 outcomes/two failure markers, owner-authorized 900s recovery,
246 passed447.00s locally and246 passed649.47s on exact-head CI. The historical blocked
task checkpoint remains intact; its final status is superseded by that merged PR evidence.
Phase A merge: `96afb4691dfb141601f3239b3d93f203294347d4`; source head
`09ca6a0f2a7af251e77874b9f97832c1ad04e9f1`, exact-head CI37760293989 SUCCESS.
Historical local evidence: Flutter analyze clean,22 Flutter tests passed, Windows build passed,
real P01 lifecycle/handshake passed2.673s. Its recorded failures/counters remain unchanged.
Phase A completion does not complete Windows alpha or activate model onboarding.
F07 PR #13 merged at `4c5e9d26d57c05c9fa2e7ae8021fd7c78870f06a`. Its exact-head
CI passed on `0e4114f0d6fbda03676f49d1ef13ee004ce14773`; local real-provider,
regression and static evidence and historical failures remain revision-scoped in F07's
task record. Merge and exact-head CI do not by themselves establish overall Windows-alpha
or product-quality completion.

Completed records are historical evidence for their named revisions/environments, not
instructions to reactivate tasks or reset budgets. PR records include merge SHAs and
merged-main CI evidence. No cross-platform sensitive storage, application-level storage
encryption or PersonalStyle V1/product success is claimed.
The [pre-cleanup contract snapshot](docs/history/EXECUTION_CONTRACT_PRE_CLEANUP.md)
preserves historical initial states and the full I01/SEC01 execution specifications.

## Objective

Build a local-first humanizer that rewrites user-supplied, often AI-generated drafts to resemble the **user's authentic writing voice for the explicitly chosen context**, while preserving meaning, required information, confirmed academic rubric or professional requirements and security/consent boundaries. Establish product quality with held-out writers and a generic rewrite baseline, not AI-detector scores.

### Product goal and success criterion

PersonalStyle is a local-first **personalized AI-draft humanizer**, not primarily a generic editor or AI-detector bypass tool.

Given **draft text + humanize intent + explicit context + user-authorized writing evidence + confirmed constraints/requirements**, produce a rewrite that better resembles the user's own writing *in that context* without degrading meaning, factual content, citations or applicable hard requirements.

The product success criterion is:

> On a frozen held-out evaluation, personalized humanization should improve authentic-voice resemblance and reduce editing effort or increase accept-without-edit behavior versus a declared generic baseline, while all hard fidelity, context-isolation, consent and supported rubric checks remain valid.

No numerical threshold, best-in-market claim, AI-detector bypass guarantee or measured voice-fidelity advantage is established yet. Freeze pass rules, samples and evaluation methods before scoring. [ADR-004](docs/decisions/ADR-004-voice-and-constraint-humanization.md) owns the accepted behavior and unresolved controls.

## Scope

Core V1:

- user-authorized writing examples, including user-owned samples;
- explicit context tags;
- inspectable Writing DNA;
- deterministic bounded relevant example/preference selection;
- generic and personalized rewrite generation;
- hard semantic/information/constraint/context verification;
- return the candidate;
- accept/edit feedback;
- classified edit observations and evidence-backed preference hypotheses/promotion;
- A/B/C product-performance testing;
- **accepted new V1 product target, not implemented:** optional original-answer voice onboarding, locally persisted context-scoped user voice, honest generic/provisional fallback, optional evidence-backed shared traits only after explicit policy/consent, and generalized requirements/rubric checking with an academic presentation;
- **secondary refinements:** shorten, clarify and polish; they do not replace the main Humanize in My Voice action.

Current V1 release target after the authoritative core works is one Flutter desktop app on
Windows, macOS and Linux. The terminal/CLI remains an engineering and acceptance surface.
Browser extension, iOS and Android are deferred and are not V1 release blockers. Structural
arrangements are owned by [ARCHITECTURE.md](ARCHITECTURE.md),
[ADR-002](docs/decisions/ADR-002-versioned-multi-surface-engine.md), and
[ADR-003](docs/decisions/ADR-003-desktop-first-flutter.md).

Owner-approved additions: F07 bounded/resumable long-document reliability (now merged) and later F08
document import/export precede Windows model onboarding. F08 initial import formats are
`.txt`, `.md`, `.docx`, text-based `.pdf`; initial export formats are `.docx`, `.pdf`, `.md`,
`.txt`. Parsing/export/OCR are not activated by F07. A future thin web client is approved
as a surface; deployment/transport is unresolved and requires a separate decision.
No local-web versus hosted-cloud architecture is selected here.

Excluded until observed engineering need: multi-agent systems, vector databases/embedding
retrieval, broad/general RAG, fine-tuning/reinforcement learning, autonomous or scheduled
background learning, asynchronous/background personalization, model routing, cloud-dependent
memory/state, n8n, complex orchestration graphs, unrestricted model tools, distributed
workers and production deployment. Change/activation discipline is in
[AGENTS.md](AGENTS.md#change-discipline); the disabled optional bounded reasoning extension
remains governed by [ADR-001](docs/decisions/ADR-001-single-bounded-reasoning.md).

## Consequential unknowns

### U1 — local initialization capability (resolved)

I01 is merged/verified; see the completed-task references above.

### U2 — initial Ollama model
Resolved by the owner: `F03_CURRENT_DEVELOPMENT_MODEL = ollama / qwen3:8b`, not a permanent
product requirement. Deployment/user configuration selects the model behind ModelProvider;
every generation records the exact provider/model actually used. Ordered starter tiers and
future onboarding belong to [architecture](ARCHITECTURE.md#desktop-model-onboarding-and-setup-future-s03);
current reference-model entry evidence is in the [bounded F03 task](docs/F03_TASK.md).
This supersedes the earlier 30B reference for this machine: preparation passed, but generic
generation exceeded 60 seconds with severe memory/pagefile pressure. 30B remains a Quality
option on environments that verify readiness/performance. 8B is installed but its template
compatibility qualification failed historically; the final attempt now validates exact
model/template pairs. Its single live acceptance passed and active configuration is 8B.

### U3 — held-out product-test set and success rule
Must be frozen before final product-performance testing. Do not choose the pass rule after seeing C results.

### U4 — extension host (deferred)
Browser-extension work is outside current V1 release scope. If reactivated, the host choice
must not change the authoritative engine contract.

### U5 — mobile inference (deferred)
iOS/Android companion and standalone inference are outside current V1 release scope. Their
previous architecture constraints remain preserved for future activation but do not block
desktop V1.

### U6 — desktop shell and release matrix (partially resolved)
Flutter is selected as the shared desktop shell for Windows, macOS and Linux. Exact minimum
supported OS/runtime versions remain release-time evidence and are not frozen yet.

Flutter selection does not by itself establish PersonalStyle support on those platforms.
The required engine/inference/storage mechanisms must also be supported and verified.

### U7 — application-level encryption at rest
Current policy explicitly does not claim application-level database encryption.

Before any release claims encrypted-at-rest profile storage, a concrete mechanism plus migration, recovery, backup/export, and compatibility behavior must be implemented and verified.

This does not block local V1 engineering if the product clearly relies on host OS/account/disk protection and does not misrepresent the guarantee.

### U8 — macOS/Linux protected profile boundary
SEC01, F01 and F02 currently provide sensitive-storage evidence on Windows only. Before
PersonalStyle handles sensitive persisted writing on macOS or Linux, platform-appropriate
ownership/permission mechanisms and negative/positive executable evidence must exist.
This does not invalidate the existing Windows evidence and does not block core F03 work on
the already verified Windows path.

### U9 — shared baseline voice and context inheritance
Default to exact-context-only evidence. Define consent, compatibility, provenance, trait
eligibility, conflict behavior and revocation before implementing baseline sharing; never
import casual examples automatically into academic or professional rewriting.

### U10 — voice-discovery evidence and lifecycle
Three short situational writing answers are a proposed UX default, not an adequacy threshold.
Freeze question types, source/provenance rules, sample sufficiency, local retention and
inspect/delete/learning-consent behavior before V01/V02 execution.

### U11 — requirements/rubric semantics
Define parseable criterion types, rubric/constraint precedence, explicit user confirmation,
source-citation verification boundaries, unknown/review-required status and misuse cases.
Start with pasted text; F08 determines compatible file-import surface capability.

### U12 — learning diagnostics, versions and held-out benchmark
Determine which style features can actually be learned, how false classifications are
contained, and how writing resemblance and rubric fidelity are evaluated on held-out
writers. Freeze quality thresholds, model/prompt/evaluator versions and competitor comparison
protocol *before* scoring. No punctuation/emoji blacklist or AI-detector score gate.

### U13 — release sequencing and acceptance freeze
F08 remains the next existing alpha dependency, not automatically activated. New V/R
capabilities are V1 product-target gates but not retroactive blockers for the previously
approved Windows alpha; owner must select and contract each task before code changes.

## Task plan

| ID | Task | Depends on | Current state |
|---|---|---|---|
| I01 | Establish runnable/testable Python harness | none | merged / verified |
| SEC01 | Mechanize Windows local security boundary | I01 | merged / verified |
| F01 | Persist user-authorized writing examples + explicit context metadata | I01 + SEC01 | merged / verified (Windows) |
| F02 | Derive inspectable Writing DNA/context profile | F01 | merged / verified (Windows protected store) |
| F03 | Generic + personalized generation using metadata retrieval | F02 + U2 | merged / verified; [historical evidence](docs/F03_TASK.md), PR #8 |
| F04 | Hard verification path and bounded candidate retry | F03 | merged / verified; [historical evidence](docs/F04_TASK.md), PR #9 |
| F05 | Record accept/edit events and classify edit type | F04 | merged / verified; [historical task](docs/F05_F06_TASK.md), PR #10 |
| F06 | Evidence-backed context preference promotion | F05 | merged / verified; PR #10, context_preference_promotion.v1 |
| P01 | Mechanize versioned engine protocol + authenticated capability handshake | F05 + F06 + SEC01 | merged / verified; PR #11 |
| S03-WIN-ALPHA-A | Windows Flutter foundation and engine connection | P01 | merged / verified; PR #12 at96afb4691dfb141601f3239b3d93f203294347d4 |
| F07 | Long-document bounded rewrite and recovery | S03-WIN-ALPHA-A + F04 + SEC01 | merged; [task](docs/F07_TASK.md), PR #13, exact-head CI passed |
| F08 | Document import/export in the declared initial formats | F07 | not_started |
| S03-WIN-ALPHA-B | Windows model setup/readiness | F08 | not_started; separate owner activation required |
| SEC02 | Mechanize macOS protected local profile boundary | S03-WIN-ALPHA + F01 | not_started |
| SEC03 | Mechanize Linux protected local profile boundary | S03-WIN-ALPHA + F01 | not_started |
| V01 | Voice evidence/provenance, context eligibility, optional shared-trait policy | F02 + F06; U9/U10 | not_started; requires owner task activation |
| V02 | Optional contextual voice discovery + local profile management through authoritative engine | V01 + P01 | not_started; requires owner task activation |
| V03 | User-voice humanization, safe generic-pattern diagnostics and qualified edit learning | V02 + F04; U12 | not_started; requires owner task activation |
| R01 | General requirements/rubric parsing, confirmation and criterion verification | F04; F08 for supported document imports; U11 | not_started; requires owner task activation |
| V04 | Integrated context + voice + rubric acceptance and benchmark | V03 + R01; U3/U12 | not_started; requires owner task activation |
| UX01 | Design-only Figma flows for voice setup, contexts, humanization and rubric statuses | ADR-004 | design exploration; not implementation evidence |
| E01 | Frozen A/B/C product-performance test with voice/rubric evaluation | F06 + V04 + U3 + U12 | not_started |
| S01 | Terminal/CLI acceptance surface | F06 | not_started |
| S03-WIN-ALPHA | Final Windows Flutter desktop-alpha acceptance | Phase A + F07 + F08 + Phase B + SEC01 | incomplete; Phase A merged; later phases unstarted |
| S03 | Flutter desktop app + Windows/macOS/Linux release acceptance for expanded V1 target | S03-WIN-ALPHA + SEC02 + SEC03 + V04 + U6 | not_started |

Deferred backlog, not V1 blockers: S02 browser-extension adapter, S04 iOS/Android companion
client, and S05 standalone mobile inference. Reactivating any deferred surface requires an
explicit owner decision and a fresh bounded task contract.

Do not fully design later tasks until dependencies and evidence sharpen. A next candidate
requires explicit owner selection and a bounded task contract; completing a dependency
does not auto-activate it. All I01 through F07 slices and S03 Phase A are merged in their
declared scope. F07's task ledger preserves historical retry/failure budgets; do not reset
it or reinterpret its checkpoints as current active work. At the observed main revision
`4c5e9d26d57c05c9fa2e7ae8021fd7c78870f06a`, F08 remains the next existing
Windows-alpha dependency, not_started. Phase B remains not_started; Windows alpha and
cross-platform V1 remain incomplete. New voice/rubric task IDs are bounded future
capabilities, not implicit authorization or implementation.

**Scheduling boundary:** finish the existing F08 -> Phase B -> final Windows-alpha
acceptance lane before claiming that milestone complete. V01/V02/V03 and R01/V04
are separately activated, ordered by dependencies, and required for the *expanded V1
product-target* and product-quality claims. The owner can explicitly reprioritize with
an updated task contract and dependency impact review; no doc change auto-activates work.

### Windows desktop alpha

Owner-approved Windows-alpha order: F04 -> combined F05+F06 feedback-learning slice -> P01 ->
S03-WIN-ALPHA Phase A -> F07 long-document reliability (merged) -> F08 document import/export ->
S03 Phase B model setup/readiness -> final Windows alpha acceptance. The new V01-V04/R01
voice and rubric work is a separately selected expanded-V1 product lane; final cross-platform
V1 requires those product capabilities plus SEC02/macOS and SEC03/Linux evidence.
S03-WIN-ALPHA is a distinct usable Windows UI milestone; it does not wait for macOS/Linux.
It must verify Windows core workflows, authenticated engine ownership, selected-model setup
and SEC01-protected persistence on the declared Windows environment. It is not cross-platform
V1 or E01 product-performance completion. SEC02 and SEC03 remain required before claiming
macOS/Linux sensitive storage or final S03 Windows/macOS/Linux release acceptance.
The same Flutter shell and engine boundary apply. Phase A evidence remains in
[its historical task](docs/S03_WIN_ALPHA_TASK.md). F07 is bounded by
[its historical task](docs/F07_TASK.md); F08 and model onboarding remain unstarted.

### S03 desktop model setup acceptance

Specification for later S03, which remains unstarted. S03 includes the Flutter model setup
workflow in [architecture](ARCHITECTURE.md#desktop-model-onboarding-and-setup-future-s03) and
[ADR-003](docs/decisions/ADR-003-desktop-first-flutter.md#model-onboarding-decision), in addition
to existing desktop workflow, security, packaging and platform release acceptance.

- Offer option 1 `qwen3:8b` (Standard/default and current F03 development target), option 2
  `qwen3:30b` (Quality, only after environment readiness/performance verification), and option 3
  `qwen3:235b` (Maximum/high-end optional, unverified unless separately tested).
  Require explicit choice/confirmation; never silently substitute. A later existing-model
  path accepts only models satisfying defined provider/runtime/model compatibility validation.
- Demonstrate the complete choose/inspect/estimate/runtime-check/instructions/recheck/model-check/
  exact-install-action/identity-recheck/bounded-probe/READY flow on each claimed desktop OS.
  Instructions must be platform-specific and obtain exactly the selected model.
- Distinguish shown instructions, engine/provider availability checks and executed inference
  evidence. Prove missing/stopped Ollama, missing/wrong/incompatible model, setup actions that
  did not succeed, probe failure and timeout all leave setup not READY with actionable UX.
- Treat hardware/resource estimates as advisory unless a known hard runtime requirement is
  violated. Show warnings/alternate tiers for likely unsuitable selections and prove that
  changing tiers requires user confirmation; no silent fallback or invented hardware cutoff.
- Keep detection, exact identity, readiness and bounded probe ownership in the engine/provider,
  with Flutter limited to setup UX. Verify readiness invalidation after runtime/model changes;
  probes use synthetic text and do not mutate sensitive profile data or bypass budgets.
- Record platform/runtime/model/probe evidence for every claimed supported starter combination;
  a bounded probe is inference setup evidence, not security or overall release completion.

Freeze detailed compatibility/probe acceptance in S03's bounded task before implementation.
F03 continues to prove only its generation/provider seam with the selected 8B development
evidence; this roadmap addition does not move onboarding into F03 or activate later work.

## Completion definitions

### Run complete

A run is complete only when it has a recorded terminal state:

- `SUCCEEDED`: all hard run invariants passed and a result was returned;
- `FAILED`: no acceptable candidate exists within the authorized budget or a non-recoverable hard failure occurred;
- `ESCALATED`: completion requires an external decision/input;
- `CANCELLED`: the authorized caller stopped the run.

"Generated a draft" is not complete.

### Feature complete

A feature is complete only when:
1. its acceptance criteria are explicit;
2. the current artifact passes the required checks;
3. evidence is recorded for the current revision/environment;
4. no unresolved blocker contradicts completion;
5. required handoff/state is current.

Code existence, confidence, TODO comments, or proposed tests do not count.

### Voice + requirements feature complete (new V1 product target)

For each activated V/R task, acceptance must map to revision-specific evidence: source
provenance and consent, context-isolation negative cases, protected store persistence and
migration/restart behavior (when applicable), verified source/meaning fidelity, honest
criterion-level rubric status, bounded failure paths, protocol/client compatibility and
required exact-head CI. User-facing Figma screens alone or claimed AI-detector evasion do
not count. See [ADR-004](docs/decisions/ADR-004-voice-and-constraint-humanization.md#definition-of-done--failures).

### V1 implementation complete

V1 implementation is complete when the A/B/C product-test path is runnable end-to-end:

- A: generic rewrite;
- B: context-personalized rewrite without accumulated learning;
- C: context-personalized rewrite with accumulated learning;

and the system can collect hard-invariant, edit-effort, acceptance, context, latency and
resource evidence on a held-out product-test set. For the expanded product target,
V01-V04/R01 must also be verified, including user-authentic voice evidence, explicit
context isolation, academic rubric status and guarded learning.

This does **not** mean PersonalStyle meets the product success criterion.

### Security gate complete

A release security gate is complete only when the applicable security controls in [AGENTS.md](AGENTS.md#security-contract) have executable evidence for the current artifact and supported surfaces.

A passed functional test suite does not imply the security gate passed.

### Surface complete

A CLI, extension, desktop, iOS, or Android surface is complete only when:
1. it reaches the authoritative engine through the defined protocol/library boundary;
2. it does not duplicate protected personalization/harness logic;
3. required workflows pass on the declared supported platform/version matrix;
4. protocol incompatibility, engine-unavailable, permission-denied, and migration-required states have explicit user-visible failure behavior;
5. its client and protocol versions are recorded in applicable evidence.

A successful build on one developer machine is not surface completion.

### Cross-platform release complete

A cross-platform release is complete only when every surface claimed as supported has current release evidence for every OS/runtime version claimed as supported.

Unsupported or unverified older OS versions must be labeled best-effort or unsupported, not silently counted as complete.

### Platform support evidence

"Supported" is an evidence claim.

A platform/version is supported only when:
- selected UI/runtime framework supports it;
- required engine/inference dependencies support it;
- package/build/install succeeds;
- platform acceptance tests pass;
- upgrade/migration behavior from supported prior state passes.

Older versions outside that matrix are best-effort or unsupported.

Do not design around "all historical OS versions." Maintain an explicit release matrix instead.

### Product success validated

Before the scored product test, freeze:
- test set;
- model/version;
- prompt version;
- retrieval policy;
- metric definitions;
- success comparison rule.

Product success is validated only if B/C improve the predeclared authentic-voice and
user-effort criteria versus the relevant baseline while meeting hard semantic/factual,
consent, cross-context isolation and supported rubric/requirement criteria. Subjective
rubric items and unverified source truth must be reported as requiring human review.

If they do not, the product requirement is not met. Do not redefine the metric after seeing results to manufacture success.

### Product-test evidence signals

Evidence includes hard semantic/constraint/rubric validity, context accuracy and leakage
negative tests, authentic-voice similarity using held-out user-authored samples and
human review, stylometric diagnostics, normalized edit effort, accept-without-edit rate,
user preference, latency and resource use. Testing discipline remains in [AGENTS.md](AGENTS.md#product-testing-discipline).
