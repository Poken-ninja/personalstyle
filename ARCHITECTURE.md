# PersonalStyle Architecture

## Problem

Given input text, intent, and context, transform the text so its expression better matches the user's demonstrated writing behavior while preserving original meaning, required information, and explicit constraints.

The personalization framing is:

**Style × Context × Intent**

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
