# P01 - authenticated versioned local engine boundary

```text
TASK: P01
STATE: blocked - LOCAL_REGRESSION_INCOMPLETE
BASE / MERGE_BASE: 0ffd79f305044e739815e26fd97bd1798085c717
BRANCH: task/p01-engine-protocol
ENTRY: main==origin/main at expected merge; tree clean; PR10 merged; no open implementation PR/worktree
DECLARED_WRITE_SET: README.md; EXECUTION_CONTRACT.md; ARCHITECTURE.md; docs/P01_TASK.md;
  src/personalstyle/protocol.py; tests/test_protocol.py; scripts/p01_transport_acceptance.py
ATTEMPTS_USED: 2/2
DIAGNOSIS_USED: 2/2
RECOVERY_USED: 0/1
VERSIONS product/protocol/config/storage/profile/prompt: 0.1.0 /1.0 /1 /2 /1 /1
CHECKPOINT: targeted/static/real transport passed; local full regression incomplete; draft PR/CI next
```

Owner selects P01 only. Standard-library HTTP, fixed127.0.0.1, foreground process;
no LAN/public bind, framework, migrations, UI, OS storage expansion or personalization change.
Startup: python -m personalstyle.protocol --config <owner config> --port 0.
Parent generates secrets.token_urlsafe(32) (256random bits) and supplies one bounded
stdin JSON line {"credential":"..."}. Never command-line/URL/config/SQLite/log material.
Credential lives for the engine session; restart revokes it; no persistent pairing.
Startup stdout exposes only ready host/port/protocol, never credentials or profile paths.

POST /v1, Authorization: Bearer <credential>, application/json, Content-Length required.
Any Origin (even empty), duplicate auth/length headers, transfer/content encoding fail closed.
Every envelope carries protocol_version, client_version (SemVer), client_kind (desktop|cli),
requested_capability and payload. Extra envelope metadata is ignored for additive minor
compatibility; business payloads remain strict. All1.x requests with supported capabilities
are compatible; response explicitly identifies engine1.0 and requested version, never a
silent downgrade. Other majors and unknown capabilities fail before protected behavior.
Handshake returns engine/product/protocol versions, supported capabilities and compatibility.

Capabilities: handshake; rewrite; example.write; feedback.write; preference.evaluate.
Payloads reuse engine input dataclasses; rewrite constraints are a JSON list. Feedback payload
is {run_id, event:<FeedbackInput fields>}. Evaluation payload is {context} only.
No client-supplied database path, SQL, migration, configuration, verified flag or receipt.
Rewrite delegates generate_pair -> verify_pair, preserves full accepted provenance/budgets;
never reports an unverified candidate as success. Feedback uses record_feedback with the
engine's retained live receipt, never a deserialized client success object. Retain only the
latest successful verified pair per session (one slot bounded by existing input/output bounds).
A superseded/restarted source gives SOURCE_RUN_UNAVAILABLE; no mutation. Client rewrite
retries start new runs, never automatic transport/provider retries. Example/feedback UUID
idempotency and explicit preference evaluation remain engine-owned; no replay database/cache.

Body ceiling = existing MAX_REQUEST_BYTES (64KiB+4KiB) +4KiB protocol metadata overhead.
Header/request-line aggregate8KiB; duplicate/nonfinite/deep/invalid JSON rejected.
Absolute ingress deadline and socket I/O deadline reuse harness timeout (currently60s);
preparation/model/attempt/call/context limits are unchanged. One serial engine worker and
one queued connection; no per-item requests/queries, corpus serialization or repeated startup.
Ingress deadline expires before engine invocation; cancelled before legitimate long model work.
Response contains requested results or minimal mutation metadata, never store handles/paths.

Fixed errors: AUTHENTICATION_REQUIRED, AUTHENTICATION_INVALID, PROTOCOL_MAJOR_INCOMPATIBLE,
CAPABILITY_UNSUPPORTED, REQUEST_MALFORMED, REQUEST_RESOURCE_LIMIT, ORIGIN_CALLER_REJECTED,
ENGINE_OPERATION_FAILED; safe engine_code whitelist preserves known engine failures.
No raw writing, prompts, outputs, credentials, exception text or stack traces in normal logs/errors.
Explicit authenticated rewrite result output is inspection, not ordinary diagnostic logging.

Acceptance targeted: real loopback HTTP fixture proves bind/auth/revocation/origin/version/
capability/input/body/header/deadline controls before protected calls, sanitized errors/logs,
unchanged engine budgets, authoritative generation+verification provenance, protected feedback/
example UUID retry behavior, deterministic exact-context evaluation, no SQLite/migration bypass.
Use deterministic providers; no Ollama for serialization. Measure fixed call counts, no N+1.
After targeted green: one full pytest(600s), Ruff, mypy, pip check, one bounded actual child-
process/HTTP synthetic handshake+protected example workflow, then push and exact-head CI once.
CI15minutes remains bounded; no automatic increase. Final handoff records exact revision,
checks, failures, counters, runtime/versions, blockers and next action. No automatic merge.
Attempt1 primary; attempt2 only concrete production correction after failed verification.
Fixture/format repairs recorded without material attempt. Same failure twice -> diagnosis.
No Flutter, SEC02/03, packaging, background service, model setup, cloud or later task.

## Targeted checkpoint

