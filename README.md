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
F04 is active: engine-owned hard verification and bounded repair. Read the
[current F04 contract](docs/F04_TASK.md). F05 and later remain unstarted.
Generation quality and PersonalStyle V1 completion are not claimed. Model tiers and future
desktop onboarding remain defined in [architecture](ARCHITECTURE.md).
See [current status and evidence](EXECUTION_CONTRACT.md#completed-tasks-and-evidence).

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
