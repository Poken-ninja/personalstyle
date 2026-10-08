# P01 - authenticated versioned local engine boundary

```text
TASK: P01
STATE: active
BASE / MERGE_BASE: 0ffd79f305044e739815e26fd97bd1798085c717
BRANCH: task/p01-engine-protocol
ENTRY: main==origin/main at expected merge; tree clean; PR10 merged; no open implementation PR/worktree
DECLARED_WRITE_SET: README.md; EXECUTION_CONTRACT.md; ARCHITECTURE.md; docs/P01_TASK.md;
  src/personalstyle/protocol.py; tests/test_protocol.py; scripts/p01_transport_acceptance.py
ATTEMPTS_USED: 1/2
DIAGNOSIS_USED: 0/2
RECOVERY_USED: 0/1
VERSIONS product/protocol/config/storage/profile/prompt: 0.1.0 /1.0 /1 /2 /1 /1
CHECKPOINT: attempt1 targeted acceptance green; final regression/static/process evidence next
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
