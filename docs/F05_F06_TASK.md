# F05-F06 ? Feedback learning loop

```text
TASK: F05-F06
STATE: locally_verified; draft PR #10 final exact-head CI/review authoritative
BASE / MERGE_BASE: 31e3710ebb4140b02e0c63f420826329ff4ba72f
BRANCH: task/f05-f06-feedback-learning
ENTRY: clean main == origin/main; F04 merge present; owner authorization; WIP 1
DECLARED_WRITE_SET: README.md; AGENTS.md; ARCHITECTURE.md; EXECUTION_CONTRACT.md;
  docs/decisions/ADR-003-desktop-first-flutter.md; docs/F05_F06_TASK.md;
  src/personalstyle/feedback.py; src/personalstyle/learning.py;
  src/personalstyle/verification.py; src/personalstyle/generation.py; src/personalstyle/profile.py;
  src/personalstyle/storage.py (feedback persistence/explicit schema migration);
  src/personalstyle/config.py; personalstyle.toml (storage schema only);
  tests/test_feedback.py; tests/test_learning.py; tests/test_initialization.py;
  tests/test_storage.py; tests/test_profile.py (unknown-version cases now use 3);
  tests/test_generation.py; tests/test_verification.py
ATTEMPTS_USED: 4/5 (historical 3 preserved; owner continuation ceiling 5)
DIAGNOSIS_USED: 2/2 (cancelled-job inspections; historical counters below preserved)
RECOVERY_USED: 1/1 (owner-authorized same-head CI rerun)
CHECKPOINT: implementation e72f9d3; final local evidence below; no merge or P01
```

Owner authorizes the combined experiment, not later tasks. Align only governing docs;
retain historical task records. F05 must be targeted-green before F06 implementation.
The initial missing promotion rule required the historical controlled stop
F06_PROMOTION_POLICY_UNRESOLVED. Owner continuation below resolves it explicitly.

F05: accept/edit events only for engine-issued successful verified candidates; retain run,
request/context/model/prompt/profile/example/DNA provenance and accepted/edited text.
Explicit owner authorization, learning authorization and held-out provenance required.
Accept is weak positive evidence; never style promotion. Classify style/expression,
meaning/fact, constraint, context/recipient and mixed/unknown corrections. Deterministic
classification accepts owner-annotated presentation-only edits with unchanged lexical content as style;
semantic edits without conclusive evidence remain mixed/unknown. Non-style owner annotations
are accepted conservatively; a style annotation alone cannot override hard evidence.
No model classifier or real inference is needed for this initial bounded representation.

Durable feedback needs a distinct SQLite table in the existing canonical protected store,
therefore storage_schema 1 ->2 is necessary (not an unrelated redesign). Explicit atomic
1->2 migration; legacy reads remain validated, normal writes require schema2; unknown schemas
fail. Migration adds a writer-version column so the old implicit INSERT cannot write through
a migration. Config shape, product/protocol/profile/prompt versions remain unchanged.
Boundary checks, parameterized SQL, rollback/idempotency, operation/input limits and sensitive
logging controls remain. Engine-issued receipts are in-process only; serialized success flags
or modified receipts cannot authorize recording. No new network/protocol authority.

F06: smallest read-derived exact-context eligible style evidence/hypothesis snapshot,
linked to versioned feedback records; deterministic ordering, no held-out/ineligible/non-style
evidence. Before actual promotion inspect authoritative docs/config/source for a criterion.
If absent, expose fixed blocked outcome and no active preferences; record exact owner decision
needed. No durable derived tables until a specified policy requires them.

Acceptance: F05 authorized verified source roundtrip/idempotency/classification/provenance
and protected atomic persistence pass targeted tests. Then F06 eligible scoped evidence and
policy guard pass targeted tests. Only with both phases green and no owner blocker run one
final full pytest (600s), Ruff/mypy/pip check once, real acceptance only when materially
required, required CI once. Never use a remote pass to waive an unresolved product decision.
On a promotion-policy stop, open one draft PR; do not run the local final expensive cycle.
Existing draft-PR CI may run automatically; it is not compound-task completion evidence.

Same implementation failure twice -> bounded diagnosis; counters persist across phases.
Record fixed failure, observed/expected/class/evidence/action/remaining budget. Final compact
handoff records exact revision, versions, scoped writes, targeted/full/static/model/CI counts,
approximate implementation vs final-verification time, owner intervention and scope violations.
Normal turns aim at 3?8min; 10?15min is an advisory checkpoint threshold, not document-enforced.
No P01, UI, OS security, E01, other provider, embedding, agents or background work.
Stop with a draft PR and compact evidence; no automatic merge or next-task activation.

