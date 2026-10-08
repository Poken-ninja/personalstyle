# S03-WIN-ALPHA - Phase A Windows Flutter foundation

```text
TASK: S03-WIN-ALPHA
SELECTED_SCOPE: Phase A only
STATE: active - overall Windows alpha incomplete
OVERALL_MILESTONE: active selection; not complete
PHASE_A: passing - Windows local acceptance complete; draft PR handoff
BRANCH: task/s03-win-alpha
BASE / MERGE_BASE: b811eb1147afe3e2010d69324eb822ed60a0f12a
DECLARED_WRITE_SET: README.md; EXECUTION_CONTRACT.md; docs/S03_WIN_ALPHA_TASK.md;
  desktop/** only after A1 passes
IMPLEMENTATION_ATTEMPTS_USED: 2/2
DIAGNOSIS_USED: 1/2
RECOVERY_USED: 0/1
CHECKPOINT: analyze/test/Windows build and corrected real P01 lifecycle acceptance PASS
```

## Authority and entry evidence

Owner activates Phase A only. Harness-Engineering stays read-only; Python engine remains
authoritative. Startup found clean main==origin/main at the expected merge. Live GitHub
main matches; PR11 is MERGED with that merge commit. Exact-head CI37732243766 and
merged-main CI37735504435 SUCCESS. PR11 records246 remote tests, owner-authorized local
recovery246 passed447.00s and real authenticated child-process/HTTP acceptance12.02s.
Historical P01 timeout at600s/210 outcomes/two markers and successful recovery remain
preserved in the original task/PR; no historical record is rewritten as passing.

WIP=1: no open PRs, one main worktree at activation. Existing local task branches are
historical; no competing implementation/worktree was active. No existing Flutter pubspec
or client found in this repository. Created this one branch; no separate status-only commit.

## Phase A bounded contract

After A1 passes, create one shared desktop/ Flutter client with Windows support only.
Client owns presentation/session lifecycle, never engine product policy or canonical writes.
Planned separate surface version0.1.0+1; not declared as an existing client before creation.
Core/protocol/config/storage/profile/prompt stay0.1.0/1.0/1/2/1/1.

Scope: Windows readiness -> Flutter shell -> one owned foreground P01 process -> authenticated
handshake -> minimal rewrite/example/feedback UI -> one actual lifecycle acceptance.
Inspect actual python -m personalstyle.protocol --config ... --port 0 startup interface.
Generate a cryptographically secure ephemeral credential in memory; bounded stdin startup
JSON and bounded readiness response; reported host must be127.0.0.1. Authorization header
only, never URL/config/SQLite/log/UI. Invalidate session on exit; stop owned process on close.

One adapter sends protocol/client metadata and requires handshake/rewrite/example.write/
feedback.write/preference.evaluate. Major incompatibility or missing capability fails visibly;
no downgrade, browser/LAN access, automatic mutation retries or additional replay database.
Package original/intent/explicit context/constraints as protocol data. Display accepted verified
results only; accept/edit feedback and authorized examples use existing engine capabilities
and UUID identity mechanisms. No client classification/promotion or model-selection policy.

UI states: STARTING, ENGINE_UNAVAILABLE, PROTOCOL_INCOMPATIBLE, READY, REWRITING, RESULT,
OPERATION_FAILED. Minimal original/intent/context/constraints/rewrite/result/status/accept/
edit-submit/example UI. Useful fixed errors distinguish startup/exit/auth/protocol/capability/
request/operation failure; never expose credentials, stacks, prompts, DB paths or writing logs.

Targeted Flutter tests prove wire envelopes/auth/handshake/negatives/states/verified rendering/
feedback/example requests/sanitization/delegation using bounded fake wire responses only.
Final Phase A gates: flutter analyze; flutter test; flutter build windows; one actual Windows
Flutter/test-harness -> real P01 process -> stdin credential -> authenticated loopback handshake
with required capabilities -> clean shutdown, synthetic data only. No Ollama needed. Record
SDK/Dart/Windows/toolchain/client/protocol/host/capabilities/shutdown without credential.
No Python full regression. Python/P01 targeted checks only if backend behavior changes.

AC-A1 real Windows project builds; A2 real owned P01 process; A3 secure ephemeral startup
credential/no leaks; A4 authenticated1.x loopback handshake; A5 safe unavailable/incompatible
states; A6 thin rewrite/example/feedback delegation; A7 no direct store/product-policy fork;
A8 analyze/test/build pass; A9 actual Windows lifecycle/handshake acceptance passes.
At initial entry all nine were unverified. Passing Phase A leaves overall alpha
active; it does not complete onboarding/installer/desktop V1 or establish macOS/Linux support.

Budgets: primary attempt1, one material corrective attempt2 only after concrete failed
acceptance. Fixture/layout/static corrections recorded separately; counters persist.
Same material failure twice -> bounded diagnosis; no repeat-until-green or self-extension.
No model setup/Phase B, packaging/signing/autoupdate, macOS/Linux/SEC02/03, browser/mobile,
LAN/cloud, alternate provider, direct SQLite, personalization changes, encryption or E01.
After Phase A green: push this branch, one draft PR titled
S03-WIN-ALPHA: Flutter Windows foundation and engine connection. No automatic merge.