Run1: 24 passed, one fixture timeout (8.41s total).
OBSERVED: protected example operation outlasted test-client5s wait.
EXPECTED: existing Windows ACL subprocess/storage operation gets its existing bounded allowance.
FAILURE_CLASS: verification_defect (fixture transport wait, not engine/server deadline).
EVIDENCE: TimeoutError in test helper getresponse; no production failure reported.
NEXT ACTION: test-client wait60s, consistent with existing operation bound; rerun targeted test.
BUDGET REMAINING: implementation1; diagnosis2; recovery1. Fixture correction consumes none.

Corrected integrated fixture: 1 passed55.55s. Complete targeted run: 25 passed60.64s.
Production adapter delegates to existing engine; five calls per successful fixture rewrite,
four on rejected identical-repair run, no extra transport retries. Three independent feedback
runs activate exact-context preferences; duplicates preserve one example/three feedback rows.
Later generation retains exact preference IDs/versions, example/DNA/model/version provenance.
Rejected rewrite returns only fixed failure metadata, never an unverified successful result.
Adapter review: no SQL/remote calls inside returned-item loops; one session/store object,
one bounded live receipt, no corpus/history serialization. No existing engine/config/tests altered.
Final minor-version/error whitelist completion receives directly affected checks before final suite.

## Final-cycle failure and bounded correction

Directly affected final checks: 2 passed0.31s. Source revision:
3af1f9432ff95a382b168f37226b25812edb7506. Link targets/whitespace passed; base remained0ffd79f.
OBSERVED: sole full local pytest invocation exceeded600s after210 reported outcomes,
including two failure markers; parent terminated pytest before its traceback summary.
EXPECTED: complete configured regression within declared local600s ceiling.
FAILURE_CLASS: environment/runtime verification failure; root cause unresolved, not a pass.
EVIDENCE: subprocess.TimeoutExpired600s; no completed full result. Isolated apparent
failed checks (profile exact-context isolation and protocol Origin rejection) passed2/2 in37.77s.
Diagnosis1: OS memory snapshot16GB total/about2.2GB available, pages/sec0 at snapshot;
no recent sleep/resume event retrieved. A tool timing gap is insufficient to claim suspend
or paging caused the failure. No applications/settings/ACLs changed; no recovery consumed.
NEXT ACTION: preserve failed full run; no automatic timeout increase or full-suite repeat.

Separate ingress review exposed concrete defect: max_words:0 passed pure RewriteRequest
validation and reached dispatch. New targeted test observedHTTP200 instead of400 (0.14s).
FAILURE_CLASS: implementation_defect (recognized constraint syntax validation too late).
Attempt2 reuses existing F04 deterministic_failures before dispatch, no duplicated policy.
One initial sandbox invocation failed before test setup (host temp ACL); rerun as host user
exposed the defect. No host temp/store permissions were modified.
BUDGET REMAINING: implementation0; diagnosis1; recovery1.

Attempt2 targeted acceptance: 26 passed74.99s. Final pip check passed.
Initial static failures: Ruff SIM905 (constant representation), RUF059 (unused fixture token),
BLE001 (broad exception sanitizers); mypy BinaryIO vs BufferedIOBase annotation mismatch.
Representation/fixture/type corrections do not alter product behavior or consume attempt3.
BLE001 repeated after fixed-error rethrow without chaining: stopped repetition, diagnosis2
read installed rule and checked two synthetic snippets (no production writes/engine calls).
Explicit chained fixed-error translation passes; outer boundary alone serializes fixed codes,
never exception text/chain. No lint suppression, logging of exceptions or weakened check.
Only directly affected checks rerun; unchanged pip result retained. Diagnosis exhausted2/2.

## Durable handoff

Corrected source is the final PR head of task/p01-engine-protocol; PR records its full SHA
and exact-head CI run/result. Historical3af1f94 remains the first implementation/full failure
revision. No completed passing local regression is claimed for either revision.

- Targeted acceptance:26 passed74.99s; after annotation/error-routing-only static correction,
  directly affected sanitization/deadline checks2 passed1.31s. Nine targeted invocations total,
  including fixture failure, diagnosis and deliberately red defect test; one full invocation.
- Ruff: initial four findings, then two BLE001 findings; final changed-file check passed.
  Other files passed initial whole-scope check and remain unchanged. No suppressions.
- Mypy: initial two new-file annotations; corrected-file check passed. Other source unchanged.
- Pip check: passed once; no broken requirements.
- One real child-process HTTP acceptance passed12.02s: credential via stdin, authenticated
  handshake, protected synthetic example.write, same-UUID retry, exact read-back, credential
  absent from DB/stdout/stderr, process stopped. No Ollama calls or user profile data.
- Changed-path measurements (observations, not targets): handshake0.0093s; first write5.4645s.
  Adapter has no SQL/per-item remote loops; successful rewrite fixture uses exactly5 model
  calls; failed identical repair4, preserving max8calls/max3attempts/120s preparation/60s generation.
- Python3.14.6; SQLite3.50.4. Product0.1.0/protocol1.0/config1/storage2/profile1/prompt1 unchanged.
- Seven declared files only; no source/config/schema/behavior changes in existing engine modules.

BLOCKER: sole local full regression timed out600s with two unsummarized failure markers.
Isolated apparent failures passed, so root cause remains unresolved; no timeout increase,
suite splitting/skipping, assertion weakening or false pass. Remote CI cannot erase that result.
ATTEMPTS_USED:2/2; DIAGNOSIS_USED:2/2; RECOVERY_USED:0/1.
Next permitted action: owner review of blocked checkpoint and authorize/identify an environment
recovery/verification continuation. No further material repair or diagnosis without extension.
Do not merge or activate Flutter/SEC02/SEC03. Final exact-head CI status belongs to the PR.