## Persistent attempt evidence

Attempt 1 F05 targeted run: 21 passed /1 failed in 68.36s, parent71.04s.
OBSERVED: purported unknown-edit fixture removed known numeric/calendar literals and was
classified meaning_fact. EXPECTED: inconclusive semantic-only wording edits stay unknown.
FAILURE_CLASS: verification_defect; fixture contradicted its intended semantic-only case.
NEXT ACTION: retain numeric/calendar literals in that fixture, keeping the unknown assertion.
Attempt 2 additionally makes owner style annotation necessary for the bounded presentation
classification; annotation alone cannot override lexical/fact/constraint/context evidence.
This material guard refinement consumes attempt2, no budget reset. Diagnosis0/2, recovery0/1.
Remaining implementation1; no repeated identical failure or model call.
The existing unknown-version tests now use3 because explicitly migrated storage2 is known;
rejection assertions remain unchanged. F04 receipts stay in-process; no secret/auth framework.

Phase A guard: F05 targeted acceptance passed, 22 tests in62.36s (parent63.343s).
Phase B policy inspection: AGENTS personalization rules, ARCHITECTURE feedback adapter,
EXECUTION_CONTRACT F06 roadmap, accepted ADRs, personalstyle.toml and current source contain
no promotion threshold/criterion. General evidence-backed/deterministic requirements do not
define an executable decision. Implement only inspectable read-derived evidence before the
blocked decision boundary; no preference table, generation consumption or promotion.

Phase B?s first material evidence-path edit consumes compound implementation attempt3/3;
no phase reset. Targeted evidence/isolation tests are running. Diagnosis0/2, recovery0/1.
No promotion policy was introduced; no active preference is writable or consumed.

## Controlled stop and compact experiment evidence

```text
TASK: F05-F06
STATE: blocked; F06_PROMOTION_POLICY_UNRESOLVED
FINAL_REVISION: exact committed checkpoint in draft PR handoff
BASE / MERGE_BASE: 31e3710ebb4140b02e0c63f420826329ff4ba72f; current main unchanged
PRODUCT / PROTOCOL / CONFIG / STORAGE / PROFILE / PROMPT: 0.1.0 /1.0 /1 /2 /1 /1
CLASSIFICATION / LEARNING_EVIDENCE: feedback_classification.v1 /learning_evidence.v1
ATTEMPTS_USED: 3/3 (initial F05; F05 annotation guard; F06 evidence path)
DIAGNOSIS_USED: 0/2
RECOVERY_USED: 0/1
IMPLEMENTATION_PHASE_TURNS: 3; counters never reset at phase transition
TARGETED_RUNS: 3; F05 21pass/1fixture failure, then22pass; F06 evidence2pass
FINAL_LOCAL_FULL_REGRESSION_RUNS: 0; owner policy guard prevents final cycle
FINAL_LOCAL_STATIC_SUITE_RUNS: 0
REAL_MODEL_ACCEPTANCE_CYCLES: 0; deterministic fixtures only
FINAL_EXPENSIVE_LOCAL_VERIFICATION_TIME: 0
APPROX_IMPLEMENTATION_WALL: 20min including ~3.6min targeted tests and activation docs
OWNER_INTERVENTION_NEEDED: yes; explicit promotion criterion before further implementation
SCOPE_VIOLATIONS: none observed
ACTIVE_PREFERENCES_PROMOTED: 0
NEXT_PERMITTED_ACTION: owner promotion-policy decision and explicit additional implementation budget;
  draft PR remains blocked; no merge, P01, UI or later tasks
```

F05 pass22tests/62.36s (parent63.343s), F06 scoped evidence2tests/78.37s (parent78.914s).
F05 tests prove protected exact feedback read-back, UUID retry/conflict behavior, provenance/
version increments, fixed classification categories, absence of ordinary raw logs, rejection
of unauthorized/mutated/serialized receipts, guarded transaction rollback, explicit atomic
1->2 migration preserving samples, and rejection of an old writer?s INSERT after migration.
F06 tests prove scoped streaming evidence accumulation and deterministic ordered source
fingerprint, exclusion of held-out/ineligible/accept/fact/constraint/context/mixed/unrelated
feedback, no read mutation/raw source prose, and fixed blocked promotion with no active state.
Hypotheses describe observed paragraph/line/separator changes only, not active directives.
Counts are observations, not claims of independent sources or a confidence/promotion threshold.