## A1 observed blocker

Existing SDK (not on PATH):
C:/Users/mamid/AppData/Local/Temp/Offline-relay-security-flutter/bin/flutter.bat.
Executed flutter --version and flutter doctor -v as host user; no installs/configuration changes.

- Flutter3.47.6, framework5fc346839b; engine692136cb65; Dart3.13.5; DevTools2.60.0.
- SDK reports channel[user-branch]/unknown channel and missing Flutter/Dart PATH entries.
  These warnings are recorded, not silently repaired or treated as release support evidence.
- Windows11, version10.0.26100.7462, Windows desktop windows-x64 detected.
- enable-windows-desktop present; Windows platform check passed.
- Compiler/toolchain: doctor [X] Visual Studio not installed; necessary to develop Windows apps.
  Required prerequisite: supported Visual Studio with Desktop development with C++ workload,
  including its default components. No machine-wide installation authorized/performed.

OBSERVED: Flutter SDK available, but required Windows compiler/toolchain absent.
EXPECTED: Windows desktop tooling ready before Flutter project creation.
FAILURE_CLASS: environment prerequisite missing - WINDOWS_CPP_TOOLCHAIN_MISSING.
EVIDENCE: flutter doctor -v Visual Studio error above; doctor exit0 is not a readiness pass.
NEXT ACTION: owner provisions required toolchain, then explicitly resumes A1 preflight.
BUDGET REMAINING: implementation2, diagnosis2, recovery1; implementation has not started.

Analyze/test/build/real lifecycle acceptance: NOT RUN, because A1 failed.
Client version: not created. Bind/handshake/shutdown: not executed by a Flutter client.
No code/config/schema/test changes, no dependency install, no model calls, no PR yet.

## Owner-requested A1 recheck

Resumed existing task/s03-win-alpha atb811eb1147afe3e2010d69324eb822ed60a0f12a;
live main unchanged, no open PRs, one worktree. Existing README/contract/task changes preserved.
Re-executed existing SDK flutter --version and flutter doctor -v: Flutter3.47.6/Dart3.13.5,
Windows10.0.26100.7462/windows-x64; enable-windows-desktop present. Unknown-channel/PATH
warnings remain observations; SDK/channel/system configuration unchanged.
Doctor still reports Visual Studio not installed. Required remaining prerequisite is
Visual Studio with Desktop development with C++ workload and all default components.
STATE remains blocked - WINDOWS_CPP_TOOLCHAIN_MISSING. No desktop project or feature edit;
implementation0/2, diagnosis0/2, recovery0/1 unchanged. Analyze/test/build/real lifecycle
acceptance not run because A1 failed. No commit/push/PR or Phase B work.
Next permitted action: owner provisions Windows C++ toolchain, then resumes A1 preflight.

## A1 passed on current resume

Existing branch/checkpoint preserved; HEAD/main/origin/main remain b811eb1147afe3e2010d69324eb822ed60a0f12a.
Live GitHub main matches and open PR list is empty. WIP=1.
Rechecked flutter --version / flutter doctor -v: Flutter3.47.6, Dart3.13.5,
Windows11 10.0.26100.7462 x64, Windows desktop enabled. Visual Studio Community2026
18.10.3 (18.10.12224.181), Windows SDK10.0.26100.0 now pass doctor.
Unknown-channel warning remains; PATH points at a different SDK. Use the explicit existing
SDK path above without channel/PATH changes. Actual build remains an acceptance gate.
Prior prerequisite stops consumed no implementation attempts. Attempt1 starts now;
diagnosis0/2, recovery0/1. No backend changes or model calls authorized/needed.

## Attempt 1 checkpoint

Created Windows-only Flutter shell and thin stdin/HTTP session adapter plus core UI.
Targeted run1: 10 wire tests passed; widget compilation failed (AppExitResponse services
import missing; fixture incorrectly awaited void resetPhysicalSize). Classified static/
fixture defects; import/fixture correction changes no protected behavior, counters stay1/2,
0/2,0/1. Expected: both test files compile and targeted acceptance passes.
Next action: rerun targeted Flutter tests after these specific corrections. No Python/model runs.

Targeted run2: same AppExitResponse compilation failure persisted; fixture void-await fixed.
Stopped repetitive repair and consumed non-modifying diagnosis1/2: inspected installed SDK
AppLifecycleListener imports and sky_engine declarations. AppExitResponse is defined in
dart:ui, not exported from services.dart. Correct explicit dart:ui import justified by source.
Static correction only; implementation remains1/2, recovery0/1. No acceptance criteria changed.

Targeted run3: 20 passed; one fixture assertion failed because Dart record equality compares
nested Map identity. Actual serialized fields matched. Corrected verifier to assert capability
and deep payload separately, preserving all expected values. No production behavior repair.

