# F04 ? Hard verification and bounded repair

## Activation and checkpoint

```text
TASK: F04
STATE: active
VERIFICATION_STATUS: not_verified
AUTHORITY: project owner
BRANCH: task/f04-verification
BASE / MERGE_BASE: 88895b8a0801aec7eb2f14eae7d2bdfdcf8001d4
REPOSITORY_REVISION / CHECKPOINT: activation from base; exact committed head recorded in PR handoff
ENTRY_GUARD_RESULT: passed; clean main == origin/main; F03 merged/CI verified; WIP 1
DECLARED_WRITE_SET: README.md; EXECUTION_CONTRACT.md; docs/F04_TASK.md;
  src/personalstyle/verification.py; tests/test_verification.py;
  src/personalstyle/cli.py (thin explicit adapter only if needed)
ATTEMPTS_USED: 1/3
DIAGNOSIS_USED: 0/2
RECOVERY_USED: 0/1
PRODUCT / PROTOCOL / CONFIG / STORAGE / PROFILE / PROMPT: 0.1.0 / 1.0 / 1 / 1 / 1 / 1
MODEL: ollama / qwen3:8b; exact identity/digest retained from F03
NEXT_PERMITTED_ACTION: attempt 1; targeted F04 tests; final bounded verification; draft PR and stop
```

Activation/status edits consume no implementation attempt. First material feature edit
consumes attempt 1. Budgets persist; no self-extension. Same failure twice stops for
bounded diagnosis rather than an identical retry. Target normal work to 10?15 minutes;
checkpoint long verification instead of expanding scope.

## Contract

Consume engine-generated F03 generic/personalized candidates; SUCCEEDED requires both
accepted candidates to pass every hard gate. FAILED returns fixed codes and counters,
never an unverified candidate as success. The original request remains unchanged.
Deterministic checks: nonempty bounded text, context/provenance equality, original numeric
and explicit calendar literals, and recognized `max_words:N`, `max_characters:N`,
`required_literal:TEXT`, `forbidden_literal:TEXT` constraints. Invalid recognized syntax
fails request validation. Other names/facts, meaning, free-form constraints and substantive
context appropriateness use strict structured second-pass model comparison. Conservative
literal retention may reject an equivalent reformulation; it never replaces semantic checks.
Style/personalization quality is not a hard gate. Model judgment is fallible second-pass
verification, never labeled independent verification or proof of perfect fidelity.

Verification uses `hard_verification.v1`; repair uses `hard_repair.v1`, separately recorded
prompt identifiers. These additive prompt families preserve the immutable F03 rewrite
prompt contract 1; no config/schema/product/protocol bump or migration is needed.
Untrusted text remains in JSON user data, separate from fixed system policy.

One outer model-call ceiling <=8 includes F03 preparation + both initial generations,
semantic comparisons and repairs. Each mode's first candidate is attempt 1; <=3 generation
attempts per mode, shared calls. Repair only after recorded hard-gate failure, with failure
codes/attempt-specific changed instruction and previous candidate as data. Identical repair
output, same failure twice, exhausted calls/attempts, malformed evaluator response, identity,
storage or provider failure terminate explicitly. No hidden retries; preparation <=120s,
each model operation <=60s, existing 6000-context/2000-output/8000-runtime bounds.
Repair rereads only protected exact-context evidence and requires the original selected
IDs/versions/DNA fingerprint; source changes terminate rather than silently changing evidence.
No durable mutation; no ordinary raw prompt/example/output/error logging. Existing security
and storage/version boundaries remain authoritative. No F05/F06/P01/UI/OS storage/provider
routing/embeddings/agents/alternate provider work.

Fixed failures include REQUIRED_INFORMATION_MISSING, STRUCTURAL_CONSTRAINT_FAILED,
MEANING_CHANGED, REQUIRED_FACTS_CHANGED, USER_CONSTRAINT_FAILED, CONTEXT_INAPPROPRIATE,
VERIFIER_RESPONSE_INVALID, VERIFICATION_INPUT_INVALID, IDENTICAL_REPAIR,
VERIFICATION_REPEATED_FAILURE, GENERATION_ATTEMPTS_EXHAUSTED,
MODEL_CALL_BUDGET_EXHAUSTED, PERSONALIZATION_SOURCE_CHANGED and existing provider/store codes.

## Acceptance and verification

- AC1: accepted candidates pass literal/structural, semantic/fact, constraint and context gates;
  invalid candidates rejected; style excluded; malformed verdicts fail closed.
- AC2: classified hard failures produce changed bounded repair; identical/repeated failure,
  attempt/call limits and provider errors terminate without false success.
- AC3: exact model/prompt/context/example/DNA provenance retained; prompt/data separation,
  protected source reread, no mutation or sensitive ordinary logging; prior boundaries green.
- AC4: targeted F04 tests while editing. Final only: full pytest once (600s ceiling), Ruff,
  mypy, pip check once, one bounded synthetic real exact-8B acceptance cycle (<=600s),
  required GitHub CI once. No repeated live development probes.
- AC5: real cycle demonstrates verified pass, deliberate rejection, repaired hard failure,
  unrepaired terminal failure, bounded counters and no mutation/leakage; no quality claim.
- AC6: committed handoff + draft PR record exact revision/base, versions/runtime identity,
  budgets, passing/failed evidence, blockers and next action. Never auto-merge or activate F05.

For each failure record observed/expected/class/evidence/next action/budget remaining.
Historical F03 evidence is preserved. Required CI owns the exact committed-head verdict in
the PR handoff, avoiding a new status commit merely to reference its own SHA.

## Attempt 1 targeted evidence

OBSERVED: 20 passed / 1 failed in 9.77s; character boundary test used 38 for a
39-character synthetic original. EXPECTED: a candidate exactly at its character limit passes.
FAILURE_CLASS: verification_defect; test fixture bound contradicted the assertion.
EVIDENCE: deterministic check correctly rejected length 39 >38.
NEXT ACTION: correct only the fixture bound to len(original), retaining overflow rejection;
rerun targeted tests. No feature-code repair or acceptance weakening.
BUDGET REMAINING: implementation 2; diagnosis 2; recovery 1.

## Final verification checkpoint

Targeted F04 tests: 24 passed in 9.06s (parent 9.532s), after the fixture correction.
Implementation remains 1/3; diagnosis 0/2; recovery 0/1.
Full pytest: single final run started under the unchanged 600-second parent ceiling.
Ruff/mypy/pip check, single live acceptance and current-head CI remain pending.
CLI --generate now consumes F03 through F04; terminal FAILED exits 1 with no candidate.
No feature work or repeated live calls while final verification is pending.
