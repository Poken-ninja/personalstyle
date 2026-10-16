# H01 — Harness performance and execution-loop audit

```text
TASK: H01
BRANCH: task/h01-harness-performance
BASE: origin/main at 9a7a2049ca9d19f5d5d9d163b54a174d073d27a8
STATE: implementation attempt 1 active
SCOPE: test execution, reporting, safe temporary directories, and CI evidence reuse only
PRODUCT BEHAVIOR: unchanged
PR #18: remains draft; not merged or modified
IMPLEMENTATION: 1/1 primary attempt in progress
CORRECTION: 0/1 available only for a demonstrated defect
```

## Objective

Shorten the time from a small change to trustworthy verification without weakening product,
security, migration, consent, protocol, or acceptance gates. Keep one builder and one
authoritative task budget. This audit does not authorize changes to product code or PR #18.

## Diagnosis evidence

The current pytest configuration only sets `testpaths = ["tests"]`; it has no default
duration report, JUnit output, fail-fast policy, or standard temporary-directory policy.
`scripts/run_pytest_shard.py` assigns all 12 Python test modules exactly once across four
shards and validates coverage before executing a complete module shard. The GitHub workflow
runs those shards in parallel on Windows, plus import/startup, Ruff, mypy, pip check, and
whitespace checks. The workflow has a bounded 15-minute job timeout and does not publish
per-test timing artifacts.

### Measured timings

- Exact-head CI run `38928344583` passed all six jobs in **6m18s wall time**. The test-step
  durations were: `feedback-security` 5m36s, `documents-profile` 5m01s,
  `protocol-storage` 4m41s, and `provider-learning` 3m09s. Shards overlap; their durations
  must not be summed as wall time. Static/startup checks took about 43s. CI reports only
  shard/job timing today, not test-level timing.
- After the V01 revocation repair, local full regression reached its **900s ceiling** with
  one failure marker and no flushed traceback/summary. Collection order maps the marker to
  `test_profile.py::test_invalid_source_or_version_never_returns_profile[provenance-PROFILE_SOURCE_INVALID]`;
  that case passed once in isolation. Its original cause is **unknown**, not proven code,
  environment, or test defect. The previous intermittent `PREFERENCE_SOURCE_INVALID`
  observation is also unresolved. Neither is erased by passing CI.
- On the same repair, focused revocation cases took **173.69s**, followed by the broader V01
  evidence/learning modules (**20 passed in 447.18s**). The focused cases are included in
  that broader module run, so at least the focused portion was repeated before CI.
- One bounded synthetic revocation test was instrumented without changing the ACL verifier:
  **83 PowerShell ACL subprocesses**, **32.090s cumulative subprocess time**, median
  **0.370s**, maximum **1.560s**; the test passed in **33.15s**. The probe emitted aggregate
  counts/timings only. This is one measured scenario, not a suite-wide estimate.
- Historical local full-suite evidence includes 845.86s and 1062.62s runs with two failures,
  then a pre-revocation-repair 852.83s pass. These are different revisions and remain
  historical; none substitutes for exact-head evidence.

### What the evidence says

Repeated protected-store checks call Windows PowerShell separately for directory and file
verification, including before/after transaction checks. The measured synthetic test spent
about 97% of its elapsed time inside those subprocess calls. This is a demonstrated hot
path, but it is part of the security boundary and must not be mocked, cached, weakened, or
removed to improve speed. First optimize redundant test setup only if a test can retain the
same real boundary assertions and measured security evidence.

The owner-reported 50–60 minute work cycles cannot be divided precisely into coding,
waiting, approvals, environment interruptions, and tests from current records. The evidence
does establish avoidable verification: a 900s local full run was repeated in addition to
parallel exact-head CI, and targeted revocation tests were repeated inside a larger module
run. A conservative avoidable budget is up to **15 minutes per final gate** from skipping a
redundant local full regression when exact-head CI covers every module and quality check;
the targeted/module overlap added further time, measured as 173.69s for that repeated subset.
Actual end-to-end savings remain uncertain because no work-cycle telemetry exists.

Pytest TEMP permission failures and Windows subprocess/transport errors are documented
environment/history evidence. The current harness does not standardize `--basetemp` or save
structured outcomes as tests finish. Killing a full run at its ceiling can therefore lose
the traceback and final summary; a progress marker is not a classified test failure.

## Verification policy implemented

1. **Tier 1 — fast preflight:** changed-file whitespace and relevant Ruff/type checks, shard
   coverage validation, then the smallest directly affected tests through the verified-temp
   runner. A failure stops the task at this tier.
2. **Tier 2 — affected integration:** run the smallest storage, consent, security, protocol,
   migration, or document integration set required by the changed dependency path. Retain
   actual protected-storage checks when storage/security behavior is affected. Do not rerun
   the same focused cases in a broader local module run unless the broader interaction is
   itself the question.
3. **Tier 3 — complete acceptance:** use exact-head GitHub CI as the complete regression and
   static gate when its 12-module coverage check and quality job pass. Do not automatically
   run the same full Python suite locally. Require a local full run only when the task
   contract requires an environment-specific result, CI misses a required path, or diagnosis
   needs local behavior. Keep local failures unresolved until evidence classifies them.

Reuse is revision-specific: any relevant code, test, dependency, config, migration, or
workflow change invalidates the affected evidence. Exact-head CI never erases a prior local
failure or timeout.

## Bounded H01 write set

The following minimum harness changes are implemented in attempt 1:

- `AGENTS.md`: make risk-based local verification and exact-head CI reuse authoritative,
  replacing the blanket final-local-full-regression sequence. It distinguishes builder
  guidance from mechanisms enforced by scripts/CI;
