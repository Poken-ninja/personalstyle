# PersonalStyle Architecture

## Purpose

This file owns the **structural design** of PersonalStyle. Builder/security rules live in
[AGENTS.md](AGENTS.md); roadmap, dependencies and completion definitions live in
[EXECUTION_CONTRACT.md](EXECUTION_CONTRACT.md). Structure is not runtime evidence;
completed task records describe what exists and was verified.

## Product boundary

PersonalStyle transforms:

```text
original text
+ intent
+ explicit context
+ explicit constraints
+ relevant user evidence
        ↓
personalized rewrite
```

The product must preserve meaning and required information while adapting expression to demonstrated behavior for the relevant context.

The personalization model is:

> Style × Context × Intent

## Multi-surface architecture

PersonalStyle remains one authoritative product engine with thin clients. Current V1 release
scope is desktop-first:

```text
FLUTTER DESKTOP
  - Windows
  - macOS
  - Linux
        |
        v
ENGINE / VERSIONED CLIENT BOUNDARY
        |
        v
PERSONALSTYLE ENGINE
  - validation
  - context
  - retrieval
  - Writing DNA
  - generation loop
  - verification
  - feedback classification
  - preference promotion
  - budgets/state
        |
        +------> PERSONALIZATION STORE
        |
        +------> MODEL PROVIDER
                    |
                    +------> OLLAMA (initial desktop provider)
```

The CLI remains an engineering/acceptance surface and may call the engine in-process.
The Flutter shell owns presentation, platform integration and local UX state only. It must
not reimplement personalization, verification, retry, migration or persistence policy, and
it never writes the canonical profile store directly.

The model runtime is behind a provider boundary. Ollama is the initial desktop provider;
provider/model identity is runtime configuration and must not leak into Flutter-owned
product rules. F03 may implement the smallest provider seam needed for Ollama without
building unused provider frameworks.

Browser extension, iOS and Android are deferred surfaces. ADR-002 preserves the long-term
thin-client/protocol constraints if they are activated later; they are not V1 release
blockers. ADR-003 owns the current desktop scope and Flutter shell decision.

Current protected persistence/read evidence is Windows-only. macOS and Linux may not be
called supported for sensitive PersonalStyle workflows until platform-appropriate storage
ownership/permission mechanisms and executable evidence exist. That future work extends the
platform boundary; it does not invalidate Windows evidence already recorded for SEC01/F01/F02.

### Local-first meaning

"Local-first" means user personalization state remains local by default and external
transmission is not silently required. Cloud inference, sync or remote storage requires a
separate explicit architecture decision.

### Desktop model onboarding and setup (future S03)

Model choice is explicit deployment/user configuration. The starter options appear in this
order; the first is the easiest/default onboarding suggestion, not an automatic selection:

| Option | Ollama model | Role |
|---|---|---|
| 1 | `qwen3:8b` | Standard / default user tier; current F03 development/acceptance target |
| 2 | `qwen3:30b` | Quality tier; environment must pass readiness/performance verification |
| 3 | `qwen3:235b` | Maximum / high-end optional; unverified unless separately tested |

The user must explicitly choose/confirm the model. No silent model substitution is allowed.
PersonalStyle does not require one fixed model for all users; every generation records the
exact provider/model identity actually used. The later "use existing compatible Ollama model"
path requires defined provider/runtime/model compatibility validation; an arbitrary installed
model is not automatically supported. Starter-tier support also needs executable evidence on
the declared platform/runtime matrix, not just a tier label.

The future setup flow is:

```text
Choose model
-> inspect OS/hardware/resources
-> explain estimated download/resource requirements
-> check whether Ollama is installed/running
-> if missing, show platform-specific setup instructions
-> recheck Ollama
-> check whether selected model is installed
-> if missing, show the exact install/pull action
-> recheck selected model identity
-> run a bounded synthetic inference probe
-> mark setup READY only after the probe succeeds
```

**Instructions** explain how the user installs/starts Ollama on Windows, macOS or Linux and
obtains the chosen model (for a starter tier, `ollama pull <exact selected model>`).
**Mechanism** is the engine/provider checking installed/running runtime, required runtime/API
capabilities, selected model identity and text-generation/response compatibility itself.
**Evidence** is that exact selected model completing the bounded synthetic probe. Showing
instructions, an installed model, a running service or a UI checkbox is not readiness evidence.

OS/hardware/resource estimates are advisory before download unless a hard runtime requirement
is known. Identify the basis for estimates and known hard requirements. If a tier is likely
unsuitable, explain why, warn and offer another tier; changing the selection requires explicit
user confirmation and a new check for that choice. Do not invent fixed RAM/VRAM cutoffs or
download/start a replacement automatically. Known hard requirements and actual runtime/probe
failures must not be bypassed by an advisory warning.

Flutter owns choice presentation, guidance and setup UX. The engine/provider owns runtime
detection, exact selected-model identity, readiness state and bounded probe rules. Rechecking
after setup actions verifies the actual environment; changed model identity/runtime or a
failed probe invalidates readiness and requires revalidation. The probe uses synthetic text,
no real writing/profile mutation, and a deterministic time/output/call ceiling without hidden
retries (the current F03 runtime ceiling is 60 seconds). Failed/timed-out/incompatible probes
leave setup not READY and show an actionable failure. READY here means selected-model inference
setup only, not protected storage, surface/release completion or security support on an OS.

