# F07 - Long-document bounded rewrite and recovery

```text
TASK: F07
STATE: locally passing - draft PR pending exact-head CI
BRANCH: task/f07-long-document
REPOSITORY_REVISION / BASE / MERGE_BASE: 96afb4691dfb141601f3239b3d93f203294347d4
WIP: 1
DECLARED_WRITE_SET: README.md; AGENTS.md; ARCHITECTURE.md; EXECUTION_CONTRACT.md;
  personalstyle.toml; docs/F07_TASK.md; scripts/f07_acceptance.py;
  src/personalstyle/{config,feedback,protocol,provider,storage,document}.py;
  tests/{test_document,test_feedback,test_initialization,test_learning,test_profile,
  test_protocol,test_provider,test_storage}.py
ENTRY_GUARD: passed; owner explicitly authorized the proposed bounded state/migration
IMPLEMENTATION_ATTEMPTS_USED: 2/2
DIAGNOSIS_USED: 2/2
RECOVERY_USED: 1/1
STRUCTURAL_CORRECTION: 1/1
FINAL_REGRESSION_DIAGNOSIS: 1/1
P01_TRANSPORT_REPAIR: 1/1 (owner-authorized bounded graceful-close repair)
STORAGE_BOUNDARY_DIAGNOSIS: 1/1 (owner-authorized non-modifying cycle)
FINAL_GATE_INSTRUMENTED_REPRODUCTION: 1/1 (owner-authorized single900s run)
FINAL_REGRESSION_RECOVERY: 1/1 (owner condition satisfied; single 900s run)
CHECKPOINT: instrumented294 passed441.37s; definitive294 passed437.77s; Ruff/mypy/pip/diff checks pass; draft PR handoff
```

## Authority and entry evidence

Owner selects F07 only. Fetch completed; clean local main fast-forwarded from the P01 merge
to96afb4691dfb141601f3239b3d93f203294347d4 and equals origin/main. PR12 is MERGED at that SHA;
open PR list empty, one worktree, no unmerged local task branches. Created this one F07 branch
after verifying the clean tree. Harness-Engineering remains read-only.

Read README/AGENTS/execution/architecture/configuration and existing generation, verifier,
provider, protected SQLite, feedback/profile, protocol and CLI paths. This is entry inspection,
not an implementation attempt or failed-implementation diagnosis cycle.

Phase A historical evidence remains in docs/S03_WIN_ALPHA_TASK.md and PR12: source
09ca6a0f2a7af251e77874b9f97832c1ad04e9f1, exact-head CI37760293989 SUCCESS, analyze clean,
22 Flutter tests, Windows release build and real authenticated lifecycle acceptance2.673s.
Its failures/counters are preserved. Overall Windows alpha is incomplete; Phase B not_started.

Owner roadmap: Phase A -> F07 -> F08 -> Phase B model setup/readiness -> final Windows alpha.
F08 initial import: .txt/.md/.docx/text-based .pdf; export: .docx/.pdf/.md/.txt. Not implemented.
Future web surface approved; deployment/transport unresolved. No local-web/cloud decision.

Current versions remain product0.1.0/protocol1.0/config1/storage2/profile1/prompt1;
desktop0.1.0+1. Configured provider/model is ollama/qwen3:8b. No runtime qualification,
dependency installation, model call, feature/config/schema change or migration performed.

## Objective and bounded behavior

Rewrite approximately2,000-5,000 words without a full-document generation call, using:
validate/fingerprint -> meaningful deterministic segmentation -> durable manifest -> existing
engine generation/hard verification per segment -> verified checkpoint -> bounded classified
repair -> ordered reassembly -> whole-document verification -> verified result.

Proposed document input boundary: at most5,000 whitespace-delimited words AND64KiB UTF-8
(the existing per-text byte ceiling). Test each boundary and boundary+1; fail explicitly before
work, never truncate. This is a per-request bound, not a lifetime example/database quota.
No F07 input support is claimed until implemented and tested. Segment/prompt framing and
document-wide execution/call ceilings must be fixed before attempt1 or any live acceptance;
none is inferred from the short-text model-call limit or changed after observing results.

Prefer sections/paragraph boundaries, retaining ordering and separator/structure information.
An oversized paragraph needs an explicit deterministic sentence/fallback policy within the
actual provider input/output bounds; never silently drop text. Freeze the segmentation and
structure contract before implementation. Reuse existing engine behavior, never copy it.

Manifest requirements: stable document ID/revision and fingerprint; stable segment ID/order;
source content/fingerprint; separators/order/structure; intent/context/constraints/protected
information; relevant exact-context profile/example/DNA/preference input identity; provider,
exact model/digest and prompt/verification contracts; per-segment state/evidence; durable
attempt/call usage; progress and blocked failure. Sensitive source/output checkpoints use
the protected engine boundary, never ordinary logs or an unguarded sidecar file.

Resume must reconstruct next action after restart, reuse valid verified segments, repair only
required failed/stale work and preserve earlier checkpoints. Source-only edits invalidate that
segment and dependent assembly evidence. Order/structure changes invalidate genuinely dependent
evidence. Intent/context/constraints/personalization/model/prompt/verification changes invalidate
the work they affect. An unrelated context's global store revision alone must not unnecessarily
invalidate a relevant semantic snapshot. No silent budget reset across restart or reopening.

## Required state-change decision

Observed implementation evidence:

- storage.py SCHEMA_V1/SCHEMA defines store_meta/examples/feedback/preferences only; _schema
  requires the exact sqlite_master object set and accepts only user_version1/2. Extra tables
  cannot be added invisibly to schema2. Config loader explicitly requires storage_schema2.
- generate_pair returns an in-memory pair. verify_pair returns an in-memory _VerifiedPair
  receipt and retains model-call/attempt/history counters only in that result.
- Protocol EngineSession retains one _verified receipt in memory; CLI prints explicit results.
  Neither provides document/segment checkpoint enumeration, restart or persisted call budgets.
- Feedback persists authorized accept/edit events from live verified receipts. Using feedback
  or examples as a checkpoint would falsely create user/learning evidence and change semantics.
- Existing conservative prompt bound is6,000 UTF-8 bytes including framing/personalization;
  semantic verification includes both source and candidate. Output ceiling2,000 tokens,
  preparation120s, each generation/semantic call60s. Segmentation must account for those actual
  bounds, not treat a whole5,000-word request as fitting because the input validator accepts it.
- Current verifier detects literal number/calendar presence and constraints plus bounded
  semantic second-pass judgments. It does not implement document-order/structure verification.

Required change proposal, NOT implemented/approved by this checkpoint:

1. Extend the existing protected canonical SQLite store with document-run manifest and
   segment-checkpoint state, using the same sole engine writer/ACL/reparse/file-identity/
   transaction/read-back protections. Store source, accepted output, dependency fingerprints,
   structured verification evidence and cumulative budget reservations atomically.
2. Because schema2 is merged and exact-schema validated, use an explicit ordered2->3 migration
   (preserving the1->2 path), compatible initialization/configuration and fail-closed old-writer
   behavior. Keep operational checkpoint revisions separate from learning/profile changes.
   Do not silently revise merged schema2 or use an unprotected JSON/second-store workaround.
3. Persist/reserve calls before external work so a crash cannot regain budget. Reconstruct
   verification authority from validated engine-owned state; serialized success flags alone
   must not forge _VerifiedPair/feedback authority. Reuse generation/verification internals
   through the smallest necessary adaptation; short-text behavior remains compatible.
4. Declare per-segment limits and one document-wide budget/deadline, including whole-document
   checks. Current F04 policy allows at most3 generation attempts and8 model calls per pair
   (preparation counts), stops identical repairs/repeated failure, and has no durable resume.
   Applying fresh budgets on every resume would violate the existing outer-budget contract.

Owner explicitly required stopping when reliable resume needs a schema/state change.
This guard is reached before feature edits. Smallest next owner decision: authorize the
protected document/checkpoint state and explicit schema3 migration within F07; then freeze
the detailed state, invalidation and document-wide budget contract before attempt1.
No migration, table, checkpoint of user prose or new protocol capability exists from this task.

## Acceptance and verification plan

All F07 criteria below are NOT RUN / NOT IMPLEMENTED; planned checks are not evidence.

| Criterion | Required executable evidence |
|---|---|
| F07-AC1 | About2,000 synthetic words complete via multiple bounded segment calls |
| F07-AC2 | About5,000 synthetic words complete through the same path |
| F07-AC3 | Declared maximum word/byte/operation boundaries exist and are tested |
| F07-AC4 | Boundary+1 is rejected clearly before partial silent processing |
| F07-AC5 | Deterministic segmentation and ordered reassembly preserve declared source/structure boundaries |
| F07-AC6 | Every segment receives existing semantic/information/constraint/context/structural verification |
| F07-AC7 | Controlled middle failure leaves earlier verified segments durably checkpointed |
| F07-AC8 | Restart/resume reuses valid unaffected segments; only stale/failed required work runs |
| F07-AC9 | Single source-segment edit invalidates that segment/dependent assembly, preserving unrelated verified work |
| F07-AC10 | Request/profile/model/prompt/verification changes invalidate exactly their dependent evidence |
| F07-AC11 | Whole-document verification rejects missing/reordered required information and invalid structure |
| F07-AC12 | Fresh-process inspection reconstructs progress/blocked state and persistent spent budgets |
| F07-AC13 | Existing short-text F03/F04/F05/F06/protocol behavior remains compatible |

During implementation: targeted segmentation/state/resume/invalidation/reassembly/security
tests only. Final: targeted F07; directly affected F03/F04/F05/F06 compatibility; full Python
regression once; Ruff/mypy/pip check once; deterministic synthetic-provider2,000/5,000/boundary/
boundary+1/middle failure+resume/single edit acceptance; real configured-provider acceptance
for both2,000 and5,000 words within the predeclared ceiling; exact-head required CI.
Real evidence records exact provider/model/digest, segment count, calls/repairs and elapsed time,
bounded multi-call behavior and verified reassembly. Synthetic content only. If5,000-word
acceptance cannot finish within that bound, record blocked; no relaxed criterion or ceiling.
No model/runtime probe or test suite is justified before the current state decision is resolved.

## Failure control and checkpoint

Budgets: implementation2, diagnosis2, recovery1, all0 used. First material feature-code edit
starts attempt1. Documentation activation does not consume an implementation attempt.
Persist budgets across interruption. Identical repeated failure -> diagnose/block, never
repeat-until-green. Per-segment runtime budgets must likewise survive restart.

OBSERVED: no suitable durable document/segment/run-budget mechanism exists in schema2.
EXPECTED: safe inspectable restart/resume without lost verified work or renewed retry budgets.
FAILURE_CLASS: architecture/state compatibility decision boundary - F07_DURABLE_STATE_CHANGE_REQUIRED.
EVIDENCE: exact schema/guard, in-memory generation/verifier/session state and feedback-only
persistence described above; source inspection, not a failed runtime acceptance.
NEXT ACTION: owner authorizes the documented protected checkpoint/schema change before implementation.
BUDGET REMAINING: implementation2, diagnosis2, recovery1.

Only the declared activation docs are changed. Historical task files remain untouched.
F07 has no code/tests/runtime results, no active or partial segment work to lose, and no PR.
Keep this honest local activation checkpoint; no task commit/push/PR until authorized continuation
or owner direction. No completion/long-document support claim.

## Repeated activation preflight

Fetched origin again. main/origin/main/HEAD remain96afb4691dfb141601f3239b3d93f203294347d4;
PR12 remains MERGED, open PR list empty, exactly one worktree on task/f07-long-document.
Current tree is NOT clean: it contains the five existing authorized F07 activation documents
only (README, AGENTS, execution, architecture and this task). Preserved them; no reset,
stash, branch recreation, preliminary commit or feature/config edit used to conceal that fact.
The original clean-main/branch-creation check remains historical evidence above.

