# ADR-001: Optional single bounded reasoning component

## Status

Accepted as a **maximum allowed experimental extension**, disabled by default.

## Decision

Start with a deterministic harness plus ordinary bounded generation.

Do not activate a separate reasoning/agent component in the initial vertical slice.

If evaluation exposes a specific ambiguity or adaptation problem that the simpler pipeline cannot solve, PersonalStyle may test **one** bounded reasoning component behind the deterministic harness.

Do not introduce a multi-agent architecture.

## Activation guard

The bounded reasoning experiment may begin only when all are recorded:

1. the concrete failure/problem in the simpler system;
2. evidence that deterministic rules or ordinary generation are insufficient;
3. the exact bounded decisions the reasoner may make;
4. the baseline it must beat;
5. the evaluation metrics and success rule;
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

## Verification

Compare the simpler pipeline against the reasoner-enabled variant on the same frozen evaluation setup.

Measure:
- hard semantic/constraint validity;
- context accuracy;
- editing effort;
- accept-without-edit rate;
- user preference;
- latency;
- resource cost.

## Removal condition

If the bounded reasoner does not produce a meaningful predeclared improvement, keep it disabled or remove it.

The existence of this ADR is not evidence that the component has been implemented or validated.
