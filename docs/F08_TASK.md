# F08 — Document import/export

```text
TASK: F08
STATE: blocked — Phase A acceptance INCOMPLETE; native export/read-back unverified and the historical owner-store save failure remains unreproduced
BRANCH: task/f08-document-import-export
BASE / MERGE_BASE: 4c5e9d26d57c05c9fa2e7ae8021fd7c78870f06a
F07: merged by PR #13 at 4c5e9d26d57c05c9fa2e7ae8021fd7c78870f06a
WIP: 1
IMPLEMENTATION: Phase A primary pass and one bounded UI diagnostics repair used; Phases B/C not started
IMPLEMENTATION_ATTEMPT: 2/2 — owner-authorized safe error/pending-mutation diagnostics repair
DIAGNOSIS: 0/2
RECOVERY: 0/1
REPAIR RULE: at most two materially different repairs per classified failure;
             no identical retries; after repeated failure, stop and diagnose
```

## Entry assessment

Verified local `main == origin/main == 4c5e9d26d57c05c9fa2e7ae8021fd7c78870f06a`;
PR #13 is merged. The worktree was clean and there was one worktree. PR #14 is open,
draft, documentation-only, based on this same main, and changes `README.md`, `AGENTS.md`,
`ARCHITECTURE.md`, `EXECUTION_CONTRACT.md`, and ADR-004. Its branch will not be modified or
merged here. This task therefore avoids those shared documents; their stale F07-pending-CI
status must be reconciled in a later authorized documentation change.

The F07 implementation is in `src/personalstyle/document.py`; it exposes bounded
`rewrite_document`, `inspect_document`, deterministic segmentation, and durable schema-3
checkpoints. P01 currently exposes short-text rewrite and canonical example/feedback/preference
operations, but no document import/export or F07 document operation. Flutter Phase A has no
file-selection plugin and only a short-text rewrite path. F08 may add the thinnest protocol
adapter that delegates to those existing engine functions; it may not copy their behavior.
The existing P01 request body ceiling is 73,728 bytes, derived for short-text envelopes.
F08 document-content operations need a separate 512 KiB ceiling: sixfold escaping of a 64 KiB
UTF-8 string plus bounded request metadata. Only `document.export` and `document.rewrite`
may use this larger envelope; all other operations retain the 73,728-byte ceiling. The
server's pre-read cap is bounded at that document ceiling and rechecks the capability-specific
limit after parsing. This was the compatibility basis for the actual protocol minor change.

Current declarations: product `0.1.0`, protocol `1.1` (additive F08 capabilities), config schema `1`, storage schema `3`,
profile schema `1`, prompt contract `1`, Flutter client `0.1.0+1`, model `ollama / qwen3:8b`.
No database state is required by file import/export beyond F07's existing document
checkpoints. Do not create F08 tables or bump storage/profile/config versions without a
demonstrated compatibility requirement. Assess any protocol minor-version change against
the additive same-major contract before changing it; keep engine/config/client declarations
coherent and test old-client behavior if a change is required.

## Objective and ownership

Support the authorized formats through the authoritative Python engine and the thin Flutter
desktop client:

| Phase | Import | Export |
|---|---|---|
| A — active | `.txt`, `.md` | `.txt`, `.md` |
| B | `.docx` | `.docx` |
| C | text-based `.pdf` | `.pdf` |

Flutter owns native file selection, cancellation, user confirmation, and display. It must not
read/parse/convert document contents or implement file/resource/security policy. The engine
owns extension and content validation, decoding/parsing, normalization, limits, conversion,
error codes, safe local file access, and output atomicity. No format handler calls an external
service or sends document content to a model/provider. F07 rewrite calls remain explicit and
delegate to `document.rewrite_document`; F07 checkpoint, retry, verification, and resume rules
remain authoritative.

Preserve UTF-8 text and paragraph/line boundaries where the format supports them. For DOCX/PDF,
preserve supported paragraphs, headings, and lists as feasible; state formatting losses such
as fonts, page layout, images, tables, columns, annotations, and embedded media rather than
claiming round-trip fidelity. Text-based PDF is extraction only; reject scanned/image-only
documents and encrypted PDFs. OCR is out of scope.

## Declared write set

Expected bounded implementation scope:

```text
docs/F08_TASK.md
src/personalstyle/documents.py          engine-owned format/file boundary
src/personalstyle/protocol.py           minimal authenticated operation adapters
src/personalstyle/cli.py                only if needed for deterministic engine acceptance
desktop/pubspec.yaml + pubspec.lock     native file-selection dependency if justified
desktop/lib/engine.dart                protocol calls only
desktop/lib/main.dart                  thin selection/status/display flow
desktop/test/                           picker/cancel/wire/UI tests
tests/test_documents.py                engine parsers/export/atomicity/resource tests
tests/test_protocol.py                 only affected P01 adapter tests
pyproject.toml                          only reviewed DOCX/PDF runtime dependencies
```

Do not modify `README.md`, `AGENTS.md`, `ARCHITECTURE.md`, `EXECUTION_CONTRACT.md`, or
ADR-004 while PR #14 changes those files. Do not edit PR #14's branch. Do not touch Figma.
Do not modify F07 segmentation, verification, retry, storage, or migration behavior except a
specific F08 integration defect, with targeted regression evidence and this task's repair
budget. No frontend styling redesign: UI designs are separate.

## Dependency/licensing and packaging review

Phase A candidate: Flutter `file_selector`, published by `flutter.dev`, BSD-3-Clause; its
documented Windows support starts at Windows 10 and the native open/save APIs return a path
or `null` on cancellation. The task will pin a compatible resolved version in `pubspec.lock`.
No Python dependency is needed for plain UTF-8 text/Markdown.

