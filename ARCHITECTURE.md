# PersonalStyle Architecture

## Purpose

This file describes the **structural design** of PersonalStyle. Builder behavior, completion rules, failure handling, budgets, verification integrity, and scheduling policy live in `AGENTS.md`.

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

PersonalStyle is one product engine with multiple thin surfaces.

```text
CLI / TERMINAL
BROWSER EXTENSION
DESKTOP APP
IOS APP
ANDROID APP
      |
      v
VERSIONED PERSONALSTYLE PROTOCOL
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
      +------> INFERENCE PROVIDER
```

The engine is the only canonical writer of personalization state.

Clients do not read/write SQLite directly and do not reimplement personalization logic.

### Terminal

The CLI may call the engine in-process, but its behavior must match the public engine/protocol contract so terminal-only shortcuts do not become a second implementation.

### Browser extension

Current architectural assumption: "extension" means browser extension.

The extension is a thin client. It does not host its own personalization state or retry policy. It connects to an authorized PersonalStyle engine endpoint/companion and handles engine unavailable/incompatible-version states explicitly.

If the intended extension is later VS Code or another host, replace only the surface adapter; keep the engine contract.

### Desktop application

The desktop app is a presentation/client layer over the same engine.

The initial desktop inference provider may be Ollama where supported.

### iOS and Android

The desktop Ollama provider is not assumed to exist natively on mobile.

Mobile supports one of two engine arrangements:

1. **Companion mode** — paired authenticated connection to the user's PersonalStyle engine on another trusted device.
2. **Standalone mode** — a future mobile-supported inference provider implements the same engine/provider boundary and passes the mobile compatibility suite.

Standalone mobile is not complete until its provider, hardware limits, minimum OS versions, persistence behavior, and release tests are explicitly verified.

### Local-first meaning

"Local-first" means user personalization state remains local by default and external transmission is not silently required.

Companion mode may transmit over a trusted local connection after explicit pairing. Cloud inference, sync, or remote storage requires a separate explicit architecture decision.

## Version boundaries

Keep independent version identities:

```text
core/product version
protocol version
config schema
storage schema
profile schema
prompt contract
client/surface version
model/provider identity
```

Protocol compatibility uses same-major + capability negotiation.

Schemas use explicit ordered migrations. Unknown future schema versions fail closed. Older supported state must migrate before writes resume.

A surface never infers compatibility from product version alone.

## Platform support policy

"Supported" is an evidence claim.

A platform/version is supported only when:
- selected UI/runtime framework supports it;
- required engine/inference dependencies support it;
- package/build/install succeeds;
- platform acceptance tests pass;
- upgrade/migration behavior from supported prior state passes.

Older versions outside that matrix are best-effort or unsupported.

Do not design around "all historical OS versions." Maintain an explicit release matrix instead.

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

Selection hierarchy:
1. exact context;
2. explicitly compatible broader context;
3. explicitly global evidence.

Unrelated context evidence is excluded.

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

Entities that affect future generations must be versioned or otherwise reconstructable.

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
Check meaning preservation and required-information fidelity where deterministic checks are insufficient.

If the generator and semantic verifier use the same model, this is a separate verification pass but **not independent evaluation**.

Independent verification requires a genuinely distinct mechanism.

#### Style/product-quality layer
Style similarity is a product-quality signal, not a single hard oracle.

Use several signals and real user behavior so one metric cannot define success by itself.

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

The model may propose a hypothesis, but only deterministic policy writes/promotes durable preference state.

The adapter classifies edits before learning. Style/expression changes may contribute preference evidence; meaning/fact, constraint, and context corrections are routed as generation/verification failure evidence instead of being blindly learned as style.

WritingExample and LearningEvent records must preserve provenance/learning eligibility so held-out or third-party reference text cannot silently enter the style profile.

No hidden background learning runs in V1.

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

## Budget model

There is one authoritative outer run budget.

Current configuration should bound:
- generation attempts;
- total model calls;
- wall-clock timeout.

Nested model/API retry libraries must not multiply this budget invisibly.

The first generation is attempt 1.

## Product-test architecture

Product testing is separate from normal user state.

Use held-out cases that are excluded from:
- example retrieval;
- Writing DNA derivation;
- preference evidence;
- prompt/profile construction.

Compare:

```text
A = generic rewrite
B = personalized from examples/profile
C = B + learned preferences
D = optional bounded reasoning, only after an engineering need is proven
```

Freeze before a scored comparison:
- held-out cases;
- model/version;
- prompt version;
- retrieval policy;
- metric definitions;
- success rule.

Use:
- hard semantic/constraint validity;
- context accuracy;
- stylometric diagnostics;
- normalized edit effort;
- accept-without-edit rate;
- user preference;
- latency/resource use.

Do not use the same extracted style traits as both the sole generation control and sole quality judge.

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

### Local and companion transport

Default:
- in-process/loopback;
- companion networking disabled.

When companion mode is enabled:
- explicit pairing/authentication is required;
- each client has revocable authentication material;
- capabilities are scoped;
- non-loopback traffic is protected against interception;
- incompatible/downgrade protocol requests fail;
- mutation requests are protected against accidental replay/duplication;
- browser-origin access cannot rely on "localhost" as proof of trust.

