# PersonalStyle

PersonalStyle is a local-first adaptive writing assistant that learns from a user's own writing examples and edits, then rewrites text in a context-appropriate way while preserving meaning and explicit constraints.

## Product success criterion

PersonalStyle is successful only if continued use reduces editing effort or increases accept-without-edit behavior versus a generic rewrite baseline without harming semantic or constraint fidelity.

## Current repository status

I01 is merged and verified; the Python harness is runnable/testable and the GitHub merge
gate is enforced. SEC01 is merged and verified for its declared Windows protection
boundary. F01 is merged and verified for Windows sensitive writing persistence at
`8a2e3bfc2ab70507a1b10c2eca3cb49913886177`.

F02 is the currently selected bounded task; see [docs/F02_TASK.md](docs/F02_TASK.md)
for its state, budgets and evidence. F03 and later tasks remain unstarted.
PersonalStyle V1 and product success are not complete. No cross-platform sensitive
storage or application-level encryption is claimed.

## Document ownership

- [AGENTS.md](AGENTS.md): builder rules, deterministic boundaries, completion, failure, loop control, scheduling policy.
- [ARCHITECTURE.md](ARCHITECTURE.md): system structure, state/data flow, verification layers, and engineering failure modes.
- [docs/decisions/](docs/decisions/): consequential architecture decisions.
- [personalstyle.toml](personalstyle.toml): current project/runtime policy values.
- [EXECUTION_CONTRACT.md](EXECUTION_CONTRACT.md): current bounded work plan, readiness, first task, budgets, and handoff contract.

## Delivery direction

Build one authoritative core first, then thin surfaces for:
- terminal / CLI;
- browser extension (current assumption);
- desktop application;
- iOS;
- Android.

All surfaces share one versioned engine/protocol. They do not maintain separate personalization logic.

Build the core vertical slice:

```text
writing examples
-> explicit context
-> inspectable style profile
-> bounded metadata selection
-> rewrite generation
-> hard verification
-> result
-> accept/edit event
-> evidence-backed adaptation
-> A/B/C performance testing
```

No vector database, multi-agent system, background autonomous learning, n8n workflow, or complex graph is justified for V1.

The current Ollama provider is a desktop/terminal provider; standalone mobile inference requires a separately supported mobile provider. Mobile companion mode may use an authenticated PersonalStyle engine on another trusted device.

Older clients/OS versions are supported only when the declared protocol/capability and release compatibility matrix is actually verified.

## Completion

"Code exists" is not complete.

Security is part of V1 engineering, not a later deployment add-on. Real user writing must not be persisted before the core security boundary is mechanized.

See `AGENTS.md` for the explicit definitions of:
- run complete;
- feature complete;
- V1 implementation complete;
- surface complete;
- security gate complete;
- cross-platform release complete;
- product success validated;
- run/personalization/harness/compatibility failure.

Versioning and merge-conflict rules live in `AGENTS.md`; the multi-surface decision is in `docs/decisions/ADR-002-versioned-multi-surface-engine.md`.


## Security baseline

- local/in-process or loopback by default;
- companion networking disabled by default;
- network clients require authentication;
- non-loopback companion traffic requires protected transport;
- browser/page/imported/model content is untrusted data;
- secrets do not belong in project config, prompts, URLs, or normal logs;
- clients never write canonical profile storage directly;
- raw prompts/outputs are not logged by default;
- application-level database encryption is **not currently claimed**.

See `AGENTS.md` and `ARCHITECTURE.md` for the security completion and failure contract.
