# PersonalStyle

PersonalStyle is a local-first adaptive writing system that learns from demonstrated writing behavior and user edits.

## Engineering rule

> Problem first. Simplest architecture that reliably solves the problem.

See [AGENTS.md](AGENTS.md) for the engineering contract and [ARCHITECTURE.md](ARCHITECTURE.md) for the architecture baseline.

## Current status

The repository is initialized around a deterministic harness, explicit context/state, bounded generation, and independent verification.

The agent component is disabled initially.

## Design priorities

1. Preserve meaning and constraints.
2. Match demonstrated user behavior for the relevant context.
3. Learn from evidence rather than guesses.
4. Keep execution bounded and observable.
5. Prefer simpler architecture until measurement shows a need for more.
