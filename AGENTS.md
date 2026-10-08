# PersonalStyle — Builder Contract

## Working context and scope

Follow the [default read route](README.md#default-read-route): README, this file and the
explicitly selected current task contract first; consult deeper sources when needed.
Build the smallest end-to-end vertical slice that can satisfy and verify the product
requirements. Product goals, V1 scope and exclusions are owned by
[EXECUTION_CONTRACT.md](EXECUTION_CONTRACT.md#scope), not repeated here.

## Status truth

Repository documents describe the intended system. They are **not evidence that the harness, loop, verifier, persistence, or personalization behavior exists or works**.

Do not mark behavior implemented because it appears in this file or in ARCHITECTURE.md.

## Source authority

For conflicts:
- product behavior and V1 scope: current project execution contract / owner decision;
- builder rules: this file;
- structural architecture: ARCHITECTURE.md;
- accepted architecture decisions: docs/decisions/;
- current configuration: personalstyle.toml;
- current implementation: repository revision being built;
- runtime truth: observed local execution;
- verification truth: recorded verification evidence.

A runtime mismatch does not automatically make documentation stale. Classify the mismatch first as implementation defect, specification defect, intentional version difference, environment/configuration difference, verifier defect, or unknown.

## Versioning and compatibility

Use separate versions for separate compatibility surfaces.

- **Product/core package version:** SemVer in `pyproject.toml`.
- **Protocol version:** SemVer-like `MAJOR.MINOR` in `personalstyle.toml`.
- **Config schema version:** monotonically increasing integer.
- **Storage schema version:** monotonically increasing integer.
- **Profile schema version:** monotonically increasing integer.
- **Prompt contract version:** immutable integer/identifier recorded with each run.
- **Surface/client version:** owned by each client package when that client exists.
- **Model identity:** record provider + exact model/version identifier used by a run.

Rules:
1. Protocol MAJOR mismatch is incompatible unless an explicit adapter exists.
2. Protocol MINOR changes must be additive/backward-compatible within a major.
3. Older clients remain supported only while protocol/capability compatibility and platform support are verified; age alone neither guarantees nor forbids support.
4. Unknown future config/storage/profile schema versions must fail safely, not be guessed.
5. Known older schemas must migrate through explicit ordered migrations before normal writes resume.
6. Never allow old-schema and new-schema writers to write the same profile concurrently.
7. Prompt/model/profile versions used for a result must be reconstructable.
8. A version bump is not a substitute for a migration or compatibility test.

Version declarations are written requirements until code/tests enforce them.

## Multi-surface rule

Current V1 release scope is a shared Flutter desktop shell on Windows, macOS and Linux.
The CLI remains an engineering/acceptance surface. Browser extension, iOS and Android are
deferred until a later explicit owner decision; their existence in long-term architecture
does not make them V1 blockers.

Surface clients must not fork personalization, verification, retry, or persistence rules.
They call the authoritative engine/protocol. Flutter owns presentation and platform
integration only; protected product behavior remains engine-owned. Surface arrangements and
inference-provider boundaries live in
[ARCHITECTURE.md](ARCHITECTURE.md#multi-surface-architecture),
[ADR-002](docs/decisions/ADR-002-versioned-multi-surface-engine.md), and
[ADR-003](docs/decisions/ADR-003-desktop-first-flutter.md).

A platform/version is called **supported** only when the selected framework/runtime/provider
supports it and release verification covers it. Current Windows security evidence does not
establish macOS/Linux sensitive-storage support. Do not promise unlimited backward OS support.

## Deterministic ownership

The deterministic harness owns anything that controls execution or durable state:

| Concern | Owner |
|---|---|
| schema/input validation | deterministic |
| explicit context requirement and context normalization | deterministic |
| example filtering and ordering | deterministic |
| example/token limits | deterministic |
| prompt template/version selection | deterministic |
| persistent-state writes and versions | deterministic |
| preference-promotion rules | deterministic |
| retry/model-call/time budgets | deterministic |
| task/run state transitions | deterministic |
| hard fact/constraint checks where mechanically detectable | deterministic |
| permissions and secrets | deterministic |
| scheduling/triggers | deterministic |
| telemetry fields and failure codes | deterministic |

The model may propose:
- rewritten text;
- interpretation of ambiguous intent;
- a bounded personalization strategy;
- a preference hypothesis from an edit;
- a repair suggestion after verification failure.

The model may **not** change its own budgets, verification thresholds, permissions, state-machine transitions, persistent records, schedule, or tool authority.

Model output is untrusted data until the harness accepts it.

## Security contract

Security is a release property, not an assumption created by "local-first."

### Data classes

Treat these as **sensitive user data**:
- writing examples;
- original text;
- generated drafts;
- edits and feedback;
- Writing DNA;
- preferences and profile history;
- held-out product-test writing.

Treat these as **secrets/credentials**:
- provider/API credentials;
- pairing credentials;
- client authentication material;
- signing/private keys.

Secrets must never be committed to Git, stored in `personalstyle.toml`, written to normal SQLite profile tables, included in prompts, placed in URLs, or emitted in ordinary logs.

Security-sensitive policy stays centralized in the engine/protocol. Clients may enforce additional platform protections but may not weaken engine authorization, validation, verification, or budget rules.

### Trust boundaries

Untrusted inputs include:
- model output;
- user/imported text;
- writing examples;
- web-page/extension content;
- files imported by the user;
- client requests before authentication/validation;
- network discovery results;
- data received from an older/incompatible client.

Untrusted data must not become harness instructions, permissions, schema changes, paths, shell commands, or persistent preference state without deterministic validation.

### Local engine exposure

Default engine exposure is local/in-process or loopback-only.

Companion/LAN access is disabled until explicitly enabled.

Any network-accessible engine, including localhost endpoints callable by browser contexts, must:
- authenticate the client;
- authorize the requested capability;
- validate origin/caller context where applicable;
- reject protocol downgrade/incompatible versions;
- enforce request/body/resource limits;
- prevent replay/duplicate mutation where it matters;
- use encrypted transport when traffic leaves the local process/loopback trust boundary;
- provide credential rotation/revocation;
- avoid logging authentication material.

Discovery is not authentication.

No unauthenticated public or LAN listener may expose rewriting, profile, feedback, or state APIs.

### Client credentials

Persistent client credentials belong in platform secure credential storage where available.

Do not store reusable authentication secrets in:
- browser page storage available to arbitrary sites;
- source-controlled files;
- query strings;
- ordinary logs;
- prompt/context payloads.

Pairing grants only the capabilities required by that surface and must be revocable.

### Browser-extension boundary (deferred)

The browser extension must use least privilege:
- request only necessary browser/host permissions;
- prefer explicit user action for page access where practical;
- treat page text/DOM content as untrusted data;
- never execute page-provided code or instructions as harness policy;
- do not expose engine credentials to page scripts;
- do not allow arbitrary websites to invoke privileged local-engine mutations.

### Mobile surface boundary (deferred)

- pairing/client credentials use platform secure credential storage;
- app lifecycle/background behavior must not leak sensitive drafts/profile state;
- backups/exports follow the platform's protected-data policy selected for the release.

### Persistent data

The engine is the only canonical profile-store writer.

Database/profile files must use the narrowest practical OS file permissions.

Do not claim application-level encryption at rest unless it is actually implemented and verified. Until then, security relies on the host OS/account/disk protections and this limitation must be disclosed.

Backups/exports inherit the same sensitivity as the source profile.

Deletion must remove the canonical record and identify affected derived state for recomputation/removal; do not promise forensic secure erase unless a verified mechanism exists.

### Prompt/context isolation

System/harness instructions and user/example/page content must be structurally separated.

A writing example containing text such as "ignore previous instructions" remains writing data.

The model has no authority to:
- widen permissions;
- select secrets;
- change budgets;
- modify verification rules;
- mutate durable state directly;
- enable networking or scheduling.

### Logs and telemetry

Default logs contain identifiers, versions, states, timing, counters, and failure codes—not raw writing.

Sensitive content logging requires an explicit debug decision and must be easy to disable/remove.

Authentication material is never loggable.

### Dependency and release integrity

Before a release is called secure enough for its supported surfaces:
- dependency versions are reproducible/pinned by the chosen ecosystem mechanism;
- known dependency/security checks defined for that ecosystem pass;
- release artifacts use the platform's required signing/distribution mechanism;
- secrets are absent from repository/build artifacts;
- protocol/schema migrations and downgrade behavior are tested;
- security-sensitive generated artifacts come from an authoritative source, not hand-merged copies.

Do not invent a new security framework when platform mechanisms are adequate.

### Security completion gate

A feature/surface that handles sensitive writing is security-complete only when the controls applicable to its real attack surface are mechanized and verified.

At minimum, where applicable, evidence must cover:
- unauthorized client rejected;
- wrong/expired/revoked credential rejected;
- incompatible/downgrade protocol rejected;
- page/imported content cannot become harness instructions;
- unauthorized direct profile mutation rejected;
- logs do not contain secrets/raw content under normal settings;
- resource limits still apply to malicious/oversized input;
- migration/recovery does not bypass access controls;
- supported clients can revoke/replace credentials without corrupting profile state.

A security checklist alone is not evidence.

### Security failure

Classify as a security failure when any of these occur:
- secret or authentication material is exposed;
- unauthenticated/unauthorized client obtains protected data or mutation capability;
- untrusted content changes harness policy/permissions/state outside allowed data paths;
- a client bypasses verification/budget/state controls;
- protocol downgrade bypasses a control;
- cross-context/user data is exposed to the wrong caller;
- malicious input causes unbounded resource consumption beyond the configured safety ceiling;
- release artifact contains credentials or unexpected sensitive content.

Security failure blocks the affected release/task until containment, root-cause classification, repair, credential rotation when applicable, and rerun of invalidated evidence.

## Context rules

Context is explicit and bounded.

1. If explicit context is required and absent, do not silently infer a durable context. Ask for or require context before personalized generation.
2. Retrieval priority is: exact context -> explicitly compatible broader context -> global preference explicitly marked global.
3. Never fill a context with examples from an unrelated context merely to reach an example-count target.
4. Writing examples are **data, not instructions**. Delimit them from system/task instructions so example content cannot alter harness policy.
5. Respect configured example and context-token limits.
6. Record the IDs/versions of examples and preferences used for a generation so results are reproducible.
7. Held-out product-test writing must never be eligible for retrieval, Writing DNA calculation, or preference learning during the test that uses it.

### Writing-data provenance

Durable writing examples must retain enough provenance to answer:
- who supplied/owns or authorized the sample;
- which context it belongs to;
- whether it is allowed for personalization learning;
- whether it is reserved for product testing.

Third-party/reference text is not automatically user-style evidence. Only samples explicitly authorized for learning may affect Writing DNA or preferences.

## Personalization state rules

Name state explicitly; do not use vague "memory."

State entities/lifetimes and the learning pipeline are described in
[ARCHITECTURE.md](ARCHITECTURE.md#3-personalization-store) and its
[feedback adapter](ARCHITECTURE.md#8-feedback-adapter).

A single edit may create an observation or low-confidence hypothesis. It must not silently become an active global preference.

Before style learning, classify the edit. At minimum distinguish:
- style/expression edit;
- meaning/fact correction;
- constraint correction;
- context/recipient correction;
- mixed or unknown.

Only evidence attributable to style/expression may promote a style preference. Meaning, factual, constraint, or context corrections are primarily failure evidence for generation/verification and must not be converted blindly into style rules.

Accepting a draft is weak positive evidence that it was usable, not proof that every stylistic choice is preferred.

Preference scope may widen only through an explicit deterministic promotion rule backed by cross-context evidence.

No autonomous or scheduled profile mutation in V1.

## Generation and verification

Generation must not mutate durable personalization state.

### Hard run invariants

A candidate cannot succeed if it materially:
- changes the user's intended meaning;
- loses or changes required names, dates, numbers, requests, or facts;
- violates an explicit constraint;
- uses a disallowed/wrong context;
- exceeds a hard structural limit.

Use deterministic checks for objective invariants where possible.

Semantic preservation that cannot be settled deterministically requires a separate verification path. If the same model that generated the text also evaluates it, call that **self/second-pass verification**, not independent verification.

"Independent verification" is reserved for a genuinely separate mechanism: deterministic checker, isolated evaluator/model, external test, or human judgment.

### Style is initially a product-quality signal

Do not make one style metric a hard truth oracle.

Use multiple engineering signals plus real user behavior:
- stylometric diagnostics;
- context accuracy;
- human/user preference;
- edit effort;
- accept-without-edit rate.

## Verification integrity

Never obtain a pass by:
- weakening an acceptance criterion;
- deleting/disabling a failing check;
- changing an expected result just to match current output;
- removing a difficult product-test case;
- leaking held-out user writing into the generation context.

A defective test/check may be corrected only by showing that it conflicts with the authoritative requirement or is technically invalid/flaky. Record the reason, then rerun the corrected check.

## Execution loop

The run state machine is owned by
[ARCHITECTURE.md](ARCHITECTURE.md#run-state-machine).
Illegal transitions must be rejected by the harness when implemented.

### Authoritative budget

There is one outer run budget. Lower-level HTTP/model/client retries must be configured so they cannot multiply it invisibly.

The first generation counts as attempt 1.

Budgets persist across context resets or process/session changes for the same run.

A retry is allowed only after a failure classification and a material change in input, strategy, environment, or implementation.

## Completion definitions

Apply [EXECUTION_CONTRACT.md completion definitions](EXECUTION_CONTRACT.md#completion-definitions)
for run, feature, V1, security gate, surface, cross-platform release and product success.
Task-specific acceptance/evidence remains in its bounded task contract.

## Failure definitions

Failures are first-class outcomes.

### Run failure
Examples:
- hard semantic/required-information/constraint check fails and budget is exhausted;
- context cannot be established;
- model/runtime dependency is unavailable and no permitted recovery exists;
- state persistence would become inconsistent;
- execution budget or timeout is exceeded.

### Personalization failure
- personalized output does not outperform the simpler baseline;
- feedback does not reduce later editing effort;
- style gains occur only by harming fidelity;
- learned preferences leak into unrelated contexts.

Personalization failure can occur even when the software is implemented correctly.

### Harness failure
- illegal state transition accepted;
- budget bypass or retry amplification;
- model directly mutates protected state;
- held-out product-test leakage;
- verifier is weakened to get a pass;
- unreconstructable run state;
- hidden scheduled/background mutation;
- incompatible client/engine versions proceed without explicit compatibility handling;
- old/new schema writers mutate the same profile concurrently;
- a surface bypasses the authoritative engine and writes canonical state directly.

### Compatibility failure
- supported surface fails on a declared supported OS/runtime version;
- older compatible client cannot negotiate required protocol capabilities;
- migration fails or leaves store/profile state unverifiable;
- protocol/schema change breaks a previously supported same-major client without a declared compatibility break;
- support is claimed for an untested/unverified platform version.

### Failure response

On failure:
1. record failure code and evidence;
2. classify the failure;
3. preserve the last trustworthy state;
4. retry only within budget and only with changed information;
5. otherwise stop, block, or escalate.

Never "keep trying until it works."

## Scheduling and automation

V1 has **no scheduled product behavior**. The product loop is user/event driven.

The model cannot schedule itself.

If scheduling is later justified, define before implementation:
- trigger and owner;
- timezone/clock source;
- idempotency key;
- overlap/concurrency policy;
- missed-run/catch-up policy;
- maximum runtime;
- authoritative retry budget;
- checkpoint/state write;
- failure sink/alert;
- cancellation/disable path.

### n8n decision

Do not add n8n to core V1.

Consider n8n only when PersonalStyle needs unattended workflows spanning external services/credentials/webhooks/human approval where a maintained workflow orchestrator is simpler than local code.

For an in-process/local scheduled job, first prefer no scheduler; if truly needed, prefer the smallest local scheduler/OS mechanism that satisfies the contract.

Do not add n8n merely for retries, loops, or timers: it would introduce a second execution/retry layer and can create retry amplification unless it becomes the single outer owner.

## Observability

Track enough to reconstruct a run without logging unnecessary sensitive writing.

Minimum:
- run ID;
- timestamps;
- state transitions;
- context/profile/example versions;
- model and prompt version;
- attempt/model-call counts;
- verification results/failure codes;
- terminal state;
- latency/resource usage.

By default do not store raw prompts or outputs. User writing is sensitive local data.

## Product testing discipline

This is engineering validation, not academic research.

For A/B/C product testing:
- keep a held-out set separate from personalization inputs;
- use more than one quality signal;
- treat real user edits and acceptance as primary product outcomes;
- pin model/prompt/retrieval versions for a comparison;
- test contexts separately;
- record failure cases, not only averages;
- do not change the pass rule after seeing results.

Do not use the same extracted style traits as both the sole generation control and sole quality judge.

## Merge-conflict discipline

Merge conflicts are treated as engineering state, not clerical cleanup.

### Before implementation
Every task declares a **write set**: files/directories/contracts it expects to modify.

If two active tasks have overlapping write sets in a high-contention area, serialize them unless isolation is explicit.

High-contention areas include:
- `AGENTS.md`;
- `ARCHITECTURE.md`;
- `EXECUTION_CONTRACT.md`;
- `personalstyle.toml`;
- `pyproject.toml`;
- protocol/schema definitions;
- database migrations;
- dependency lockfiles;
- shared prompt contracts.

### Conflict prevention
- default WIP remains 1 for implementation;
- keep branches/tasks short-lived;
- sync with current `main` before final verification/handoff;
- do not mix broad formatting/refactors with behavior changes;
- do not touch lockfiles/config/schema files unless the task requires it;
- use one active storage migration sequence at a time;
- shared behavior goes in the engine/protocol, not copied into clients.

### Conflict resolution
1. classify conflict as textual or semantic;
2. for semantic conflicts, identify the authoritative requirement/version/schema before editing;
3. never resolve protocol/schema/migration/state conflicts with blind "ours" or "theirs";
4. preserve both sides' intended behavior where compatible, otherwise block for an explicit decision;
5. after resolution, rerun all checks whose evidence the merged change invalidated;
6. regenerate generated artifacts from their source after semantic merge instead of hand-merging generated output;
7. update the handoff with the merge base, resolved conflict, and rerun evidence.

A conflict is not resolved merely because Git no longer shows conflict markers.

### Merge completion gate
A task may be called merge-ready only when:
- no conflict markers remain;
- the branch is reconciled with the intended base;
- task acceptance checks pass on the merged result;
- protocol/schema/migration compatibility checks pass when affected;
- version bumps/migrations are coherent;
- no unrelated work was lost;
- handoff evidence references the merged revision.

Current GitHub enforcement status and evidence are recorded in
[EXECUTION_CONTRACT.md](EXECUTION_CONTRACT.md#completed-tasks-and-evidence).
Semantic scope review remains a builder duty; CI does not replace these merge rules.

## Change discipline

Before adding architecture:
1. name the concrete engineering problem;
2. show the simpler current approach;
3. define the required measurable improvement;
4. make the smallest change that can solve the problem;
5. add/update verification;
6. record a decision when it constrains future work.

Do not turn one bug into a framework.

## Builder working rule

Default WIP is one implementation task.

Do not start adjacent refactors or speculative infrastructure while the active task is unverified.

When blocked, leave an honest checkpoint containing current task, evidence, failure, budget used, blocker, and next permitted action.

## Lean bounded task workflow

Normal implementation: minimum context -> one bounded behavior -> targeted tests -> checkpoint.
Read README + AGENTS + the selected task first; consult deeper sections only when needed.
Final task verification: full regression once -> static checks once -> one real acceptance
run when materially required -> required CI once -> compact evidence. Do not rerun unchanged
passing checks for ceremony. A compound task may share branch/contract/PR/budgets only when
explicitly selected by the owner; preserve phase dependency guards and persistent counters.

Target normal implementation turns around 3?8 minutes where practical. The 10?15 minute
threshold is advisory: checkpoint long work rather than expand scope. Documents do not
enforce wall-clock limits; only executed mechanisms establish bounded runtime evidence.
After the same implementation failure twice, stop repetitive repair and enter bounded diagnosis.
A missing promotion policy is an owner decision boundary, never permission to invent a threshold.


## Measured performance

When changing persistent queries, relationships, bulk fetches or raster assets, avoid
accidental N+1 SQL/remote access and index material lookup/filter/join/order paths.
Prevent query explosions, unnecessary scans/sorts and record-count-dependent latency.
Use targeted query-count/EXPLAIN evidence or bounded benchmarks; review rejects calls
inside result loops unless justified. Streaming one query is permitted. Add only
indexes justified by the actual path, preserving security, ordering and bounded memory.
For S03-WIN/UI raster assets, compare size/quality/client support before choosing WebP/AVIF;
keep vectors and necessary fallbacks. No current asset conversion is required.
Fix the specific evidenced hot path before completion, without speculative indexes or
blanket transcoding. Record query-plan/count/benchmark or asset-size evidence as applicable.