Policy evidence: current AGENTS personalization rules, architecture feedback pipeline,
execution F06 roadmap, accepted ADRs, configuration and source specify no executable
promotion criterion. An owner must define independent evidence units, support requirement,
contradiction handling and explicit authorization/trigger for a context-only hypothesis to
become an active versioned preference. No builder-chosen threshold or cross-context widening.
Later personalization consumption is unimplemented because no authorized preference exists.

This is the requested controlled stop, not completed F05-F06 or product-learning success.
One draft PR?s existing required CI may run automatically; it does not override the policy
blocker or substitute for the deferred final local cycle. Exact CI status belongs to its
handoff. Historical task records, provider/generation behavior and dependency declarations
are unchanged. No real writing was provisioned or production profile migrated in this task.
Live engine receipts deliberately fail after serialization/process restart; durable feedback
retains its full source snapshot. Authenticated/lifecycle transport remains future P01 scope.


## Owner continuation: promotion policy resolved

Authority: owner continuation decision in draft PR #10 and continuation instruction.
Historical attempts used: 3; owner extends total ceiling to 5; remaining 2.
Diagnosis remains 0/2; recovery remains 0/1. Attempt 4 begins with the next
material feature-code edit. Attempt 5 is reserved for one concrete defect repair.
Current state: active; historical F06_PROMOTION_POLICY_UNRESOLVED stop above is preserved.
Base: 31e3710ebb4140b02e0c63f420826329ff4ba72f; checkpoint: 9152c6011475eb3df58e72fe345b64b2248701b1.
Continuation write set: this task; README.md; EXECUTION_CONTRACT.md; ARCHITECTURE.md;
src/personalstyle/{storage,learning,profile,generation,verification,feedback}.py;
tests/test_{learning,feedback,generation,verification}.py. No unrelated changes.

Policy context_preference_promotion.v1: only engine-verified, learning-authorized,
non-held-out style_expression edits in the exact context qualify. Features remain
paragraph_count, line_count, separator_characters, with increase/decrease direction.
Each verified source run contributes at most one independent unit per feature.
Any conflicting directions from that run make it ambiguous for that feature.
Order by first persisted creation revision (feedback.profile_version), then feedback ID;
repeated same-run events cannot advance that unit. Inspect latest three non-ambiguous
units: fewer than three is unpromoted; three agreeing activate; disagreement is
contested/inactive. Retain the previous direction while inactive; a new direction or
reactivation requires three agreeing units. No global or cross-context promotion.
Explicit engine evaluation is the synchronous authorized trigger; no background work.
Persist append-only preference versions, policy, context/feature/direction/state,
exact supporting feedback/run IDs and source profile version. Extend unmerged schema 2;
no production profile was migrated at the historical checkpoint. Schema-2 checkpoint
files lacking the new table fail validation rather than being silently guessed.
Only active exact-context preferences enter generation as data; record exact IDs/versions.
F04 checks their source integrity; style remains outside hard correctness gates.
Existing prompt contract 1 permits personalization evidence: preference metadata is an
additive evidence field, with no change to instruction authority or hard verification.
Other compatibility versions remain unchanged. Targeted acceptance precedes exactly one
full/static final cycle; no real model cycle unless deterministic fixtures cannot prove
consumption. Preserve owner PR decision and historical failed evidence.

Timing clarification: the prior >=66-minute wall interval included approximately
30 minutes of laptop sleep. It is not all active harness execution. No precise
sleep-adjusted duration is claimed; historical measured targeted durations remain separate.


Attempt 4 started: primary owner-authorized promotion/consumption implementation.
ATTEMPTS_USED: 4/5; DIAGNOSIS_USED: 0/2; RECOVERY_USED: 0/1.
Owner performance decision adds AGENTS.md to the continuation write set.
Feedback schema 2 retains bounded validated observation metadata/run ID alongside its
source payload so promotion can group independent runs without retaining the corpus
or issuing per-feedback SQL. One streamed validation plus three fixed feature aggregates;
no N+1 per-record query. Latest-state preference lookup uses one grouped join.

