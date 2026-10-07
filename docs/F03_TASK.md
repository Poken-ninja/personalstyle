# F03 — Generic and personalized generation

## Selection and persistent checkpoint

```text
TASK: F03
STATE: blocked; exact-model generic generation exceeded the unchanged 60-second deadline
VERIFICATION_STATUS: local deterministic regressions/static checks passed; real F03 pair failed
AUTHORITY: project owner selected F03 and initial development model
BASE / MERGE_BASE / CHECKPOINT: 8df79125131cce2fc373494a9846cd18bafc8e75
BRANCH: task/f03-generation
ENTRY_GUARD_RESULT: passed for implementation activation; branch/runtime/exact installed digest verified; owner decision resolves cold-bound blocker; new preparation mechanism still requires execution evidence
DECLARED_ACTIVATION_WRITE_SET: README.md; EXECUTION_CONTRACT.md; docs/F03_TASK.md; personalstyle.toml (model value only)
ACTUAL_ACTIVATION_WRITE_SET: README.md; EXECUTION_CONTRACT.md; docs/F03_TASK.md
DECLARED_ONBOARDING_DOCS_AMENDMENT_WRITE_SET: README.md; ARCHITECTURE.md; EXECUTION_CONTRACT.md; docs/decisions/ADR-003-desktop-first-flutter.md; docs/F03_TASK.md
DECLARED_ENVIRONMENT_CHECKPOINT_WRITE_SET: README.md; EXECUTION_CONTRACT.md; docs/F03_TASK.md
DECLARED_DIAGNOSIS_2_WRITE_SET: docs/F03_TASK.md; README.md and EXECUTION_CONTRACT.md (current status only)
PROPOSED_IMPLEMENTATION_WRITE_SET: src/personalstyle/generation.py; src/personalstyle/provider.py; src/personalstyle/storage.py (minimal read extension only if needed); src/personalstyle/profile.py (shared snapshot only if needed); src/personalstyle/cli.py (thin adapter); tests/test_generation.py; tests/test_provider.py; tests/test_initialization.py and tests/test_security.py (model-independent fixtures); personalstyle.toml (selected model value); docs/F03_TASK.md
PRODUCT / PROTOCOL: 0.1.0 / 1.0
CONFIG / STORAGE / PROFILE / PROMPT: 1 / 1 / 1 / 1
INITIAL_DEVELOPMENT_MODEL: ollama / qwen3:30b
WRITING_DNA_ALGORITHM: writing_dna.v1
PYTHON / SQLITE_RUNTIME: 3.14.6 / 3.50.4
ATTEMPTS_USED: 2 of 3
DIAGNOSIS_USED: 2 of 2
RECOVERY_USED: 2 of 2 (owner extended ceiling from 1 to 2; pytest environment repair completed)
IMPLEMENTATION_REVISION: 16155a5698de29d95886daac524543bd39a6fd99; feature code unchanged during recovery
DIAGNOSIS_2_STATE: completed; entry_capable for observed warm state only; inference calls 2 of 2
NEXT_PERMITTED_ACTION: owner decision on the evidenced runtime blocker and exhausted recovery/diagnosis budgets; no retry, substitution, feature edit, F04 or merge
```

Default read: [README](../README.md), [AGENTS](../AGENTS.md), then this task. Consult
[architecture](../ARCHITECTURE.md), [roadmap](../EXECUTION_CONTRACT.md),
[ADR-003](decisions/ADR-003-desktop-first-flutter.md), F01/F02 records and touched code as
needed. Harness-Engineering is read-only reference material. Selection/configuration and
this checkpoint are activation work, not implementation attempt 1.

## Active owner decision: preparation is separate from generation

### Owner-authorized environment recovery 2/2