Reread governing documents/config and rechecked actual source guards/state. The durable-state
decision is still unresolved; existing schema2 and in-memory receipts/counters are unchanged.
Owner restatement numbers acceptance1-13 by separating maximum-boundary and boundary+1 checks;
the table above now matches that numbering without removing any prior requirement.
git diff --check passes. No tests/model calls/feature implementation performed.
Counters remain implementation0/2, diagnosis0/2, recovery0/1. Single next action remains the
owner decision on the documented protected document/checkpoint state and schema2->3 migration.

Exclusions: F08/parsing/PDF/DOCX/OCR/export files; web/site/deployment choice; Phase B; browser/
mobile/macOS/Linux/SEC02/03; alternate models/providers/routing; RAG/vector DB; background work;
schedulers/distributed workers/agents; direct client canonical writes; unrelated refactoring.


## Owner authorization and implementation contract (2026-10-08)

AUTHORITY: project owner, explicit AUTHORIZED continuation. The earlier schema/state stop
above remains historical evidence, not a current blocker. Owner authorizes only protected
F07 document/segment state and explicit schema 2->3 migration; no scope expansion.

Actual write set: the five activation documents; personalstyle.toml (storage_schema only);
src/personalstyle/{storage,config,feedback,provider,document}.py; tests/test_document.py;
tests/test_initialization.py and tests/test_learning.py (current-schema fixture declarations);
tests/test_feedback.py (explicit ordered migration invocation); scripts/f07_acceptance.py.
No dependencies, Flutter, protocol capability, learning policy or prompt contract changes.
Storage becomes 3; all other compatibility declarations remain unchanged.

Smallest schema: documents(id, revision, payload) and document_segments(document_id, id,
ordinal, payload), with unique document/order lookup. Existing schema 2 objects/data remain
unchanged. Checkpoint revisions do not advance profile_version. Explicit migrations retain
1->2, then 2->3; normal writes never migrate implicitly. Schema-2 reads remain supported;
normal canonical writes require schema 3. No serialized document result grants F05 authority.

Frozen bounds: 5,000 whitespace words, 64KiB UTF-8, at most 128 segments, each source segment
at most 1,000 UTF-8 bytes. Reject unsupported shape before persistence/model work. Paragraph
boundaries are retained verbatim; oversize paragraphs split at sentence boundaries, then word
boundaries, then Unicode code points if needed. Original separators/order are stored separately.
Stable IDs use source fingerprints plus deterministic occurrence; ordinal is separate.
Source edits invalidate changed sources; insertion/reorder reuses unchanged segment proofs.

One document has a persistent 1,800-second wall-clock deadline from first execution, including
resume, and at most 1,024 model calls (128 segments x existing 8-call ceiling). Every external
preparation/generation call is reserved durably first; crashes consume reservations. Each
segment has at most 8 calls and 3 generation attempts per mode across resumes. Existing
120-second preparation and 60-second generation/verification deadlines remain unchanged.
Explicit resume can continue an environment-blocked segment only with remaining budget;
repeated identical failure blocks rather than being automatically retried. Dependency changes
start new segment evidence, but never reset the document deadline/total calls.

Document verification composes existing per-segment F04 hard semantic/fact/context checks
with deterministic exact segment order, source/output integrity, separator/paragraph structure,
required-information retention and whole-document explicit constraints. It never sends the
whole document to a model. This remains same-model second-pass semantic verification, not an
independent semantic oracle. Document constraints max_words/max_characters and required_literal
are checked globally; forbidden_literal and other semantic constraints also apply per segment.

Relevant personalization fingerprint includes exact-context DNA (excluding global revision),
selected examples and active preferences; unrelated context revision alone does not invalidate.
Model dependency includes exact digest, config/model policy and prompt/verifier/document contract.
Reading checkpoints revalidates the protected store and persisted integrity/dependencies.

IMPLEMENTATION_ATTEMPTS_USED: 1/2 (starts with the following first feature-code edit).
DIAGNOSIS_USED: 0/2. RECOVERY_USED: 0/1.
CHECKPOINT: authorization recorded; implementing migration/state first. No tests passed yet.


## Attempt 1 checkpoint - targeted evidence

Initial protected migration/state run: 3 passed in 18.81s. Extended deterministic/document
run: 17 passed in 20.57s. Schema 2 examples/feedback/preferences rows survive unchanged;
failed boundary recheck rolls back the entire migration; repeat migration is byte-idempotent.
A fresh process reads protected checkpoint state. EXPLAIN uses document_order, no temporary
sort. Segment enumeration/read-back are each one ordered/bulk query; batched changed rows
use executemany. Per-segment reservation and completion transactions are necessary for
failure-localized recovery, not N+1 result enumeration.

A segment operation reserves its remaining worst-case 8-call/3-attempt-per-mode capacity
before F03/F04 starts; only observed unused capacity is released on an atomic completion or
classified failure checkpoint. A crash retains the reservation. This avoids one ACL/SQLite
transaction per SQL/model statement while preserving crash-safe budgets. Hard verification
failures never restart with a fresh F03 pair; only classified environment failures may resume
within surviving budgets. F04 retains its own bounded classified repair rules unchanged.

Both targeted runs emitted a pytest cache-directory warning (WinError 183); test execution
passed. No cache/security policy changed. No real model calls, final regression/static cycle,
commit, push or PR yet. Historical blocked entry remains above. Counters 1/2, 0/2, 0/1.


OBSERVED: extended valid-feedback migration fixture produced no active preference.
EXPECTED: three independent explicitly classified style edits establish a valid historical
preference fixture before testing preservation.
FAILURE_CLASS: verification_defect (fixture omitted required style_expression hint).
EVIDENCE: 19 passed, 1 failed in 40.28s; existing F05 intentionally classifies unhinted edits
as mixed_unknown. This is correct product behavior, not a migration/learning defect.
NEXT ACTION: supply explicit style_expression hint in the fixture, preserving all assertions;
rerun affected targeted tests. No production repair or implementation attempt consumed.
BUDGET REMAINING: implementation1, diagnosis2, recovery1.


## Attempt 2 - bounded corrective implementation

OBSERVED: insertion/reorder fixture reused only 1 of 2 unchanged verified segments.
EXPECTED: reuse both unchanged source proofs; generate only the inserted paragraph.
FAILURE_CLASS: implementation defect - positional segment identity over-invalidates.
EVIDENCE: focused test failed (1 failed in 0.21s), reused_segments=1 instead of 2.
NEXT ACTION: bind stable IDs to source fingerprint plus deterministic occurrence, retain
ordinal separately for reassembly; lookup prior proofs by stable ID. No policy duplication.
BUDGET REMAINING after this repair starts: implementation0, diagnosis2, recovery1.
Current implementation counter is 2/2. Earlier 1/2 checkpoints remain historical.


Attempt 2 targeted result: 21 passed in 40.77s, including insertion/reorder reuse. Before the
repair, directly affected F03/F04/F05/F06 plus F07 run passed 92 in 195.10s. The subsequent
21-test F07 run verifies the only material correction. Valid historical schema-2 feedback
remains learning-readable and its active preferences/data unchanged after upgrade. A real
protected document blocked checkpoint is inspected in a fresh Python process, with exact
progress/calls/dependencies and no prose. A typing-only cast documents that \s* always matches;
it does not change runtime behavior. Current counters implementation2/2, diagnosis0/2,
recovery0/1. No implementation repairs remain authorized.

Final verification plan now starts: full configured pytest once, 900-second process ceiling;
Ruff/mypy/pip check once; real synthetic 2,000/5,000-word qualification with the fixed
1,800-second per-document deadline. Preserve all failures; no timeout/model/policy changes.


Final base reconciliation: fetched origin; HEAD/main/origin/main all remain
96afb4691dfb141601f3239b3d93f203294347d4. PR12 MERGED at that SHA; open PRs empty, one worktree.
The final real fixture uses coherent complete sentences, exactly 100 words per paragraph
(1 section label + 99 body words), before any provider acceptance observation. No source
prose is printed. Full regression is in progress; no result claimed yet.


Schema compatibility note: schema-2 examples and their writer_schema=2 CHECK are retained
verbatim as the unchanged example-row format marker. PRAGMA/store_meta schema version 3 and
exact schema validation establish the new writer boundary; old schema-2 writers reject it.
No examples-table rebuild, data conversion or learning/profile version increment is needed.
The acceptance-only progress observer prints metadata after canonical checkpoint commits;
it adds no SQL per returned item and no model calls or client-side product policy.


## Final regression / bounded diagnosis 1

Full configured pytest completed once: 265 passed, 2 failed in 416.24s (900s ceiling).
The complete tool output retains both tracebacks. Exact failing nodes:
- test_profile.py::test_invalid_source_or_version_never_returns_profile[schema-DATABASE_UNAVAILABLE_OR_CORRUPT]
- test_storage.py::test_unavailable_or_incompatible_store_has_no_mutation[future-version]
Both end with Failed: DID NOT RAISE StoreError (test_profile.py:187, test_storage.py:195).
Both wrote PRAGMA user_version=3 into a newly initialized valid schema-3 store, so neither
introduced the intended incompatible/future schema. All other 265 outcomes passed.

OBSERVED: former future-version probes now select the owner-authorized current schema.
EXPECTED: unknown future schema is rejected without mutation/profile derivation.
FAILURE_CLASS: verification_defect - stale future-schema fixture, not storage guard failure.
AUTHORITY: explicit owner schema 2->3 decision; unknown future versions still fail safely.
CORRECTION: change only these corruption inputs from 3 to 4; retain every rejection and
no-mutation assertion. Add tests/test_profile.py and tests/test_storage.py to declared write
set solely for these justified fixture literals. No production change or extra implementation
attempt. Diagnosis1/2 consumed identifying the common verifier defect; recovery0/1 unchanged.
NEXT ACTION: rerun only the two corrected checks, then static verification and real qualification.
Do not rewrite the historical full run as a pass or repeat its 265 unchanged passing checks.
BUDGET REMAINING: implementation0, diagnosis1, recovery1.


## Interrupted static-check continuation

Interruption preserved branch/head and all changes; no verification Python/pytest process
remained. No results from the interrupted static batch were recoverable and cache timestamps
preceded this task, so only those unconfirmed checks were executed on continuation. No
pytest rerun. Corrected future-schema checks had already passed: 2 in 7.59s.

Pip check PASSED; Python 3.14.6 AMD64 / SQLite runtime 3.50.4.
Ruff: four test-only findings (I001 import formatting, B008 constant UUID default,
PLR0402 import aliases). Mypy: storage.py:364 local Connection/None inference conflict.
FAILURE_CLASS: static verification defects, no product behavior failure.
CORRECTION: import normalization, move unchanged UUID default to module constant, and
explicit Connection|None annotation. No assertions, budgets or production behavior change.
Only failed static checks rerun; pip/pytest evidence retained. Material counters unchanged:
implementation2/2, diagnosis1/2, recovery0/1. Real provider acceptance has not begun.


Static corrections verified: Ruff affected test file has 0 remaining findings (3 import
fixes); the initial project/script scan had no other findings. Mypy PASSED (13 source files).
Pip check remains PASSED and is not rerun. No runtime behavior changed by these corrections.
Real qualification now begins once, configured ollama/qwen3:8b, synthetic 2,000 then 5,000
words; each document retains 1,800 seconds, the harness process ceiling is 3,660 seconds
(two document ceilings plus bounded startup/reporting allowance). No retries/substitution.
Stop on the first blocked result; preserve the protected synthetic checkpoint.


## Live acceptance checkpoint

Qualification process tool session 77637; protected synthetic state retained at
C:/Users/mamid/AppData/Local/Temp/personalstyle-f07-wk8mppl1/profile/profile.db.
First document ID b88169e5-4286-45c6-8289-da46dad5b83b: source 2,000 words, 20 segments.
Observed checkpoint: 3 verified, 15 model calls, no failure. No completion claim yet.
Use the authoritative inspect_document API to reconstruct progress after interruption;
do not launch a duplicate qualification or reset its persisted calls/deadline.


## Final blocked checkpoint - real qualification / diagnosis 2