Representative synthetic in-memory SQLite evidence: 3,000 examples, 3,000 feedback,
9,000 preference-history rows /100 contexts; 50 exact-context reads each, no model calls.
Before -> after indexes (milliseconds, illustrative local sample): examples 9.66->2.02;
feedback 9.49->1.58; promotion 7.43->2.12; preference latest-state lookup 23.70->1.13.
Plans changed whole-index/table SCAN to exact-context SEARCH. examples_eligible(context,
learning_eligible,held_out,id) and feedback_context(context,id) preserve order without
sort. feedback_runs(context,run_id) removes promotion GROUP BY temp tree; latest-three
ORDER BY retains a bounded top-three sort. preferences_context(context,feature,version
DESC) removes full scans/group/sort on the actual latest-per-feature exact-context query.
These four indexes serve distinct actual paths; existing PK indexes do not cover them.
No email/FK/asset work. All index creation is in the atomic unmerged schema-2 migration.


Attempt-4 targeted run: 63 passed /3 failed in178.71s (parent179.211s).
OBSERVED: three policy tests rejected their in-memory SQLite fixture at schema validation.
EXPECTED: policy fixture must satisfy the real DELETE journal-mode requirement.
FAILURE_CLASS: verification_defect; SQLite in-memory databases report journal_mode=memory.
EVIDENCE: all three fail at ExampleStore._schema before feedback handling; protected
promotion/generation integration and affected F03/F04 regressions passed.
NEXT ACTION: disposable file-backed SQLite policy fixture, preserving schema assertion;
run only corrected/new targeted cases. No feature-code correction or repeated repair.
BUDGET REMAINING: implementation1 (used4/5); diagnosis2; recovery1.


Continuation targeted acceptance: corrected/new policy, protected integration and query-plan
cases5passed/29.18s (parent29.567s); final invalid-source/provenance-repair cases5passed/0.29s
(parent0.545s). Together with the unaffected63passing cases from the first run, all changed
paths have current targeted evidence. No feature-code repair; attempts4/5, diagnosis0/2,
recovery0/1. Query count stays four feedback SELECTs at1 and11 records (one streamed
validation, three fixed feature aggregates); exact-context plans use the measured indexes.
Protected integration proves atomic promotion rollback, active-only exact-context consumption,
exact preference ID/version provenance, tamper rejection, contested exclusion, no generation
mutation and no raw normal logs. F04 repair retains preference metadata and all hard gates.
The in-process deterministic provider exercises the complete loop, so additional real Ollama
calls are not materially required. Existing F03/F04 live runtime evidence is not re-run.
Reconciliation: local main==origin/main==31e3710ebb4140b02e0c63f420826329ff4ba72f;
merge base identical, no conflict or unrelated changes. Final expensive cycle is next, once.


Final cycle on implementation e72f9d3aa05090a476d37c967c474300ed62dd95:
full pytest220passed/405.29s (parent405.708s); mypy11sourcefiles passed/0.671s;
pip check passed/2.015s. Ruff initial check failed I001 (1.392s).
OBSERVED: extra blank line between imports and fixture assignments in test_learning.py.
EXPECTED: Ruff import-block formatting; no assertion or behavior change.
FAILURE_CLASS: verification_defect (fixture formatting only).
NEXT ACTION: remove that one blank line and re-run only the failed Ruff check.
BUDGET REMAINING: implementation1 (4/5 used), diagnosis2, recovery1.
The historical alias defects are removed; historical failed CI is retained, not re-run.
Passing full/static evidence is not invalidated by this nonsemantic blank-line correction.


## Continuation final local handoff

