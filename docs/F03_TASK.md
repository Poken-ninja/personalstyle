# F03 — Generic and personalized generation

## Selection and persistent checkpoint

```text
TASK: F03
STATE: blocked
VERIFICATION_STATUS: not_verified; feature implementation has not started
AUTHORITY: project owner selected F03 and initial development model
BASE / MERGE_BASE / CHECKPOINT: 8df79125131cce2fc373494a9846cd18bafc8e75
BRANCH: task/f03-generation
ENTRY_GUARD_RESULT: failed; installed exact qwen3:30b synthetic probe exceeded the 60-second deadline
DECLARED_ACTIVATION_WRITE_SET: README.md; EXECUTION_CONTRACT.md; docs/F03_TASK.md; personalstyle.toml (model value only)
ACTUAL_ACTIVATION_WRITE_SET: README.md; EXECUTION_CONTRACT.md; docs/F03_TASK.md
DECLARED_ONBOARDING_DOCS_AMENDMENT_WRITE_SET: README.md; ARCHITECTURE.md; EXECUTION_CONTRACT.md; docs/decisions/ADR-003-desktop-first-flutter.md; docs/F03_TASK.md
DECLARED_ENVIRONMENT_CHECKPOINT_WRITE_SET: README.md; EXECUTION_CONTRACT.md; docs/F03_TASK.md
PROPOSED_IMPLEMENTATION_WRITE_SET: src/personalstyle/generation.py; src/personalstyle/provider.py; src/personalstyle/storage.py (minimal read extension only if needed); src/personalstyle/profile.py (shared snapshot only if needed); src/personalstyle/cli.py (thin adapter); tests/test_generation.py; tests/test_provider.py; tests/test_initialization.py and tests/test_security.py (model-independent fixtures); personalstyle.toml (selected model value); docs/F03_TASK.md
PRODUCT / PROTOCOL: 0.1.0 / 1.0
CONFIG / STORAGE / PROFILE / PROMPT: 1 / 1 / 1 / 1
INITIAL_DEVELOPMENT_MODEL: ollama / qwen3:30b
WRITING_DNA_ALGORITHM: writing_dna.v1
PYTHON / SQLITE_RUNTIME: 3.14.6 / 3.50.4
ATTEMPTS_USED: 0 of 3
DIAGNOSIS_USED: 1 of 2
RECOVERY_USED: 0 of 1
IMPLEMENTATION_REVISION: none
NEXT_PERMITTED_ACTION: owner-directed environment reassessment with changed evidence; no feature implementation, substitute model or longer deadline
```

Default read: [README](../README.md), [AGENTS](../AGENTS.md), then this task. Consult
[architecture](../ARCHITECTURE.md), [roadmap](../EXECUTION_CONTRACT.md),
[ADR-003](decisions/ADR-003-desktop-first-flutter.md), F01/F02 records and touched code as
needed. Harness-Engineering is read-only reference material. Selection/configuration and
this checkpoint are activation work, not implementation attempt 1.

## Current model decision and tiers

Owner amendment replaces the previous 235B development selection:
`INITIAL_DEVELOPMENT_MODEL = ollama / qwen3:30b`. This is the reference for F03 development
and its real-runtime entry evidence, not a permanent product requirement.

| Model | Owner-selected role |
|---|---|
| `qwen3:8b` | Option 1: Standard / default user option; explicit user choice required |
| `qwen3:30b` | Recommended/reference development model |
| `qwen3:235b` | Maximum/optional enthusiast tier |

These roles are owner choices, not executed performance/support guarantees. Deployment/user
configuration chooses the model behind the existing ModelProvider architecture; PersonalStyle
must not require one fixed model for every user. Every generation records its exact actual
provider/model identity and digest. No implicit substitution for the selected development
model is allowed; choosing 8B or 235B for development needs a new owner decision.