Observed real configured-provider result (one cycle; no rerun/substitution):
- provider ollama; exact model qwen3:8b; Ollama runtime 0.40.1; num_ctx 8000.
- full digest 500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41.
- synthetic source 2,000 words / 20 segments; 19 VERIFIED, segment ordinal19 BLOCKED.
- 97 model calls, zero repair generations; elapsed 788.142s / document ceiling1,800s.
- failure code GENERATION_RESOURCE_LIMIT; whole_document_verification not_verified.
- failed segment calls2, attempts generic1/personalized0: preparation completed, then the
  normal generic provider operation failed under the unchanged60-second ceiling.
- canonical learning/profile/examples/feedback/preferences unchanged; normal logs contain
  no source/example/output content. Only authorized operational checkpoints were written.
- 5,000-word real case NOT RUN because the cycle stops at its first blocked result.

Diagnosis2/2 is a single metadata-only fresh-process inspection, no model/network call or
profile mutation. It revalidates protected checkpoints/integrity, reconstructs19/20 progress,
exact identity/calls/failed phase and observes902.890s remaining on the persisted document
clock. Verified segments' generic operation mean2.378s/max2.657s; personalized mean2.421s/
max2.719s. The60-second failure is real; these timings do not establish its underlying cause.
No hardware unsuitability, general model incompatibility or concrete root cause is claimed.
No retry, timeout increase, model change, feature repair or state reset performed.

OBSERVED: segment20 generic operation returns GENERATION_RESOURCE_LIMIT; earlier19 survive.
EXPECTED: all20 segments and assembly verification complete, then5,000-word qualification.
FAILURE_CLASS: environment/runtime operation deadline failure; underlying cause unresolved.
EVIDENCE: real acceptance JSON plus fresh-process metadata inspection above. The document-wide
1,800s ceiling was not exhausted. Existing per-operation preparation120s/generation60s intact.
BUDGET USED: implementation2/2; diagnosis2/2; recovery0/1.
BUDGET REMAINING: implementation0; diagnosis0; recovery1 (not permission for identical retry).
NEXT PERMITTED ACTION: owner reviews this timeout evidence and selects a bounded environment
recovery with materially changed information, preserving the19 valid checkpoints. No F08.

Acceptance status: AC3-AC13 have targeted/deterministic/migration/compatibility evidence as
recorded above, including executed synthetic2,000/5,000 inputs, failure/resume, single-source
edit and insertion/reorder reuse. Real AC1 is NOT PASSING and real AC2 is NOT RUN; no verified
assembled real document exists. Therefore F07 is NOT COMPLETE / NOT MERGE-READY.
Local regression history remains265 passed/2 stale-verifier failures in416.24s, then the two
justified corrected probes passed in7.59s. It is not restated as a clean267-test full run.
Ruff and mypy corrections passed; pip check passed. GitHub F07 CI NOT RUN: no committed F07
head or PR exists. Existing Phase A CI is historical evidence only.

All five original activation documents/history and subsequent F07 work remain uncommitted
on task/f07-long-document at96afb4691dfb141601f3239b3d93f203294347d4. No commit/push/PR was
created because locally passing completion was not reached. Protected synthetic checkpoints
remain at the path above. Overall Windows alpha incomplete; F08/Phase B unstarted.


## Owner-authorized recovery 1/1

Authority: explicit project-owner continuation. Implementation remains2/2, diagnosis2/2;
recovery now1/1. No historical failure/counter reset. Owner additionally authorizes one
clean full regression after both repaired real acceptances pass, because the previous
full run was not clean. Current task write set adds tests/test_provider.py and no new
architecture/dependency/schema surface beyond the already authorized schema3 checkpoint.

Inspected actual composition: per segment preparation1 + generic1 + personalized1 + two
F04 hard semantic checks =5 normal calls, maximum8 and three generations/mode unchanged.
Saved source665 bytes, framing1472, num_ctx8000. Earlier full run elapsed788.142s including
failed final operation; verified generation means2.378s/2.421s, most elapsed time is outside
those two generation calls. Old50-segment/250-call5,000-word projection lacks safe margin.

Selected coherent repair: deterministic adjacent-paragraph coalescing up to1,400 source
UTF-8 bytes, preserving source separators/order and all per-paragraph protected information;
plus an explicit F07 provider operation ceiling120s capped by remaining document time.
Existing short-text provider.generate remains capped60s; preparation stays120s, document
stays1,800s. No call/repair count increase, no removal of any F04 check or generic baseline.
F03/F04 remain the owners of generation/verification; F07's adapter chooses the explicitly
bounded long-document provider method. No automatic retry is added.

This changes segmentation/provider execution dependency: new long_document.v2 contract.
Existing19 proofs must be marked STALE and retained with their source/output/evidence/calls/
original deadline. They cannot be reused for new groups or have their deadline renewed.
Repaired qualification is a new explicitly authorized contract/run, not continuation with
reset old counters. Existing storage schema remains3; product/protocol/config/profile/prompt
versions remain0.1.0/1.0/1/1/1. SYSTEM/VERIFY_SYSTEM strings and hard check semantics unchanged.

Before live work, execute affected targeted tests and a protected synthetic-provider overhead
measurement. Record exact prompt sizes,10 expected segments/50 normal calls for2,000 words;
25 expected segments/125 normal calls for5,000; maximum80/200 calls respectively. Only launch
if measured overhead plus conservative scaling of prior model time has credible margin below
1,800s. Per-call maximum120s, preparation120s, all capped/guarded by remaining document budget.
Do not extend any ceiling after observing the repaired live results. Stop on first block.


Recovery affected tests: initial sandbox invocation47 passed/23 setup errors from pytest
user temp access; classified sandbox environment mismatch, no product assertions failed.
Same tests under real Windows account70 passed in42.52s. Cache creation warning remains
non-fatal. No ACL weakening, temp deletion or system configuration change.
The fixed F07 paragraph/order instruction is an additive long_document.v2 composition,
tracked separately from unchanged F03 prompt_contract1 and hard_verification.v1; it is
included in the existing conservative UTF-8 input/framing bound, not hidden outside it.
Paragraph-aligned deterministic fact checks plus existing group semantic checks enforce
correspondence; no hard check removed. Full regression not rerun yet; live not started.

Focused framing test initially failed because its minimal fixture omitted the digest dependency
required by prepare. Classified verification_fixture_defect; supplied the existing digest,
without changing production behavior or assertions. Feasibility/live were not launched.


Recovery pre-live evidence: corrected framing fixture1 passed0.09s; coalesced synthetic
400-word protected run2 segments/10 calls VERIFIED in17.530s, fixed overhead8.765s/group.
Actual largest prompt upper bound5,110 bytes including fixed structure instruction and
framing, ceiling6,000; num_ctx8,000/output2,000 unchanged.2,000=>10 groups/50 normal/80 max
calls;5,000=>25 groups/125 normal/200 max. Operation120s, preparation120s, document1,800s.
Forecast uses prior normal elapsed estimate(788.142-60)/19=38.323s and doubles its estimated
model-dependent portion for doubled source size, retaining measured fixed overhead once:
25*(8.765+2*(38.323-8.765))=1,697.035s. This is feasibility evidence with limited margin,
not a guaranteed pass or relaxed timeout. Live cycle must stop on its first blocked result.
Historical original store was updated through the protected authoritative writer:
19 proofs nowSTALE, evidence/output retained unchanged, calls97 and original deadline exactly
preserved; manifest failureDOCUMENT_CONTRACT_SUPERSEDED/whole-document stale. No old budget
reset or evidence reused for v2. Real recovery qualification is a new authorized v2 run.

Recovery live cycle started; tool process session77795, synthetic protected root
C:/Users/mamid/AppData/Local/Temp/personalstyle-f07-osl9og7_. Outer process ceiling3,660s,
each document1,800s;2,000 first,5,000 only after complete verified2,000. No duplicate
qualification/resume or deadline reset is authorized if this turn is interrupted.


## Recovery 1/1 final blocked checkpoint

OBSERVED: first coalesced real segment fails DOCUMENT_STRUCTURE_INVALID after existing
F03 generation and F04 second-pass verification. The deterministic source/output paragraph
separator lists differ. No candidate is returned as verified. Accepted-output/evidence fields
are intentionally empty on this failed segment; the exact rejected prose is not logged.
EXPECTED: every segment preserves its declared paragraph boundaries and passes all gates;
complete2,000-word assembly before beginning5,000-word qualification.
FAILURE_CLASS: implementation/runtime structural-contract mismatch at the F07/F04 boundary.
EVIDENCE: one authorized repaired real cycle; no identical rerun or model substitution.
NEXT ACTION: stop for an owner-authorized bounded correction decision; no remaining repairs.
BUDGET REMAINING: implementation0/2; diagnosis0/2; recovery0/1.

Executed real recovery evidence:
- exact provider/model: ollama/qwen3:8b.
- full digest:500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41.
- source2,000 words,10 deterministic coalesced segments,0 verified segments.
- model calls5; repair/retry generations0; elapsed27.397s.
- per-operation120s, preparation120s, document1,800s, no ceiling increase.
- stateBLOCKED, failureDOCUMENT_STRUCTURE_INVALID, whole-document not_verified.
- canonical learning/profile/examples/feedback/preferences unchanged; normal logs sensitive-free.
- current run has no persisted verified model receipt, so runtime_versions is empty in its
  summary. Historical inspected runtime0.40.1 remains historical evidence, not a newly
  reconstructed successful receipt.
- document33c24b4a-47ea-425a-877c-f2535c9209ef persists in the protected recovery root above.
-5,000-word live case NOT RUN: qualification stopped at the first blocked result.

Architectural blocker: coalescing introduces internal paragraph-correspondence constraints.
The existing F04 semantic pass can accept a rewrite that the subsequent deterministic F07
separator check rejects. This structural failure currently occurs outside F04's classified
repair loop and therefore terminates the segment. Adding a longer provider deadline and
reducing segment count alone does not establish reliable structure-preserving generation.
No further correction, separator-rule weakening or additional model call is authorized by
this exhausted recovery. A future owner decision must bound any integration of document
structural failures with repair while preserving existing verification/call/attempt limits.

All19 prior verified proofs remain preserved as STALE with their exact output/evidence,
97 calls and original deadline. No stale proof was reused for v2, no old budget reset.
The new failed checkpoint remains independently inspectable; unrelated canonical state
was not changed. Implementation2/2, diagnosis2/2, recovery1/1 consumed, history retained.
Targeted recovery evidence70 passed42.52s plus framing/coalescing checks and corrected
framing fixture as recorded above. The clean final full regression and static/CI completion
cycle were NOT RUN because both required live acceptances did not pass. Earlier full-run
265-pass/2-failure history and isolated corrections remain unchanged, not a clean full pass.

F07 NOT COMPLETE / NOT LOCALLY PASSING / NOT MERGE-READY. No commit, push or draft PR
created, because the locally passing completion guard was not reached. No F08, Phase B or
other product task started. One next permitted action: owner reviews this structural failure
and explicitly authorizes or declines a new bounded correction; no autonomous continuation.


## Exceptional owner-authorized structural correction

Owner explicitly authorizes exactly one structural integration correction, separate from
exhausted implementation2/2, diagnosis2/2 and recovery1/1. STRUCTURAL_CORRECTION0/1 until
first feature edit, then1/1. No counters/history reset, further tuning or general optimization.
Observed v2 failure27.397s/5 calls remains a failure. Scope: remove dependence on model-produced
paragraph separators by an ordered JSON unit contract, retaining F04 and whole-document gates.

