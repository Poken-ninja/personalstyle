# ADR-002: One engine, versioned multi-surface clients

## Status

Accepted architecture direction. Not yet implemented or runtime-verified.

## Decision

PersonalStyle will have one authoritative product engine and multiple thin user surfaces.

Target surfaces:
- terminal / CLI;
- browser extension **as the current reversible interpretation of "extension"**;
- desktop application;
- iOS application;
- Android application.

If "extension" later means VS Code or another host, that surface must use the same engine protocol rather than duplicating product logic.

## Engine boundary

The PersonalStyle engine owns:
- input and context validation;
- retrieval and Writing DNA;
- generation orchestration;
- verification;
- feedback classification;
- preference promotion;
- persistence;
- run state;
- budgets;
- version/schema migration policy.

Surface clients own:
- presentation;
- local UX state;
- platform permissions;
- transport to the engine;
- platform-specific lifecycle/error handling.

Surface clients must not implement independent personalization rules or write the engine database directly.

## Protocol boundary

All non-embedded clients communicate through a versioned PersonalStyle protocol.

Every connection/request must make available:
- client/surface version;
- protocol version;
- requested capability;
- engine version/capabilities in the response or handshake.

Compatibility rule:
- protocol MAJOR change may break compatibility;
- protocol MINOR change must be additive/backward-compatible within that major;
- PATCH changes must not change the contract;
- compatibility is determined by protocol/capability, not simply by client age.

An older client may continue to work while it remains compatible with the engine's protocol major and required capabilities. Major-version mismatch must fail explicitly rather than corrupt state or silently degrade behavior.

## Storage boundary

Only the engine instance for a profile may write the canonical personalization store.

Clients never bypass the engine to write SQLite.

Schema versions are explicit and migrations are ordered.

Before a destructive or irreversible migration:
- establish a backup/checkpoint;
- confirm the migration path is supported;
- prevent concurrent old/new-schema writers;
- verify the migrated store before normal writes resume.

Unsupported downgrade must fail explicitly.

## Inference providers

Inference is behind a provider boundary.

Initial desktop/terminal provider:
- Ollama.

Current Ollama desktop support does not provide a native iOS/Android local runtime. Therefore standalone mobile inference is not considered solved by the desktop provider.

Mobile has two allowable architecture paths:

1. **Companion mode**
   - iOS/Android client connects to the user's PersonalStyle engine on another trusted device;
   - connection requires explicit pairing/authentication;
   - no public unauthenticated local API.

2. **Standalone mobile mode**
   - uses a mobile-supported on-device inference provider implementing the same engine/provider contract;
   - provider and minimum OS/hardware support must be selected and verified before that task activates.

Cloud inference is not implied by this ADR. Adding it requires an explicit owner decision because it changes the local-first/privacy boundary.

## OS compatibility

Do not promise "all old versions."

A platform/OS version is **supported** only when:
- the chosen client framework supports it;
- all required plugins/runtime/provider components support it;
- CI or release verification covers it.

Anything older may be best-effort or unsupported, but must not be labeled supported without evidence.

Minimum supported OS versions are release-time compatibility data and may change as dependencies change.

## Completion

A surface is complete only when it:
- performs the required PersonalStyle workflow through the authoritative engine/protocol;
- passes its platform acceptance tests on the declared supported version matrix;
- handles incompatible protocol, engine unavailable, migration-needed, and permission-denied states explicitly;
- does not duplicate protected engine logic;
- records its client/protocol version in relevant telemetry/handoff evidence.

"Builds on one machine" is not cross-platform completion.

## Failure

Multi-surface architecture failure includes:
- clients produce different personalization behavior from duplicated rules;
- old/new clients corrupt shared state;
- incompatible versions connect without an explicit failure;
- two schema versions write concurrently to the same profile store;
- a surface bypasses harness budgets or verification;
- a mobile client assumes unavailable Ollama-local behavior;
- compatibility is claimed for an OS/version that is not verified.

## Merge-conflict consequence

Shared behavior belongs in the engine/protocol, not copied into each client. This reduces the highest-risk semantic merge conflicts.

Changes to protocol, schemas, migrations, or shared product rules must be serialized or coordinated through explicit ownership and compatibility verification.
