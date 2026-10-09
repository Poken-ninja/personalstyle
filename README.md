# PersonalStyle

PersonalStyle is a local-first **personalized AI-draft humanizer**: it adapts user-supplied
writing to a user's own authorized, context-appropriate voice while preserving meaning,
facts and explicit requirements. Generic polishing is secondary. The expanded voice/rubric
product direction is specified in [ADR-004](docs/decisions/ADR-004-voice-and-constraint-humanization.md),
not yet implemented or proven. The product is not yet complete.

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
F07 is merged in [PR #13](https://github.com/Poken-ninja/personalstyle/pull/13)
at `4c5e9d26d57c05c9fa2e7ae8021fd7c78870f06a`; exact-head CI run
`37865805821` passed on `0e4114f0d6fbda03676f49d1ef13ee004ce14773`.
Real 2,000/5,000-word model acceptance and bounded local regressions passed at the
recorded task revision. Historical failures/counters remain intact in
[docs/F07_TASK.md](docs/F07_TASK.md); this status update does not overwrite them.
F08 is next in the roadmap but remains not_started and requires explicit activation.
SEC02/SEC03 remain unstarted. Delivery proceeds through a Windows
desktop alpha before macOS/Linux protected storage and final cross-platform desktop V1;
see the [roadmap](EXECUTION_CONTRACT.md#windows-desktop-alpha).
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
| [docs/decisions/](docs/decisions/) | Accepted architecture/product decisions, including [ADR-004](docs/decisions/ADR-004-voice-and-constraint-humanization.md) for humanization, context and rubric direction |
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
