# GitHub merge gate handoff

```text
TASK: GitHub gate (owner-authorized after I01)
STATE: passing
VERIFICATION_STATUS: valid (remote CI and main protection)
BASE / CHECKPOINT: 19585fd9c50311138d85e93f2cb0769d983c498d
BRANCH: task/github-gate
DECLARED_WRITE_SET: .github/workflows/python-harness.yml; docs/GITHUB_GATE_HANDOFF.md; remote main protection settings
ATTEMPTS_USED: 2 of 3
DIAGNOSIS_USED: 0 of 2
RECOVERY_USED: 0 of 1
BLOCKER: none
NEXT_ACTION: merge this gate through its required check; then evaluate SEC01 entry
```

I01 PR #1 merged as `19585fd9c50311138d85e93f2cb0769d983c498d`; local main
fast-forwarded without conflicts. I01 implementation budgets remain 3/3, 0/2, 0/1.
This gate is a separate task and does not change I01 acceptance criteria or product policy.

Acceptance:
1. PR and main push run the existing install/import, CLI, tests, Ruff, mypy and dependency
   consistency checks in a bounded Windows/Python 3.14 job named `Python harness checks`.
2. A real PR run passes; record its revision and URL.
3. Main requires this GitHub Actions check with up-to-date base, PR-based changes,
   enforcement for administrators, no force push/deletion, and resolved conversations.
   Do not add a required human approval count without an available reviewer decision.
4. Read back remote configuration and record enforcement evidence; a workflow file alone
   does not establish branch protection. Do not call the gate complete without this evidence.

Implementation budget is conservatively 3 attempts / 2 diagnoses / 1 recovery, with a
10-minute CI job ceiling. No retry of a failed workflow without failure classification and
new information. Dependency lock/security release work remains separate from this CI gate.
Actions are pinned to SHAs resolved from the upstream v5.0.0/v6.0.0 tags. The job uses read-only
repository permission, does not persist checkout credentials, and uses pull_request rather
than pull_request_target. No secrets or writing data are introduced.

Observed capability failure: gh was absent; owner-approved GitHub CLI installation succeeded.
`gh auth status` then exited 1 (not logged in). Connector supports PR operations but has no
branch-protection mutation tool. Owner must log in locally with administrative permission;
credentials must not be pasted, committed or logged. SEC01 has not started and remains
dependent on completing the gate in the owner's requested sequence.

Authentication resolved by owner's local login; admin permission verified. Remote main
protection configured and read back: strict required `Python harness checks` from GitHub
Actions app 15368, enforce_admins true, PR required (0 approvals), conversations resolved,
force pushes/deletions false. No existing rules were overwritten (previously unprotected).

Failure evidence: PR #2 at 4dc11ef3efded49a18a88cf5840941f79b6a2368 ran
https://github.com/Poken-ninja/personalstyle/actions/runs/37540408668 ; Python checks
passed but whitespace step exited 1 because shallow checkout lacked HEAD^.
Class: verification_defect in new workflow configuration. Expected: compare real parent
commit, preserving whitespace criterion. Repair: attempt 2 fetches complete history.
Remaining: 1 implementation attempt / 2 diagnosis / 1 recovery.
Enforcement evidence: `gh pr view 2` reported mergeStateStatus BLOCKED with FAILURE for
the required check. No merge was attempted and no gate was bypassed.

Passing evidence: attempt 2 at `9d8a88e8f38a904fecfe3d99d6463c28c2910e9f` passed
the required check in 40 seconds on Windows / Python 3.14.7:
https://github.com/Poken-ninja/personalstyle/actions/runs/37540610582/job/112532422123
All install/import/startup/test/lint/type/dependency/whitespace steps succeeded. Main
protection readback confirmed all acceptance settings above. This final handoff-only
commit preserves the passing workflow and product implementation; its PR check must also
pass before merge. Gate task 2/3 attempts, 0/2 diagnosis, 0/1 recovery. No admin bypass.
