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

V1 is a single-process deterministic harness around model calls. The optional bounded reasoning component is disabled until evidence justifies it.

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

Embeddings/vector retrieval are deferred until evaluation demonstrates a retrieval failure that metadata selection cannot solve.

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

A feature should not exist merely because it is measurable. It should have a clear intended use in personalization or evaluation.

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

#### Style layer
Style similarity is diagnostic/optimization evidence in V1, not a single hard oracle.

Product-level truth comes from a combination of held-out style diagnostics and user behavior.

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

## Evaluation architecture

Evaluation is separate from normal product state.

Use a held-out dataset that is excluded from:
- example retrieval;
- Writing DNA derivation;
- preference evidence;
- prompt/profile construction.

Compare:

```text
A = generic rewrite
B = personalized from examples/profile
C = B + learned preferences
D = optional bounded reasoning, only after evidence of need
```

Freeze before a scored comparison:
- held-out cases;
- model/version;
- prompt version;
- retrieval policy;
- metric definitions;
- success rule.

Use several lenses:
- hard semantic/constraint validity;
- context accuracy;
- stylometric diagnostics;
- normalized edit effort;
- accept-without-edit rate;
- user preference;
- latency/resource use.

Do not use the same extracted style traits as both the sole generation control and sole evaluation judge.

## Research-informed risks

External work suggests several traps relevant to PersonalStyle:

### Model fingerprint can dominate user style
Recent personalization benchmarks find that personalization can create author-differentiated output while still remaining systematically unlike genuine human writing.

**Design response:** never equate a high model/judge style score with "writes like the user." Keep held-out human comparisons and real edit behavior.

### Few-shot style imitation is context-sensitive
Large evaluations find stronger performance in structured domains such as email than in nuanced informal writing, and prompting/example choices materially affect results.

**Design response:** evaluate contexts separately; pin prompt/example-order policy; do not report one aggregate style score as universal performance.

### Post-editing still leaves model traces
Human edits can make generated text more stylistically similar to the writer, but post-edited text may remain closer to model output than to unassisted human writing.

**Design response:** treat edit reduction as a longitudinal product metric, not proof of perfect authorship imitation.

### Metric circularity
Recent benchmark work reports disagreement between authorship-style measures and LLM judges, including circularity when trait extraction and evaluation reinforce the same representation.

**Design response:** use an ensemble of independent signals and real user behavior.

### Reproducibility failures are easy
Personalization repositories/benchmarks expose ambiguity around retriever versions, prompt formatting, test-data preparation, and dataset availability.

**Design response:** record exact model, prompt, retrieval policy, example IDs/order, data split, and profile version for every evaluation.

References:
- https://aclanthology.org/2025.findings-emnlp.532/
- https://aclanthology.org/2026.acl-long.2030/
- https://github.com/yashsawant22/personalbench
- https://github.com/LaMP-Benchmark/LaMP
- https://proceedings.mlr.press/v328/nicolicioiu26a.html

## Scheduling architecture

There is no scheduler in core V1.

If scheduled work is later required, scheduling remains outside model control and must have an explicit deterministic schedule contract: trigger, timezone, idempotency, overlap policy, misfire/catch-up policy, timeout, retry ownership, persistence, and failure sink.

### n8n

n8n is intentionally absent from V1.

It becomes a candidate only for external multi-service workflows where its connectors, credential handling, webhooks, human approvals, and operations UI materially reduce complexity.

It is not justified for the interactive rewrite loop or as a generic retry engine.

If n8n is ever adopted, it must be the explicit owner of the workflow-level schedule/retry policy rather than stacking its retries around an already retrying PersonalStyle loop.

Useful references:
- https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.scheduletrigger/
- https://docs.n8n.io/deploy/host-n8n/configure-n8n/scaling/enable-queue-mode
- https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/configuration-examples/configure-workflow-timeouts

## Deferred architecture

Do not add until measured evidence identifies a concrete problem:
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
