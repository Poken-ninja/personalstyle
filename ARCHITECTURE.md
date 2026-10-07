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