```text
TASK / STATE: F05-F06 / locally_verified; unmerged draft PR #10
VERIFIED_IMPLEMENTATION_REVISION: e72f9d3aa05090a476d37c967c474300ed62dd95
PUBLISHED_HEAD / CI: exact SHA and run recorded in draft PR #10 final handoff
BASE / MERGE_BASE: 31e3710ebb4140b02e0c63f420826329ff4ba72f (unchanged)
PRODUCT / PROTOCOL / CONFIG / STORAGE / PROFILE / PROMPT: 0.1.0 /1.0 /1 /2 /1 /1
POLICY: context_preference_promotion.v1
ATTEMPTS_USED: 4/5; owner extended historical ceiling3 to5; no reset
DIAGNOSIS_USED: 0/2
RECOVERY_USED: 0/1
TARGETED_RUNS: 6 cumulative; 3 historical +3 continuation
FINAL_FULL_REGRESSION_RUNS: 1; 220passed/405.29s
FINAL_STATIC_CYCLES: 1; Ruff passed after one formatting-only failed-check re-run;
  mypy11sourcefiles passed; pip check passed; unchanged passing checks not repeated
REAL_MODEL_CYCLES: 0; deterministic provider integration proves changed behavior
FINAL_EXPENSIVE_LOCAL_INTERVAL: approximately7min (full suite parent405.708s)
CONTINUATION_IMPLEMENTATION_INTERVAL: first clock03:17Z to source commit03:28:20Z,
  approximately11min including targeted runs; not a precise active-time benchmark
OWNER_INTERVENTION: promotion policy/budget extension and measured performance decision
SCOPE_VIOLATIONS: none observed
BLOCKERS: none local; required exact-head CI/review status belongs to PR #10
NEXT_PERMITTED_ACTION: review draft PR #10 and its exact-head CI; no automatic merge/P01
```

Ruff corrected check passed. Final handoff delta from the verified implementation is
status/evidence documentation plus one nonsemantic blank-line correction in the test import
block; feature behavior/configuration/tests' assertions are unchanged. No passing expensive
check was repeated. Python/SQLite runtime evidence is recorded with the PR handoff.

Acceptance: two supports do not activate; three agreeing verified source runs activate;
same-run repetitions do not multiply support; per-feature conflicting runs are excluded;
opposition contests without flipping; three later agreeing runs reactivate. Exact-context
isolation and held-out/ineligible/non-style/accept exclusions pass. Active preferences enter
personalized prompts only, with exact version provenance and unchanged example/DNA evidence.
F04 source checks reject modified preference provenance; hard repair retains preference data
without making style a hard gate. Invalid/unauthorized/incompatible source metadata fails
closed. Protected promotion rollback and explicit schema-1 migration rollback remain green.
All4 measured indexes are included in schema2; no schema3, lifetime quota, N+1 per-record
lookup, alternate provider, background learning, P01, Flutter or asset conversion.
Sensitive source writing never appears in the derived preference result or ordinary logs.
No quality improvement, global preference, cross-platform storage or V1 completion is claimed.

Historical checkpoint CI37720942635:210tests passed, Ruff failed on import formatting/aliases;
not final evidence. Historical >=66-minute wall interval included owner-reported ~30-minute
laptop sleep; actual active duration remains uninstrumented. Historical observations above
are preserved and this clarification supersedes attributing that whole interval to work.

Runtime metadata: Python3.14.6; SQLite3.50.4. The first metadata-print shell command
lost its quoted labels and raised NameError before collecting metadata; a here-string
corrected the command, with no code/environment modification or verification re-run.


## Owner-authorized harness timeout configuration repair

DECLARED_WRITE_SET: .github/workflows/python-harness.yml; docs/F05_F06_TASK.md.
Authority: explicit owner decision; one harness-only commit, no feature/test modification.
Classification: HARNESS_TIMEOUT_CONFIGURATION_DEFECT. This supersedes the preliminary
CI environment classification without rewriting historical observations.
Both attempts of run37723618402 on7e58f15c8bed6a30d94ef2fc521fac9bfcac9ceb were
cancelled because the10-minute job ceiling expired during full pytest. Attempt1 reached
188passed/567.22s; attempt2 reached183passed/556.17s. Neither establishes a feature failure;
remaining tests and later static steps were incomplete. Those runs are historical only.
Local final evidence remains220passed/405.29s plus passing Ruff/mypy/pip check.

Repair: raise only the Python harness job timeout10->15minutes. All pytest, Ruff, mypy,
pip check and whitespace steps remain intact; no assertion, feature, product timeout,
version, permission or branch-protection change. Fifteen minutes remains an enforced
GitHub job ceiling. No local full/static rerun is warranted by this workflow/docs delta.
One new exact-head CI run is authorized. If it passes, correct the stale PR title, verify
mergeability and stop for owner review; no automatic merge. If it still times out, stop
for bounded step/runtime or partition diagnosis; never raise the ceiling again automatically.

Counters preserved: feature implementation4/5, diagnosis2/2, recovery1/1. This separately
owner-authorized, fully specified harness repair is1/1; no new feature attempt or budget reset.
Current state: locally_verified; new-head required CI pending; draft PR remains unmerged.
Next action: observe new exact-head CI once; no P01 or Flutter.