Phase B candidates are `python-docx` (MIT; uses `lxml`) and Phase C candidates are `pypdf`
(BSD-3-Clause, pure Python) plus ReportLab (BSD) for PDF creation. These are review candidates,
not yet accepted dependencies. Before adding them, verify exact supported Python 3.14/Windows
wheel/install behavior, transitive licenses, package size and runtime cost. Unicode PDF export
requires an embedded font: review the chosen font's redistribution license and weight before
including any asset. Exclude PyMuPDF while only its AGPL/commercial licensing path is under
consideration. No native parser, OCR runtime, or network service is authorized.

References reviewed: [file_selector license and platform metadata](https://pub.dev/packages/file_selector/license),
[file_selector native dialog API](https://pub.dev/documentation/file_selector/latest/file_selector/openFile.html),
[python-docx project metadata](https://github.com/python-openxml/python-docx/blob/master/pyproject.toml),
[pypdf license](https://github.com/py-pdf/pypdf/blob/main/LICENSE),
[ReportLab license FAQ](https://docs.reportlab.com/developerfaqs/), and
[ReportLab Unicode TrueType font support](https://docs.reportlab.com/reportlab/userguide/ch3_fonts/).
Dependency decisions and exact versions/checksums belong in the phase handoff after runtime
and packaging checks, not as speculative pins now.

## Phases and acceptance

### Phase A — `.txt` / `.md` vertical slice

Implement engine-owned strict UTF-8/BOM-aware read and UTF-8 output for `.txt` and `.md`, a
minimal authenticated P01 adapter, and native Flutter open/save dialogs. The engine rechecks
the actual suffix/content and a declared bounded byte limit even when the dialog filters it.
Cancellation performs no engine call or write. Import produces plain text without Markdown
rendering. Export preserves the submitted text and paragraph boundaries. Use safe same-directory
temporary output and atomic replacement; failures leave an existing destination intact and
remove partial temporary output. Reject traversal/non-absolute paths, non-regular files,
symlinks/reparse points and explicit remote/UNC destinations where applicable. Do not log
paths, file contents, prompts, outputs, or credentials.

Phase A tests must cover valid UTF-8/BOM, Unicode, line/paragraph boundaries, empty input,
invalid UTF-8, NUL/binary input, wrong/unsupported extension, input/output limits, selected
path validation, cancellation/no call, atomic failure preserving the previous output,
sanitized engine errors, Flutter request delegation, and no partial files. A bounded local
acceptance imports a synthetic `.txt` and `.md`, passes the result through the engine workflow,
exports both formats, and reads them back exactly. Include long-document integration with the
existing F07 API and prove multiple segment calls/checkpoint reuse; do not substitute the
short-text `rewrite` endpoint for F07 documents.

### Phase B — `.docx`

Only after Phase A targeted acceptance passes, add the smallest reviewed parser/writer.
Freeze before implementation: compressed input cap, aggregate uncompressed ZIP cap, member
count cap, extraction/output text cap, and parser time bound, with rationale tied to the
existing F07 64 KiB text/5,000-word limits and measured representative fixtures. Reject
malformed, encrypted/unsupported, oversized, traversal-entry, duplicate/unsafe, and resource-
exhausting archives before returning partial text. Preserve paragraph order and supported
heading/list markers. Export accepted document text to DOCX with paragraph boundaries; document
known formatting losses. Add real temporary `.docx` read/write acceptance and fresh-open
round-trip verification. No macro execution or embedded file extraction.

### Phase C — text-based `.pdf`

Only after Phase B targeted acceptance passes, add the smallest reviewed text extractor and
PDF writer. Freeze input bytes, page count, extracted UTF-8 text, output size and per-operation
time limits before coding. Reject encrypted PDFs, malformed PDFs, image-only/scanned PDFs,
unsupported forms and oversized/decompression/resource failures with fixed sanitized codes.
Do not read annotations, attachments, JavaScript or launch actions. Preserve extracted reading
order/paragraph boundaries where available; explain that columns/layout/fonts/images may not
round-trip. PDF export must embed a reviewed Unicode-capable font and produce readable output.
Add real synthetic PDF import/export acceptance; no OCR.

## Security, data and output invariants

- All traffic remains authenticated P01 loopback. No request URL credentials, redirects,
  proxy use, LAN mode, cloud call, or implicit document upload to a model.
- Accept only user-selected local file paths sent through the authenticated protocol; engine
  validates the path, actual format, file type and resource bounds before reading/writing.
- File operations do not mutate canonical profile state. F07 document checkpoints remain the
  only durable state used for long-document rewrite/resume.
- Use deterministic fixed failure codes. Do not return stack traces, file contents, raw paths,
  prompts or exception details. No raw document content in ordinary logs.
- Export must be derived from explicit UI-selected content/result; no automatic export or
  silent overwrite. Native save-dialog cancellation is a no-op. Atomic output failure must not
  leave a partial destination.
- No path traversal, symlink/reparse redirection, unsafe temporary path, unbounded parser work,
  or partial-success text after an error.

## Required acceptance across phases

F08-AC1: `.txt` and `.md` import/export work end-to-end through Flutter → authenticated P01 →
engine, with strict UTF-8 and exact text/paragraph boundary tests.

F08-AC2: `.docx` import/export works through the same engine boundary after license, packaging,
resource-cap and formatting-loss reviews.

F08-AC3: text-based `.pdf` import/export works through the same boundary after license, font,
packaging, encrypted/malformed/scan and resource-limit reviews.

F08-AC4: malformed, empty, wrong-extension, unsupported/encrypted, oversized and Unicode cases
produce deterministic outcomes without silent truncation or partial document success.

F08-AC5: paragraph structure, order and required facts survive applicable format conversion;
formatting limitations are documented and tested.

F08-AC6: invalid paths, traversal, symlink/reparse targets and export failures cannot cause
unsafe writes; atomic failure preserves any prior destination and leaves no partial output.

F08-AC7: UI cancellation is a no-op; import/export errors are useful and sanitized; Flutter
contains no parser, conversion, F07 logic, direct SQLite access or canonical writer.

F08-AC8: long imported documents use the F07 bounded multi-segment path; checkpoint, verification,
retry budget and resume behavior remain unchanged and are covered by targeted integration tests.

F08-AC9: no network transmission or raw document/credential/path logging occurs in normal use.

F08-AC10: targeted phase tests, affected F03/F04/F07/P01 regressions, final Python and Flutter
checks, required real-format acceptance, and exact-head CI pass before F08 is called complete.

F08 completion is not Windows alpha completion. Do not implement S03 Phase B, V01–V04, R01,
Figma designs, OCR, cloud, macOS/Linux acceptance or import of additional formats.

## Verification and failure control

During each phase, run only its targeted engine/Flutter tests plus directly affected regressions.
Do not repeat the full suite or real-provider runs after unrelated edits. At final completion run
one complete Python regression, one Flutter analyze/test/build gate, required static checks,
real supported-format acceptance, and required exact-head CI. A real F07 live model acceptance
is not repeated unless a demonstrated F08 defect changes the F07 execution path enough to
invalidate prior evidence; deterministic provider fixtures are the default.

Classify failures before repair: `DOCUMENT_FORMAT_UNSUPPORTED`, `DOCUMENT_EXTENSION_MISMATCH`,
`DOCUMENT_EMPTY`, `DOCUMENT_MALFORMED`, `DOCUMENT_ENCRYPTED`, `DOCUMENT_RESOURCE_LIMIT`,
`DOCUMENT_PATH_INVALID`, `DOCUMENT_IMPORT_FAILED`, `DOCUMENT_EXPORT_FAILED`,
`DOCUMENT_NOT_VERIFIED`, and `STORAGE_BOUNDARY_INVALID` where applicable. Two materially
different repairs are the maximum for one classified failure; no identical retry. After the
second failure, stop for diagnosis. Diagnosis budget is two cycles total; recovery is one
environment-only action. A failed phase blocks later phases while preserving already verified
work and all evidence.

Pre-implementation environment evidence: Python 3.14.6; `pip check` passed. Flutter 3.47.6
stable, Dart 3.13.5, Windows x64. Sandboxed Flutter/Dart invocation stalled, while the
installed SDK version commands completed under elevated execution; no SDK or machine-wide
dependency was changed. Current Phase A state is blocked by Windows plugin symlink support. F07 evidence is in its historical
task; its stale `draft PR pending CI` status is deferred because PR #14 edits the shared status
documents.

## Phase A checkpoint — 2026-10-08

Implemented the engine-owned `.txt`/`.md` UTF-8 boundary, authenticated protocol 1.1
operations, same-directory atomic export, and a thin Flutter native picker/delegation path.
The F07 route calls the existing `rewrite_document` API and selects the configured Ollama
provider when no test/provider override is supplied. The Flutter timeout for
`document.rewrite` is 1,800 seconds, matching the existing F07 document deadline; all other
client calls retain 600 seconds. No F07 segment, verification, retry, migration, or storage
behavior changed. No parser or file I/O was added to Dart. Protocol 1.0 remains same-major
compatible, while the new document capabilities are advertised under additive protocol 1.1.

Current local evidence:

- Python 3.14.6; `pip check`: passed.
- `.venv/Scripts/python.exe -m pytest --basetemp .pytest-f08-final tests/test_documents.py
  tests/test_protocol.py -q --tb=short`: 53 passed in 98.61 seconds on the final protocol
  adapter. This includes both formats through the authenticated P01 handler, bounds/error
  cases, and pre-dispatch security regressions.
- `tests/test_protocol.py::test_import_to_f07_rewrite_export_and_restart_reuses_checkpoints`:
  final expanded acceptance passed in 167.93 seconds: about 2,080 synthetic words, 20 F07
  segments, configured-provider adapter represented by a deterministic Ollama/qwen3:8b
  fixture, whole-document verification, export, and new engine-session inspection plus full
  checkpoint reuse. The fixture asserts more than five model calls and the verified result.
  This is not a real Ollama inference acceptance.
- A preceding combined targeted run reported 101 passed and one test-fixture failure. The
  fixture first created the SQLite file before invoking the exclusive private-file helper; it
  was corrected to prepare the private file first. A two-segment smoke version passed in 33.90
  seconds. The first 20-paragraph run exceeded the test helper's 60-second socket timeout; it
  was rerun with a socket ceiling matching F07's existing 1,800-second document deadline and
  passed in 167.93 seconds. Flutter's `document.rewrite` wait was aligned to that existing
  deadline. Neither change modifies F07's engine budget.
- `flutter analyze --no-pub`: passed with no issues after correcting a Dart getter syntax error.
- `flutter test --no-pub test/ui_test.dart test/engine_test.dart`: 25 passed. Covers import and
  export cancellation no-ops, exact protocol delegation, verified document rendering, and
  existing lifecycle/security UI tests.
- Targeted Ruff: passed. `mypy src`: passed. `pip check`: passed. `git diff --check`: passed.
- Python tests initially could not create `%TEMP%\\pytest-of-mamid` due an existing
  `PermissionError`; rerunning with a fresh workspace `--basetemp` succeeded without changing
  protected profile-store ACLs.

Environment blocker:

- `flutter pub get` resolved and locked `file_selector 1.1.0` and its platform packages, then
  exited nonzero with: `Building with plugins requires symlink support. Please enable
  Developer Mode in your system settings.`
- `flutter build windows --no-pub` stopped with the same message. No Developer Mode/system
  setting or machine-wide dependency was changed. The lockfile records resolved package
  versions and checksums; the direct package and Windows implementation licenses are
  BSD-3-Clause.
- Native picker/build acceptance is therefore not yet evidenced. Phase A remains blocked;
  Phases B (`.docx`) and C (text PDF) have not started. No draft PR has been opened. Shared
  status documents remain untouched because PR #14 is editing them.

## Resume checkpoint — 2026-10-08

Owner reports Windows Developer Mode was enabled. Actual symlink capability remains
unverified/unavailable to this execution environment: a disposable workspace-local symbolic
link creation probe failed twice with `NewItemSymbolicLinkElevationRequired` / `Administrator
privilege required`, once in the normal sandbox and once in an elevated execution attempt.
No SDK, machine policy, or repository files other than this checkpoint were changed. The
disposable probe directory was not left behind. Since the same host capability failure
persisted under the elevated attempt, no Flutter plugin/build retry was made.

Phase A remains blocked before native plugin generation. Existing Python, Flutter analysis,
Flutter widget-test, and static-check evidence above remains valid for the unchanged code.
Windows build and native file-picker/engine acceptance remain unverified. Implementation
attempts and prior counters are unchanged. Phases B/C remain unstarted; PR #14 is untouched.

Next permitted action: provide an execution environment that can create workspace symlinks
(or correct the host's symlink privilege configuration), then verify with the same disposable
probe before retrying Flutter plugin setup/build. Do not repeat the Flutter build while the
probe fails, and do not begin Phases B/C until Phase A passes.

## Resume checkpoint — 2026-10-08 (Developer Mode recheck)

The owner-provided `cmd /c mklink /D` check was reproduced successfully in a fresh
workspace-local probe, confirming symlink creation is available through the Windows command
path. The temporary probe was removed; the owner's `.f08-manual-symlink-test/` directory was
left untouched. Flutter tool commands themselves stalled without output in sandboxed runs;
the elevated package setup completed successfully:

- `flutter pub get`: passed; resolved `file_selector 1.1.0` and generated Windows plugin
  registration (`file_selector_windows`); lockfile includes package checksums.
- `flutter analyze --no-pub`: passed, no issues.
- `flutter test --no-pub test/ui_test.dart test/engine_test.dart`: 25 passed.
- `flutter build windows --no-pub`: passed; produced
  `desktop/build/windows/x64/runner/Release/personalstyle_desktop.exe`.
- Real Windows client/P01 acceptance: passed in 2.742s; client `0.1.0+1`, Dart `3.13.5`,
  Windows 11 Home build 26100, engine protocol `1.1`, bind `127.0.0.1`, authenticated
  handshake advertised `handshake`, `rewrite`, `example.write`, `feedback.write`,
  `preference.evaluate`, `document.import`, `document.export`, `document.rewrite`, and
  `document.inspect`; owned engine exited and endpoint closed; zero profile mutations and
  zero model calls.

Native picker acceptance is still **not evidenced**. A fresh built app reached `READY`, but
this execution session could not focus/control the Flutter window (`SetForegroundWindow`
returned false; UI Automation exposed only the Flutter pane), so no dialog selection or
cancel result is claimed. The app process launched for this check was closed; temporary
screenshots were removed. No import/export operation was performed through the UI. Therefore
Phase A remains blocked, not passing, despite the successful plugin setup, build, unit tests,
and authenticated engine acceptance. Phases B/C remain unstarted, PR #14 remains untouched,
and task counters remain implementation 1/2, diagnosis 0/2, recovery 0/1.

Next permitted action: obtain direct interactive control of the Windows app and complete a
synthetic native picker selection/cancellation check through the UI, then verify the resulting
authenticated engine operation and safe output. Do not claim Phase A complete or begin Phases
B/C until that evidence is recorded.
## Visible error diagnosis checkpoint — 2026-10-08

Observed report: the built development client showed `OPERATION_FAILED` and the sanitized
message `The request is invalid or too large. Check your input.` No document text, request
payload, credential, or profile data was available from the owner session, so the exact
triggering action cannot be attributed from that screenshot alone.

Code-path reconstruction:

- Startup is `WritingScreen.initState -> start -> EngineSession.start -> readiness stdin /
  READY -> authenticated ProtocolClient.handshake`. Success sets `READY`. Startup failures
  map to `ENGINE_UNAVAILABLE` or `PROTOCOL_INCOMPATIBLE`; startup does not call `operate()` and
  cannot set `OPERATION_FAILED` in the current source.
- `OPERATION_FAILED` is set by `operate()` after a button-triggered rewrite, document import,
  document export, feedback, or example operation throws.
- The reported text is `messageFor(EngineFailure.invalidRequest)`. The client produces that
  failure for a locally oversized request, or maps wire `REQUEST_MALFORMED` / `REQUEST_RESOURCE_LIMIT`
  to it.
- A Rewrite action with the untouched/empty form deterministically reaches the engine's
  `RewriteRequest.validate` checks (non-empty original/intent and explicit valid context), is
  rejected before provider/storage dispatch as `REQUEST_MALFORMED`, and is rendered as the
  reported `OPERATION_FAILED` message. The Rewrite button is currently enabled in READY even
  when these required fields are empty. That is an existing UI validation gap; no evidence
  establishes that this was the owner's actual triggering request.
- Protocol 1.1 is coherent across config, client and engine; the real Windows handshake passed
  and advertised the document capabilities. This rules out a protocol negotiation failure in
  the acceptance run, but does not prove which action caused the owner's screen.

Smallest deterministic regression evidence: 28 passed across the existing P01 pre-dispatch
rejection and generation validation tests, including malformed request rejection before any
provider call. No production or test source was modified during this diagnosis. The observed
message therefore matches existing application request-validation behavior and is not, by
itself, evidence of a new F08 regression or an environment failure. Exact attribution remains
unknown until the action immediately preceding the screen is known. If it appeared before any
button interaction, that contradicts the current startup path and warrants checking which
binary/process was launched.

Separate future requirement: reconcile the desktop presentation with the newer Figma designs
in a dedicated UX task. This is not F08 authorization; no redesign, voice onboarding, or rubric
UI was implemented here.

F08 remains blocked on owner-confirmed native picker selection/cancellation and associated
manual UI acceptance. Next manual action: relaunch the current built executable, record whether
this error is present before interaction, then press **Open .txt or .md document** and confirm
native-dialog cancellation or selection with a synthetic local file. Do not include document
contents or credentials in the report. No task budget changed; PR #14 remains untouched.
## Phase A acceptance audit — owner evidence, 2026-10-14

**Owner-observed native UI evidence (not automated test evidence):**

- The Windows native file picker opened.
- The owner selected the synthetic TXT fixture; import succeeded and the app displayed
  `Document imported.`
- Both expected paragraphs appeared in their original order, and the engine displayed `READY`.
- Reopening the native picker and cancelling succeeded; imported content remained unchanged.
- Reopening and selecting/importing the synthetic document again succeeded without a visible error.

No writing content, paths, or credentials are copied into this handoff.

**Phase A criterion audit:**

- Engine-owned `.txt`/`.md` strict UTF-8/BOM import, Unicode/paragraph preservation, empty,
  malformed, unsupported/wrong extension, size limits and path/reparse checks: covered by
  `tests/test_documents.py` (16 passing in the earlier recorded run).
- Engine export exact UTF-8 output, same-directory temporary file + atomic replacement,
  previous-target preservation on injected failure, temp cleanup, output/resource/path checks:
  covered by `tests/test_documents.py`.
- Authenticated P01 `.txt` and `.md` import/export, exact read-back, path rejection and no raw
  content/path/credential logs: covered by the parameterized
  `test_document_text_operations_use_authenticated_engine_and_atomic_output`.
- Long `.md` import → F07 multi-segment rewrite/verification → export → process-session restart
  and checkpoint reuse: deterministic synthetic provider integration passed; this does not
  exercise the native save dialog or real-model quality.
- Flutter UI delegation and import/export picker cancellation no-op: covered with wire/picker
  fakes by the 25 passing Flutter tests. Owner additionally observed native **open** picker
  selection and cancellation, including authenticated UI import.
- Windows plugin resolution, analyzer, Flutter tests and Windows build: passed on the resolved
  `file_selector` plugin state. Real child-process authenticated protocol 1.1 handshake and
  clean shutdown: passed on loopback.
- **Still unverified:** the native **save** dialog through Flutter, successful export from a
  verified UI result through Flutter → authenticated P01 → engine, and read-back of that UI
  export. Engine/protocol atomic-write tests are not substitutes for this native UI path.

**Smallest additional acceptance:** in the current Windows app, use the synthetic imported
TXT, provide the required explicit intent/context and complete a verified document rewrite;
then select **Export verified document**, save to a new synthetic `.txt` path through the native
save dialog, and confirm the saved UTF-8 file matches the displayed verified output and
paragraph order. Also cancel the save dialog once and confirm no export request/output occurs.
This is owner-observed UI evidence; do not capture source prose in logs or handoff. Once this
passes, no product-code changes are currently indicated. Then run only checks invalidated by
any changes, inspect the final diff for accidental files/content, and proceed with the
previously authorized Phase A commit/push/draft PR workflow. Until then Phase A is not verified.

Figma mismatch remains a separate future UX implementation requirement; voice onboarding,
rubric UI and redesign are outside F08. Phases B/C remain unstarted. PR #14 is untouched.
Counters remain implementation 1/2, diagnosis 0/2, recovery 0/1.

## Final native export preflight — 2026-10-14

The owner-confirmed native TXT import and open-dialog cancellation remain manual evidence as
recorded above. Before requesting the final native export interaction, the configured live
rewrite prerequisites were checked without changing product state:

- The task branch remains `task/f08-document-import-export`; all existing F08 work and counters
  are preserved.
- `personalstyle.toml` selects `ollama / qwen3:8b`. Ollama runtime `0.40.1` is present and
  `/api/tags` reports exact digest
  `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41` for that tag.
- The supplied intent and both constraint strings are accepted by the actual
  `RewriteRequest.validate` parser. P01 protocol `1.1` routes `document.rewrite` to the existing
  authoritative `rewrite_document` function with the configured Ollama provider. Owner-observed
  import already exercised the authenticated UI/client path; no model call was made in this
  preflight.
- Exact-context eligibility could not be established. The configured `data` profile directory
  and database do not exist. The protected `ExampleStore` boundary check failed with
  `SecurityError: Profile directory is unavailable` before any context or example query. No ACL,
  profile directory, database, example, consent, or synthetic profile was created. Therefore no
  exact context is currently valid to recommend, and `document.rewrite` cannot reach a genuine
  verified result in this checkout until the owner initializes the protected profile and makes
  an existing owner-authorized, learning-eligible example available for the exact context.
- The configured local model is installed, but no readiness/preparation or inference operation
  was launched because the protected profile prerequisite failed first.

Classification: `STORAGE_BOUNDARY_INVALID` / missing protected profile directory, not an
Ollama-unavailable or request-parser failure. The smallest safe remedy is for the owner to
explicitly authorize preparation of the profile directory through the existing SEC01 setup path
and provide an authentic owner writing example through the existing authorized example flow for
the chosen exact context. Do not seed synthetic writing or represent it as authentic consent.

Native save dialog, successful app-to-engine export, cancellation/no-output, and saved-file
read-back remain untested because there is no genuine F04-verified UI result to export. Phase A
remains blocked; no model call or manual export was attempted. Next action requires the owner to
decide whether to initialize the protected profile and use an existing/authentic authorized
example. Phases B/C remain unstarted, PR #14 remains untouched, and counters remain
implementation 1/2, diagnosis 0/2, recovery 0/1.

## Selective WIP checkpoint — 2026-10-14

Phase A implementation is checkpointed as incomplete. Runtime path inspection confirms
Flutter starts the engine with `--config ../personalstyle.toml` while its working directory is
`desktop/`. The engine resolves the configuration relative to that working directory, then
resolves `storage.path = data/personalstyle.db` relative to the configuration file's parent.
The effective canonical path is therefore repository-root `data/personalstyle.db`, not
`desktop/data`. Both the effective directory and database were absent on inspection, so the
profile is genuinely uninitialized at the configured location; this is not a desktop-relative
path lookup defect.

The SEC01-approved initializer is the existing explicit CLI operation
`personalstyle --prepare-storage` (from the repository root, using the project environment). It creates
only an empty profile directory and applies/verifies the OS-protected permissions using
`prepare_private_directory`; it creates no SQLite database or example and performs no ACL
bypass. It must be run only after explicit owner authorization. The UI's existing
`example.write` flow can then store an authentic owner-authored sample only after the owner
checks `I own this writing and authorize storing it`; learning eligibility additionally requires
the owner to explicitly check its separate authorization box. The synthetic F08 acceptance TXT
must never be enrolled as a style example.

No profile initialization or consent change was performed. No existing eligible exact context
can currently be confirmed. Native import evidence and all prior test/build evidence remain
preserved; native save/cancel and exported-file read-back remain outstanding. The implementation
and task record are selectively committed as a WIP checkpoint only; Phase A is INCOMPLETE, not
verified. Counters remain implementation 1/2, diagnosis 0/2, recovery 0/1. Phases B/C remain
unstarted and PR #14 remains untouched.

## Sanitized example-write diagnosis and UI correction — 2026-10-15

The configured profile directory passed SEC01 verification; the canonical SQLite file was
absent at inspection. The reported `casual.chat` identifier satisfies the engine's context
syntax. Flutter's `example.write` payload contains a generated UUID, entered sample, selected
context, local-user provenance, `authorizedExample`, `exampleLearning`, and `held_out=false`.
Storage authorization is required to submit; learning authorization is separate and may remain
false. The engine limits example text to 64 KiB and the P01 envelope to its existing bounded
request ceiling. On first valid example, the engine creates/protects the database, initializes
schema 3, inserts atomically, then reads back the record and rechecks the boundary.

Three isolated synthetic tests passed (69.12 seconds): authenticated P01 mutation/idempotency,
SQLite example round-trip, and rollback of initial schema creation. They used a separate
SEC01-protected temporary store and fixture provider; no model was called and no owner data was
read or mutated. These results did not reproduce a storage defect.

The exact historical engine code cannot be recovered: P01's sanitized response includes a
whitelisted `engine_code`, but Flutter reduced engine failures to `EngineFailure.operation`
and discarded that code. The pending UI state retained the mutation capability/payload but not
the error response. Therefore `OPERATION_FAILED` is insufficient evidence to claim a particular
storage or SQLite cause. This is classified as a client diagnostic defect; the original
example-write failure remains unknown.

One bounded F08 implementation repair (attempt 2/2) maps only known engine codes to safe client
categories, displays the safe reference code, names the pending mutation, and explains same-ID
retry semantics. Direct safe engine codes (including validation, source, verification and
document failures) receive an appropriate sanitized classification; arbitrary codes and details
are discarded. A new rewrite/example/feedback mutation cannot replace an uncertain pending
write, import is disabled while one is pending, and a process exit preserves the in-memory
pending status without enabling a retry against a dead session. No automatic retry occurs.
The repair did not replay or alter the owner submission, and it cannot recover the old dropped
engine code, so the original example-write root cause remains unknown.

Verification after the final client changes: `flutter test --no-pub test/engine_test.dart
test/ui_test.dart` passed 29 tests; `flutter analyze --no-pub` passed; `git diff --check`
passed. `flutter build windows --debug --no-pub` built
`desktop/build/windows/x64/runner/Debug/personalstyle_desktop.exe`. The Release build was
attempted but Windows returned `LNK1104` because the owner-launched Release executable was
still running and locked. It was not terminated. The Debug build does not replace the required
Release build/native acceptance evidence. After the owner closed the old Release process, the
current source passed `flutter build windows --release --no-pub`; the owner-facing Debug
session was left running.

The earlier successful Windows Release build, owner-observed native import and cancellation,
and authenticated Python import→F07 rewrite→export/restart fixture remain preserved as their
respective evidence. Native save-dialog cancellation, actual UI export and saved-file read-back
remain unverified. No genuine verified UI result is currently available to export, and no model
call or builder-initiated owner-profile write was made during this diagnostic repair. Phase A remains
INCOMPLETE; no F08 completion commit/PR was created. Phases B/C remain unstarted and PR #14
remains untouched. Attempt 2/2 is consumed; no further F08 implementation repair is available
under this task contract without a new owner decision.

## Owner-observed example-save diagnostic — 2026-10-15

The owner used the updated diagnostic UI for one newly authorized owner-authored example
submission. The UI displayed the sanitized `STORAGE_BOUNDARY_INVALID` reference and warned
that save status was uncertain. The old pending request was not replayed. No writing or consent
values were recorded here.

Read-only inspection of the configured canonical location found the profile directory present
and SEC01-verified, the SQLite database absent, and no journal/WAL/SHM sidecars. Consequently
there are currently no canonical examples available for `casual.chat`. This is consistent with
no example being durably saved in that database, but it does not establish which
`SecurityError` phase failed during the request. The code maps directory/file ACL and path
boundary failures to the same public code; no safe phase-level trace was retained. No profile
content was read by the builder; no reset or permission modification was made, and no model
call was made. The owner submission did not leave a canonical database at the configured path.

Classification: the client now surfaces the engine's safe code, but the underlying protected
storage operation remains **unknown**. Synthetic protected-store/protocol tests passed and did
not reproduce it. F08 remains blocked at the profile prerequisite; do not retry or create more
examples automatically. Any change to example persistence/security diagnostics requires a
separate owner-approved scope because storage/security code is outside this F08 write set.

## Owner-authorized storage-boundary phase trace — 2026-10-15

Exceptional diagnostic counter: `STORAGE_BOUNDARY_PHASE_DIAGNOSTIC: 1/1` (phase-reporting
instrumentation implemented; the controlled owner attempt was pending at this checkpoint). Historical
F08 implementation attempt 2/2 remains exhausted; no counters were reset.

The authorized diagnostic change carries only a fixed security-operation phase from
`SecurityError` to `StoreError`, then to a sanitized P01 `engine_phase` field. Flutter accepts
only the ten phase identifiers declared by the engine and renders fixed explanatory labels.
Arbitrary exception text, paths, OS command output, writing, credentials and SQLite details are
not exposed. The original `STORAGE_BOUNDARY_INVALID` code and all checks, permissions, transaction,
retry and consent behavior are unchanged. This reports where a later failure occurs; it does not
yet establish the original failure's cause.

Targeted verification after instrumentation:
- Python storage, SEC01 security, and sanitized protocol error tests: **62 passed in 91.89s**.
- Flutter engine/UI tests: **29 passed**; the known phase identifier is displayed as a fixed
  label and an untrusted phase string is discarded.
- Ruff on changed Python files: passed.
- mypy `src`: passed (14 source files).
- `flutter analyze --no-pub`: passed.
- `git diff --check`: passed.

No model call, profile initialization, ACL modification, owner-store access, or example replay
was performed during instrumentation verification. At this checkpoint the canonical database
was absent and the controlled attempt had not yet been performed; its subsequent result is
recorded below.

## Controlled storage-phase reproduction — 2026-10-15

The one owner-authorized controlled submission reproduced `STORAGE_BOUNDARY_INVALID` with
the safe phase `path_validation`. No exception details, writing, credential, or path were
returned to Flutter. A read-only component audit found no reparse points in the configured
profile path; the database target remained absent. No SQLite open, profile write, ACL change,
or model call occurred.

Root cause is established in the current desktop launch integration. `EngineSession` passes
the default config string `../personalstyle.toml` while the app's working directory is
`desktop/`. `protocol.main` uses `options.config.absolute()` and joins the configured storage
path to its parent without normalizing the parent traversal. A deterministic reproduction of
that exact expression confirms the resulting profile path still contains `..`. SEC01's
`_check_path` intentionally rejects any such component as `path_validation`; that security
rejection is correct. This is a F08 desktop launch-path defect, not an ACL or SQLite failure.

The smallest repair is for the Flutter launcher to pass an absolute, normalized config path
to the child process (and test that the resolved argument contains no `..`). It requires no
storage/security relaxation, schema change, data reset, or consent change. The diagnostic-only
authorization is exhausted (`STORAGE_BOUNDARY_PHASE_DIAGNOSTIC: 1/1`); no launch-path repair
was made in this diagnostic checkpoint. Do not ask the owner to resubmit the example until a
separately authorized bounded repair is implemented and built. The historical failed example
operation is now explained by the same reproduced launch-path defect; it was not committed to
the configured canonical database.

## Owner-authorized launch-path correction — 2026-10-15

Exceptional correction counter: `LAUNCH_PATH_CORRECTION: 1/1 used`. F08 implementation
attempts remain 2/2; this separate owner-authorized correction does not reset or rewrite them.
Flutter now converts the configured child-process config argument to an absolute normalized
filesystem path before spawning P01. A focused regression test covers the existing
`../personalstyle.toml` launch form and asserts the child argument has no `..` segment. P01's
path validation and SEC01 checks are unchanged. The correction does not initialize storage or
submit/replay an example. Targeted verification and a rebuilt-app acceptance result will be
recorded below before any claim that the issue is resolved.

After the correction, `flutter test --no-pub test/engine_test.dart test/ui_test.dart` passed
**30 tests** and `flutter analyze --no-pub` passed. The pre-fix Release app remains open and
locks the standard Release executable, so the corrected Windows Release build is pending its
normal app close. The controlled failure's `path_validation` phase confirms that request was
rejected before database access; no resubmission is requested. No F08 acceptance completion is
claimed until the corrected app is built and startup/path readiness is confirmed.

The owner closed the pre-fix app. The corrected `flutter build windows --release --no-pub`
then passed, and the corrected Release executable was launched successfully (PID 29960) from
the desktop working directory. No example was resubmitted and no profile operation was run.
At launch checkpoint no profile operation had run; native export/read-back remained
unverified.

The owner subsequently reported an operation error with phase `directory_acl_verify`; the
specific button/action was not stated. Read-only
inspection confirmed the running engine uses the repository-root config, the expected
`data/personalstyle.db` setting, and the same Windows account as the builder. The canonical
directory passed SEC01 verification on a fresh check. The database file and journal/WAL/SHM
sidecars were absent, so the reported operation did not create or mutate the canonical store.
No content was opened. This new phase is after path validation; it does not invalidate the
confirmed `..` launch-path defect or its fix, but it shows the operation still fails before
database creation. The remaining cause (for example, an ACL subprocess failure/timeout versus
a transient verification discrepancy) is not established by the fixed phase code. The
single diagnostic counter is exhausted; no additional retry, permission edit, or speculative
repair is authorized. F08 remains blocked pending a new bounded diagnostic authorization.

## Owner-authorized ACL failure-detail diagnostic — 2026-10-15

Exceptional counter: `ACL_FAILURE_DETAIL_DIAGNOSTIC: 1/1 used`. Historical implementation,
phase-diagnostic and launch-path counters remain unchanged. This bounded diagnostic added
fixed identifiers for ACL verification outcomes (owner, inheritance, rule count, identity,
permissions, process start/timeout, and command failure). Only an exact identifier from the
PowerShell helper is propagated through `StoreError` and the sanitized protocol response;
stderr, arbitrary stdout, exception messages, paths, profile data and credentials remain
excluded. Flutter maps those identifiers to fixed human-readable labels. Storage checks,
ACL policy, database behavior, retries and consent are unchanged.

Synthetic verification: focused ACL-category/storage/protocol tests passed **4/4**; Ruff and
`mypy src` passed; Dart formatter completed. The Flutter test command produced no output and
left no Flutter/Dart process visible; interrupting that stuck command yielded no test result,
so Flutter tests for this detail change are **unverified**. One read-only SEC01 verification
of the configured `data` directory passed. It did not create or inspect the profile database.
No failing ACL state was reproduced, so the historical `directory_acl_verify` report remains
unresolved; no exact ACL mismatch can be claimed. No app operation, model call, profile write,
consent change or permission modification was performed. F08 remains blocked/incomplete.

Next permitted action: validate the Flutter diagnostic change in a separate bounded test run
before relying on its new detail display. Do not ask the owner to resubmit the prior example
or retry a pending mutation.

## Independent Windows ACL metadata inspection — 2026-10-15

To avoid repeating the SEC01 verifier, the configured `data` directory ACL was inspected
directly using read-only Windows security metadata. It is a directory with protected
inheritance, owner matching the current account, and exactly two explicit Allow/FullControl
rules: the current account and LocalSystem. Both rules are non-inherited, use
ContainerInherit+ObjectInherit, and have no propagation flags. This matches the SEC01
directory policy. No account SID, path, file contents, or profile data was recorded.

This independently rules out a persistent mismatch in the directory's current ACL metadata.
It does not recover the historical failure cause or rule out a transient PowerShell verifier
failure at the time of the app operation. The database remains untouched by this inspection.
No permission change or app submission occurred. Do not ask the owner to retry; keep the
historical failure classified as unreproduced/unknown.

After the owner asked for a different diagnostic path, the existing bounded
`scripts/p01_transport_acceptance.py` was run once. It launched a fresh authenticated P01
child using a temporary SEC01-protected store, completed a protocol handshake, submitted one
synthetic `example.write`, repeated the same idempotency key, read the saved synthetic record
back, and stopped the child. Result: **PASSED**; handshake 0.0214s, first write 4.5593s.
The temporary store was isolated from the owner profile and cleaned up. This confirms the
current child-process/auth/storage/example-write path works with a newly prepared protected
store. Together with the current exact ACL metadata, it narrows the historical failure to an
unreproduced condition of the prior owner-store operation/session; it does not prove which
condition caused it. No further owner submission is needed for this diagnosis.

## Owner-authorized specific UI error categories — 2026-10-15

Exceptional counter: `ERROR_DETAIL_UI: 1/1 used`; F08 implementation attempts remain 2/2 and
all earlier diagnostic counters remain preserved. The UI now uses a specific safe status for
protected storage, database, model, verification, request, timeout, resource, and document
failure classes instead of displaying only `OPERATION_FAILED`. It displays a fixed human-readable
ACL detail only when the engine provides one of the allowlisted categories. If the engine does
not provide a recognized detail, the UI does not guess. The engine's current ACL metadata
passes; this change does not claim to explain the earlier failure or make storage succeed.

One concrete UI defect was found and fixed: a response rejected because its verification state
was not `verified` was mapped to generic operation failure. Such responses now use the existing
`verificationRejected` category; malformed result structure remains a generic engine operation
failure. No verification requirement was weakened.

Evidence: focused Flutter engine/UI run reached **22 engine tests passed** and found the above
UI status mismatch; after the narrow correction, `test/ui_test.dart` passed **17/17**.
`flutter analyze --no-pub` passed, and the Windows Release build passed at
`desktop/build/windows/x64/runner/Release/personalstyle_desktop.exe`. The prior focused Python
security/storage/protocol tests passed **4/4**, Ruff passed, `mypy src` passed, and direct
read-only Windows ACL metadata matched SEC01. No full regression, model call, profile write,
consent change or ACL modification was performed. No native UI action was run. The historical
ACL failure remains unreproduced and unknown; Phase A remains incomplete, native export/readback
is still unverified, and Phases B/C remain unstarted.
