# F03 — Generic and personalized generation

## Selection and persistent checkpoint

```text
TASK: F03
STATE: blocked
VERIFICATION_STATUS: not_verified; feature implementation has not started
AUTHORITY: project owner selected F03 and initial development model
BASE / MERGE_BASE / CHECKPOINT: 8df79125131cce2fc373494a9846cd18bafc8e75
BRANCH: task/f03-generation
ENTRY_GUARD_RESULT: failed; local Ollama runtime unavailable
DECLARED_ACTIVATION_WRITE_SET: README.md; EXECUTION_CONTRACT.md; docs/F03_TASK.md; personalstyle.toml (model value only)
ACTUAL_ACTIVATION_WRITE_SET: README.md; EXECUTION_CONTRACT.md; docs/F03_TASK.md
PROPOSED_IMPLEMENTATION_WRITE_SET: src/personalstyle/generation.py; src/personalstyle/provider.py; src/personalstyle/storage.py (minimal read extension only if needed); src/personalstyle/profile.py (shared snapshot only if needed); src/personalstyle/cli.py (thin adapter); tests/test_generation.py; tests/test_provider.py; tests/test_initialization.py and tests/test_security.py (model-independent fixtures); personalstyle.toml (selected model value); docs/F03_TASK.md
PRODUCT / PROTOCOL: 0.1.0 / 1.0
CONFIG / STORAGE / PROFILE / PROMPT: 1 / 1 / 1 / 1
PROVIDER / INITIAL_DEVELOPMENT_MODEL: ollama / qwen3:235b
WRITING_DNA_ALGORITHM: writing_dna.v1
PYTHON / SQLITE_RUNTIME: 3.14.6 / 3.50.4
ATTEMPTS_USED: 0 of 3
DIAGNOSIS_USED: 0 of 2
RECOVERY_USED: 0 of 1
IMPLEMENTATION_REVISION: none
NEXT_PERMITTED_ACTION: resolve runtime/model prerequisite, recheck entry guard, then attempt 1
```

Default read: [README](../README.md), [AGENTS](../AGENTS.md), then this task. Consult
[architecture](../ARCHITECTURE.md), [roadmap](../EXECUTION_CONTRACT.md),
[ADR-003](decisions/ADR-003-desktop-first-flutter.md), F01/F02 records and touched code as
needed. Harness-Engineering is read-only reference material. Selection/configuration and
this checkpoint are activation work, not implementation attempt 1.

## Entry guard and observed failure

Require clean current main containing merged F02/PR #7, owner authorization, available
Python/development checks, no conflicting implementation task, and a local Ollama runtime
that lists and actually serves a bounded synthetic request using exactly `qwen3:235b`.
Record runtime version, model digest and execution outcome before feature-code edits.
Do not substitute another model. Missing runtime/model or inability to run blocks F03.

Review on 2026-10-07: fetched main and confirmed local main equals origin/main at the base
above with a clean tree. No open PR or other selected implementation task was found.
Project/reference rules have no material conflict. U2 is resolved; availability is not.

```text
OBSERVED: Ollama executable/process absent; default local API unavailable
EXPECTED: local Ollama runtime and exact qwen3:235b model can serve a request
FAILURE_CLASS: environment_failure / MODEL_RUNTIME_UNAVAILABLE
EVIDENCE: Get-Command ollama and Get-Process ollama* returned no entries;
  LocalAppData/Programs/Ollama/ollama.exe and Program Files/Ollama/ollama.exe absent;
  default .ollama model manifest library/qwen3/235b absent;
  GET http://127.0.0.1:11434/api/version, 5-second timeout:
  System.Net.WebException: Unable to connect to the remote server.
  Installation/process/API checks repeated outside the sandbox with the same outcome.
NEXT ACTION: provision/start local Ollama and exact model, then recheck entry guard
BUDGET REMAINING: 3 implementation; 2 diagnosis; 1 recovery
```

No generation probe could run; model digest and runnable capability remain unverified.
No model download, replacement, profile mutation or feature implementation was performed.
Prerequisite assessment is not a diagnosis of a failed implementation attempt.

The selected model is recorded here; runtime configuration retains its pre-generation
`TODO` until the guard passes. An activation-only trial of the selected config value
produced 102 passing and 3 failing tests in 161.86s, then was reverted without changing
tests or source. This is failed activation evidence, not an implementation attempt.

```text
OBSERVED: startup TODO assertion failed; two security fixture replacements became no-ops
EXPECTED: existing regression cases still exercise their intended inputs
FAILURE_CLASS: verification_defect (fixtures coupled to historical model placeholder)
EVIDENCE: test_cli_help_and_startup_without_model; the model/api_key case of
  test_unsafe_config_rejected_without_content; test_injection_stays_data_and_out_of_diagnostics
AUTHORITY: owner selected qwen3:235b; configuration accepts model strings as data
CAUSE: fixtures replace literal model="TODO" in shared project config, so the selected
  value prevents insertion of the secret-key/injection test input; no security bypass observed
NEXT ACTION: keep activation docs-only; once runtime entry passes, make fixture inputs
  independent of the chosen project model while preserving all original checks
BUDGET REMAINING: 3 implementation; 2 diagnosis; 1 recovery
```

