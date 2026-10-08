# F04 ? Hard verification and bounded repair

## Activation and checkpoint

```text
TASK: F04
STATE: local_verified; required current-head CI verdict owned by draft PR handoff
VERIFICATION_STATUS: local deterministic/static/live passed; required CI pending
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
NEXT_PERMITTED_ACTION: required current-head CI; draft PR review; stop; no merge or F05
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

## Final local handoff

```text
TASK: F04
LOCAL_STATE: verified
SOURCE_REVISION: fa39fc63a9a1690fd93058c2012c46602a623158
FINAL_REVISION / REQUIRED_CI: exact committed head and CI evidence owned by draft PR handoff
BASE / MERGE_BASE: 88895b8a0801aec7eb2f14eae7d2bdfdcf8001d4; current main unchanged
ACTUAL_WRITE_SET: the six declared files; no config/schema/provider/storage changes
ATTEMPTS_USED: 1/3
DIAGNOSIS_USED: 0/2
RECOVERY_USED: 0/1
PYTHON / SQLITE_RUNTIME: 3.14.6 / 3.50.4
OLLAMA / MODEL: 0.40.0 / qwen3:8b
MODEL_DIGEST: 500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41
TARGETED: 24 passed in 9.06s; parent 9.532s
FULL_PYTEST: 186 passed in 427.57s; parent 428.187s <=600s; exactly one final run
RUFF / MYPY / PIP_CHECK: passed / passed (9 source files) / passed; one final invocation each
LIVE_ACCEPTANCE: passed; exactly one cycle; 26.803s (parent 27.064s) <=600s
CURRENT_BLOCKERS: required exact-head CI pending at local handoff
NEXT_PERMITTED_ACTION: observe CI; owner review draft PR; stop; no merge or F05
```

AC1/AC2: 24 targeted cases cover each semantic gate, required literals/numbers/calendar,
structural bounds, malformed/duplicate verdict keys, changed repair instructions, exact
identity/context/source, shared eight-call exhaustion, attempt 3 with changed failure,
identical/repeated failure, provider errors and CLI terminal rejection. No partial success.
AC3: real protected F03-to-F04 integration plus existing 162 tests; actual live database
bytes/file set unchanged, protected directory reverified and ordinary INFO log capture zero.
All versions remain 0.1.0 / 1.0 / 1 / 1 / 1 / 1; DNA writing_dna.v1. New additive verification
and repair prompt IDs are hard_verification.v1 / hard_repair.v1; F03 rewrite prompt unchanged.

AC4/AC5: one synthetic exact-8B cycle used the production 6000-context/2000-output policy,
num_ctx=8000 and existing deadlines. Preparation 7.7228s <=120; initial generic/personalized
1.0241s /0.8597s <=60; generic comparison 2.0847s <=60; repair 1.4942s <=60; personalized
comparison 2.0257s <=60. Exactly six operations, no retry/substitution outside recorded repair.
Generic attempt 1 passed all gates. A deliberately invalid personalized fixture was rejected
for REQUIRED_INFORMATION_MISSING and USER_CONSTRAINT_FAILED; repair attempt 2 passed all
gates. Generic/personalized accepted statuses verified; final state SUCCEEDED. A separate
no-repair validation of the already-generated fixture returned FAILED /
GENERATION_ATTEMPTS_EXHAUSTED at attempt 1 with no candidates and zero additional model
operations. This is part of the one acceptance cycle, not another generation/probe.

Context work.email; selected synthetic example 00000000-0000-0000-0000-000000000fa4, record
version 1; DNA source profile version 2 / profile schema 1 / fingerprint
ea27a74d741132bc70df472474ea82fc038968328763f517a35e16ba28693aba. Raw writing/output omitted.
Metadata-only environment artifact: %TEMP%/personalstyle-f04-live-evidence.json. The
committed source revision was live-tested; final handoff changes only documentation.

AC6: this handoff records source, versions, counters and the one preserved fixture failure;
the draft PR records the exact final SHA/current CI verdict. No implementation failure or
recovery occurred. Same-model second-pass judgments remain fallible; no independent-fidelity,
personalization-quality, V1, desktop or cross-platform security claim. F05 remains unstarted.
