# PersonalStyle desktop foundation

Windows development client **0.1.0+1**, speaking engine protocol **1.0**. This is Phase A
of [S03-WIN-ALPHA](../docs/S03_WIN_ALPHA_TASK.md), not a packaged desktop release.

From this directory, with Flutter/Windows C++ tooling and the repository Python development
environment already installed:

```powershell
flutter pub get
flutter run -d windows
```

Development defaults resolve `../.venv/Scripts/python.exe` and `../personalstyle.toml`
relative to the launch working directory. For a built executable or another working
directory, supply explicit owner-controlled paths at build/run time:

```powershell
flutter build windows --dart-define=ENGINE_PYTHON=C:/path/personalstyle/.venv/Scripts/python.exe --dart-define=ENGINE_CONFIG=C:/path/personalstyle/personalstyle.toml
```

These are engine launch inputs, not SQLite access granted to the client. Packaging and
model setup are later phases. Actual writing workflows require the existing protected
Windows profile and configured model to be ready; this client does not create permissions,
migrate the store, select a model or download one. Product behavior remains Python-owned.

The app owns one foreground engine process. A fresh secure 32-byte session credential is
sent only through stdin; HTTP calls use a Bearer header to the reported `127.0.0.1` endpoint.
Closing waits for owned-tree termination, including Windows venv launcher children.
Engine exit clears the session and current result. No credentials/writing are logged.

Rewrite, verified-result display, accept/edit feedback and authorized examples delegate to
P01. The adapter also exposes `preference.evaluate`; there is no client promotion policy.
Learning authorization defaults off. Mutation buttons do not retry automatically. An
uncertain submission can be confirmed explicitly with its original UUID and frozen payload.
`local_user` provenance means the local user's explicit action/ownership declaration,
not a new account or identity-verification system.

Transport bounds: P01's 73,728-byte request envelope, 1,024-byte readiness line, 60-second
startup readiness, 1 MiB response buffering, 10-second connection/shutdown waits and a
600-second outer HTTP wait. The latter allows the existing engine's 120-second preparation,
remaining bounded model calls and local work; it changes no engine generation/call budget.
Redirects/proxies are disabled. Fixed sanitized failures replace arbitrary wire exceptions.
The response buffer accommodates two bounded candidates and version/history metadata;
it is a transport safety ceiling, never a profile quota.

Verification:

```powershell
flutter analyze
flutter test
flutter build windows
dart run tool/engine_acceptance.dart C:/path/personalstyle/.venv/Scripts/python.exe C:/path/personalstyle/personalstyle.toml
```

The last command uses the actual client session adapter and real P01 child process, checks
authenticated handshake/capabilities, then verifies shutdown and endpoint closure.
It invokes no model and performs no profile mutation. Tests fake wire responses only.
