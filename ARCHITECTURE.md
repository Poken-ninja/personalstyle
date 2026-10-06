# PersonalStyle Architecture

## Problem

Given input text, intent, and context, transform the text so its expression better matches the user's demonstrated writing behavior while preserving original meaning, required information, and explicit constraints.

The personalization framing is:

**Style × Context × Intent**

Success means the personalized system is measurably closer to the user's demonstrated behavior for the relevant context than a non-personalized baseline.

## Baseline architecture

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

This is a baseline to validate, not a reason to endlessly redesign.

## Deterministic vs agentic boundary

Deterministic:
- validation
- context lookup/filtering
- profile/example selection policy
- state and persistence
- loop controller
- budgets/timeouts
- state-machine transitions
- verification policy
- security/permissions
- feedback-state mutation rules
- observability
- scheduling/triggers

Agentic:
- interpreting ambiguity
- bounded strategy choice
- interpreting evidence
- resolving conflicting signals
- choosing a bounded adjustment after verification failure

The agent cannot alter the harness that constrains it.

## Context

Context is explicit metadata, not an undifferentiated memory pool.

Examples may be tagged by content type, audience, intent, tone, channel, and relevant scope.

Selection must be deterministic and bounded. Representative examples for the relevant context should be preferred.

## State

Persist explicit entities instead of a generic memory subsystem.

Initial entities:
- UserProfile
- WritingExample
- ContextProfile
- WritingDNA
- Preference
- PreferenceEvidence
- LearningEvent
- Task
- TaskAttempt
- VerificationResult

Use versioning where mutation can affect future behavior.

## Writing DNA

Begin with inspectable features:
- sentence statistics
- vocabulary patterns
- punctuation
- contractions
- paragraph structure
- syntax tendencies
- function-word behavior
- voice patterns
- recurring phrases
- vocabulary preferences

Embeddings/vector retrieval are deferred until evaluation exposes a concrete retrieval problem.

## Generation and verification

Generation receives bounded task context:
- original text
- explicit intent
- explicit constraints
- selected profile/context profile
- representative examples
- relevant preferences

Generation does not mutate persistent state.

Verification independently checks semantic fidelity, required information, explicit constraints, structural validity, context correctness, and useful style measures.

Hard semantic or constraint failures reject the candidate.

## Feedback and adaptation

```
USER EDIT
→ OBSERVATION
→ PREFERENCE HYPOTHESIS
→ EVIDENCE
→ CONFIDENCE
→ PROFILE UPDATE
```

A single edit must not rewrite the whole profile. Preferences remain context-scoped unless evidence supports widening scope.

## Loop engineering

General execution flow:

Trigger → Execution Policy → Loop Controller → Observe → Reason → Act → Verify → Persist → Termination Decision → Success / Failure / Escalation / Wait

Trigger types include event-driven, scheduled, condition-triggered, and continuation. Scheduling is deterministic infrastructure; the model cannot schedule itself.

Retry means repeating a failed attempt. Iteration means continuing toward a goal after observing a result. Use one authoritative execution budget to avoid retry amplification.

## State machine

A state machine is used only because execution has explicit legal phases and terminal outcomes that must be enforced deterministically. It is not an agentic planning graph.

Typical states: RECEIVED → VALIDATING → CONTEXT_READY → GENERATING → VERIFYING → RETRYING → SUCCEEDED / FAILED / ESCALATED. Illegal transitions must be rejected.

## Loop controller

The deterministic controller owns:
- start/end conditions
- iteration count
- attempts
- model/tool-call budgets
- timeouts
- retry policy
- terminal states

The model can recommend actions only within these constraints.

## Success criteria

A successful run preserves meaning, required information, and explicit constraints; uses the correct context; is measurably closer to demonstrated user behavior; remains within resource limits; produces an explicit terminal outcome; and does not mutate unrelated personalization state.

Longitudinal success additionally requires that feedback improves later generations, preferences do not leak across unrelated contexts, and user editing effort decreases or acceptance increases.

## Failure criteria

A run fails on material semantic change, lost required information, explicit-constraint violation, wrong context, exceeded execution/resource limits, unrecoverable persistence/state error, or exhaustion of bounded generation attempts without an acceptable candidate. System-level failure also includes profile corruption, preference leakage, verifier acceptance of a hard-invalid output, or bypass of harness limits.

## Security

Model outputs are untrusted. Filesystem, network, secrets, tools, and persistent writes remain outside the model's direct authority.

## Evaluation

Compare:
A. Generic rewrite
B. PersonalStyle without learning
C. PersonalStyle with adaptation
D. Optional bounded agent

Track semantic and constraint pass rates, style similarity, context accuracy, acceptance, edit effort, longitudinal improvement, latency, and cost.

If a new layer does not produce a measurable improvement over a simpler baseline, remove it.

## Deferred

Defer multi-agent systems, vector databases, broad RAG, autonomous background learning, unrestricted tool use, model routing, complex graphs, and reinforcement learning until a concrete measured problem requires them.

## Architecture decision format

For meaningful changes, record:
- decision
- problem
- simpler alternatives
- why simpler failed
- expected improvement
- verification
- status
