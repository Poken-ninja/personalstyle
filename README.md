# PersonalStyle

PersonalStyle is a local-first adaptive writing assistant that uses authorized writing
examples and edits to improve context-appropriate rewrites while preserving meaning and
explicit constraints. The product is not yet complete.

## Current overview

I01, the GitHub merge gate, SEC01, F01 and F02 are merged and verified for their declared
scope. Sensitive persistence and protected-store reads are verified on Windows only.
Application-level storage encryption and cross-platform sensitive storage are not claimed.
F03 feature implementation has not started. Ollama 0.40.0 and exact `qwen3:30b` are installed;
diagnosis verified a warm synthetic request within 60 seconds. The cold diagnostic request
took 93.61 seconds under substantial paging and did not pass that bound. Entry capability
is evidence for the observed warm state and must be rechecked if runtime/model state changes.
Initial development uses `ollama / qwen3:30b`.
Owner-selected tiers are `qwen3:8b` (option 1, Standard/default user option),
`qwen3:30b` (Recommended/reference development),
and `qwen3:235b` (Maximum/optional enthusiast). Model choice is deployment/user configuration
behind ModelProvider, not one fixed product requirement; each run records its actual identity.
Users explicitly choose; no silent substitution. The future
[desktop onboarding flow](ARCHITECTURE.md#desktop-model-onboarding-and-setup-future-s03) belongs
to S03 and is not implemented.
Read the [F03 task and checkpoint](docs/F03_TASK.md). F04 and later remain unstarted.
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
