# PersonalStyle V1 Execution Contract

## Status

```text
CONTRACT_ID: PS-V1-001
CONTRACT_STATUS: contract_ready
IMPLEMENTATION_STATUS: not_started
ACTIVE_IMPLEMENTATION_LIMIT: 1
```

This file is a specification and current execution handoff. It is not evidence that initialization, implementation, or verification has occurred.

## Objective

Build the smallest local-first PersonalStyle vertical slice that can demonstrate in normal engineering tests that context-specific personalization reduces user editing effort or increases accept-without-edit behavior versus a generic rewrite baseline while preserving meaning, required information, and explicit constraints.

## Scope

Core V1:
- user-authorized writing examples;
- explicit context tags;
- inspectable Writing DNA;
- deterministic bounded example selection;
- generic and personalized rewrite generation;
- hard semantic/information/constraint/context verification;
- accept/edit feedback;
- classified edit observations and evidence-backed context preferences;
- A/B/C product-performance testing.

Target delivery surfaces after the authoritative core is working:
- terminal/CLI;
- browser extension (reversible current assumption for "extension");
- desktop application;
- iOS application;
- Android application.

Every surface must use the same engine/protocol contract. A surface is not allowed to fork personalization logic.

Excluded until measured engineering need:
- multi-agent systems;
- vector database / embedding retrieval;
- broad RAG;
- fine-tuning / reinforcement learning;
- autonomous background learning;
- n8n;
- complex graphs;
- cloud state;
- production deployment.

## Facts and current repository state

At the contract revision:
- repository and governing documentation exist;
- `pyproject.toml` declares Python >=3.12, Typer, pytest/ruff/mypy, and `personalstyle = personalstyle.cli:app`;
- `personalstyle.toml` declares local Ollama, SQLite, metadata retrieval, agent disabled, scheduling disabled, and bounded model-call/generation budgets;
- the inspected repository tree does not yet contain the declared source package or tests;
- the exact Ollama model is still `TODO`.

Runtime/test behavior is not yet observed.

## Consequential unknowns

### U1 — local initialization capability
Need builder evidence for Python >=3.12, dependency installation, and authorized local repo writes.

Blocks: I01 activation only.

### U2 — initial Ollama model
Must be selected and recorded before the first model-generation feature activates.

### U3 — held-out product-test set and success rule
Must be frozen before final product-performance testing. Do not choose the pass rule after seeing C results.

### U4 — extension host
Current reversible assumption: "extension" means browser extension.

If VS Code or another host is intended, this changes the surface adapter task but must not change the engine contract.

### U5 — standalone mobile inference
The configured Ollama desktop provider does not establish native iOS/Android inference.

Mobile companion mode is architecturally defined. Standalone mobile remains blocked until a mobile-supported inference provider and its OS/hardware requirements are selected and verified.

### U6 — app-shell framework and release matrix
No UI framework or minimum iOS/Android/macOS/Windows/Linux matrix is selected yet.

This does not block I01 or the core engine. It blocks claiming a cross-platform application release.

### U7 — application-level encryption at rest
Current policy explicitly does not claim application-level database encryption.

Before any release claims encrypted-at-rest profile storage, a concrete mechanism plus migration, recovery, backup/export, and compatibility behavior must be implemented and verified.

This does not block local V1 engineering if the product clearly relies on host OS/account/disk protection and does not misrepresent the guarantee.

## Source authority

- V1 behavior/scope: this contract + owner decisions;
- builder/control rules: `AGENTS.md`;
- structural design: `ARCHITECTURE.md`;
- architecture decisions: `docs/decisions/`;
- current policy values: `personalstyle.toml`;
- implementation: checked-out repository revision;
- runtime: observed local execution;
- verification: recorded evidence.

## Readiness

```text
Contract readiness: READY
Initialization readiness: NOT YET EVIDENCED
Feature readiness: NOT READY
```

The contract is usable without runtime evidence because I01 is the bounded task that establishes the missing runtime/test capability.

## Task plan

| ID | Task | Depends on | Initial state |
|---|---|---|---|
| I01 | Establish runnable/testable Python harness | none | not_started |
| SEC01 | Mechanize core local security boundary | I01 | not_started |
| F01 | Persist user-authorized writing examples + explicit context metadata | I01 + SEC01 | not_started |
| F02 | Derive inspectable Writing DNA/context profile | F01 | not_started |
| F03 | Generic + personalized generation using metadata retrieval | F02 + U2 | not_started |
| F04 | Hard verification path and bounded candidate retry | F03 | not_started |
| F05 | Record accept/edit events and classify edit type | F04 | not_started |
| F06 | Evidence-backed context preference promotion | F05 | not_started |
| P01 | Mechanize versioned engine protocol + authenticated capability handshake | F04 + SEC01 | not_started |
| E01 | Frozen A/B/C product-performance test | F06 + U3 | not_started |
| S01 | Terminal/CLI release acceptance | F06 | not_started |
| S02 | Extension adapter + compatibility acceptance | P01 + F06 + U4 resolved | not_started |
| S03 | Desktop app adapter + release matrix | P01 + F06 + U6 resolved | not_started |
| S04 | iOS/Android companion-mode app | P01 + F06 + U6 resolved | not_started |
| S05 | Standalone mobile inference | S04 + U5 resolved | not_started |

