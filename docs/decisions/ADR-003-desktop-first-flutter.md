# ADR-003: Desktop-first V1 with a Flutter shell

## Status

Accepted owner decision. Specification only; Flutter integration and cross-platform support
are not implemented or runtime-verified by this ADR.

## Context

The previous architecture allowed terminal, browser, desktop and mobile surfaces. Current
product priority is a desktop application on Windows, macOS and Linux. The core already has
Windows-only security/persistence evidence, while browser/mobile delivery would add unrelated
transport, permission, lifecycle and inference work before the core rewrite loop is complete.

Flutter currently supports native Windows, macOS and Linux desktop applications, making it a
reasonable shared presentation shell. Framework support alone is not PersonalStyle support.

## Decision

V1 release scope is:

- Windows desktop;
- macOS desktop;
- Linux desktop.

Use one Flutter desktop shell for those three operating systems. The terminal/CLI remains an
engineering and acceptance surface, not a separate personalization implementation.

Browser extension, iOS and Android are deferred. They are not V1 release blockers. ADR-002's
thin-client, engine-ownership and compatibility rules remain authoritative if those surfaces
are activated later.

The Flutter shell owns presentation, platform integration and local UX state. It must not own
or fork retrieval, Writing DNA, generation policy, verification, retry budgets, persistence,
profile migration or preference-learning rules.

The authoritative engine keeps those behaviors. Non-embedded clients use the defined
engine/client boundary. The engine remains the only canonical profile-store writer.

Inference stays behind a ModelProvider boundary. Ollama is the initial desktop provider, but
Flutter code must not depend on Ollama-specific product behavior. Exact model identity is
runtime configuration and must be recorded with generation evidence.

## Security consequence

Existing SEC01/F01/F02 evidence remains valid for its declared Windows scope. This decision
does not make that evidence stale and does not broaden it.

macOS and Linux sensitive persistence require platform-specific protected-storage mechanisms
and executable positive/negative evidence before those platforms can be called supported for
real PersonalStyle profile data. Do not weaken the Windows boundary to create a lowest-common-
denominator abstraction.

## Version consequence

This decision changes delivery scope and architecture documentation only. It does **not**
change an implemented wire contract, configuration shape, storage schema, profile schema,
prompt contract or Python package behavior.

Therefore no current version bump is required:

- product/core: 0.1.0;
- protocol: 1.0;
- config schema: 1;
- storage schema: 1;
- profile schema: 1;
- prompt contract: 1.

When a Flutter client package exists, it owns a separate client/surface version. A future
protocol or schema change must be versioned when that actual compatibility surface changes.

## Roadmap consequence

Core tasks F03-F06 remain conceptually unchanged. F03 should introduce only the smallest
ModelProvider seam needed to keep Ollama outside core product rules.

Before cross-platform desktop release:

- macOS protected profile handling must be implemented and verified;
- Linux protected profile handling must be implemented and verified;
- the Flutter desktop shell must pass Windows/macOS/Linux acceptance on the declared release
  matrix.

Browser/mobile tasks remain deferred until an explicit owner decision reactivates them.

## Evidence rule

A successful Flutter build is not cross-platform PersonalStyle completion. Each claimed
desktop platform needs current evidence for framework/runtime support, inference availability,
secure profile handling, installation/build behavior and required product workflows.
