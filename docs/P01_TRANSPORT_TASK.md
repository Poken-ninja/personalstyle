# P01 transport close-bound correction

```text
TASK: P01-TRANSPORT-CLOSE
BRANCH: task/p01-origin-rejection
BASE: 9a7a2049ca9d19f5d5d9d163b54a174d073d27a8
STATE: locally verified — bounded transport correction
WIP: 1
IMPLEMENTATION: 1/2 used
DIAGNOSIS: 1/1 complete
RECOVERY: 0/1
```

## Trigger and diagnosis

V01's final regression twice observed `WinError 10053` in the unchanged P01 test
`test_early_rejection_with_unread_body_stress[origin-ORIGIN_CALLER_REJECTED]`. The isolated
case now passes on both the V01 branch and unchanged `origin/main`, confirming intermittent
behavior rather than a V01 regression. Source inspection identifies a concrete edge: the
client sends `MAX_BODY_BYTES + 1`; the server rejects before dispatch and its graceful-close
path discards at most `MAX_BODY_BYTES`, potentially closing with one request byte unread.
On Windows, closing a TCP socket with unread inbound data can reset the connection. The
existing HTTP client also writes the body before reading the response, exposing that close
race. P01 still must reject before engine dispatch and must not wait for or consume an
unbounded body.

## Minimal correction and write set

Allow the existing close path to discard at most one additional byte (`MAX_BODY_BYTES + 1`)
within the same fixed time ceiling. This matches the tested just-over-limit boundary while
remaining constant-bounded. Do not change request limits, Origin/auth checks, dispatch,
response codes, timeout, or protocol behavior. Update the fake-socket bound assertion and
retain the 20-iteration rejection stress cases.

Write set: `docs/P01_TRANSPORT_TASK.md`, `src/personalstyle/protocol.py`,
`tests/test_protocol.py`.

## Acceptance and limits

- Focused rejection/auth/handshake tests pass, including 20 iterations per pre-dispatch
  class and stalled-body bounded behavior.
- Fake close-peer proves the discard bound is exactly `MAX_BODY_BYTES + 1`, with the same
  fixed close deadline.
- Engine dispatch remains absent for rejected requests; loopback, auth, Origin, request-size,
  sanitization, and normal handshake controls remain intact.
- Run affected protocol regressions and static checks once; no full suite unless V01 returns
  to its authorized final verification after this P01 correction.
- One implementation attempt, one diagnosis complete, one recovery available. If the
  focused transport verification fails, stop without a second repair.

No V01, F08, profile, consent, Flutter, UI, or user-storage changes are in scope.

## Executed evidence — 2026-10-16

- The exact Origin stress case passed once on V01 (`1 passed, 0.17s`) and once on the
  unchanged `origin/main` baseline (`1 passed, 0.37s`); the prior full-suite abort is
  intermittent and not attributable to V01 protocol changes.
- After the fixed one-byte drain correction: targeted auth/Origin/oversized/malformed/
  stalled-body/handshake and fake-close-bound checks passed (`9 passed, 0.62s`), including
  20 iterations per rejection class.
- Complete `tests/test_protocol.py`: `34 passed in 81.80s`.
- Ruff on the changed protocol source/test, mypy on `src`, pip check, and `git diff --check`
  all passed.
- Request limits, reject-before-dispatch behavior, loopback binding, auth and Origin policy
  were unchanged. The drain remains bounded to `MAX_BODY_BYTES + 1` bytes and the existing
  fixed close deadline.

P01 transport correction is locally verified. No CI, push, or PR was requested here. The
V01 branch must include this commit and pass its one outstanding full regression before V01
can be called verified.