Targeted run4: all21 tests PASS. Real P01 lifecycle/handshake acceptance PASS in3.219s:
engine0.1.0/protocol1.0,127.0.0.1, allfive required capabilities, owned process exited,
endpoint closed/session invalidated; zero model calls/profile mutations. No credential output.

OBSERVED: targeted close-during-launch wire-child check returned READY after stop.
EXPECTED: closing invalidates startup and terminates a late owned child.
FAILURE_CLASS: client lifecycle implementation defect.
EVIDENCE: single bounded wire-fixture test expected EngineException, start emitted null/success.
NEXT ACTION: attempt2 adds startup cancellation guard and serialized owned-process termination;
no protocol/Python/product-policy changes. Recheck targeted lifecycle and UI acceptance.
BUDGET REMAINING: implementation0, diagnosis1, recovery1. Used2/2,1/2,0/1.

Attempt2 targeted gate: all22 tests PASS, including close-during-launch regression.
Initial final analyze: failed on15 brace-style lints and one tool relative-import lint;
no type/behavior failures. Apply only the reported static fixes, rerun affected analyze.
This does not consume another material attempt or weaken lint policy.

## Phase A final local evidence

Base/merge-base/current origin/main: b811eb1147afe3e2010d69324eb822ed60a0f12a (fetched before
handoff; unchanged). No competing open PR. Evidence applies to the commit containing this
record and the unchanged desktop sources; exact head/PR URL recorded in the PR handoff.

Environment: Flutter3.47.6 (5fc346839b), Dart3.13.5; Windows11 Home10.0.26100.7462 x64;
Visual Studio Community2026 18.10.3/18.10.12224.181; Windows SDK10.0.26100.0.
Unknown-channel and different PATH SDK remain recorded, without channel/configuration changes.
Client0.1.0+1 (wire client0.1.0); engine0.1.0/protocol1.0/config1/storage2/profile1/prompt1 unchanged.

| Acceptance | Current executed evidence |
|---|---|
| AC-A1 / A8 | flutter build windows PASS,36.6s build phase; Release/personalstyle_desktop.exe produced |
| AC-A2 / A3 | Real shared Dart session adapter starts Python P01, secure Random.secure32-byte session credential via stdin only; owned-tree shutdown; no credential printed |
| AC-A4 | Real authenticated1.0 handshake on127.0.0.1; allfive required capabilities advertised |
| AC-A5 | Targeted wire/widget negatives: incompatible major, missing capability, engine unavailable/exit, sanitized arbitrary errors |
| AC-A6 | Widget requests prove rewrite, accept/edit feedback and authorized example delegation; verified receipt-only result rendering; no automatic mutation retries |
| AC-A7 | Source/dependency audit: Dart presentation/stdin/HTTP only; no SQLite access, model/provider, DNA, verification, classification or promotion policy; Python/config/tests unchanged |
| AC-A8 | flutter analyze PASS/no issues4.4s after reported static fixes; final flutter test PASS22 tests (~3s reported), including startup cancellation |
| AC-A9 | Corrected real lifecycle acceptance PASS2.673s; owned process exited, endpoint closed and session invalidated; no profile mutation/model calls |

Real acceptance command (from desktop, existing SDK's dart):
dart run tool/engine_acceptance.dart <repository>/.venv/Scripts/python.exe <repository>/personalstyle.toml.
It uses the same EngineSession/ProtocolClient as Flutter, not a Python handler mock.
Result: engine0.1.0,protocol1.0,compatibility=compatible,bind_host=127.0.0.1;
capabilities=handshake,rewrite,example.write,feedback.write,preference.evaluate;
shutdown=owned process exited/endpoint closed/session invalidated. Zero model calls and
profile mutations; stdout contains only this metadata, stderr empty, credential never recorded.
Earlier3.219s live pass is historical pre-repair evidence; repeated only because lifecycle code
changed and invalidated that evidence. Neither run proves live rewriting/model quality.

UI: STARTING/ENGINE_UNAVAILABLE/PROTOCOL_INCOMPATIBLE/READY/REWRITING/RESULT/OPERATION_FAILED;
original/intent/exact context/constraints; generic/personalized accepted result; accept/edit
feedback with per-event learning opt-in; owned authorized example with learning opt-in.
Wire provenance stays intact in the engine receipt; clients pass source run/candidate identity.
preference.evaluate is available through the same adapter; no client-side promotion rule.
Development launch paths/setup limitations documented in desktop/README.md.

Failures retained above: two static import compilation runs, record-map fixture equality,
reproduced close-during-launch lifecycle defect, final analyzer style issues. All relevant
checks rerun after justified correction. No criteria/test assertions weakened.
Material attempts2/2; diagnosis1/2; recovery0/1. No Python regression/model cycles run.
No current local blocker. Overall alpha remains active/incomplete; Phase B, installer,
macOS/Linux, SEC02/03 and all excluded work remain unstarted.
Next permitted action: review this one draft Phase A PR; Phase B requires separate owner activation.