```text
Previous recovery budget: 1 action
Previous recovery used: 1/1
Additional authorized recovery actions: 1
New total recovery ceiling: 2
At authorization: RECOVERY_USED 1/2; one action remaining
Authority: project owner
Reason: previous recovery was consumed by Windows pytest temporary-directory permission
  failure after a long suspend/resume period (owner-provided context)
Current action: inspect and repair only pytest's disposable temporary environment;
  rerun the unchanged full suite with the existing 600-second ceiling
Implementation: 2/3; diagnosis: 2/2; neither budget reset
Declared recovery repository write set: docs/F03_TASK.md; README.md; EXECUTION_CONTRACT.md
```

Entry verified branch `task/f03-generation`, exact HEAD
`16155a5698de29d95886daac524543bd39a6fd99` and clean tree. Host process enumeration found
no Python/pytest processes. `%TEMP%\pytest-of-mamid` was an ordinary directory (no reparse
target), owned by `MSI\CodexSandboxOffline` (SID ending 1005), with protected full-control
entries for OWNER RIGHTS, SYSTEM and Administrators. Normal host user `MSI\mamid` (SID
ending 1001) could not read its ACL, enumerate it or remove it: access denied. The sandbox
owner could inspect and remove only this pytest-owned root using normal permissions,
after an exact absolute-path/reparse guard. No ACLs or system policy were changed; no
PersonalStyle profile directory or unrelated application was touched. This establishes
an account/permission mismatch for the temporary-directory error, not a proven cause of
the original three boundary-test rejections or the original long elapsed time.

#### Recovery result and exact-model verification (2026-10-07)

