# PersonalStyle

PersonalStyle is a local-first adaptive writing assistant that uses authorized writing
examples and edits to improve context-appropriate rewrites while preserving meaning and
explicit constraints. The product is not yet complete.

## Current overview

I01, the GitHub merge gate, SEC01, F01 and F02 are merged and verified for their declared
scope. Sensitive persistence and protected-store reads are verified on Windows only.
Application-level storage encryption and cross-platform sensitive storage are not claimed.
F03 is merged and verified on `88895b8a0801aec7eb2f14eae7d2bdfdcf8001d4` with
exact `ollama / qwen3:8b`; [PR #8](https://github.com/Poken-ninja/personalstyle/pull/8)
records local/live acceptance and green merged-main CI. Its
[historical task record](docs/F03_TASK.md) preserves all failures and budgets.
F04 is merged and verified on `31e3710ebb4140b02e0c63f420826329ff4ba72f`;
[PR #9](https://github.com/Poken-ninja/personalstyle/pull/9) records exact-head and merged-main CI.
F05/F06 are merged and verified at `0ffd79f305044e739815e26fd97bd1798085c717`;
[PR #10](https://github.com/Poken-ninja/personalstyle/pull/10) and its
[historical task record](docs/F05_F06_TASK.md) retain execution evidence.
P01 is merged/verified at `b811eb1147afe3e2010d69324eb822ed60a0f12a`;
[PR #11](https://github.com/Poken-ninja/personalstyle/pull/11) preserves CI, local recovery
and real transport evidence, including the historical failed 600-second run.
S03-WIN-ALPHA Phase A is merged at `96afb4691dfb141601f3239b3d93f203294347d4`;
[PR #12](https://github.com/Poken-ninja/personalstyle/pull/12) and its
[historical task](docs/S03_WIN_ALPHA_TASK.md) preserve local and exact-head CI evidence.
The Windows alpha remains incomplete; Phase B is not started.
F07 is merged historical work ([PR #13](https://github.com/Poken-ninja/personalstyle/pull/13));
its long-document acceptance, failures and exhausted budgets remain in
[docs/F07_TASK.md](docs/F07_TASK.md). It is not awaiting CI or selected for execution.
F08 Phase A TXT/Markdown import/export is merged and verified for its declared scope
([PR #21](https://github.com/Poken-ninja/personalstyle/pull/21)), including native save-dialog
cancellation and exact saved-file read-back. **F08 overall is incomplete:** Phase B DOCX and
Phase C PDF remain frozen, unstarted and not activated.

V01 context-scoped voice evidence and separate storage/personalization authorization are
merged ([PR #18](https://github.com/Poken-ninja/personalstyle/pull/18)). H01 focused verification
and durable diagnostics are merged ([PR #19](https://github.com/Poken-ninja/personalstyle/pull/19)).
G01 authoritative generic-only humanization is merged
([PR #20](https://github.com/Poken-ninja/personalstyle/pull/20)). UX-I02 exposes the ordinary
generic desktop flow **Paste → choose context → Humanize → Review/Edit → Copy**
([PR #22](https://github.com/Poken-ninja/personalstyle/pull/22)). Generic desktop use requires
no voice enrollment; generic results are labeled accordingly and Copy does not authorize learning.

Optional voice onboarding/management UI remains future work and is not activated. Feedback
receipt semantics remain deferred. The original protected-storage failure remains unresolved,
not reproduced; merged work does not establish its cause or a fix. Windows alpha, SEC02/SEC03
cross-platform protected storage and overall V1 remain incomplete; no product success or
release readiness is claimed. Model setup/onboarding remains future work in
[architecture](ARCHITECTURE.md). The [roadmap](EXECUTION_CONTRACT.md#windows-desktop-alpha)
does not authorize continuation.

The ST01 [current status](EXECUTION_CONTRACT.md#current-status) records verified main
`05dfea97ccc3ad97c0dbe1b0d68073cf0e2f63fb` and selects **no active product task**.
Fresh work must start from current main in a clean worktree; preserve the dirty legacy F08
worktree and unfinished merge, its artifacts, the UX-C branch/stash and draft PR #14.
See [merge evidence](EXECUTION_CONTRACT.md#completed-tasks-and-evidence) and the
[UX capability handoff](docs/PERSONALSTYLE_UX_HANDOFF.md#current-checkpoint).

## Default read route

Read this README, [AGENTS.md](AGENTS.md), and the explicitly selected current task contract
first. Consult deeper documents only when the task needs their structure, dependencies,
security/compatibility decisions, configuration or touched implementation. If no task is
selected, do not infer permission from the roadmap or a completed handoff.

## Document ownership

| Document | Role |
|---|---|
| [AGENTS.md](AGENTS.md) | Stable builder rules, security, authority, verification and failure discipline |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Engine/surface structure, components and data flow |
| [EXECUTION_CONTRACT.md](EXECUTION_CONTRACT.md) | Product scope, roadmap, dependencies and completion definitions |
| [docs/decisions/](docs/decisions/) | Accepted architecture decisions |
| [personalstyle.toml](personalstyle.toml), [pyproject.toml](pyproject.toml) | Current policy/version declarations and Python package configuration |
| Selected `docs/Fxx_TASK.md` | Bounded current task scope, acceptance, budgets and checkpoint |
| Completed [task/handoff records](EXECUTION_CONTRACT.md#completed-tasks-and-evidence) | Historical revision-specific evidence; not current activation |

Current V1 release scope is desktop-first: one Flutter shell targeting Windows, macOS and
Linux over the authoritative PersonalStyle engine. The CLI remains an engineering and
acceptance surface. Browser-extension, iOS and Android clients are deferred and are not V1
release blockers. See [architecture](ARCHITECTURE.md#multi-surface-architecture),
[ADR-003](docs/decisions/ADR-003-desktop-first-flutter.md), and the
[completion definitions](EXECUTION_CONTRACT.md#completion-definitions). Security rules
remain in [AGENTS.md](AGENTS.md#security-contract).

A future web client is owner-approved; its deployment/transport model is unresolved.