Do not fully design later tasks until their dependencies and evidence sharpen.

SEC01 is intentionally summarized until I01 establishes the runnable harness. Its required outcome is: sensitive writing has a defined protected local storage/access boundary, secrets cannot enter normal config/logs/prompts, untrusted content remains data, loopback/network defaults fail safely, and security checks can be executed before F01 begins storing real user writing.

Cross-platform product behavior belongs in the engine. Surface tasks verify transport, permissions, lifecycle, installation, compatibility, and UX failure handling rather than reimplementing personalization.

# I01 — Establish Runnable/Testable Python Harness

## State

```text
TYPE: initialization
STATE: not_started
VERIFICATION_STATUS: not_verified
```

## Objective

Make the existing design/config repository minimally executable and testable without implementing PersonalStyle personalization features.

## Entry guard

I01 may become active only when:
1. the intended repository revision is checked out;
2. authorized local write access is available;
3. Python >=3.12 exists or may be provisioned;
4. declared dev dependencies may be installed in an isolated environment;
5. no other implementation task is active.

Ollama and a selected model are not prerequisites for I01.

If a guard is missing, record `not_started -> blocked` with the blocker. Resolution does not auto-activate the task.

## Permitted scope

I01 may establish:
- the declared Python package structure;
- the declared Typer CLI entry point;
- a non-generation help/startup-check path;
- deterministic configuration loading/validation;
- baseline test structure;
- meaningful deterministic smoke tests;
- one durable task/handoff state record.

## Prohibited scope

Do not implement during I01:
- writing-example product behavior;
- Writing DNA;
- SQLite product schema beyond initialization necessity;
- Ollama generation;
- prompts/personalization retrieval;
- semantic/style verification;
- adaptation/learning;
- agents;
- scheduling;
- web UI;
- n8n;
- production deployment.

Security is not excluded from V1. Core data/secrets/trust-boundary controls are prerequisites for storing real user writing.

## Acceptance criteria

### AC1 — package resolves
The package declared by `pyproject.toml` can be installed/imported in the supported isolated development environment.

Evidence: actual successful install/import result.

### AC2 — CLI resolves
The declared `personalstyle` entry point runs a help/startup-check path successfully without requiring an LLM.

Evidence: actual successful CLI result.

### AC3 — test harness is real
pytest discovers and runs the initialization smoke suite successfully.

A test that only contains an unconditional pass is not acceptable evidence.

### AC4 — configuration loads
The initialization path reads/validates current configuration and preserves the declared hard policy values, including protocol/config/storage/profile/prompt version declarations.

`model = "TODO"` must be surfaced as later generation-readiness state, not as a reason for non-generation startup to fail.

### AC5 — handoff is reconstructable
A fresh session can identify:
- I01 state;
- revision/checkpoint;
- acceptance evidence;
- blockers/failures;
- attempts/budget used;
- next permitted task/action.

## Verification integrity

I01 may not be made to pass by:
- deleting the CLI declaration;
- weakening/removing a meaningful smoke check;
- hiding a configuration error;
- changing expectations solely to fit broken behavior.

If an existing declaration is shown to be wrong, record the authoritative requirement, mismatch, correction reason, and rerun evidence.

## Action–verification–repair loop

```text
ACTIVATE
-> implementation attempt
-> run I01 acceptance checks
   -> all pass: passing
   -> fail: classify
      -> material repair within budget
      -> bounded diagnosis
      -> block/escalate/stop
```

Failure classes likely relevant:
- implementation_defect;
- environment_failure;
- dependency_failure;
- verification_defect;
- permission_failure;
- scope_mismatch;
- unknown_failure.

A repeated attempt must have new information or a material change.

## Budgets

```text
Implementation attempts: 3 total
Initial attempt: counts as attempt 1
Diagnosis cycles: 2 non-modifying cycles
Task-local recovery actions: 1
```

All activity remains subject to the configured wall-clock/resource policy. Sessions, agent changes, or context resets do not reset these counters.

Only the project owner may authorize more budget; the extension must record why new evidence makes further work worthwhile.

## Stop / escalation

### Success
All I01 acceptance criteria have current evidence.

### Block
Use when continuation requires an unavailable dependency, permission, environment capability, or owner decision.

Record blocker, evidence, required input, owner, and resume condition.

### Controlled stop
Stop when:
- attempt/diagnosis/recovery budget is exhausted;
- the next action exceeds I01 scope;
- repository state cannot be trusted;
- authorization would be exceeded.