The later [S03 desktop setup contract](../ARCHITECTURE.md#desktop-model-onboarding-and-setup-future-s03)
owns user onboarding, platform instructions and the explicit-choice/availability/probe/READY
flow. F03 only proves the minimal ModelProvider/Ollama generation seam and 30B development
evidence. It does not implement a setup wizard or require 30B for all users.

Keep `personalstyle.toml` at `model = "TODO"` until runtime entry passes and F03 implementation
actually begins. This amendment changes a model decision and status only: product 0.1.0,
protocol 1.0 and config/storage/profile/prompt versions 1 remain unchanged. No implemented
compatibility surface, prompt contract, source, tests or schema changed.

## Current entry guard and environment evidence

Require clean current main containing merged F02/PR #7, owner authorization, available
Python/development checks, no conflicting implementation task, and a local Ollama runtime
that lists and actually serves a bounded synthetic request using exactly `qwen3:30b`.
Record runtime version, model digest and execution outcome before feature-code edits.
Do not substitute another model. Missing runtime/model or inability to run blocks F03.

### Resumed environment entry: installed model, bounded probe failed

Owner authorized runtime installation, provisioning exactly `qwen3:30b` and one bounded
synthetic probe. Before installation, local branch and draft PR #8 both matched
`4523172cf89f79cece317b49eedd03ce649d3129`; the tree was clean. Local main, origin/main
and GitHub main remained `8df79125131cce2fc373494a9846cd18bafc8e75`. No other implementation
task was active. This remains environment entry, not feature implementation.

Observed environment on 2026-10-07:

| Evidence | Observation |
|---|---|
| OS/architecture | Windows 11 Home, build 26100, x86-64 |
| Installed physical RAM | 16,868,618,240 bytes (15.71 GiB) |
| Initial available RAM / disk | 1,696,632,832 bytes / 129,040,261,120 bytes free on C: |
| GPU / driver | NVIDIA RTX 5070 Laptop; 8151 MiB total VRAM; driver 610.47; compute capability 12.0 |
| Runtime | Ollama 0.40.0; CLI and `/api/version` agree; listener verified at `127.0.0.1:11434` only |
| Installed model | `qwen3:30b`; GGUF, qwen3moe, 30.5B, Q4_K_M; 18,556,699,314 bytes |
| Full model digest | `ad815644918f0eaab341c12b67837cc6dd4562342cdaf118f83d5d554cb37226` |
| Probe-time inventory | 2026-10-07T06:34:53.5293236Z; available RAM 2,921,107,456 bytes (2.72 GiB); free virtual memory 8,365,899,776 bytes; GPU free 7888 MiB; C: free 105,902,972,928 bytes |
| Probe interval | 2026-10-07T06:34:53.764180Z to 2026-10-07T06:35:54.299000Z |
| Outcome | No completed response before the 60-second hard deadline; successful model load not attested |

Installed the official [Ollama 0.40.0 Windows release](https://github.com/ollama/ollama/releases/tag/v0.40.0)
outside the repository. Installer SHA-256 matched the release asset:
`135bf4d927b1de03e884cd2fe66729bdf4d6a2983c5a453b99eb403489e460e1`.
Authenticode was valid with publisher Ollama Inc. The exact model pull exited 0 after
digest verification; `/api/tags` supplied the full identity above and `/api/show` reported
completion/thinking capabilities. No other model was provisioned or substituted.

The sole generation request used synthetic text requesting the single word READY, not
PersonalStyle writing/profile data. It called `/api/generate` for exactly `qwen3:30b` with
`stream=false`, `think=false`, `temperature=0`, `num_ctx=2048`, `num_predict=32`, and a
64-KiB response cap. One outer subprocess deadline bounded the cold-load/request/response
and loaded-identity attestation to 60 seconds, without HTTP/model retries. The worker was
terminated at timeout; parent completion including termination took 60.529 seconds.
The deadline was not increased. No response, load-duration or loaded-digest success evidence
was obtained, so this does not establish whether loading could finish with a longer wait.

Cleanup was not another inference probe: `ollama stop qwen3:30b` exited 0 within its separate
15-second cleanup bound, and `/api/ps` then returned no loaded models. Runtime and exact
model files remain installed outside Git; loopback-only runtime remains available.

```text
OBSERVED: one exact-model synthetic request exceeded its hard 60-second deadline
EXPECTED: exact qwen3:30b loads and completes a bounded request within 60 seconds
FAILURE_CLASS: environment_failure / GENERATION_RESOURCE_LIMIT
EVIDENCE: installed full digest and probe-time resources above; timeout terminated worker;
  no completed generation or successful loaded-model attestation
NEXT ACTION: stop blocked; owner-directed environment reassessment requires changed evidence;
  no automatic retry, timeout increase, model substitution or feature implementation
BUDGET REMAINING: 3 implementation; 1 diagnosis; 1 recovery
```

F03 entry failed. Counters remain implementation 0/3, diagnosis 1/2, recovery 0/1:
authorized prerequisite provisioning and probe cleanup did not repair feature code or
consume an implementation attempt. `model = "TODO"`, all compatibility versions,
source/tests and acceptance requirements remain unchanged. PR #8 stays draft.
This checkpoint's committed revision and documentation/CI evidence are recorded in PR #8.

### Historical 30B assessment before runtime installation

Reassessment after the owner amendment (2026-10-07), outside the sandbox:

| Resource | Observation |
|---|---|
| OS/architecture | Windows 11 Home, build 26100, x86-64 |
| RAM | 16,868,618,240 bytes installed (15.71 GiB); 1,418,362,880 bytes available (1.32 GiB) |
| GPU | NVIDIA RTX 5070 Laptop: 8151 MiB dedicated VRAM total, 7877 MiB free |
| NVIDIA capability | Driver 610.47, compute capability 12.0 |
| Disk | C: NTFS, 129,050,492,928 bytes free (129.05 GB / 120.19 GiB) |
| Ollama | No executable in PATH/usual paths or running process; local `/api/version` cannot connect within the 5-second probe |

Inventory uses Windows CIM and `nvidia-smi`, not WMI's limited AdapterRAM field. Integrated
graphics shares system RAM and does not add independent memory capacity. Free values fluctuate.
The official [30B listing](https://ollama.com/library/qwen3:30b) reports Q4_K_M, 19 GB,
registry short identity `ad815644918f`; this is not a verified local digest.
[Windows requirements](https://docs.ollama.com/windows) and
[GPU support](https://docs.ollama.com/gpu) match the OS/driver; installation needs at least
4 GB, so disk space is sufficient for runtime plus the 19-GB model.

Feasibility inference: 30B cannot fit wholly in the 8-GiB GPU. Total physical RAM plus VRAM
makes a CPU/GPU split plausible, unlike the previous 235B assessment. However, current free
RAM plus VRAM is only about 9 GiB, below the roughly 17.7-GiB model file before runtime/context
overhead. This is an advisory suitability warning, not a newly proven minimum-RAM threshold.
Hardware/resource estimates alone do not replace runtime/probe evidence or impose a hard
pre-download gate unless a hard runtime requirement is known. Paging is not verified runtime
evidence. No measured claim is made that a request meets the existing 60-second ceiling.
The model's smaller active parameter count does not mean all its weights fit in 8-GiB VRAM.

```text
OBSERVED: Ollama unavailable; current free-RAM estimate warns of unsuitable resource availability
EXPECTED: exact qwen3:30b can load and serve one bounded synthetic request
FAILURE_CLASS: environment_failure / MODEL_RUNTIME_UNAVAILABLE; resource warning advisory
EVIDENCE: current inventory above; 19-GB registry model listing; local API unreachable
NEXT ACTION: explain resource warning and reassess known runtime requirements;
  install/start supported local Ollama; then provision
  exactly qwen3:30b and record runtime version, full digest and bounded execution evidence
  in a separately resumed environment assessment. No installation/download in this amendment.
BUDGET REMAINING: 3 implementation; 1 diagnosis; 1 recovery
```

F03 stays blocked. This docs-only amendment does not authorize feature implementation, model
substitution, a longer runtime ceiling, F04 activation or PR merge.

## Historical 235B activation evidence — superseded model selection

The records below describe the earlier 235B checkpoint only. They preserve observed failures
and do not impose a 235B requirement on the current 30B entry guard.

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
AUTHORITY AT THAT CHECKPOINT: owner selected qwen3:235b; configuration accepts model strings as data
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

The current environment checkpoint records the failed exact-model probe above; it is not
a passing F03 generation artifact. Source/tests/configuration remain unchanged and PR #8
remains draft. Its committed head, documentation checks and required CI are recorded there.

The prior onboarding amendment is specification only. Its five-document scope, exact committed
head, docs checks and required CI evidence are recorded in draft PR #8. F03 remains blocked;
S03/F04 are not activated. Counters remain implementation 0/3, diagnosis 1/2, recovery 0/1.

Prior 30B-selection amendment checks (`dbd303f7d7dd85f9140c60417db75b680cd08826`):
Ruff, mypy (6 source files), pip check, 35 local references,
the current 30B entry / optional-or-historical 235B reference audit and `git diff --check`
pass. Source/tests/configuration and all compatibility versions match the verified base.

```text
OBSERVED: full local regressions: 104 passed, 1 failed in 172.97s
EXPECTED: test_locked_database_fails_without_partial_record receives
  DATABASE_UNAVAILABLE_OR_CORRUPT for its deliberately held SQLite write lock
FAILURE_CLASS: unknown; unreproduced protected-boundary rejection, environment failure suspected
EVIDENCE: actual fixed code STORAGE_BOUNDARY_INVALID; no source/test/config change;
  isolated unchanged test passes in 6.63s during diagnosis cycle 1
NEXT ACTION: rerun complete verification using changed evidence from isolated reproduction;
  do not alter expected codes, ACL checks, test inputs or timeout ceilings
BUDGET REMAINING: 3 implementation; 1 diagnosis; 1 recovery
```

Diagnosis inspected the existing SEC01/storage error paths and isolated the unchanged test.
Boundary failures reject the mutation; no bypass or partial success was observed. The
underlying reason for the initial rejection was not established. Preserve that failed
evidence even if later checks pass. This used diagnosis 1, no implementation or recovery.
Final full-suite and required GitHub evidence for this amendment are recorded in its PR.

Historical activation checks: all 17 affected startup/security cases pass after reverting the config
trial (24 deselected). Ruff, mypy (6 source files), pip check, 35 local documentation
references and `git diff --check` pass. The initial full local run's three failures remain
recorded above; no full local passing run or F03 runtime success is claimed.
Required GitHub regression evidence for the committed checkpoint is recorded in its PR.
Source, tests, configuration, versions and historical task evidence are unchanged.

Entry failed before implementation. F03 acceptance remains unverified regardless of a green
activation-only regression check. Commit/PR evidence identifies this checkpoint through Git
history and the PR; it is not a passing generation artifact. Resume only after changed
environment evidence satisfies the guard. F04 and later remain unstarted.
