# F05-F06 ? Feedback learning loop

```text
TASK: F05-F06
STATE: blocked; F06_PROMOTION_POLICY_UNRESOLVED; F05 targeted-green
BASE / MERGE_BASE: 31e3710ebb4140b02e0c63f420826329ff4ba72f
BRANCH: task/f05-f06-feedback-learning
ENTRY: clean main == origin/main; F04 merge present; owner authorization; WIP 1
DECLARED_WRITE_SET: README.md; AGENTS.md; ARCHITECTURE.md; EXECUTION_CONTRACT.md;
  docs/decisions/ADR-003-desktop-first-flutter.md; docs/F05_F06_TASK.md;
  src/personalstyle/feedback.py; src/personalstyle/learning.py;
  src/personalstyle/verification.py (engine-issued feedback receipt only);
  src/personalstyle/storage.py (feedback persistence/explicit schema migration);
  src/personalstyle/config.py; personalstyle.toml (storage schema only);
  tests/test_feedback.py; tests/test_learning.py; tests/test_initialization.py;
  tests/test_storage.py; tests/test_profile.py (unknown-version cases now use 3)
ATTEMPTS_USED: 3/3
DIAGNOSIS_USED: 0/2
RECOVERY_USED: 0/1
CHECKPOINT: F05 feedback + F06 scoped evidence targeted-green; promotion blocked
```

Owner authorizes the combined experiment, not later tasks. Align only governing docs;
retain historical task records. F05 must be targeted-green before F06 implementation.
A missing explicitly specified/executable promotion rule requires controlled stop:
F06_PROMOTION_POLICY_UNRESOLVED. Do not invent a threshold or active preference.

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
