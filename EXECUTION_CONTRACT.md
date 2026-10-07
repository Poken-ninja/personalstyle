# PersonalStyle V1 Execution Contract

## Current status

```text
CONTRACT_ID: PS-V1-001
CONTRACT_STATUS: contract_ready
IMPLEMENTATION_STATUS: I01 / SEC01 / F01 / F02 merged and verified; V1 incomplete
ACTIVE_PRODUCT_TASK: none
NEXT_CANDIDATE: F03; not activated
F03_AND_LATER: not_started
ACTIVE_IMPLEMENTATION_LIMIT: 1
CURRENT_VERIFIED_MAIN: e965f6781c9259bb45ab6bed7db0211e3bc9a505
```

This document owns product scope, roadmap, dependencies and completion definitions.
Status and specifications are not execution evidence. Task-specific scope, acceptance,
budgets and evidence live in the selected bounded task contract; stable builder and
security rules live in [AGENTS.md](AGENTS.md).

## Completed tasks and evidence

| Task | Verified outcome | Historical record / merge evidence |
|---|---|---|
| I01 | Runnable/testable Python harness | [I01 handoff](docs/I01_HANDOFF.md); [PR #1](https://github.com/Poken-ninja/personalstyle/pull/1) |
| GitHub gate | Required Python harness check and protected main enforced | [Gate handoff](docs/GITHUB_GATE_HANDOFF.md); [PR #2](https://github.com/Poken-ninja/personalstyle/pull/2) |
| SEC01 | Declared Windows local protection boundary | [SEC01 handoff](docs/SEC01_HANDOFF.md); [PR #3](https://github.com/Poken-ninja/personalstyle/pull/3) |
| F01 | Authorized writing persistence through the Windows protected boundary | [F01 task](docs/F01_TASK.md); [PR #4](https://github.com/Poken-ninja/personalstyle/pull/4) |
| F02 | Read-derived deterministic exact-context Writing DNA | [F02 task](docs/F02_TASK.md); [PR #5](https://github.com/Poken-ninja/personalstyle/pull/5) |

Completed records are historical evidence for their named revisions/environments, not
instructions to reactivate tasks or reset budgets. PR records include merge SHAs and
merged-main CI evidence. No cross-platform sensitive storage, application-level storage
encryption, generation or PersonalStyle V1/product success is claimed.
The [pre-cleanup contract snapshot](docs/history/EXECUTION_CONTRACT_PRE_CLEANUP.md)
preserves historical initial states and the full I01/SEC01 execution specifications.

## Objective

Build the smallest local-first PersonalStyle vertical slice that can demonstrate in normal engineering tests that context-specific personalization reduces user editing effort or increases accept-without-edit behavior versus a generic rewrite baseline while preserving meaning, required information, and explicit constraints.

### Product goal and success criterion

PersonalStyle is a local-first adaptive writing assistant.

Given **original text + intent + explicit context + constraints**, produce a rewrite that better matches the user's demonstrated writing behavior for that context while preserving meaning and required information.

The product success criterion is:

> With continued use, PersonalStyle should reduce the user's editing effort and increase accept-without-edit behavior versus a generic rewrite baseline without degrading semantic or constraint fidelity.

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
- A/B/C product-performance testing.

Current V1 release target after the authoritative core works is one Flutter desktop app on
Windows, macOS and Linux. The terminal/CLI remains an engineering and acceptance surface.
Browser extension, iOS and Android are deferred and are not V1 release blockers. Structural
arrangements are owned by [ARCHITECTURE.md](ARCHITECTURE.md),
[ADR-002](docs/decisions/ADR-002-versioned-multi-surface-engine.md), and
[ADR-003](docs/decisions/ADR-003-desktop-first-flutter.md).

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
Must be selected and recorded before the first model-generation feature activates.

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

### U8 — macOS/Linux protected profile boundary
SEC01, F01 and F02 currently provide sensitive-storage evidence on Windows only. Before
PersonalStyle handles sensitive persisted writing on macOS or Linux, platform-appropriate
ownership/permission mechanisms and negative/positive executable evidence must exist.
This does not invalidate the existing Windows evidence and does not block core F03 work on
the already verified Windows path.

### U7 — application-level encryption at rest
Current policy explicitly does not claim application-level database encryption.

Before any release claims encrypted-at-rest profile storage, a concrete mechanism plus migration, recovery, backup/export, and compatibility behavior must be implemented and verified.

This does not block local V1 engineering if the product clearly relies on host OS/account/disk protection and does not misrepresent the guarantee.

## Task plan

| ID | Task | Depends on | Current state |
|---|---|---|---|
| I01 | Establish runnable/testable Python harness | none | merged / verified |
| SEC01 | Mechanize Windows local security boundary | I01 | merged / verified |
| F01 | Persist user-authorized writing examples + explicit context metadata | I01 + SEC01 | merged / verified (Windows) |
| F02 | Derive inspectable Writing DNA/context profile | F01 | merged / verified (Windows protected store) |
| F03 | Generic + personalized generation using metadata retrieval | F02 + U2 | not_started |
| F04 | Hard verification path and bounded candidate retry | F03 | not_started |
| F05 | Record accept/edit events and classify edit type | F04 | not_started |
| F06 | Evidence-backed context preference promotion | F05 | not_started |
| P01 | Mechanize versioned engine protocol/client boundary | F04 + SEC01 | not_started |
| SEC02 | Mechanize macOS protected local profile boundary | F01 | not_started |
| SEC03 | Mechanize Linux protected local profile boundary | F01 | not_started |
| E01 | Frozen A/B/C product-performance test | F06 + U3 | not_started |
| S01 | Terminal/CLI acceptance surface | F06 | not_started |
| S03 | Flutter desktop app + Windows/macOS/Linux release acceptance | P01 + F06 + SEC02 + SEC03 + U6 | not_started |

Deferred backlog, not V1 blockers: S02 browser-extension adapter, S04 iOS/Android companion
client, and S05 standalone mobile inference. Reactivating any deferred surface requires an
explicit owner decision and a fresh bounded task contract.

Do not fully design later tasks until dependencies and evidence sharpen. A next candidate
requires explicit owner selection and a bounded task contract; completing a dependency
does not auto-activate it. F03 requires U2 model selection and remains unstarted.

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

### V1 implementation complete

V1 implementation is complete when the A/B/C product-test path is runnable end-to-end:

- A: generic rewrite;
- B: context-personalized rewrite without accumulated learning;
- C: context-personalized rewrite with accumulated learning;

and the system can collect the required hard-invariant, edit-effort, acceptance, context, latency, and resource evidence on a held-out product-test set.

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

Product success is validated only if B/C improve the predeclared personalization/user-effort criteria versus the relevant baseline while meeting the hard semantic/constraint requirements.

If they do not, the product requirement is not met. Do not redefine the metric after seeing results to manufacture success.

### Product-test evidence signals

Evidence includes hard semantic/constraint validity, context accuracy, stylometric
diagnostics, normalized edit effort, accept-without-edit rate, user preference, latency
and resource use. Testing discipline remains in [AGENTS.md](AGENTS.md#product-testing-discipline).
