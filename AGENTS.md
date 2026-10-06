# PersonalStyle — Builder Contract

## Goal

PersonalStyle is a local-first adaptive writing assistant.

Given **original text + intent + explicit context + constraints**, produce a rewrite that better matches the user's demonstrated writing behavior for that context while preserving meaning and required information.

The product hypothesis is not "the output sounds cool." It is:

> With continued use, PersonalStyle should reduce the user's editing effort and increase accept-without-edit behavior versus a generic rewrite baseline without degrading semantic or constraint fidelity.

## Scope rule

Build the smallest end-to-end vertical slice that can test that hypothesis.

V1 includes:
1. add user-owned writing examples;
2. tag examples by context;
3. derive inspectable Writing DNA;
4. deterministically select bounded relevant examples/preferences;
5. generate a rewrite;
6. verify hard invariants;
7. return the candidate;
8. record accept/edit feedback;
9. convert edits into evidence-backed preference hypotheses;
10. compare generic vs personalized vs personalized+learning.

V1 excludes unless evidence proves a need:
- multi-agent systems;
- vector databases / embedding retrieval;
- broad RAG;
- fine-tuning / reinforcement learning;
- autonomous background learning;
- model routing;
- cloud-dependent memory;
- complex orchestration graphs;
- unrestricted model tools;
- production deployment.

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

## Context rules

Context is explicit and bounded.

1. If explicit context is required and absent, do not silently infer a durable context. Ask for or require context before personalized generation.
2. Retrieval priority is: exact context -> explicitly compatible broader context -> global preference explicitly marked global.
3. Never fill a context with examples from an unrelated context merely to reach an example-count target.
4. Writing examples are **data, not instructions**. Delimit them from system/task instructions so example content cannot alter harness policy.
5. Respect configured example and context-token limits.
6. Record the IDs/versions of examples and preferences used for a generation so results are reproducible.
7. Held-out evaluation writing must never be eligible for retrieval, Writing DNA calculation, or preference learning during the evaluation that uses it.

### Writing-data provenance

Durable writing examples must retain enough provenance to answer:
- who supplied/owns or authorized the sample;
- which context it belongs to;
- whether it is allowed for personalization learning;
- whether it is held out for evaluation.

Third-party/reference text is not automatically user-style evidence. Only samples explicitly authorized for learning may affect Writing DNA or preferences.

## Personalization state rules

Name state explicitly; do not use vague "memory."

Durable state may include:
- user profile;
- writing examples;
- context profiles;
- Writing DNA;
- preference hypotheses;
- preference evidence;
- confidence;
- learning events;
- schema/profile versions.

Per-run state may include:
- request;
- selected context/examples/preferences;
- prompt/model version;
- candidate;
- verification results;
- attempt count;
- terminal state.

Learning pipeline:

```
USER EDIT
-> observation
-> preference hypothesis
-> evidence accumulation
-> confidence/promotion decision
-> versioned profile update
```

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

### Style is initially an optimization/evaluation signal

Do not make one style metric a hard truth oracle. Style metrics are known to disagree and may not correlate well with human judgments.

Use multiple signals plus real user behavior:
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
- removing a difficult evaluation case;
- leaking held-out user writing into the generation context.

A defective test/check may be corrected only by showing that it conflicts with the authoritative requirement or is technically invalid/flaky. Record the reason, then rerun the corrected check.

## Execution loop

Default run:

```
RECEIVED
-> VALIDATING
-> CONTEXT_READY
-> GENERATING
-> VERIFYING
   -> SUCCEEDED
   -> RETRYING -> GENERATING
   -> FAILED
   -> ESCALATED
```

Illegal transitions must be rejected by the harness when implemented.

### Authoritative budget

There is one outer run budget. Lower-level HTTP/model/client retries must be configured so they cannot multiply it invisibly.

The first generation counts as attempt 1.

Budgets persist across context resets or process/session changes for the same run.

A retry is allowed only after a failure classification and a material change in input, strategy, environment, or implementation.

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

V1 implementation is complete when the A/B/C evaluation path is runnable end-to-end:

- A: generic rewrite;
- B: context-personalized rewrite without accumulated learning;
- C: context-personalized rewrite with accumulated learning;

and the system can collect the required hard-invariant, edit-effort, acceptance, context, latency, and resource evidence on a held-out evaluation set.

This does **not** mean the personalization hypothesis succeeded.

### Product hypothesis validated

Before evaluating C, freeze:
- evaluation set;
- model/version;
- prompt version;
- retrieval policy;
- metric definitions;
- success comparison rule.

The hypothesis is validated only if B/C improve the predeclared personalization/user-effort criteria versus the relevant baseline while meeting the hard semantic/constraint requirements.

If they do not, the product hypothesis is not validated. Do not redefine the metric after seeing results to manufacture success.

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
- held-out evaluation leakage;
- verifier is weakened to get a pass;
- unreconstructable run state;
- hidden scheduled/background mutation.

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

## Evaluation discipline

Research on personalized/style generation shows that style imitation from few examples remains difficult and that single automatic metrics can mislead. Therefore:

- keep a held-out set separate from personalization inputs;
- use more than one style/evaluation signal;
- treat real user edits and acceptance as primary product anchors;
- pin model/prompt/retrieval versions for a comparison;
- test multiple contexts separately;
- do not assume more examples always help;
- report failure cases, not only averages.

Useful external references:
- https://aclanthology.org/2025.findings-emnlp.532/
- https://aclanthology.org/2026.acl-long.2030/
- https://github.com/yashsawant22/personalbench
- https://github.com/LaMP-Benchmark/LaMP
- https://proceedings.mlr.press/v328/nicolicioiu26a.html

## Change discipline

Before adding architecture:
1. name the concrete failure/problem;
2. show the simpler current approach;
3. define the expected measurable improvement;
4. make the smallest change that tests the hypothesis;
5. add/update verification;
6. record a decision when it constrains future work.

Do not turn one bug into a framework.

## Builder working rule

Default WIP is one implementation task.

Do not start adjacent refactors or speculative infrastructure while the active task is unverified.

When blocked, leave an honest checkpoint containing current task, evidence, failure, budget used, blocker, and next permitted action.