S03 owns this onboarding UI/integration and its platform acceptance; see
[S03 acceptance](EXECUTION_CONTRACT.md#s03-desktop-model-setup-acceptance) and
[ADR-003](docs/decisions/ADR-003-desktop-first-flutter.md#model-onboarding-decision).
The owner superseded the earlier 30B development reference with 8B for this machine.
30B preparation passed (~45.6s), but production-shaped generic generation exceeded 60s
with severe memory/pagefile pressure. This evidence is machine-specific, not a general
30B support prohibition. The [F03 checkpoint](docs/F03_TASK.md) records both 30B history
and the selected 8B compatibility/qualification outcome; tier selection is not readiness.

F03 owns only its minimal ModelProvider/Ollama generation seam and selected 8B development
evidence; it does not implement this setup wizard or activate S03.

### Staged desktop delivery

F04 -> owner-selected combined F05+F06 feedback-learning slice -> P01 -> Windows desktop
alpha -> SEC02/macOS + SEC03/Linux -> cross-platform desktop V1. The Windows alpha is
a distinct milestone using the same Flutter shell/authoritative engine and existing SEC01
Windows protection; it can precede other OS boundaries. macOS/Linux remain unsupported for
sensitive persistence until SEC02/SEC03 pass. Final S03 still requires all three platforms;
Windows alpha does not claim cross-platform release completion. Detailed dependencies and
acceptance belong to the [roadmap](EXECUTION_CONTRACT.md#windows-desktop-alpha).

## Version boundaries

The engine, protocol, stored schemas, prompts, clients and model identity are separate
compatibility surfaces. [AGENTS.md](AGENTS.md#versioning-and-compatibility) owns versioning
rules; [ADR-002](docs/decisions/ADR-002-versioned-multi-surface-engine.md) defines the
same-major/capability protocol arrangement. Supported-platform release evidence is defined
in [EXECUTION_CONTRACT.md](EXECUTION_CONTRACT.md#platform-support-evidence).

## V1 architecture

```text
USER REQUEST
    |
    v
INPUT VALIDATION
    |
    v
CONTEXT RESOLUTION
    |
    v
PROFILE / EXAMPLE SELECTION
    |
    v
GENERATION
    |
    v
HARD VERIFICATION
    |
    +---- fail + budget ----> REGENERATE
    |
    +---- terminal fail ----> FAILED / ESCALATED
    |
    v
RESULT
    |
    v
ACCEPT / EDIT EVENT
    |
    v
OBSERVATION + PREFERENCE EVIDENCE
    |
    v
DETERMINISTIC PROMOTION POLICY
    |
    v
VERSIONED PERSONALIZATION STATE
```

V1 is a single-process deterministic harness around model calls. The optional bounded reasoning component is disabled until an observed engineering problem justifies it.

## Components

### 1. Input boundary

Input contains:
- original text;
- requested intent;
- explicit writing context;
- explicit constraints.

The boundary validates schema and hard limits before a model call.

### 2. Context resolver

Maps the explicit request context to a bounded context profile.

It does not perform free-form memory search.

Eligibility/context policy is owned by [AGENTS.md](AGENTS.md#context-rules).

### 3. Personalization store

SQLite is the current local storage baseline.

Logical entities:

```text
UserProfile
WritingExample
ContextProfile
WritingDNA
PreferenceHypothesis
PreferenceEvidence
LearningEvent
Run
RunAttempt
VerificationResult
```

Durable profile state includes writing/context profiles, examples, Writing DNA, preference
hypotheses/evidence/confidence, learning events, and schema/profile versions. Per-run state
contains the request, selected context/examples/preferences, prompt/model version, candidate,
verification results, attempt count and terminal state. Entities affecting future generations
must be versioned or otherwise reconstructable.

### 4. Example selector

Initial selection is metadata-based, deterministic, and bounded by configuration.

Inputs:
- context;
- available example metadata;
- profile version;
- maximum example count/token budget.

Outputs:
- ordered example IDs and versions.

Embeddings/vector retrieval are deferred until a concrete retrieval failure shows metadata selection is insufficient.

### 5. Writing DNA

Writing DNA begins as inspectable features, not an opaque representation.

Candidate feature families:
- sentence-length distribution;
- punctuation;
- contractions;
- paragraphing;
- function-word patterns;
- vocabulary preferences;
- recurring phrases;
- directness/voice indicators.

A feature should not exist merely because it is measurable. It should have a clear intended use in personalization or verification.

### 6. Generator

Generation receives a bounded immutable snapshot:

```text
original
intent
constraints
context profile version
Writing DNA version
selected example IDs/versions
active preference IDs/versions
prompt version
model version
```

Generation cannot write durable state.

### 7. Verifier

Verification is layered.

#### Deterministic layer
Use deterministic checks for objective rules such as:
- word/character limit;
- required literal names/numbers/dates when extractable;
- structural/schema constraints;
- context ID eligibility;
- resource budgets.

#### Semantic layer

A separate verification path handles meaning/required-information fidelity that cannot be
settled deterministically. [AGENTS.md](AGENTS.md#generation-and-verification) owns invariant
rules and the distinction between second-pass and independent verification.

#### Style/product-quality layer

Style diagnostics and real user behavior are product-quality signals; evaluation rules
are owned by [AGENTS.md](AGENTS.md#product-testing-discipline).

### 8. Feedback adapter

User acceptance/edit creates a learning event.

```text
edit
-> observation
-> scoped hypothesis
-> evidence accumulation
-> deterministic promotion decision
-> new profile version
```

Deterministic promotion policy owns durable updates; the model may only propose a hypothesis.
The current bounded feedback implementation uses one schema-2 SQLite feedback table in the
existing protected canonical store, with an explicit schema-1 migration. It accepts live
engine-issued F04 receipts and stores authorized source/context/version provenance. Serialized
success flags cannot authorize writes; receipt lifecycle/transport remains engine-owned.
Owner policy `context_preference_promotion.v1` evaluates the latest three independent,
non-ambiguous verified style-feedback runs for each exact context and bounded presentation
feature. Agreement activates; opposition contests; fewer than three remains unpromoted.
Explicit engine evaluation appends versioned preference states/evidence in the same
schema-2 store. Only active exact-context IDs/versions enter later generation as data.
No global widening, background mutation or second canonical writer is introduced.
The [historical task](docs/F05_F06_TASK.md#owner-continuation-promotion-policy-resolved)
owns the precise policy and verification evidence.
[AGENTS.md](AGENTS.md#personalization-state-rules) owns edit classification/promotion rules,
and [writing-data provenance](AGENTS.md#writing-data-provenance) governs learning eligibility.

## Run state machine

```text
RECEIVED
  -> VALIDATING
  -> CONTEXT_READY
  -> GENERATING
  -> VERIFYING
      -> SUCCEEDED
      -> RETRYING -> GENERATING
      -> FAILED
      -> ESCALATED

Any non-terminal state -> CANCELLED when authorized
```

The state machine is an execution control mechanism, not an agent-planning graph.

## Product-test architecture

Held-out product-test writing is separate from personalization inputs. The comparison paths are:

```text
A = generic rewrite
B = personalized from examples/profile
C = B + learned preferences
D = optional bounded reasoning, only after an engineering need is proven
```

The optional D path remains governed by
[ADR-001](docs/decisions/ADR-001-single-bounded-reasoning.md).
[AGENTS.md](AGENTS.md#product-testing-discipline) owns testing discipline;
[EXECUTION_CONTRACT.md](EXECUTION_CONTRACT.md#product-success-validated) owns frozen
comparison/completion criteria. Run budgets are owned by
[AGENTS.md](AGENTS.md#authoritative-budget).

## Security architecture

### Trust boundary

```text
UNTRUSTED CLIENT / PAGE / USER TEXT / IMPORT / MODEL OUTPUT
                    |
                    v
          AUTH + INPUT VALIDATION
                    |
                    v
          PERSONALSTYLE ENGINE
        /          |           \
  PROFILE STORE  INFERENCE   TELEMETRY
```

Only the engine crosses into canonical state.

### Transport and surface boundaries

The default engine is in-process/loopback, with companion mode disabled. Companion
connections terminate at the engine's authenticated, capability-scoped protocol boundary;
browser page content remains outside that boundary. Credential and platform protection
rules are owned by [AGENTS.md](AGENTS.md#security-contract).

P01 selects a loopback-only JSON HTTP adapter around existing engine entry points,
with per-session credentials and protocol/capability checks. It does not fork engine
behavior or grant client store/migration authority. Its active contract is
[docs/P01_TASK.md](docs/P01_TASK.md); implementation/verification status lives there.

### Storage

SQLite is the canonical local-store baseline; schema/profile migrations execute only
inside the engine's trusted migration path. Storage protection and encryption-claim rules
are owned by [AGENTS.md](AGENTS.md#persistent-data).

### Scheduling boundary

Core V1 has no scheduler. Scheduling remains outside model control; any later orchestration
arrangement is governed by [AGENTS.md](AGENTS.md#scheduling-and-automation).

## Merge-conflict architecture

The architecture reduces semantic merge conflicts by assigning single ownership:

- product/business behavior -> engine;
- transport compatibility -> protocol;
- platform UX -> client surface;
- canonical state -> engine/store;
- schema changes -> ordered migration sequence.

Planned implementation should keep these boundaries reflected in directory/package ownership.


Generated client/schema artifacts, if introduced, have one authoritative source.
[AGENTS.md](AGENTS.md#merge-conflict-discipline) owns collision prevention, regeneration,
conflict resolution and merge verification. Deferred mechanisms and their activation
conditions are owned by [EXECUTION_CONTRACT.md](EXECUTION_CONTRACT.md#scope) and
[AGENTS.md](AGENTS.md#change-discipline).