Chosen minimal design long_document.v3: source paragraphs receive engine-owned u0/u1/... IDs
in source order. Generation/repair returns {units:[{id,text},...]}, using Ollama's supported
JSON-schema format (https://docs.ollama.com/capabilities/structured-outputs). Strict engine
validation rejects duplicate JSON keys, missing/extra/duplicated/reordered IDs, empty units,
and new paragraph separators inside units. Source separators are reconstructed exactly;
rewritten prose remains untrusted until existing F04 information/semantic/constraint/context
checks pass. Persist unit IDs/source and accepted-output fingerprints with segment evidence;
no new tables, schema change or client behavior. Whole-document verification rechecks this
mapping and source-derived assembly. Short-text prompt/output/provider behavior unchanged.
The F07 additive prompt/output contract is separately versioned v3; no global F03 prompt1
change. Input/context/output bounds include encoding/instructions, no hidden retries.
Existing generated v1/v2 evidence/checkpoints must be marked stale without losing original
calls/deadlines/failure/proofs. Targeted suite must pass before live; any targeted/live/final
required failure stops this exhausted exceptional cycle. Live2,000 then5,000 only on pass;
model8B, operation120s, document1,800s, generation/repair call budgets unchanged.

First material structural-contract edit begins now: exceptional STRUCTURAL_CORRECTION1/1
consumed. Historical implementation2/2, diagnosis2/2, recovery1/1 remain unchanged.

The v2 plaintext-output rejection test now expects DOCUMENT_STRUCTURE_INVALID at the
structured decoder, earlier than F04, because plaintext is no longer a legal document
wire response. This is a contract/version correction, not acceptance weakening. Echo wire
fixtures now return units for document requests and retain plaintext for short-text calls.
Unit edge whitespace is normalized; paragraph separators are always authoritative source
metadata. Internal new paragraph separators remain forbidden. Supported structured format
is used only by the explicit document method; short-text and semantic response contracts
are unchanged. Targeted run below is the sole correction gate; no live calls yet.


Exceptional targeted gate PASSED:122 tests in130.89s (F07/document, provider, generation,
verification). Covers schema2->3 migration/data survival/rollback/idempotency, durable
restart/budgets/failure-localized resume, local/dependency invalidation, ordered unit mapping,
missing/duplicate/reordered/merged/split/extra units and duplicate JSON-key rejection,
source-derived separator reconstruction, both existing F04 semantic calls and unchanged
short-text provider deadlines/format. Existing non-fatal pytest cache warning persists.
No targeted failure/correction rerun in this exceptional cycle. Live eligibility now passed;
next is one configured-provider2,000 then5,000 cycle, stopping on first blocked result.

Exceptional live process session24926. One bounded cycle only; do not restart/duplicate
if interrupted. Historical v1 run97 calls/deadline/evidence preserved, all20 generated
segments nowSTALE (including failed last segment; original failure retained).

Exceptional live protected root:C:/Users/mamid/AppData/Local/Temp/personalstyle-f07-rp7k21kp.
2,000-word document60c77670-222c-4dbb-ab8c-6264e303c425: first checkpoint1/10 VERIFIED,
5 calls; no completion claim. v2 failed run retained5 calls/deadline/failure, oneSTALE segment.

Live v3 checkpoint:2,000-word document7/10 VERIFIED,35 observed calls, no failure.
Process/session24926 remains active; no duplicate acceptance or budget reset on resume.


Exceptional real2,000-word acceptance PASSED: document60c77670-222c-4dbb-ab8c-6264e303c425,
long_document.v3,10/10 verified segments,50 calls,0 repairs/retries,466.375s of1,800s,
operation120s/preparation120s. Whole-document verification VERIFIED. Exact ollama/qwen3:8b,
digest500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41, runtime0.40.1;
observed conservative input upper bound4,830/6,000. Canonical learning state unchanged;
ordinary logs sensitive-free. Same bounded cycle proceeds to5,000; no completion claim yet.

Same-cycle5,000-word documenteef4c181-93d8-4b97-88a3-3e7c602cf1b5 started;
2/25 VERIFIED,10 calls, no failure. Protected root/session unchanged; do not duplicate.

Long-running live checkpoint:5,000-word v3 document7/25 VERIFIED,35 calls, no failure;
session24926 active.2,000-word final evidence remains passing. No extra model call,
repair cycle, timeout increase, full regression, static rerun or new task launched.

Ongoing v3 real5,000-word checkpoint15/25 VERIFIED,75 calls, no failure; same
documenteef4c181-93d8-4b97-88a3-3e7c602cf1b5 / process24926 / protected root above.
No new correction or run is authorized; continue observing this process on interruption.


Exceptional real5,000-word acceptance PASSED: documenteef4c181-93d8-4b97-88a3-3e7c602cf1b5,
long_document.v3,25/25 verified segments,125 calls,0 repairs/retries,1,415.205s of1,800s,
operation120s/preparation120s. Whole-document verification VERIFIED. Same exact ollama/qwen3:8b,
digest500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41, runtime0.40.1;
input upper bound4,830/6,000. Canonical learning state unchanged; normal logs sensitive-free.
Single authorized two-document cycle exited0; no further live call required/authorized.
Both historical failed real cycles remain failures above. All counters unchanged except the
explicit exceptional correction1/1. Next: reconcile current main, one clean configured full
pytest under900s, static checks, then commit/push/one draft PR and exact-head CI if all pass.
Migration/checkpoint cases are part of the targeted and complete configured suite; do not
repeat unchanged passing cases merely to create duplicate evidence. F07 not yet locally
passing until clean full/static final evidence exists; GitHub CI not yet run for F07.

Final base/WIP reconciliation: fetched origin; HEAD/main/origin/main/merge-base all
96afb4691dfb141601f3239b3d93f203294347d4; one worktree, no open PRs. No merge conflict
or unrelated change to reconcile. Final clean configured pytest started once, session40699,
900s ceiling, followed sequentially by Ruff/mypy/pip/whitespace only on pass. Do not rerun
on interruption; preserve/retrieve this process result. No live model process remains.


## Exceptional correction final checkpoint - regression blocked

STRUCTURAL_CORRECTION1/1 consumed. Historical implementation2/2, diagnosis2/2,
recovery1/1 unchanged/exhausted. No new repair, diagnosis or recovery cycle performed.

OBSERVED: single clean configured full pytest completes285 passed/1 failed in555.54s,
inside900s ceiling. Failing test:
tests/test_protocol.py::test_pre_dispatch_rejections[value13-headers13-REQUEST_RESOURCE_LIMIT].
The deliberately oversized Content-Length73729 handshake request fails in the test client's
connection.getresponse()/socket.recv_into with ConnectionAbortedError [WinError10053].
EXPECTED: explicit REQUEST_RESOURCE_LIMIT response, with no protected engine dispatch.
FAILURE_CLASS: protocol transport verification failure; implementation/environment/verifier
root cause UNKNOWN. Unchanged protocol source/test alone does not prove a pre-existing or
flaky failure. No isolation/rerun or root-cause investigation is authorized/performed.
EVIDENCE: complete regression result and redacted traceback below. The previous historical
265-pass/2-failure full run remains failed; current285-pass/1-failure run also is NOT a pass.
NEXT ACTION: owner decides whether to authorize a separate bounded diagnosis/correction of
this exact protocol rejection failure. No further automatic correction or verification.
BUDGET REMAINING: implementation0; diagnosis0; recovery0; exceptional structural correction0.

Both v3 real cases remain passing as measured above:2,000 words466.375s/50 calls/10 segments;
5,000 words1,415.205s/125 calls/25 segments, no repairs, whole-document verification passed,
exact qwen3:8b digest, no canonical learning mutation or normal sensitive-content logging.
Targeted122 tests passed130.89s, including migration/checkpoint compatibility. No feature
changes were made after those tests/live runs. Structural correction resolved the observed
paragraph-whitespace dependency in executed acceptance; it does NOT waive regression.

Sequential final gate stopped on pytest exit1. Ruff/mypy/pip check NOT RUN for this corrected
revision; earlier checks are historical only. Required F07 CI NOT RUN; no commit/push/PR
created because local completion failed. Existing main/base unchanged96afb469...;
all bounded work and protected checkpoints preserved. F07 remains blocked/not complete/
not merge-ready. F08 and S03 Phase B remain not_started.

Pytest's failure diagnostic automatically displayed its synthetic session-only fixture
credential. It is redacted from durable evidence below; the test server/session ended with
fixture teardown, so that credential has no continuing authority. Do not copy it into task
records, PRs or logs. This is distinct from the passing live normal-log capture. No user
credential, user writing, prompt or output is included in this traceback.

Complete regression traceback evidence follows (ephemeral credential redacted):

```text
............................   [100%]
================================== FAILURES ===================================
___ test_pre_dispatch_rejections[value13-headers13-REQUEST_RESOURCE_LIMIT] ____

boundary = (<personalstyle.protocol.EngineServer object at 0x00000179CD8A3B90>, <test_protocol.SpySession object at 0x00000179CEBDB110>, '<REDACTED_SESSION_CREDENTIAL>')
value = {'protocol_version': '1.0', 'client_version': '0.1.0', 'client_kind': 'desktop', 'requested_capability': 'handshake', ...}
headers = {'Content-Length': '73729'}, code = 'REQUEST_RESOURCE_LIMIT'

    @pytest.mark.parametrize("value,headers,code", [
        (envelope(protocol_version="2.0"), {}, "PROTOCOL_MAJOR_INCOMPATIBLE"),
        (envelope("sqlite.write"), {}, "CAPABILITY_UNSUPPORTED"),
        (envelope(client_kind="browser"), {}, "ORIGIN_CALLER_REJECTED"),
        (envelope(), {"Origin": "https://example.com"}, "ORIGIN_CALLER_REJECTED"),
        (envelope(), {"Origin": ""}, "ORIGIN_CALLER_REJECTED"),
        (envelope(protocol_version="1"), {}, "REQUEST_MALFORMED"),
        (envelope(client_version="bad"), {}, "REQUEST_MALFORMED"),
        (envelope(payload={"database_path": "other.db"}), {}, "REQUEST_MALFORMED"),
        (envelope("rewrite", {"verified": True}), {}, "REQUEST_MALFORMED"),
        (envelope("preference.evaluate", {"context": "*"}), {}, "REQUEST_MALFORMED"),
        (envelope("feedback.write", {"run_id": str(uuid4()), "event": {}, "receipt": {}}), {}, "REQUEST_MALFORMED"),
        (envelope(), {"Content-Encoding": "gzip"}, "REQUEST_MALFORMED"),
        (envelope(), {"Transfer-Encoding": "chunked"}, "REQUEST_MALFORMED"),
        (envelope(), {"Content-Length": str(MAX_BODY_BYTES + 1)}, "REQUEST_RESOURCE_LIMIT"),
    ])
    def test_pre_dispatch_rejections(boundary, value, headers, code):
        server, session, token = boundary
>       status, body = request(server, token, value, headers=headers)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_protocol.py:118:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
tests\test_protocol.py:56: in request
    response = connection.getresponse()
               ^^^^^^^^^^^^^^^^^^^^^^^^
..\AppData\Local\Programs\Python\Python314\Lib\http\client.py:1459: in getresponse
    response.begin()
..\AppData\Local\Programs\Python\Python314\Lib\http\client.py:336: in begin
    version, status, reason = self._read_status()
                              ^^^^^^^^^^^^^^^^^^^
..\AppData\Local\Programs\Python\Python314\Lib\http\client.py:297: in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <socket.SocketIO object at 0x00000179CEBF5540>
b = <memory at 0x00000179CEAD0940>

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.

        If *b* is non-empty, a 0 return value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        if self._timeout_occurred:
            raise OSError("cannot read from timed out object")
        try:
>           return self._sock.recv_into(b)
                   ^^^^^^^^^^^^^^^^^^^^^^^
E           ConnectionAbortedError: [WinError 10053] An established connection was aborted by the software in your host machine

..\AppData\Local\Programs\Python\Python314\Lib\socket.py:729: ConnectionAbortedError
============================== warnings summary ===============================
.venv\Lib\site-packages\_pytest\cacheprovider.py:469
  C:\Users\mamid\personalstyle\.venv\Lib\site-packages\_pytest\cacheprovider.py:469: PytestCacheWarning: could not create cache path C:\Users\mamid\personalstyle\.pytest_cache\v\cache\nodeids: [WinError 183] Cannot create a file when that file already exists: 'C:\\Users\\mamid\\personalstyle\\.pytest_cache\\v\\cache'
    config.cache.set("cache/nodeids", sorted(self.cached_nodeids))

.venv\Lib\site-packages\_pytest\cacheprovider.py:423
  C:\Users\mamid\personalstyle\.venv\Lib\site-packages\_pytest\cacheprovider.py:423: PytestCacheWarning: could not create cache path C:\Users\mamid\personalstyle\.pytest_cache\v\cache\lastfailed: [WinError 183] Cannot create a file when that file already exists: 'C:\\Users\\mamid\\personalstyle\\.pytest_cache\\v\\cache'
    config.cache.set("cache/lastfailed", self.lastfailed)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED tests/test_protocol.py::test_pre_dispatch_rejections[value13-headers13-REQUEST_RESOURCE_LIMIT]
1 failed, 285 passed, 2 warnings in 555.54s (0:09:15)

```


## Owner-authorized final-regression diagnosis1/1

Authority: explicit owner continuation; consume exceptional FINAL_REGRESSION_DIAGNOSIS1/1.
Historical implementation2/2, diagnosis2/2, recovery1/1, structural correction1/1 unchanged.
No production/test/config edits authorized or performed in this diagnosis. Both real v3
acceptances remain valid and will not be rerun. Owner conditionally authorizes one900s final
regression recovery only if the exact isolated test and smallest relevant protocol subset pass.

Non-modifying inspection against main96afb469...: protocol.py/test_protocol.py/security.py/
generation.py/verification.py/learning.py/pyproject.toml unchanged. Protocol setup, Timer,
shutdown, credential/authentication, ingress timeout60 and MAX_BODY_BYTES73728 unchanged.
Config only requires storage3; storage adds schema3/checkpoints, feedback accepts historical
source versions2/3, provider adds explicit document generation/format. None is invoked by the
failing boundary fixture: ExampleStore.__init__ only retains an absolute never-opened path,
SpySession only dispatches after validation, and the rejected oversized handshake has no
provider/database operation. F07 document.py is not imported by protocol startup.

Exact rejection path: authenticated Content-Length73729 exceeds73728; do_POST raises413
REQUEST_RESOURCE_LIMIT before reading the body or dispatching. _reply emits bounded JSON
with Connection:close, then the standard HTTP server closes the socket. Test supplies a small
JSON body while advertising73729. Unread-body close/reset is a plausible Windows transport
mechanism, NOT an established root cause. No diagnosis probe beyond the authorized isolated
case/subset is performed. Next: exact failing case once; capture traceback/stderr with any
ephemeral fixture credential redacted. No feature/test changes or live generation.


Diagnosis result: exact oversized case passed1 in0.25s; relevant protocol subset passed21
in2.48s (all pre-dispatch rejections, malformed JSON, authenticated handshake/revocation,
absolute ingress timeout, and real server startup/shutdown assertions). protocol.py and
test_protocol.py remain unchanged from merged main. No provider/storage call occurred in
these rejected requests. No production/test/config changes between diagnosis and recovery.
Classification: non-reproduced Windows transport failure, consistent with a transient;
root cause remains unconfirmed. This does not establish F07 passing or prove a protocol fix.

Owner conditional authorization is satisfied. Consume FINAL_REGRESSION_RECOVERY1/1 for
exactly one full configured pytest execution,900s ceiling. Preserve the285/1 failure above.
No further full-suite retry, feature correction, or live long-document acceptance authorized.
Static gates follow only if this single full regression passes.

## Exceptional final-regression recovery1/1 - blocked

The single owner-authorized full configured pytest recovery completed with **285 passed,
1 failed in421.15s**, wall421.447s, within the unchanged900s ceiling. No production/test/
configuration change occurred between diagnosis and this recovery. No real model acceptance
was rerun. Exact oversized case1 passed0.25s and protocol subset21 passed2.48s remain
historical diagnosis evidence; they do not erase either full-suite failure.

OBSERVED: test_pre_dispatch_rejections[value3-headers3-ORIGIN_CALLER_REJECTED] failed with
WinError10053 in HTTPConnection.getresponse -> HTTPResponse.begin -> socket.recv_into.
EXPECTED: structured ORIGIN_CALLER_REJECTED response before engine execution.
FAILURE_CLASS: repeated pre-dispatch transport failure; root cause unknown. The original
oversized rejection and now Origin rejection share connection-abort symptoms. Classification
as a one-off/transient is insufficient after this recurrence; this does not prove an
F07-introduced regression or a specific Windows/server defect.
EVIDENCE: both protocol.py and test_protocol.py unchanged from main96afb469...; no database/
provider call in these pre-dispatch fixtures. Original285/1 failure and redacted traceback
above preserved; current complete redacted output below. No server traceback was reported.
NEXT ACTION: owner decision authorizing a bounded P01 pre-dispatch transport investigation/
repair; no further diagnosis, implementation, recovery or full-suite rerun authorized now.
BUDGET REMAINING: implementation0/2; diagnosis0/2; recovery0/1; structural correction0/1;
exceptional final-regression diagnosis0/1; exceptional final-regression recovery0/1.

F07 remains blocked, not locally passing. Live v3 2,000-word466.375s and5,000-word1415.205s
acceptances, all durable checkpoints, stale historical proofs, migration/checkpoint targeted
evidence and every earlier failure remain preserved. Ruff/mypy/pip final checks not run:
sequential final gate stopped at pytest exit1. No commit/push/PR/merge; F08 and S03 Phase B
remain not_started. Base reconciliation during this recovery again found HEAD/main/origin/main
and merge-base96afb4691dfb141601f3239b3d93f203294347d4; one worktree, no open PR.

Complete recovery output (ephemeral credentials redacted):

```text
........................................................................ [ 25%]
............................................................F........... [ 50%]
........................................................................ [ 75%]
......................................................................   [100%]
================================== FAILURES ===================================
____ test_pre_dispatch_rejections[value3-headers3-ORIGIN_CALLER_REJECTED] _____

boundary = (<personalstyle.protocol.EngineServer object at 0x0000016CE8F5B650>, <test_protocol.SpySession object at 0x0000016CE90090F0>, '<REDACTED_SESSION_CREDENTIAL>')
value = {'protocol_version': '1.0', 'client_version': '0.1.0', 'client_kind': 'desktop', 'requested_capability': 'handshake', ...}
headers = {'Origin': 'https://example.com'}, code = 'ORIGIN_CALLER_REJECTED'

    @pytest.mark.parametrize("value,headers,code", [
        (envelope(protocol_version="2.0"), {}, "PROTOCOL_MAJOR_INCOMPATIBLE"),
        (envelope("sqlite.write"), {}, "CAPABILITY_UNSUPPORTED"),
        (envelope(client_kind="browser"), {}, "ORIGIN_CALLER_REJECTED"),
        (envelope(), {"Origin": "https://example.com"}, "ORIGIN_CALLER_REJECTED"),
        (envelope(), {"Origin": ""}, "ORIGIN_CALLER_REJECTED"),
        (envelope(protocol_version="1"), {}, "REQUEST_MALFORMED"),
        (envelope(client_version="bad"), {}, "REQUEST_MALFORMED"),
        (envelope(payload={"database_path": "other.db"}), {}, "REQUEST_MALFORMED"),
        (envelope("rewrite", {"verified": True}), {}, "REQUEST_MALFORMED"),
        (envelope("preference.evaluate", {"context": "*"}), {}, "REQUEST_MALFORMED"),
        (envelope("feedback.write", {"run_id": str(uuid4()), "event": {}, "receipt": {}}), {}, "REQUEST_MALFORMED"),
        (envelope(), {"Content-Encoding": "gzip"}, "REQUEST_MALFORMED"),
        (envelope(), {"Transfer-Encoding": "chunked"}, "REQUEST_MALFORMED"),
        (envelope(), {"Content-Length": str(MAX_BODY_BYTES + 1)}, "REQUEST_RESOURCE_LIMIT"),
    ])
    def test_pre_dispatch_rejections(boundary, value, headers, code):
        server, session, token = boundary
>       status, body = request(server, token, value, headers=headers)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_protocol.py:118:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

server = <personalstyle.protocol.EngineServer object at 0x0000016CE8F5B650>
token = '<REDACTED_SESSION_CREDENTIAL>'
value = {'protocol_version': '1.0', 'client_version': '0.1.0', 'client_kind': 'desktop', 'requested_capability': 'handshake', ...}
raw = None, headers = {'Origin': 'https://example.com'}, path = '/v1'

    def request(server, token, value=None, *, raw=None, headers=None, path="/v1"):
        wire = json.dumps(envelope() if value is None else value).encode() if raw is None else raw
        fields = {"Content-Type": "application/json"}
        if token is not None:
            fields["Authorization"] = "Bearer " + token
        fields.update(headers or {})
        connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=60)
        try:
            connection.request("POST", path, wire, fields)
>           response = connection.getresponse()
                       ^^^^^^^^^^^^^^^^^^^^^^^^

tests\test_protocol.py:56:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <http.client.HTTPConnection object at 0x0000016CE7C7BD50>

    def getresponse(self):
        """Get the response from the server.

        If the HTTPConnection is in the correct state, returns an
        instance of HTTPResponse or of whatever object is returned by
        the response_class variable.

        If a request has not been sent or if a previous response has
        not be handled, ResponseNotReady is raised.  If the HTTP
        response indicates that the connection should be closed, then
        it will be closed before the response is returned.  When the
        connection is closed, the underlying socket is closed.
        """

        # if a prior response has been completed, then forget about it.
        if self.__response and self.__response.isclosed():
            self.__response = None

        # if a prior response exists, then it must be completed (otherwise, we
        # cannot read this response's header to determine the connection-close
        # behavior)
        #
        # note: if a prior response existed, but was connection-close, then the
        # socket and response were made independent of this HTTPConnection
        # object since a new request requires that we open a whole new
        # connection
        #
        # this means the prior response had one of two states:
        #   1) will_close: this connection was reset and the prior socket and
        #                  response operate independently
        #   2) persistent: the response was retained and we await its
        #                  isclosed() status to become true.
        #
        if self.__state != _CS_REQ_SENT or self.__response:
            raise ResponseNotReady(self.__state)

        if self.debuglevel > 0:
            response = self.response_class(self.sock, self.debuglevel,
                                           method=self._method)
        else:
            response = self.response_class(self.sock, method=self._method)

        try:
            try:
>               response.begin()

..\AppData\Local\Programs\Python\Python314\Lib\http\client.py:1459:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <http.client.HTTPResponse object at 0x0000016CE7CBB5B0>

    def begin(self):
        if self.headers is not None:
            # we've already started reading the response
            return

        # read until we get a non-100 response
        while True:
>           version, status, reason = self._read_status()
                                      ^^^^^^^^^^^^^^^^^^^

..\AppData\Local\Programs\Python\Python314\Lib\http\client.py:336:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <http.client.HTTPResponse object at 0x0000016CE7CBB5B0>

    def _read_status(self):
>       line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

..\AppData\Local\Programs\Python\Python314\Lib\http\client.py:297:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <socket.SocketIO object at 0x0000016CE90EA3E0>
b = <memory at 0x0000016CE8FC0880>

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.

        If *b* is non-empty, a 0 return value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        if self._timeout_occurred:
            raise OSError("cannot read from timed out object")
        try:
>           return self._sock.recv_into(b)
                   ^^^^^^^^^^^^^^^^^^^^^^^
E           ConnectionAbortedError: [WinError 10053] An established connection was aborted by the software in your host machine

..\AppData\Local\Programs\Python\Python314\Lib\socket.py:729: ConnectionAbortedError
============================== warnings summary ===============================
.venv\Lib\site-packages\_pytest\cacheprovider.py:469
  C:\Users\mamid\personalstyle\.venv\Lib\site-packages\_pytest\cacheprovider.py:469: PytestCacheWarning: could not create cache path C:\Users\mamid\personalstyle\.pytest_cache\v\cache\nodeids: [WinError 183] Cannot create a file when that file already exists: 'C:\\Users\\mamid\\personalstyle\\.pytest_cache\\v\\cache'
    config.cache.set("cache/nodeids", sorted(self.cached_nodeids))

.venv\Lib\site-packages\_pytest\cacheprovider.py:423
  C:\Users\mamid\personalstyle\.venv\Lib\site-packages\_pytest\cacheprovider.py:423: PytestCacheWarning: could not create cache path C:\Users\mamid\personalstyle\.pytest_cache\v\cache\lastfailed: [WinError 183] Cannot create a file when that file already exists: 'C:\\Users\\mamid\\personalstyle\\.pytest_cache\\v\\cache'
    config.cache.set("cache/lastfailed", self.lastfailed)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED tests/test_protocol.py::test_pre_dispatch_rejections[value3-headers3-ORIGIN_CALLER_REJECTED]
1 failed, 285 passed, 2 warnings in 421.15s (0:07:01)
FINAL_REGRESSION_RECOVERY_WALL_SECONDS: 421.447
```



## Owner-authorized P01 transport investigation/repair

Authority: owner continuation authorizes one bounded transport cycle only. All F07 counters
and historical failures remain unchanged. P01_TRANSPORT_REPAIR0/1; consume1/1 only when
production repair begins after concrete mechanism classification. Extend declared write set
only with src/personalstyle/protocol.py and tests/test_protocol.py for the required transport
repair/regression tests. No security/body/model limits, Origin policy, engine dispatch, retry
policy or F07 behavior change authorized. No live long-document acceptance rerun.

Inspection: every reply sets exact JSON Content-Length and Connection:close. wfile uses
stdlib unbuffered socket writer; finish flushes and closes it, then TCPServer.shutdown_request
performs SHUT_WR and close. Early Origin/auth/header/oversize rejection does not consume
body; JSON/envelope rejection consumes declared bounded body first. Test HTTPConnection
sends headers/body before getresponse, opens a fresh connection per request, never reuses it.
Existing absolute ingress Timer60 can SHUT_RDWR; bounded body/header validation unchanged.
Next: small dedicated synthetic transport harness, no full-suite diagnosis.

Concrete bounded diagnosis (80 requests,20 per class,60s observation ceiling): oversized
18 structured/2 WinError10053; Origin20/20; bad authentication20/20; fully consumed malformed
JSON20/20. Server-side finish observed unread kernel input on4 oversized/4 Origin/1 bad-auth
closes,0 consumed-body closes. Engine dispatches0; clean shutdown; elapsed0.324s. Only fixed
counts/socket-state booleans recorded, no credentials/body. This reproduces the early-reject
transport failure independently of F07/full regression; it is not a one-off transient.

Classification: P01 transport close sequencing defect: response flush/SHUT_WR immediately
followed by close while inbound data can remain unread. Consume P01_TRANSPORT_REPAIR1/1.
Smallest repair: EngineServer.shutdown_request sends SHUT_WR after handler finish/flush,
then discards raw socket input for at most100ms and at most MAX_BODY_BYTES73728, whichever
first; closes in finally. It does not parse/dispatch rejected data, trust Content-Length for
drain size, read attacker-specified lengths to completion, add sleeps/retries, or change limits.
An arbitrarily large/stalled peer still closes at the fixed byte/time boundary; the response
write side closes first so compliant clients can receive the structured rejection immediately.
Incomplete-header ingress timeout retains existing EOF behavior because no complete HTTP
request is available; complete pre-dispatch rejection cases retain their fixed JSON errors.
Next: targeted protocol stress/resource/normal-flow tests only, then one900s full gate only
if targeted passes. Any required failure stops; no second transport repair authorized.


Transport targeted verification:34 passed in59.08s,240s subprocess ceiling. Fixed20
repetitions for all14 pre-dispatch envelope/header classes (280),5 malformed JSON classes
(100),5 large-unread-body early rejection classes (100), stalled rejected body (20),
incomplete-header ingress timeout (20):520 stress iterations total. Complete rejection
requests returned the expected sanitized JSON code with no connection-abort outcome.
Incomplete-header expiry retained bounded EOF; no complete HTTP request exists in that case.
No rejected request reached engine dispatch. Fixed-byte/time discard unit checks passed,
as did authenticated normal workflow, protected mutations/provenance, revocation, no-leak
assertions and server startup/shutdown. Existing non-fatal pytest-cache WinError183 warning
remains unchanged; no ACL/security policy modified.

Proceed with the single owner-authorized post-transport full regression,900s ceiling;
no further full rerun or material repair authorized. No F07 behavior changes or live model
calls. Static checks follow only after the full gate passes.

## P01 transport repair1/1 final gate - F07 blocked

Single authorized post-repair full configured regression: **293 passed,1 failed in474.34s**,
wall474.623s, within900s. All34 protocol tests including the fixed520 stress iterations
passed in this full run; no protocol connection abort recurred. The targeted transport result
remains34 passed59.08s. This is executed evidence for the bounded close repair, not a clean
F07 final regression.

OBSERVED: tests/test_profile.py::test_exact_context_isolation_eligibility_and_deterministic_updates
failed at store.add of the synthetic held-out fixture with STORAGE_BOUNDARY_INVALID.
EXPECTED: authorized synthetic held-out example persists through the protected boundary and
remains excluded from Writing DNA; full regression passes.
FAILURE_CLASS: protected-storage verification failure; underlying SecurityError cause unknown.
ExampleStore.add translates SecurityError into fixed STORAGE_BOUNDARY_INVALID, as required.
No evidence establishes whether the cause is an OS/ACL/subprocess environment issue or code
defect. Do not guess, loosen the guard, or silently repeat the test.
EVIDENCE: complete current traceback below. All other293 tests passed, including schema2->3
migration/canonical-data survival/rollback/idempotency/checkpoint cases. No extra compatibility
rerun was performed. All original285/1 transport failures and diagnosis remain above.
NEXT ACTION: owner decision authorizing a bounded protected-storage boundary investigation.
BUDGET REMAINING: all existing F07 counters exhausted; P01_TRANSPORT_REPAIR1/1 consumed.
No second full-suite retry, storage diagnosis/repair, or further feature change authorized.

F07 remains blocked. No live2,000/5,000 acceptance was repeated. Successful live proofs and
all durable checkpoint/failure history preserved. Ruff/mypy/pip final gates not run because
the sequential full-regression gate failed. No commit/push/PR/merge. F08 and S03 Phase B
remain not_started. The repair remains uncommitted with the bounded F07 work.

Complete post-transport full output (synthetic fixtures only; session credentials redacted):

```text
........................................................................ [ 24%]
........................F............................................... [ 48%]
........................................................................ [ 73%]
........................................................................ [ 97%]
......                                                                   [100%]
================================== FAILURES ===================================
_____ test_exact_context_isolation_eligibility_and_deterministic_updates ______

store = <personalstyle.storage.ExampleStore object at 0x000002937BD907D0>

    def test_exact_context_isolation_eligibility_and_deterministic_updates(store):
        first = example()
        store.add(first)
        initial = derive_writing_dna(store, "work.email")
        assert initial == derive_writing_dna(store, "work.email")
        assert initial["source_fingerprint"] == hashlib.sha256(
            f"{first.id}:1\n".encode("ascii")
        ).hexdigest()
        store.add(example(2, context="friends.chat", text="One two three four five six?"))
        store.add(example(3, learning_eligible=False, text="EXCLUDED_INELIGIBLE"))
>       store.add(example(4, learning_eligible=False, held_out=True, text="EXCLUDED_HELDOUT"))

tests\test_profile.py:49:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <personalstyle.storage.ExampleStore object at 0x000002937BD907D0>
example = ExampleInput(id='00000000-0000-0000-0000-000000000004', text='EXCLUDED_HELDOUT', context='work.email', supplier='local user', authorizer='local user', source_kind='user_owned', authorized=True, learning_eligible=False, held_out=True)

    def add(self, example: ExampleInput) -> dict[str, str | int]:
        example.validate()
        connection = None
        try:
            verify_private_directory(self.path.parent)
            new = not self.path.exists()
            if new:
                prepare_private_file(self.path)
            identity = self._boundary()  # Must precede opening for mutation.
            connection = self._connect()
            if not new:
                self._schema(connection)
            self._recheck(identity)
            connection.execute("BEGIN IMMEDIATE")
            if new:
                for statement in SCHEMA.values():
                    connection.execute(statement)
                connection.execute("INSERT INTO store_meta VALUES (3, 1)")
                connection.execute(f"PRAGMA application_id={APPLICATION_ID}")
                connection.execute("PRAGMA user_version=3")
            else:
                self._schema(connection)  # Revalidate after acquiring the write lock.
                if connection.execute("PRAGMA user_version").fetchone() != (3,):
                    raise StoreError("STORAGE_MIGRATION_REQUIRED")
            row = connection.execute("SELECT * FROM examples WHERE id=?", (example.id,)).fetchone()
            if row is not None and tuple(row[:8]) != example.payload():
                raise StoreError("IDEMPOTENCY_CONFLICT")
            if row is None:
                timestamp = datetime.now(UTC).isoformat()
                connection.execute(
                    "INSERT INTO examples VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, 2)",
                    (*example.payload(), timestamp),
                )
                connection.execute("UPDATE store_meta SET profile_version=profile_version+1")
            stored = connection.execute("SELECT * FROM examples WHERE id=?", (example.id,)).fetchone()
            if stored is None or tuple(stored[:8]) != example.payload():
                raise StoreError("PERSISTENCE_VERIFICATION_FAILED")
            # cache_spill=OFF retains dirty pages until guarded commit; no stale ACL grant.
            self._recheck(identity)
            connection.execute("COMMIT")
        except SecurityError:
>           raise StoreError("STORAGE_BOUNDARY_INVALID") from None
E           personalstyle.storage.StoreError: STORAGE_BOUNDARY_INVALID

src\personalstyle\storage.py:271: StoreError
============================== warnings summary ===============================
.venv\Lib\site-packages\_pytest\cacheprovider.py:469
  C:\Users\mamid\personalstyle\.venv\Lib\site-packages\_pytest\cacheprovider.py:469: PytestCacheWarning: could not create cache path C:\Users\mamid\personalstyle\.pytest_cache\v\cache\nodeids: [WinError 183] Cannot create a file when that file already exists: 'C:\\Users\\mamid\\personalstyle\\.pytest_cache\\v\\cache'
    config.cache.set("cache/nodeids", sorted(self.cached_nodeids))

.venv\Lib\site-packages\_pytest\cacheprovider.py:423
  C:\Users\mamid\personalstyle\.venv\Lib\site-packages\_pytest\cacheprovider.py:423: PytestCacheWarning: could not create cache path C:\Users\mamid\personalstyle\.pytest_cache\v\cache\lastfailed: [WinError 183] Cannot create a file when that file already exists: 'C:\\Users\\mamid\\personalstyle\\.pytest_cache\\v\\cache'
    config.cache.set("cache/lastfailed", self.lastfailed)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED tests/test_profile.py::test_exact_context_isolation_eligibility_and_deterministic_updates
1 failed, 293 passed, 2 warnings in 474.34s (0:07:54)
POST_TRANSPORT_FULL_WALL_SECONDS: 474.623
```



## Owner-authorized storage-boundary diagnosis1/1

Authority: explicit owner continuation; consume STORAGE_BOUNDARY_DIAGNOSIS1/1. Every
existing F07/exceptional counter and all failures/live evidence remain unchanged. No
production/test edits, full regression, model calls, permission changes or publication.

Inspection against main96afb469...: changed storage.py (schema3/explicit migration/checkpoints),
config.py/TOML (storage3), feedback.py (historical2/3 source decoding); test_profile.py and
test_storage.py only changed future-version probes3->4. Failing exact-context test and its
store fixture are unchanged. security.py/profile.py/learning.py/test_security.py unchanged.
P01 protocol.py/test_protocol.py changed only in the separately authorized close repair.
No shared conftest exists. Fresh protected fixture adds directly; it never calls migration.

Complete error path: add() can catch SecurityError from directory check, private-file creation,
_boundary (ACL/reparse/file-link checks), or _recheck (same guards plus inode/device identity).
The public StoreError suppresses printing but retains __context__; _acl can wrap OSError or
10s subprocess.TimeoutExpired, or raise after nonzero PowerShell verification. No inference
about the original hidden exception is justified without current runtime evidence.

Migration inspection: feedback_connection pre-read closes in finally; explicit2->3 then uses
one guarded read/write connection, BEGIN IMMEDIATE, exact-schema checks, transactional DDL/
metadata update, guarded COMMIT, rollback-if-active and close in finally; post-open verification
uses another scoped read connection. No second DB/temp DB/reset/WAL; DELETE journal required,
cache_spill disabled, SQLite-created rollback journal inherits protected parent permissions.
No file handle stored in ExampleStore. Existing add/get/eligible read connections close in
finally; schema3 normal-write guard only changes expected version. No missing close found by
inspection; this does not prove absence of a runtime/order-dependent leak.

Next: exact test once with in-memory observation of exception chains, fixed security messages,
file metadata and connection counts only. Isolated ceiling120s; relevant subset only on pass,
300s ceiling; at most one preceding-test sequence only if both pass,300s ceiling. No raw
writing/credential/DB payload or PowerShell stderr printed. No behavior monkeypatching.

## Storage-boundary diagnosis1/1 - completed, cause unresolved

Isolated exact-context test:1 passed19.04s (observer wall19.287s),120s ceiling.
Relevant eight-test subset:8 passed42.85s (wall43.072s),300s ceiling:
- exact-context isolation;
- example exact round-trip/idempotency/conflict;
- hostile-data/fresh-process read-only profile;
- schema2->3 canonical-data survival/idempotency;
- migration failed-guard rollback;
- schema2 feedback/active-preference preservation;
- real private-directory ACL/CLI positive path;
- insecure boundary rejected before SQLite open.

Only expected deliberate SecurityErrors occurred: migration rollback guard injection and
the unprotected-directory negative check. For the latter, in-memory observation captured
security._acl nonzero exit1, fixed marker Unprotected ACL, then verify_private_directory
and storage.add translation. This confirms the observer sees the hidden error path; it
does NOT establish the cause of the historical failing held-out addition. No unexpected
exception/traceback occurred in the isolated/subset runs. No raw stderr/payload emitted.

Collection-only inspection:294 items; failing profile test is zero-based position96.
Immediate predecessors are learning tests; protocol tests run later, not before this
failure. Inspected memory_store fixture yields one SQLite connection and closes it in
teardown; receipt/verification monkeypatches are fixture-scoped. Selected one bounded
seven-test reproduction in original relative order:
- protected promotion/consumption/provenance/F04-integrity workflow;
- actual query plans/fixed query count;
- invalid feedback authorization/source_version/not_verified/run_id (four cases);
- exact-context profile test.

Single sequence result:7 passed43.40s (observer wall43.609s),300s ceiling. Only its deliberate
protected-commit rejection raised SecurityError. No failure repetition or full-suite run.

After each diagnosis process, visible live SQLite connections/active transactions were0
(before also0); no journal/WAL/SHM sidecars on inspected stores. After predecessor sequence,
no visible DB file objects or surviving Python descendants. Process inspection recorded
names/PIDs/parent IDs only, no command lines. This does not claim a system-wide OS handle
audit or prove absence of every possible leak. Directory/file protection re-verified for
both sequence stores; ordinary files had one link and no reparse attributes. Environment
variable changes none; security functions and verification.derive_personalization restored.
All observation is in-memory; no production/test changes or permission/policy modifications.
Existing tests initialize their own disposable protected fixtures normally.

CLASSIFICATION: original protected-storage failure remains non-reproduced with unknown
underlying mechanism. The original process has exited and its sanitized traceback did not
retain the suppressed SecurityError cause. Current passing executions cannot reconstruct
that historical exception. Do not call it a proven transient, ACL defect, subprocess timeout,
handle leak, migration defect, or fixture defect.

F07 attribution: not established. The failing test/fixture, security.py, profile.py, and
_boundary/_recheck/get/add cleanup are unchanged from main. Fresh fixture does not migrate.
F07 changes schema declarations/validation/new-store schema version and adds explicit
migration/checkpoints; no evidence from this cycle implicates those changes. This is not
proof that every possible F07/order interaction is excluded.

Implicated public path only: storage.ExampleStore.add catches SecurityError originating
from directory/file/path/identity guards (security._check_path/_acl/_boundary/_recheck).
Which guard failed historically is unknown. Security._acl still enforces unchanged10s
subprocess bound; no runtime evidence here identifies timeout or nonzero OS verification
as the historical cause.

SMALLEST BOUNDED REPAIR PROPOSED: none justified until the actual failing guard/cause is
captured. Next owner decision would be whether to authorize one instrumented final-gate
reproduction with the same bounded ceiling, capturing only fixed cause/type/timing and
file-state metadata at the underlying failure. That is a future decision, not authorization
to run it now or to add production retries/change ACL timeouts. No code repair authorized.

STORAGE_BOUNDARY_DIAGNOSIS1/1 consumed. All other counters unchanged/exhausted. F07 remains
blocked pending a clean full gate; both live acceptances/checkpoints/historical failures
remain preserved. No full regression/static/model rerun, commit, push, PR, F08 or Phase B.

Isolated (sanitized observer output):

```json
{"exit_code": 0, "elapsed_seconds": 19.287, "summary_lines": ["1 passed, 1 warning in 19.04s"], "exception_reports": [], "security_events": [], "store_metadata": [{"node": "tests/test_profile.py::test_exact_context_isolation_eligibility_and_deterministic_updates", "store_alias": "test_temp/data/personalstyle.db", "sidecars": {"-journal": false, "-wal": false, "-shm": false}, "directory": {"exists": true, "device": 11860479274809220916, "inode": 1688849861340344, "links": 1, "size_bytes": 0, "attributes": 16}, "file": {"exists": true, "device": 11860479274809220916, "inode": 9851624185949369, "links": 1, "size_bytes": 69632, "attributes": 32}}], "connections_before": {"live": 0, "closed_objects": 0, "transactions": 0}, "connections_after": {"live": 0, "closed_objects": 0, "transactions": 0}, "environment_changed_names": [], "security_functions_restored": true, "platform_name": "nt"}
```

Relevant subset (sanitized observer output):

```json
{"exit_code": 0, "elapsed_seconds": 43.072, "summary_lines": ["8 passed, 1 warning in 42.85s"], "exception_reports": [], "security_events": [{"node": "tests/test_document.py::test_schema3_failed_guard_rolls_back_entire_migration", "function": "migrate_document_schema", "line": 380, "chain": [{"type": "SecurityError", "frames": [{"file": "storage.py", "line": 380, "function": "migrate_document_schema"}, {"file": "test_document.py", "line": 398, "function": "recheck"}], "fixed_message": "<not emitted>"}]}, {"node": "tests/test_storage.py::test_insecure_boundary_blocks_before_sqlite_open", "function": "_acl", "line": 101, "chain": [{"type": "SecurityError", "frames": [{"file": "security.py", "line": 101, "function": "_acl"}], "fixed_message": "Private profile permissions could not be verified"}], "acl_result": {"returncode": 1, "stderr_bytes": 319, "fixed_markers": ["Unprotected ACL"]}}, {"node": "tests/test_storage.py::test_insecure_boundary_blocks_before_sqlite_open", "function": "verify_private_directory", "line": 109, "chain": [{"type": "SecurityError", "frames": [{"file": "security.py", "line": 109, "function": "verify_private_directory"}, {"file": "security.py", "line": 101, "function": "_acl"}], "fixed_message": "Private profile permissions could not be verified"}]}, {"node": "tests/test_storage.py::test_insecure_boundary_blocks_before_sqlite_open", "function": "add", "line": 234, "chain": [{"type": "SecurityError", "frames": [{"file": "storage.py", "line": 234, "function": "add"}, {"file": "security.py", "line": 109, "function": "verify_private_directory"}, {"file": "security.py", "line": 101, "function": "_acl"}], "fixed_message": "Private profile permissions could not be verified"}]}], "store_metadata": [{"node": "tests/test_profile.py::test_exact_context_isolation_eligibility_and_deterministic_updates", "store_alias": "test_temp/data/personalstyle.db", "sidecars": {"-journal": false, "-wal": false, "-shm": false}, "directory": {"exists": true, "device": 11860479274809220916, "inode": 14918173765831121, "links": 1, "size_bytes": 0, "attributes": 16}, "file": {"exists": true, "device": 11860479274809220916, "inode": 20829148276755132, "links": 1, "size_bytes": 69632, "attributes": 32}}, {"node": "tests/test_storage.py::test_exact_roundtrip_idempotency_and_conflict", "store_alias": "test_temp/profile/personalstyle.db", "sidecars": {"-journal": false, "-wal": false, "-shm": false}, "directory": {"exists": true, "device": 11860479274809220916, "inode": 162129586585505021, "links": 1, "size_bytes": 0, "attributes": 16}, "file": {"exists": true, "device": 11860479274809220916, "inode": 56857945295720174, "links": 1, "size_bytes": 69632, "attributes": 32}}, {"node": "tests/test_profile.py::test_punctuation_hostile_text_and_read_only_fresh_process", "store_alias": "test_temp/data/personalstyle.db", "sidecars": {"-journal": false, "-wal": false, "-shm": false}, "directory": {"exists": true, "device": 11860479274809220916, "inode": 58265320179274338, "links": 1, "size_bytes": 0, "attributes": 16}, "file": {"exists": true, "device": 11860479274809220916, "inode": 26177172834259937, "links": 1, "size_bytes": 69632, "attributes": 32}}, {"node": "tests/test_document.py::test_schema2_upgrade_preserves_all_canonical_data_and_is_idempotent", "store_alias": "test_temp/profile/profile.db", "sidecars": {"-journal": false, "-wal": false, "-shm": false}, "directory": {"exists": true, "device": 11860479274809220916, "inode": 32651097298605050, "links": 1, "size_bytes": 0, "attributes": 16}, "file": {"exists": true, "device": 11860479274809220916, "inode": 67553994410726650, "links": 1, "size_bytes": 69632, "attributes": 32}}, {"node": "tests/test_document.py::test_schema3_failed_guard_rolls_back_entire_migration", "store_alias": "test_temp/profile/profile.db", "sidecars": {"-journal": false, "-wal": false, "-shm": false}, "directory": {"exists": true, "device": 11860479274809220916, "inode": 30117822508210046, "links": 1, "size_bytes": 0, "attributes": 16}, "file": {"exists": true, "device": 11860479274809220916, "inode": 53480245575194532, "links": 1, "size_bytes": 49152, "attributes": 32}}], "connections_before": {"live": 0, "closed_objects": 0, "transactions": 0}, "connections_after": {"live": 0, "closed_objects": 0, "transactions": 0}, "environment_changed_names": [], "security_functions_restored": true, "platform_name": "nt"}
```

Single predecessor sequence (sanitized observer output):

```json
{"exit_code": 0, "elapsed_seconds": 43.609, "summary_lines": ["7 passed, 1 warning in 43.40s"], "exception_reports": [], "security_events": [{"node": "tests/test_learning.py::test_protected_promotion_consumption_exact_provenance_and_f04_integrity", "function": "feedback_connection", "line": 301, "chain": [{"type": "SecurityError", "frames": [{"file": "storage.py", "line": 301, "function": "feedback_connection"}, {"file": "test_learning.py", "line": 208, "function": "reject_commit"}], "fixed_message": "<not emitted>"}]}], "store_metadata": [{"node": "tests/test_learning.py::test_protected_promotion_consumption_exact_provenance_and_f04_integrity", "store_alias": "test_temp/data/profile.db", "sidecars": {"-journal": false, "-wal": false, "-shm": false}, "directory": {"exists": true, "device": 11860479274809220916, "inode": 41939771530092785, "links": 1, "size_bytes": 0, "attributes": 16}, "file": {"exists": true, "device": 11860479274809220916, "inode": 15762598696001816, "links": 1, "size_bytes": 94208, "attributes": 32}}, {"node": "tests/test_profile.py::test_exact_context_isolation_eligibility_and_deterministic_updates", "store_alias": "test_temp/data/personalstyle.db", "sidecars": {"-journal": false, "-wal": false, "-shm": false}, "directory": {"exists": true, "device": 11860479274809220916, "inode": 25051272927461569, "links": 1, "size_bytes": 0, "attributes": 16}, "file": {"exists": true, "device": 11860479274809220916, "inode": 11821949022063255, "links": 1, "size_bytes": 69632, "attributes": 32}}], "connections_before": {"live": 0, "closed_objects": 0, "transactions": 0}, "connections_after": {"live": 0, "closed_objects": 0, "transactions": 0}, "environment_changed_names": [], "security_functions_restored": true, "platform_name": "nt", "post_sequence_boundary": [{"store_alias": "test_temp/data/profile.db", "protected_directory_and_file_verified": true}, {"store_alias": "test_temp/data/personalstyle.db", "protected_directory_and_file_verified": true}], "verification_function_restored": true, "visible_db_file_objects": [], "python_powershell_process_metadata": [{"ProcessId": 22376, "ParentProcessId": 12016, "Name": "powershell.exe"}, {"ProcessId": 24956, "ParentProcessId": 21604, "Name": "powershell.exe"}, {"ProcessId": 26408, "ParentProcessId": 24956, "Name": "python.exe"}, {"ProcessId": 14000, "ParentProcessId": 26408, "Name": "python.exe"}, {"ProcessId": 30332, "ParentProcessId": 14000, "Name": "python.exe"}, {"ProcessId": 24464, "ParentProcessId": 30332, "Name": "python.exe"}, {"ProcessId": 23808, "ParentProcessId": 24464, "Name": "powershell.exe"}], "surviving_python_descendants": []}
```




## Owner-authorized instrumented final-gate reproduction1/1

Authority: owner explicitly authorizes one instrumented full suite900s, then exactly one
separate uninstrumented full suite900s only if the first passes. All historical counters and
failed/passing evidence remain unchanged. Consume FINAL_GATE_INSTRUMENTED_REPRODUCTION1/1.
No product/security/schema behavior change, storage repair, live model acceptance, or
concurrent verification authorized. Branch/base/WIP rechecked: task/f07-long-document;
HEAD/main/origin/main/merge-base96afb4691dfb141601f3239b3d93f203294347d4; one worktree;
no open PR. Existing uncommitted work preserved.

Observer exists only in child-process memory (pytest plugin/sys.settrace). It records only
fixed exception/type/code/operation/frame identifiers, process ID, safe fixture category,
file-state/sidecar/ACL metadata and known connection state on failures. It does not emit
raw writing, credentials, request headers, DB payloads, raw PowerShell output or actual
protected paths. No runtime function/control-flow monkeypatches; no repository diagnostic
artifact. Trace is disabled in finally and disappears on exit. Full source/config/test
hashes checked before/after. Stop at any required failure, no second reproduction.


Instrumented full suite PASSED:294 passed441.37s, observer wall441.483s,900s ceiling.
No unexpected exception/failure metadata. sys.settrace disabled in finally; child exited0.
Production/test/config hashes before/after identical. No diagnostic file or repository
instrumentation was created, so no artifact removal needed. Original hidden storage cause
remains unresolved; this pass does not rewrite that history or establish F07 fully passing.

Owner conditional authorization satisfied: start exactly one definitive vanilla pytest
full suite900s without plugin/sys.settrace/runtime wrapper inside the test process. Outer
subprocess capture/deadline only. No live model call, production change or concurrent work.
Static checks follow only on clean definitive result; stop if it fails, no repeat.

## Instrumented/definitive final-gate result - clean regression, lint blocked

Instrumented reproduction1/1:294 passed441.37s, wall441.483s,900s ceiling; no failure
metadata. In-memory observer disabled and child exited. Source/test/config hashes unchanged;
no diagnostic-only artifact created or retained in the working tree.

Separately authorized definitive uninstrumented regression: **294 passed437.77s**, wall438.063s,
900s ceiling. Vanilla pytest, no observer/plugin/sys.settrace. Schema2->3 migration, canonical
data survival, rollback/idempotency, checkpoint/restart/invalidation and all protocol cases
were included and passed; no additional compatibility or live-provider rerun needed.
Existing non-fatal pytest-cache WinError183 warning remains. The historical storage guard
failure is not erased and its underlying cause remains unknown; no storage repair performed.

Sequential final static gate: Ruff run once, exit1:
- tests/test_document.py import block I001: OPERATION_SECONDS must follow MAX_WORDS;
- tests/test_protocol.py:187 RUF012: Peer.timeouts=[] is a mutable class attribute.

OBSERVED: clean definitive full regression, then two test-only lint findings.
EXPECTED: all required final gates green before publication/local-passing status.
FAILURE_CLASS: verification hygiene / static-test configuration defect; not a runtime
storage-boundary or live long-document failure. No test assertion or product repair indicated.
EVIDENCE: exact Ruff output below; no lint correction or second Ruff run performed.
NEXT ACTION: owner decision authorizing only the two lint corrections, affected Ruff recheck
and remaining mypy/pip/whitespace gates, preserving unchanged passing pytest/live evidence.
BUDGET REMAINING: all historical/exceptional counters exhausted, including
FINAL_GATE_INSTRUMENTED_REPRODUCTION1/1. No additional feature/storage correction authorized.

F07 remains blocked by lint, not marked locally passing. mypy/pip final gates not run after
Ruff failed; no publication/commit/PR. No production/test changes in this continuation:
only durable status/evidence records. No temporary instrumentation remains. Both configured-
provider live2,000/5,000 acceptances and every original failure/checkpoint remain preserved.
F08 and S03 Phase B remain not_started.

Ruff evidence:

```text
I001 [*] Import block is un-sorted or un-formatted
  --> tests\test_document.py:3:1
   |
 1 |   """F07 protected schema upgrades and durable document behavior."""
 2 |
 3 | / import copy
 4 | | import json
 5 | | import sqlite3
 6 | | import subprocess
 7 | | from pathlib import Path
 8 | | from uuid import UUID
 9 | |
10 | | import pytest
11 | |
12 | | from personalstyle.config import load_config
13 | | from personalstyle.document import (
14 | |     CONTRACT,
15 | |     DOCUMENT_CALLS,
16 | |     OPERATION_SECONDS,
17 | |     MAX_SEGMENTS,
18 | |     MAX_WORDS,
19 | |     SEGMENT_BYTES,
20 | |     inspect_document,
21 | |     invalidate_document_contract,
22 | |     rewrite_document,
23 | |     segment_document,
24 | |     verify_assembly,
25 | | )
26 | | from personalstyle.generation import RewriteRequest
27 | | from personalstyle.provider import Candidate, GenerationError, PreparedModel
28 | | from personalstyle.security import SecurityError, prepare_private_directory, prepare_private_file
29 | | from personalstyle.storage import APPLICATION_ID, SCHEMA_V2, ExampleStore, StoreError
30 | | from personalstyle.verification import CHECKS
   | |_____________________________________________^
31 |
32 |   ROOT = Path(__file__).resolve().parents[1]
   |
help: Organize imports
   |
15 |     DOCUMENT_CALLS,
   -     OPERATION_SECONDS,
16 |     MAX_SEGMENTS,
17 |     MAX_WORDS,
18 +     OPERATION_SECONDS,
19 |     SEGMENT_BYTES,
   |

RUF012 Mutable default value for class attribute
   --> tests\test_protocol.py:187:20
    |
185 |     class Peer:
186 |         discarded = 0
187 |         timeouts = []
    |                    ^^
188 |         closed = False
189 |         write_shutdown = False
    |
help: Consider initializing in `__init__` or annotating with `typing.ClassVar`

Found 2 errors.
[*] 1 fixable with the `--fix` option.
```

## Final owner-authorized lint correction and local completion

The owner authorized only the two test/static corrections listed above. Ruff import ordering
was corrected deterministically in tests/test_document.py. tests/test_protocol.py now marks
the intentional test Peer.timeouts list ClassVar; no assertion or behavior was changed.
Mypy exposed one related override annotation issue in the P01 transport repair. The override
now accepts the standard socketserver request union and casts to socket.socket at the point
HTTPServer's TCP-only invariant applies. The runtime path and repair behavior are unchanged.

Final local gates:
- Ruff `ruff check src tests scripts/f07_acceptance.py`: passed after the authorized corrections.
- mypy `mypy src`: passed, 13 source files. First run identified the mechanical override
  annotation issue above; the one affected check passed after correction.
- `pip check`: passed, no broken requirements.
- `git diff --check`: passed; Git reported only the existing AGENTS.md LF/CRLF working-copy
  conversion notice.
- Definitive uninstrumented pytest:294 passed in437.77s. Migration2->3 survival/rollback/
  idempotency, protected checkpoint/restart and protocol stress cases were in this run.
- Instrumented pytest:294 passed441.37s; observer exited and hashes for source/tests/config
  were unchanged. No diagnostic artifact remains or was created.
- No live model acceptance was repeated during finalization. Authoritative real-provider
  evidence remains the existing exact ollama/qwen3:8b runtime0.40.1, digest
  500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41:
  2,000 words/10 segments/50 calls/0 repairs/466.375s VERIFIED; 5,000 words/25 segments/
  125 calls/0 repairs/1,415.205s VERIFIED; each under the1,800s document ceiling and120s
  operation ceiling. Those acceptances remain preserved at their original checkpoints.
- P01 close repair: response is flushed, write side half-closed, then raw input is discarded
  only up to73,728 bytes or100ms, whichever comes first. Targeted protocol suite34 passed
  in59.08s, including520 bounded stress iterations across rejection classes, malformed input,
  auth, stalled rejected body, ingress timeout, normal authenticated workflow and lifecycle.
  Protocol cases also passed in both full regression runs. No dispatch for rejected requests,
  no content/credential log, no retry, and no request/auth/engine budget change.
- Current versions: product0.1.0; protocol1.0; config1; storage3; profile1; prompt1;
  desktop client0.1.0+1. SQLite runtime3.50.4; Python3.14.6. Storage3 is the authorized
  atomic ordered schema2->3 migration; canonical schema2 data is preserved by executed tests.

Final acceptance map: AC1/AC2 real-provider2k/5k multi-segment runs plus deterministic
test_multiple_bounded_segments_complete_and_restart_reuses; AC3/AC4 tested word/byte/segment
limits and limit+1 rejection; AC5 deterministic source-order/reassembly and structured unit
mapping tests; AC6 existing F04 checks run per segment plus whole-document constraints;
AC7-AC9 controlled middle failure, durable restart, segment-local edits and dependency
invalidation tests; AC10 whole-assembly loss/reorder/constraint rejection tests; AC11/AC12
SQLite fresh-process checkpoint inspection and persistent failure/progress/budget tests;
AC13 all294 Python regression tests, including unchanged short-text compatibility.
Schema migration and canonical-state preservation are verified by the targeted migration
tests and definitive full regression. This evidence does not claim a desktop long-document
UI, F08 import/export, PhaseB readiness, product quality or Windows alpha completion.

All task budgets/history preserved: implementation2/2; diagnosis2/2; recovery1/1;
STRUCTURAL_CORRECTION1/1; FINAL_REGRESSION_DIAGNOSIS1/1; FINAL_REGRESSION_RECOVERY1/1;
P01_TRANSPORT_REPAIR1/1; STORAGE_BOUNDARY_DIAGNOSIS1/1;
FINAL_GATE_INSTRUMENTED_REPRODUCTION1/1. Historical full-suite outcomes remain recorded,
including265/2 stale schema fixtures,285/1 transport failure (twice), and293/1 storage
boundary failure. The original hidden storage exception remains unknown; the subsequently
instrumented and definitive full runs both passed. No prior failure was rewritten as a pass.

STATE: locally passing; draft PR handoff for task/f07-long-document, exact-head CI pending.
F08 is the next planned task, not activated. S03 PhaseB is not_started. Overall Windows
alpha remains incomplete. Do not merge automatically.
