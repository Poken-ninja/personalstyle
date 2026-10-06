# PersonalStyle

PersonalStyle is a local-first adaptive writing assistant that learns from a user's own writing examples and edits, then rewrites text in a context-appropriate way while preserving meaning and explicit constraints.

## Product success criterion

PersonalStyle is successful only if continued use reduces editing effort or increases accept-without-edit behavior versus a generic rewrite baseline without harming semantic or constraint fidelity.

## Current repository status

This repository currently contains the **engineering specification and configuration baseline**.

It is not yet evidence of a runnable PersonalStyle application. At the current main revision, the source package and tests have not yet been established.

The first builder task is initialization of the minimal runnable/testable Python harness declared by `pyproject.toml`—not feature expansion.

## Document ownership

- [AGENTS.md](AGENTS.md): builder rules, deterministic boundaries, completion, failure, loop control, scheduling policy.
- [ARCHITECTURE.md](ARCHITECTURE.md): system structure, state/data flow, verification layers, and engineering failure modes.
- [docs/decisions/](docs/decisions/): consequential architecture decisions.
- [personalstyle.toml](personalstyle.toml): current project/runtime policy values.
- [EXECUTION_CONTRACT.md](EXECUTION_CONTRACT.md): current bounded work plan, readiness, first task, budgets, and handoff contract.

## V1 direction

Build one vertical slice:

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

## Completion

"Code exists" is not complete.

See `AGENTS.md` for the explicit definitions of:
- run complete;
- feature complete;
- V1 implementation complete;
- product success validated;
- run/personalization/harness failure.