The normal user recreated the pytest root, now owned by `MSI\mamid`, and could list it.
The full unchanged suite passed: **137 passed in 287.47 seconds**, parent wall 287.911
seconds, exit 0, within the existing 600-second ceiling. The command was
`.venv\Scripts\python.exe -m pytest -q -o cache_dir=%TEMP%\pytest-of-mamid\.pytest-cache`.
Only cache location changed, to keep pytest's cache in its disposable directory instead
of the existing sandbox-owned repository cache; no test/plugin/check was disabled.
Ruff (`check src tests`), mypy (`src`, eight files), and pip check passed again.
The feature revision tested is exactly `16155a5698de29d95886daac524543bd39a6fd99`;
only the declared three status/checkpoint documents changed during this recovery.
Required CI on that feature revision passed: [run 37697763676](https://github.com/Poken-ninja/personalstyle/actions/runs/37697763676).
Current checkpoint CI is recorded separately in the draft PR handoff.

After those passes, one real engine-owned `generate_pair` call used only synthetic
request/example text in a temporary SEC01/F01-protected fixture, the actual reference
configuration, and the installed provider implementation. No config overrides were used:
6000 context tokens plus 2000 output tokens allocated `num_ctx=8000`, temperature 0.2,
generation deadline 60 seconds, preparation invariant 120 seconds. Before preparation,
Ollama `/api/ps` was empty. Runtime was **0.40.0**, model **qwen3:30b**, full digest
`ad815644918f0eaab341c12b67837cc6dd4562342cdaf118f83d5d554cb37226`.

| Observation | Evidence |
|---|---|
| Preparation | Passed in 45.616595 seconds; one empty-input `/api/generate`, 44.866603 seconds, `done_reason=load` |
| Prepared identity | Installed and loaded digest matched exactly; loaded context length 8000; VRAM allocation 6,235,587,869 bytes |
| Generic generation | Failed `GENERATION_RESOURCE_LIMIT`; `/api/chat` spent 59.967737 seconds after pre-call identity checks, within the enforced overall 60-second operation |
| Personalized generation | Not attempted after generic failure |
| Model operations | Exactly 2: one preparation and one generic call; no retry/substitution |
| Fixture database | Bytes and profile file set identical before/after generation; protected boundary verified afterward |
| Ordinary logs | Zero characters captured at INFO; no raw prompt/example/output leakage observed |
| Probe duration | 109.719087 seconds through post-failure checks; parent 115.585 seconds, exit 1, below 360-second verification-process ceiling |

No completed generic response was received, so no generation-token count or model-reported
load/generation duration is claimed. The empty load response also supplied no separate
model-reported load duration; 44.866603 seconds is observed request wall time.

| Native memory observation | Before preparation | After preparation | After failure |
|---|---:|---:|---:|
| Available physical RAM (bytes) | 2,021,552,128 | 1,080,668,160 | 481,947,648 |
| Memory load (%) | 88 | 93 | 97 |
| Available pagefile/commit capacity (bytes) | 11,973,541,888 | 1,173,561,344 | 829,407,232 |

Before the probe, GPU total/free VRAM was 8151/7891 MiB, C: free disk was
101,720,313,856 bytes, and pagefile allocated/current usage was 21472/1961 MiB.
After failure, GPU free VRAM was 1754 MiB and pagefile allocated/current/peak usage was
30502/15383/15413 MiB. `/api/ps` still showed the exact loaded 30B digest and context 8000.
No system policy/configuration or applications were changed. Observed memory/commit
pressure and pagefile growth accompany the timeout; they do not prove its sole cause.

```text
OBSERVED: pytest and all static checks passed after the authorized temp-directory repair;
  exact 30B preparation passed, but normal generic generation reached its 60-second ceiling
EXPECTED: preparation <=120s and both generic/personalized candidates <=60s, exact identity,
  no retry/substitution, no mutation and no normal sensitive logs
FAILURE_CLASS: runtime_resource_limit / GENERATION_RESOURCE_LIMIT
EVIDENCE: one empty preparation 45.616595s; exact loaded digest/context verified;
  one generic HTTP operation 59.967737s plus pre-call identity checks, then explicit failure;
  personalized not called; memory load 97%, available RAM 481947648 bytes at failure
NEXT ACTION: stop and preserve failed evidence in draft PR #8; owner decision required;
  no additional inference, automatic timeout increase, model substitution or feature repair
BUDGET REMAINING: 1 implementation; 0 diagnosis; 0 recovery
```

No new failing test demonstrated a feature-code defect, so implementation remains **2/3**.
This is a successful pytest environment repair and failed real generation verification,
not a complete F03 acceptance pass. The historical failures below remain unchanged.

### Controlled stop after recovery 1/1

```text
OBSERVED: the fresh bounded host regression completed with exit 1;
  25 passed / 112 setup errors / 2 warnings in 66.78s; parent wall time 67.711s
EXPECTED: the unchanged suite can create/access temporary fixtures and pass all checks
FAILURE_CLASS: environment_failure
EVIDENCE: PermissionError [WinError 5] Access is denied:
  C:\Users\mamid\AppData\Local\Temp\pytest-of-mamid
  during pytest temporary-directory setup (getbasetemp / os.scandir);
  pytest also warned it could not create its cache paths (WinError 183)
NEXT ACTION: stop; preserve the unverified artifact and failed evidence in draft PR #8;
  further environment repair requires owner-authorized recovery; do not bypass protections
BUDGET REMAINING: 1 implementation; 0 diagnosis; 0 recovery
```

This recovery failure occurred before the temporary-fixture tests could execute. It does
not diagnose the original three protected-boundary rejections. Their cause remains unknown.
No temporary-directory ACLs were changed, no checks were weakened, and no user applications
were terminated. The original long elapsed time has no established cause. There was no
real-model preparation/generic/personalized run during implementation verification.

Passing evidence before the stop: attempt 1's 29 targeted tests; attempt 2 Ruff, mypy
(eight source files) and pip check; attempt 2's full suite passed 134 tests, including new
F03 tests, but failed three unchanged F02 cases. These partial results are not F03 acceptance.
Required CI for the new checkpoint is separate evidence and cannot replace missing local
or exact-model execution evidence. The task is not merge-ready. Versions remain unchanged.
The final documentation link-target check and `git diff --check` passed. The declared
twelve-file write set contains all changes; storage.py, existing F02 tests, schemas and
dependency declarations are untouched. Fetched origin/main remains
`8df79125131cce2fc373494a9846cd18bafc8e75`, also the merge base; there are no incoming
main commits or merge conflicts to reconcile. PR #8 remains draft.

The blocked checkpoint commit owns the implementation revision; obtain its exact SHA using
`git log -1 --format=%H -- docs/F03_TASK.md`. The PR handoff records that SHA and current CI.

```text
OBSERVED: attempt 2 Ruff/mypy/pip check passed; full pytest had 134 passed / 3 failed;
  reported elapsed 24263.93s (6h44m23s); real model verification has not run
EXPECTED: original F02 provenance/metadata/text failure cases reach their expected codes
FAILURE_CLASS: environment_failure suspected; protected-boundary rejection, root cause unknown
EVIDENCE: test_invalid_source_or_version_never_returns_profile provenance failed during store.add;
  metadata/text received STORAGE_BOUNDARY_INVALID instead of their original expected codes;
  storage.py and test_profile.py are unchanged; all new F03 tests passed
NEXT ACTION: recovery 1/1: one fresh host-environment full regression run with a hard
  600-second process ceiling; preserve all boundary checks and expectations; no model activity
BUDGET REMAINING: 1 implementation; 0 diagnosis; 0 recovery
```

The changed recovery conditions are a fresh host execution context outside the restricted
sandbox and an enforced verification process ceiling instead of the earlier invocation.
This does not establish the original cause, increase any SEC01 timeout, bypass an ACL check
or alter tests. If the boundary failures recur, stop rather than repairing SEC01 inside F03.

```text
OBSERVED: attempt 1 targeted tests passed (29 in 53.22s); Ruff failed FURB167;
  mypy reported four Optional-token-count typing errors; pip check passed
EXPECTED: every required static check passes without changing acceptance/tests
FAILURE_CLASS: implementation_defect (static verification)
EVIDENCE: provider.py re.S alias and counts typed Any | None after combined validation
NEXT ACTION: attempt 2 uses re.DOTALL and explicit integer validation/type narrowing;
  readiness review also verifies loaded context allocation to avoid an implicit reload
BUDGET REMAINING: 1 implementation after repair begins; 0 diagnosis; 1 recovery
```

The first static checks' combined shell command ended with successful pip check; that does
not erase the individually reported Ruff/mypy failures. Both are recorded and will be rerun.
Direct repair of those explicit compiler/linter findings is not an additional diagnosis cycle.

Resumed from `af33c25f256e468d9706eb8c6f6f48a232d5cd8e` with a clean tree, matching draft
PR #8 and unchanged verified main. Runtime 0.40.0 and exact 30B digest were rechecked.
No conflicting task is active. The owner resolves the prior cold-bound blocker as follows:

```text
validate request/model
-> prepare exact selected model: maximum 120 seconds, no retry, verify identity/digest
-> generic generation: maximum 60 seconds
-> personalized generation: maximum 60 seconds
```

Preparation uses Ollama's [supported empty-input load mechanism](https://docs.ollama.com/faq#how-can-i-preload-a-model-into-ollama-to-get-faster-response-times),
never user writing. Charge one preparation plus one call for each candidate against existing
`max_total_model_calls=8`; at most three model operations, no hidden retries. Metadata GET/show
checks do not invoke inference. Preparation timeout or unverifiable identity prevents generation.
The 120-second ceiling is an enforced provider invariant, not a config field/schema change.
The previous 93.61-second cold diagnostic remains failed evidence, not a readiness pass.

Actual implementation write set: README.md and EXECUTION_CONTRACT.md (current status);
docs/F03_TASK.md; src/personalstyle/provider.py; src/personalstyle/generation.py;
src/personalstyle/profile.py (one shared protected read snapshot); src/personalstyle/cli.py
(thin explicit inspection adapter); tests/test_provider.py; tests/test_generation.py;
tests/test_initialization.py; tests/test_security.py (model-independent fixtures);
personalstyle.toml (reference model only). No storage/schema/dependency/architecture changes.

Freeze selection as earliest UUIDs in F01's exact-context eligible stream, at most five;
compute DNA from the full same protected snapshot. Oversized selected evidence fails rather
than trimming text or filling from another context. For the verified Qwen3 GPT-2 byte-level
BPE/template, count UTF-8 content bytes plus conservative verified-template literal framing
as a token upper bound, never an exact token count. Enforce the configured context bound
before inference, allocate room for configured output separately, and record provider token
counts. Unknown tokenizer/template compatibility fails explicitly; no approximate-token
claim or silent truncation. No new tokenizer dependency is introduced.

Prompt contract 1 had no implemented generation template. This defines its first template
with fixed system instructions and a separate JSON user-data envelope; no existing immutable
template or implemented compatibility surface is changed. All declared versions stay unchanged.
Validation, selection/DNA reading, preparation and each generation are individually bounded;
the existing 60-second generation ceiling is never extended by preparation or transport retries.
Activation started at 0/3; the first material feature-code edit began attempt 1. Diagnosis remains 2/2 and
recovery 0/1. This owner-authorized implementation is not another diagnosis cycle.

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

### Diagnosis cycle 2/2: cold initialization and paging versus warm inference

Owner authorized this final diagnosis cycle from
`0b21bc202806a1412102ba62243bf40de5922d74`. Local HEAD, origin/task/f03-generation and
draft PR #8 matched that revision; the tree was clean and GitHub main remained the declared
base. Ollama CLI/API still reported 0.40.0. The installed exact `qwen3:30b` full digest
remained `ad815644918f0eaab341c12b67837cc6dd4562342cdaf118f83d5d554cb37226`.
Initial `/api/ps` was empty; RAM available was 4,548,423,680 bytes and GPU free 7877 MiB.
Nothing was reinstalled/redownloaded, no user applications were terminated and no system
configuration was changed by the builder.

Before inference, existing Ollama logs showed the prior failed request entered loading
with 2.6 GiB free RAM, allocated CPU model buffers of 12191.92 MiB and CUDA buffers of
5499.42 MiB, then logged HTTP 499 after client cancellation at about 61 seconds. The later
zero-content generate entry was the previously recorded unload, not a second inference.
This localized the earlier failure to startup under low available memory without proving
which phase consumed its unobserved time.

The temporary diagnostic helper initially failed with a missing `tempfile` import before
any request: `verification_defect` in temporary instrumentation, expected helper startup,
observed `NameError`; the justified correction added the missing import. It used no inference
call, changed no repository
source/test and did not open another diagnosis cycle. Both actual calls used only the same
synthetic request for READY, exact model, `think=false`, `stream=false`, temperature 0,
context 2048, output at most 32 tokens, and a 64-KiB response cap. No hidden HTTP/model retries.

| Timing (seconds) | Cold diagnostic | Warm bounded request |
|---|---:|---:|
| Observation ceiling | 300 (diagnosis only) | 60 (unchanged product bound) |
| Request wall time | 93.613 | 1.153 |
| Ollama total | 93.389498 | 1.104912 |
| Model load | 58.584391 | 0.082901 |
| Prompt evaluation | 25.400286 | 0.048263 |
| Output generation | 9.134382 | 0.957594 |
| Prompt / output tokens | 17 / 32 | 17 / 32 |

Cold observations ran 2026-10-07T06:49:25.868686Z through 06:51:02.212779Z;
warm observations ran 06:51:49.572209Z through 06:51:52.513866Z. These intervals include
resource collection before/after the timed request. Resource sampling overhead explains
parent collection time (cold 94.663s; warm 1.414s), not the recorded request timing.
Both requests returned HTTP 200, nonempty text and `done=true`, `done_reason=length` at the
32-token cap. Neither returned exactly READY; no instruction fidelity, rewrite quality or
F04 semantic/constraint verification is claimed. Warm reused the identical synthetic prompt;
its fast prompt evaluation is not evidence for uncached inputs or the full 6000-token budget.

| Resource | Cold before | Cold after | Warm before | Warm after |
|---|---:|---:|---:|---:|
| Available physical RAM (bytes, native observation) | 3,915,210,752 | 1,159,073,792 | 936,841,216 | 816,160,768 |
| Free VRAM (MiB; total 8151) | 7877 | 1796 | 1796 | 1796 |
| Pagefile current use (MiB) | 2480 | 12737 | 12799 | 12777 |
| System committed bytes | 27,119,550,464 | 46,909,075,456 | 46,916,218,880 | 46,931,341,312 |

During cold loading, a CIM sample measured just 423,092,224 available RAM bytes and
257849 pages input/sec (1669 page reads/sec), versus baseline 11 pages input/sec. Pagefile
allocation grew automatically from 18158 to 29104 MiB; current use reached 12737 MiB at
the cold after-sample. Some bounded counter queries timed out during pressure; that missing
telemetry is not a zero-paging observation. These are system-wide counters, so attribution
to this model alone is not proven. Concurrent allocation growth, Ollama CPU-buffer metadata,
and timings support startup/paging as the primary explanation rather than ordinary warm
inference latency. Precise causal separation of disk reads versus pagefile reads is unavailable.

The exact digest was attested loaded after cold, before warm and after warm via `/api/ps`:
runtime size 18,985,758,225 bytes, VRAM allocation 6,190,499,101 bytes, context 2048.
It remained loaded after both requests with bounded `keep_alive=10m` (warm expiry reported
2026-10-07T07:01:51.6308935Z). No third inference call or reload was performed.
After recording those states, diagnostic cleanup `ollama stop qwen3:30b` exited 0 under a
separate 15-second bound, and `/api/ps` returned no loaded models. Available RAM was then
3,136,958,464 bytes and GPU free 7877 MiB. Unload is a zero-content cleanup operation,
not a third inference measurement or feature recovery. The exact model/runtime remain installed.

```text
OBSERVED: cold complete request 93.613s with substantial paging; exact loaded model serves warm request in 1.153s
EXPECTED: exact model serves a bounded request within the unchanged 60-second ceiling
DIAGNOSIS_CLASSIFICATION: entry_capable for the observed warm state only
FAILURE_CLASS: prior environment_failure / GENERATION_RESOURCE_LIMIT; cold initialization under observed memory pressure
EVIDENCE: separate load/prompt/generation timings, exact loaded digest and before/during/after resources above
NEXT ACTION: stop; no more diagnosis calls; separately authorized implementation must recheck runtime entry
BUDGET REMAINING: 3 implementation; 0 diagnosis; 1 recovery
```

The warm request satisfies the existing minimal runtime entry condition; the larger cold
observation ceiling is never passing evidence. This is not `cold_start_only` under the owner's
literal definition because measured model loading alone was below 60 seconds; loading plus
prompt evaluation and generation exceeded it. Warm latency passed and the exact model stayed
loaded, so `runtime_resource_limit` for warm inference was not observed in these two calls.
Entry capability is limited to this observed warm state, not a durable READY guarantee after
unloading/restart or proof of full F03 acceptance. Cold startup still fails the unchanged
complete-request bound and must not be silently warmed/retried inside an over-budget run.
F03 remains blocked after diagnostic cleanup: the model is now unloaded, the original cold
failure is retained, and current entry must be reassessed before implementation. The warm
passing observation is preserved rather than being presented as current cold readiness.
No preload policy, timeout change, acceptance change or recovery was introduced.
Implementation remains 0/3, diagnosis is now exhausted at 2/2 and recovery remains 0/1.
PR #8 stays draft; no feature implementation or F04 is activated. All versions and
`model = "TODO"` remain unchanged. Committed checkpoint/CI evidence is recorded in PR #8.

### Historical environment entry: installed model, bounded probe failed

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

Use existing validated per-input/SQLite/SEC01 bounds, a 120-second preparation deadline and
a separate 60-second deadline for each generation (and protected source-read operation),
configured output limit and 10-minute CI ceiling. No aggregate lifetime count/file quota.
One preparation call plus one model call per candidate; no hidden provider/HTTP retries or F04 repair loop. Freeze
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

The current checkpoint records diagnosis 2/2, the cold failure and the bounded warm runtime
entry evidence above; it is not a passing F03 feature artifact. Source/tests/configuration
remain unchanged and PR #8 remains draft. Its committed head, documentation checks and
required CI are recorded there. Earlier checkpoints below retain their historical counters.

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
