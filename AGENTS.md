# PersonalStyle — Engineering Contract

## Project goal

PersonalStyle is a local-first adaptive writing system.

Given input text, intent, and context, transform the text so its expression better matches the user's demonstrated writing behavior while preserving original meaning, required information, and explicit constraints.

Personalization must be learned from actual writing examples and user edits, not only from a prose description of "my style."

## Core engineering rule

> Problem first. Simplest architecture that reliably solves the problem.

Do not introduce agents, multi-agent systems, memory, RAG, vector databases, autonomous loops, graphs, reinforcement learning, model routing, or other infrastructure merely because they are fashionable or appear in an architecture curriculum.

For every component, answer:
1. What problem does it solve?
2. Why is a simpler solution insufficient?
3. What improvement should it produce?
4. How will we verify the improvement?

Working -> Reliable -> Useful -> Maintainable -> Inspectable -> Efficient -> More autonomous.

## The 14 principles

1. Problem before architecture.
2. Simplest reliable architecture.
3. Deterministic vs agentic boundary.
4. Harness/environment first.
5. Context engineering.
6. Memory/state explicit.
7. Execution loops bounded.
8. Verification first-class.
9. Graphs/state machines only when justified.
10. Bound autonomy.
11. Failure handling before deployment.
12. Watch structural risks.
13. Use real-world anchors.
14. Evaluate complexity against a simpler baseline.

Do not mechanically force these principles. When a simpler design is better, use it.

## Current architecture baseline

```
USER
 ↓
DETERMINISTIC HARNESS
 ↓
CONTEXT + PROFILE + EXAMPLES
 ↓
BOUNDED REASONING
 ↓
LOCAL LLM
 ↓
DRAFT
 ↓
INDEPENDENT VERIFICATION
 ↓
PASS → USER
FAIL → BOUNDED RETRY
 ↓
USER ACCEPT / EDIT
 ↓
FEEDBACK
 ↓
ADAPTATION
 ↓
PERSONALIZATION STATE
```

This is the baseline to implement and validate. Do not redesign it without evidence.

## Deterministic boundary

The harness owns:
- input/schema validation
- context lookup and metadata filtering
- profile selection
- example selection and context-size limits
- persistent state and versioning
- loop control and execution budgets
- legal state transitions
- verification policy and thresholds
- retry eligibility
- security and tool permissions
- feedback recording and authorized state mutation
- scheduling/triggers
- observability and telemetry

The agent/model may make bounded decisions, but it cannot control the system that governs it.

> The agent does not own the harness. The harness owns the agent.

## Agentic boundary

A single bounded reasoning component may:
- interpret ambiguous requests
- interpret ambiguous intent or context
- choose among bounded personalization strategies
- select or interpret relevant evidence
- resolve conflicting style signals
- decide how generation strategy should change after verification failure

It must not control:
- retry limits
- budgets
- permissions
- database schema
- verification thresholds
- safety policy
- state-machine transitions
- arbitrary persistent-state mutation
- scheduling
- unrestricted filesystem/network access
- arbitrary shell execution

No multi-agent architecture unless evaluation shows that one bounded reasoning component plus deterministic components is insufficient.

## Context engineering

Context should be explicit, inspectable, and bounded.

Prefer:
- explicit context labels
- metadata filters
- relevant writing examples
- task-specific preferences
- context-size limits

Do not assume that more context is better.

Writing examples should be representative of the relevant content type/context. Avoid mixing unrelated contexts when that could distort style signals.

## Persistent state and "memory"

Do not use vague "memory" as an architectural concept. Name the state.

Persistent state may include:
- user profile
- writing examples
- context profiles
- Writing DNA
- preferences
- preference evidence
- confidence
- learning events
- useful task history
- versions

Per-task state may include:
- request
- context
- retrieved examples
- strategy
- draft
- verification results
- retry count

A single edit must not rewrite the whole profile.

Preference learning pipeline:

USER EDIT
→ OBSERVATION
→ PREFERENCE HYPOTHESIS
→ EVIDENCE
→ CONFIDENCE
→ PROFILE UPDATE

Preferences should be context-scoped unless evidence is strong enough to make them global.

## Writing DNA

Start with explicit, inspectable features before opaque representations.

Candidate features:
- sentence length
- vocabulary complexity
- punctuation
- contractions
- paragraph structure
- syntax patterns
- function-word behavior
- active/passive voice
- common phrases
- vocabulary preferences
- recurring communication patterns

Do not add embeddings/vector search unless a measured retrieval problem justifies them.

## Semantic preservation

Semantic preservation is a hard requirement.

The system must preserve:
- original meaning
- required facts/entities
- explicit constraints
- requested intent

If a hard semantic requirement fails, reject the output. Style quality cannot compensate for semantic failure.

## Verification

Separate generation from verification.

Verification should cover:
- structural constraints
- semantic fidelity
- required information
- explicit constraints
- context correctness
- style similarity when useful

Prefer deterministic checks and real user behavior over model confidence.

An output should not be accepted merely because a model says it is good.

## Loop engineering

General execution flow:

Trigger
→ Execution Policy
→ Loop Controller
→ Observe
→ Reason
→ Act
→ Verify
→ Persist
→ Termination Decision
→ Success / Failure / Escalation / Wait

Trigger types:
- event-driven
- scheduled
- condition-triggered
- continuation

Scheduling is deterministic infrastructure. The model cannot schedule itself or decide to wake itself later.

Distinguish:
- Retry = repeat a failed attempt.
- Iteration = continue toward a goal after observing a result.

Avoid retry amplification such as scheduler retry × agent retry × tool retry × network retry. There should be one authoritative execution budget.

## Failure handling

Treat failure states as part of the architecture, not as cleanup.

Potential failures:
- material semantic change
- lost required information
- violated explicit constraints
- wrong context
- personalization does not beat baseline
- feedback does not improve later output
- preference leakage across contexts
- one observation corrupts profile
- verifier approves unacceptable output
- retry/exec limits bypassed
- unbounded loop
- inconsistent persistent state
- resource limits exceeded

Failures should be explicit, observable, bounded, and recoverable where recovery is safe.

## Security

Model output is untrusted data.

Keep explicit boundaries for:
- permissions
- filesystem
- network
- secrets
- tool use
- data access

Never grant unrestricted shell, network, or persistent-state authority to the model.

Guard against:
- prompt injection
- context poisoning
- memory corruption
- tool misuse
- permission escalation
- infinite loops
- retry amplification
- state corruption

## Observability

Every execution should have enough telemetry to reconstruct what happened without storing unnecessary sensitive content.

Track at minimum:
- task/run ID
- state transitions
- attempt/iteration counts
- model-call count
- verification results
- errors/failure codes
- final state
- resource usage

Do not store prompts or outputs by default unless explicitly enabled and justified.

## Testing and evaluation

Prefer a real vertical slice plus deterministic tests.

Compare at least:
A. Generic LLM rewrite
B. PersonalStyle without learning
C. PersonalStyle with adaptation
D. Optional bounded agent

If D does not produce a measurable improvement over C, remove the agent.

Core metrics:
- semantic fidelity (hard pass/fail)
- constraint compliance (hard pass/fail)
- style similarity
- context accuracy
- human preference
- edit distance / user editing effort
- acceptance rate
- longitudinal learning improvement
- latency
- cost

Every added layer must have a measurable hypothesis.

## Change discipline

Before adding architecture:
- identify the concrete problem
- test the simplest existing approach
- define the expected improvement
- add the smallest change that can test the hypothesis
- add or update deterministic tests
- record important architectural decisions

Avoid speculative infrastructure and ceremonial abstractions.