- `scripts/run_pytest_shard.py` and a small pytest plugin: sanitized per-test JSONL
  timing/outcome records written as each pytest phase completes, plus safe unique temporary
  root handling for focused and shard runs. Records contain module, test function (no
  parameter values), phase, outcome, duration, shard, revision, tracked-worktree state,
  run ID, and fixed failure category; never test parameters, paths, exception text, writing,
  or secrets. A 20,000-event cap bounds each report.
- `.github/workflows/python-harness.yml`: retain the existing four parallel shards and
  quality gate and lint the diagnostics plugin. Flushed structured records appear in the
  existing CI log; failed/interrupted local runs retain their JSONL file. No new artifact
  action was added because a post-job upload is not guaranteed after a hard job timeout.
- `tests/test_harness.py`: coverage accounting, report redaction, failure classification,
  partial report survival, fail-fast argument wiring, and safe temporary-root handling.
- `pyproject.toml` was not changed; the runner is the explicit local pytest route and
  `--fail-fast` remains opt-in.

No production storage/security code is in the write set. Do not cache ACL results or
substitute synthetic ACL checks for tests that claim to exercise the Windows boundary.
Harness diagnostics may distinguish PowerShell timeout, launch failure, and definite ACL
mismatch using exception category and exit state, with paths/account names/output suppressed.

## Bounded implementation and recovery proposal

- One implementation attempt for a minimal report/temp-root vertical slice.
- One diagnosis allowance for any reporting or Windows temporary-root failure.
- One recovery only for a concrete, materially different harness defect.
- No full suite solely to profile. Use existing CI timings, one bounded synthetic protected
  test, and targeted runner tests. Compare the same synthetic test and comparable exact-head
  CI jobs before/after; report machine, Python version, shard, wall time, subprocess count,
  aggregate ACL time, and test outcomes. Never compare summed parallel shard time to wall
  time.
- If safe structured reports require capturing sensitive pytest parameter IDs or changing
  security-test behavior, stop and redesign the report format rather than weakening tests.

## H01 acceptance status

- Every test module is still assigned exactly once and all required CI jobs remain mandatory.
- CI retains the same four parallel complete test shards and all security/migration tests.
- A timeout/failure leaves capped sanitized per-test records in CI stdout and, for local
  runs, a retained JSONL report for completed phases where feasible; no raw parameters,
  user writing, credentials, or sensitive paths appear.
- Temporary roots are unique, writable-probed, repository-contained, and never remove
  preexisting data; only successful generated run directories are cleaned up.
- Windows ACL timeout, launch failure, and actual protection mismatch remain distinct in
  test diagnostics; production error and security semantics do not change.
- The selected synthetic protected-store scenario preserves real ACL checks and reports
  invocation count/time. H01 does not optimize or bypass those checks.
- A complete exact-head CI run remains the final acceptance evidence; local full-regression
  runs are task-specific, not automatic.

## Implementation checkpoint — 2026-10-16

Implementation attempt 1/1 is complete locally; the bounded correction allowance remains
unused. The first focused harness test run exposed one fixture-only `NameError` after its
test helper import was removed; that import was restored without production changes. The
next focused run passed **9 tests**. This fixture correction did not consume a material
correction attempt.

Evidence on the H01 branch (`task/h01-harness-performance`, base
`9a7a2049ca9d19f5d5d9d163b54a174d073d27a8`):

- Shard coverage: **12/12** modules assigned exactly once on this baseline. The V01-only
  `test_voice_evidence.py` joins `protocol-storage` automatically when present; it is not
  imported into H01 or PR #18.
- Focused harness tests: **9 passed**, including report redaction, partial failure records,
  fail-fast wiring, ACL failure categories, and unique write-probed temp roots.
- A real protected-storage roundtrip test through the final runner: **1 passed in 21.36s**
  (20.70s test body); existing Windows ACL checks remained active. A comparable direct
  pytest run took **21.03s**. The 0.33s difference is within run-to-run noise and shows no
  measurable speedup or material runner overhead.
- A deliberately failing harness fixture run left `outcomes.jsonl` containing the sanitized
  failed test/phase/category. Its parameter marker and exception text were absent. The runner
  printed the same structured outcome to stdout before the failure summary.
- Ruff on `src`, `tests`, and both runner scripts passed; mypy on `src` passed (13 files);
  pip check passed; shard coverage passed. No full local regression was run.
- No production ACL calls were cached, mocked, removed, or changed. The previously measured
  83-call/32.09s synthetic revocation case remains the baseline; H01 makes no ACL performance
  claim. No product behavior, consent policy, schema, or protocol changed.
- The initial coverage check failed because the fixed map referenced PR-18-only
  `test_voice_evidence.py`, absent from current main. The runner now adds it when present and
  independently validates every discovered module exactly once.

Exact-head CI on implementation commit `9e26a0115db01468edd1cf646ac03c646f74893b` passed
all six jobs in run `38981661870` in **5m45s wall time**. All four Python shards passed;
each performed the **12/12** exact-coverage check. The static/startup and aggregate harness
jobs passed. CI logs contain flushed per-test phase records and slowest-test summaries, so
the diagnostics were exercised on the hosted runner.

The intended iteration-time benefit is avoiding duplicate full local regressions when
exact-head CI supplies complete coverage and making interrupted runs diagnosable. The
prior PR #18 CI was 6m18s, but those runs do not have identical test contents, so this is
not a valid before/after speed comparison. No test execution speedup is claimed. The
comparable single protected-storage test also showed no meaningful change (21.03s direct,
21.36s through the runner).

V01 attempt counters and historical failures remain unchanged. PR #18 remains draft and
unmerged. F08 artifacts remain untouched. H01 implementation is locally verified and its
implementation commit passed exact-head CI; PR #19 remains a draft for owner review. No
merge is authorized by this record.