The configuration edit was activation work and its immediate reversion is not a feature
recovery action. No failing check was disabled or given a new expected behavior.

## Bounded behavior and acceptance

- F03-AC1: a minimal engine-owned ModelProvider boundary with one OllamaProvider returns
  generic and personalized candidates for the same validated original/intent/explicit
  context/constraints. Only authorized personalization evidence differs. Results remain
  unverified candidates; F03 does not claim hard-invariant verification or run success.
- F03-AC2: personalized evidence is exact-context, learning-eligible, non-held-out F01
  data plus F02 Writing DNA. Metadata selection has stable ordering, at most the existing
  `max_examples=5`, and respects `max_context_tokens=6000`. Freeze a deterministic token
  accounting method with executable boundary tests before implementation; do not present
  character estimates as exact model tokens. No unrelated-context fallback or opaque search.
- F03-AC3: prompts structurally separate harness instructions from untrusted request/example
  data. Injection strings remain data. Neither path changes durable state. Protected reads
  retain SEC01/F01 schema, ACL/reparse/hardlink/identity checks; coupled source evidence must
  describe one consistent snapshot, or fail explicitly if the source changes.
- F03-AC4: per-run metadata records provider, exact model/digest, prompt contract, mode,
  context, selected example IDs/record versions and Writing DNA algorithm/source profile
  version/fingerprint. No raw prompts, examples or outputs appear in ordinary logs/errors.
- F03-AC5: existing regressions and new F03 validation/selection/isolation/provider failure,
  resource, prompt-separation, metadata and no-mutation/no-sensitive-log tests pass, plus
  pytest, Ruff, mypy, pip check and required GitHub CI on a committed revision. A real local
  exact-model synthetic generic/personalized execution is also required, separate from mocks.
- F03-AC6: durable handoff records base/revision/write set, versions/runtime/model evidence,
  counters, passing/failed evidence, blockers and next action. Open one bounded PR and stop;
  do not merge or activate F04.

Keep product/protocol/config/storage/profile versions unchanged unless an actual compatible
surface changes. Prompt contract 1 is declared but generation is not implemented at this
checkpoint: no prompt change/version claim has occurred. Classify any proposed prompt
contract change against authoritative declarations before changing its version.

## Limits, failures and stop rules

Use existing validated per-input/SQLite/SEC01 bounds, a single 60-second operation deadline,
configured output limit and 10-minute CI ceiling. No aggregate lifetime count/file quota.
One model call per candidate; no hidden provider/HTTP retries or F04 repair loop. Freeze
request/response bounds and token-accounting details when runtime evidence permits entry.
Failure returns a fixed code, never a partial profile or misleading verified success.

Distinguish INVALID_REQUEST, NO_ELIGIBLE_EXAMPLES, PERSONALIZATION_CONTEXT_LIMIT,
PROFILE_SOURCE_INVALID, PROFILE_VERSION_INCOMPATIBLE, PROFILE_RESOURCE_LIMIT,
STORAGE_BOUNDARY_INVALID, DATABASE_UNAVAILABLE_OR_CORRUPT, MODEL_RUNTIME_UNAVAILABLE,
MODEL_UNAVAILABLE, MODEL_IDENTITY_MISMATCH, MODEL_RESPONSE_INVALID, GENERATION_RESOURCE_LIMIT,
environment_failure, verification_defect and scope_mismatch.

Budgets persist across restarts, interruptions and agents: 3 implementation attempts,
2 non-modifying diagnosis cycles, 1 recovery action. First material feature-code modification
is attempt 1. Before repeating repair, record OBSERVED / EXPECTED / FAILURE_CLASS / EVIDENCE /
NEXT ACTION / BUDGET REMAINING and changed information. Only the owner may extend budgets.
Recovery preserves the last trustworthy checkpoint and does not bypass protected storage or
reset counters. Missing authority, unsafe state, scope expansion or exhausted budget stops work.

Excluded: F04 verification/retry, F05 feedback, F06 learning, Flutter, P01 protocols/network
services, SEC02/SEC03, mobile/browser, embeddings/vector databases and agents. Ollama's local
inference connection is the sole provider integration in scope; no cloud fallback/listener.

## Handoff evidence status

Activation checks: all 17 affected startup/security cases pass after reverting the config
trial (24 deselected). Ruff, mypy (6 source files), pip check, 35 local documentation
references and `git diff --check` pass. The initial full local run's three failures remain
recorded above; no full local passing run or F03 runtime success is claimed.
Required GitHub regression evidence for the committed checkpoint is recorded in its PR.
Source, tests, configuration, versions and historical task evidence are unchanged.

Entry failed before implementation. F03 acceptance remains unverified regardless of a green
activation-only regression check. Commit/PR evidence identifies this checkpoint through Git
history and the PR; it is not a passing generation artifact. Resume only after changed
environment evidence satisfies the guard. F04 and later remain unstarted.