## Recovery

Before I01 modifications, establish a task-start version-control checkpoint.

Recovery order:
1. repair current local change;
2. revert I01-local changes;
3. restore I01 task-start checkpoint.

Do not remove unrelated pre-existing project files.

Rerun affected I01 checks after recovery before another attempt.

## Handoff record

At every session boundary persist:

```text
CONTRACT_ID / VERSION
PRODUCT_VERSION
PROTOCOL_VERSION
CONFIG / STORAGE / PROFILE SCHEMA VERSIONS
PROMPT_CONTRACT_VERSION
ACTIVE_TASK
TASK_STATE
VERIFICATION_STATUS
REPOSITORY_REVISION / CHECKPOINT
MERGE_BASE
DECLARED_WRITE_SET
ATTEMPTS_USED
DIAGNOSIS_USED
RECOVERY_USED
PASSING_EVIDENCE
FAILED_EVIDENCE
BLOCKERS
NEXT_PERMITTED_ACTION
```

## Definition of complete

I01 is complete only when AC1–AC5 have actual current evidence and the handoff record is current.

Core V1 is **not** complete when I01 completes.

A target surface is not complete merely because it builds. It must pass the applicable version/protocol/platform acceptance contract in `AGENTS.md`.

A cross-platform release is not complete until every platform/version claimed as supported has current evidence. Unverified older OS versions must not be advertised as supported.

No surface handling sensitive writing is release-complete until its applicable security gate passes. Functional correctness alone is insufficient.

See `AGENTS.md` for separate definitions of run complete, feature complete, surface complete, cross-platform release complete, V1 implementation complete, and product success validated.

## Merge safety for this contract

Before each task activates, record its expected write set.

If the write set overlaps another active task in protocol/schema/config/migrations/shared governing files, serialize the work.

After any merge/conflict resolution, evidence affected by the merged behavior becomes stale until rerun on the merged revision.

GitHub main protection and the required Python harness check were mechanized after I01;
see `docs/GITHUB_GATE_HANDOFF.md` and `docs/SEC01_HANDOFF.md` for remote evidence.
These checks enforce the recorded CI gate; semantic scope review remains a builder duty.

# SEC01 — Core local security boundary

Owner selected SEC01 after I01 and the GitHub gate on 2026-10-06. Historical initial
states above remain contract-baseline facts; current evidence is in task handoffs.

Entry: I01 merged, GitHub gate merged/enforced, clean synchronized main, authorized
workspace writes, Windows/Python development environment and no other active task.

Permitted scope: bound configuration input; reject unsupported/unsafe security settings;
prepare and verify an empty private local profile directory using Windows ACLs on explicit
CLI action; metadata-only startup diagnostics; executable negative security tests.
Excluded: writing persistence/SQLite schema, inference/prompts, learning, networking,
client authentication/pairing and protocol handshake (P01), release/signing/dependency audit.

Acceptance:
- SEC-AC1: startup rejects configuration over 64 KiB, unexpected secret fields, incompatible
  versions, unsafe network/logging/secrets flags, and escaping/absolute storage paths without
  echoing input values. Current valid configuration still passes, including model TODO.
- SEC-AC2: explicit storage preparation creates only an empty directory; protected ACL is
  owned by the current Windows account and grants inheritable FullControl only to that
  account and SYSTEM. Existing insecure/nonempty directories, reparse paths and unsupported
  operating systems fail safely without weakening existing permissions.
- SEC-AC3: startup telemetry accepts fixed event identifiers and bounded counters only;
  injected writing/credential markers and config contents never reach normal logs/output.
  User-provided paths enter fixed OS ACL code as data, never shell instructions.
- SEC-AC4: positive/negative tests exercise the real CLI/config and Windows ACL readback;
  I01 tests, Ruff, mypy and the required GitHub CI job pass on the committed revision.
- SEC-AC5: handoff records evidence, checkpoint, versions, counters, scope limitations,
  failures and next action. No claims about absent network/prompt/storage product paths.

Budget: 3 implementation attempts (first counts), 2 non-modifying diagnosis cycles,
1 recovery; counters persist. Fixed ACL subprocesses have a 10-second ceiling; configuration
has a 64 KiB ceiling; CI retains its 10-minute ceiling. Classify failure before repair;
retry only with changed information; block on unavailable OS permissions/environment;
controlled stop on exhausted budget/scope change. Recovery preserves unrelated work:
repair local changes, revert SEC01-only changes, then restore task-start Git checkpoint.

OS account/admin protection is the local trust boundary; same-account malicious code and
host administrators are not isolated by this application. No encryption or forensic erase
is claimed. Preparation/readback is a precondition for F01, not permission to bypass ACL
verification in future writers. Prompt isolation and authenticated networking must be
verified when those code paths exist, before exposing them. F01 must not start automatically.
