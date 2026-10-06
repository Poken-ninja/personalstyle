# ADR-001: Single bounded reasoning component

## Status

Accepted as the initial architecture.

## Decision

Use one bounded reasoning component behind a deterministic harness. Do not use a multi-agent architecture.

## Problem

PersonalStyle may encounter ambiguity in request intent, context selection, conflicting style signals, or how to adapt generation after verification failure.

## Why deterministic logic alone may be insufficient

Some of these cases require interpretation rather than fixed rules. A bounded reasoning component can make those narrow decisions while remaining constrained by deterministic policy.

## Why multi-agent was rejected

There is no demonstrated problem yet that requires multiple independently reasoning components, coordination protocols, message passing, or agent-to-agent recovery.

The additional complexity would add coordination, observability, security, and failure-surface cost without a verified benefit.

## Expected improvement

Handle genuinely ambiguous cases better than fixed rules while preserving deterministic control over safety, budgets, state, and verification.

## Verification

Compare a deterministic-only baseline against a single bounded reasoning component. Measure user outcome, semantic/constraint pass rates, context accuracy, edit effort, latency, and cost.

If the reasoning component does not produce a meaningful improvement, disable or remove it.

## Consequence

The harness remains the authority over execution. The reasoning component cannot expand permissions, budgets, retries, or persistence scope.