The engine must not expose an unauthenticated profile/rewrite API to the LAN.

### Surface-specific security

**CLI/Desktop**
- use OS/user file permissions;
- secrets come from an appropriate secure source, not project config;
- local debug output must not expose writing/secrets by default.

**Browser extension**
- least-privilege permissions;
- page/DOM content is untrusted;
- extension credentials are not exposed to page JavaScript;
- privileged requests go only to the authenticated engine boundary.

**iOS/Android**
- pairing/client credentials use platform secure credential storage;
- app lifecycle/background behavior must not leak sensitive drafts/profile state;
- backups/exports follow the platform's protected-data policy selected for the release.

### Storage

SQLite is the current canonical local-store baseline, but SQLite alone does not establish application-level encryption.

Do not claim encrypted-at-rest storage until a real mechanism and migration/recovery behavior are implemented and verified.

Schema/profile migrations execute only inside the engine's trusted migration path.

### Security ownership

Security-sensitive policy stays centralized in the engine/protocol. Clients may enforce additional platform protections but may not weaken engine authorization, validation, verification, or budget rules.

## Engineering failure modes

### Context contamination
Examples from the wrong context can make personalization worse.

**Control:** explicit context IDs, deterministic filtering, bounded fallback, and no unrelated fill-to-count behavior.

### Preference poisoning
A factual or semantic correction can be mistaken for a style preference.

**Control:** classify edits before learning; only style/expression evidence may promote style preferences.

### Evaluation leakage
Held-out examples can accidentally enter retrieval or profile construction.

**Control:** explicit learning eligibility and held-out flags enforced by deterministic selection rules.

### Model behavior mistaken for user style
Generated text can be internally consistent without actually matching the user's demonstrated behavior.

**Control:** use real user edits/acceptance plus held-out comparisons, not model confidence alone.

### Verification self-confirmation
A generator can approve its own mistakes.

**Control:** deterministic checks for objective rules and clearly labeled second-pass versus genuinely independent verification.

### Retry amplification
Client/network/model retries can multiply outer harness retries.

**Control:** one authoritative outer budget and explicit nested retry configuration.

### State corruption
One edit or failed run can mutate durable profile state incorrectly.

**Control:** versioned writes, promotion gates, and rollback/reconstructable events.

### Overengineering
A small failure can trigger unnecessary agents, RAG, workflows, or abstractions.

**Control:** WIP=1, bounded task contracts, deferred architecture list, and measurable activation guards.

### Sensitive writing-data exposure
Personal writing samples can expose private or identifying information.

**Control:** local storage baseline, provenance, no raw prompt/output logging by default, no unauthorized learning sources, authenticated client boundaries, and explicit disclosure of whether at-rest encryption is actually provided.

### Localhost/LAN trust mistake
A local endpoint can still be reached by untrusted browser/network contexts if exposed carelessly.

**Control:** loopback/in-process by default; authenticated authorized clients; caller/origin validation where relevant; companion networking disabled until paired.

### Credential leakage
Pairing/provider credentials can leak through config, URLs, logs, page scripts, or build artifacts.

**Control:** platform secure credential storage, no secrets in TOML/Git/prompts/logs, revocation/rotation, release scanning/checks.

### Downgrade or migration bypass
An older client/schema can accidentally bypass newer security assumptions.

**Control:** protocol negotiation, fail-closed unknown schemas, ordered migrations, no concurrent old/new writers, and compatibility/security regression tests.

## Scheduling architecture

There is no scheduler in core V1.

If scheduled work is later required, scheduling remains outside model control and must have an explicit deterministic schedule contract: trigger, timezone, idempotency, overlap policy, misfire/catch-up policy, timeout, retry ownership, persistence, and failure sink.

### n8n

n8n is intentionally absent from V1.

It becomes a candidate only for external multi-service workflows where its connectors, credential handling, webhooks, human approvals, and operations UI materially reduce implementation complexity.

It is not justified for the interactive rewrite loop or as a generic retry engine.

If n8n is ever adopted, it must be the explicit owner of workflow-level schedule/retry policy rather than stacking its retries around an already retrying PersonalStyle loop.

## Merge-conflict architecture

The architecture reduces semantic merge conflicts by assigning single ownership:

- product/business behavior -> engine;
- transport compatibility -> protocol;
- platform UX -> client surface;
- canonical state -> engine/store;
- schema changes -> ordered migration sequence.

Planned implementation should keep these boundaries reflected in directory/package ownership.

Rules:
- no client-specific copy of core personalization rules;
- one active migration lane;
- shared protocol/schema changes are high-contention and serialized;
- generated client/schema artifacts, if introduced, have one canonical source and are regenerated after merge;
- merge resolution that changes behavior invalidates affected verification evidence.

See `AGENTS.md` for the merge gate and write-set rules.

## Deferred architecture

Do not add until an observed engineering problem identifies a concrete need:
- vector database;
- general RAG;
- multi-agent execution;
- asynchronous/background personalization;
- n8n;
- fine-tuning;
- reinforcement learning;
- model routing;
- distributed workers;
- cloud state.

A future architecture change needs a recorded problem, simpler alternative, expected measurable improvement, verification plan, and rollback/removal condition.
