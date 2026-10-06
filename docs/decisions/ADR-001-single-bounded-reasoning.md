# ADR-001: Optional single bounded reasoning component

## Status

Accepted as a **maximum allowed engineering extension**, disabled by default.

## Decision

Start with a deterministic harness plus ordinary bounded generation.

Do not activate a separate reasoning/agent component in the initial vertical slice.

If the implemented system exposes a specific ambiguity or adaptation failure that the simpler pipeline cannot solve, PersonalStyle may add **one** bounded reasoning component behind the deterministic harness.

Do not introduce a multi-agent architecture.

## Activation guard

The bounded reasoning extension may begin only when all are recorded:

1. the concrete engineering failure/problem in the simpler system;
2. evidence from actual product behavior or tests that deterministic rules or ordinary generation are insufficient;
3. the exact bounded decisions the reasoner may make;
4. the existing baseline behavior it must improve;
5. the acceptance/performance checks that determine whether it helped;
6. unchanged deterministic ownership of budgets, permissions, state transitions, verification policy, scheduling, and persistent writes.

## Allowed decisions

A bounded reasoner may help interpret:
- ambiguous user intent;
- conflicting style evidence;
- ambiguous context evidence;
- a bounded generation-strategy change after a failed candidate.

It cannot control:
- retries or total budgets;
- permissions;
- persistent-state writes;
- database schema;
- verification thresholds;
- state-machine transitions;
- scheduling;
- unrestricted tools/network/filesystem.

## Acceptance

Compare the simpler pipeline against the reasoner-enabled implementation under the same product-test conditions.

Check:
- hard semantic/constraint validity;
- context accuracy;
- editing effort;
- accept-without-edit rate;
- user preference;
- latency;
- resource cost.

## Removal condition

If the bounded reasoner does not produce the predeclared engineering improvement, keep it disabled or remove it.

The existence of this ADR is not evidence that the component has been implemented or verified.
