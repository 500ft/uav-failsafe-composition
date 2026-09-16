# UAV-Recovery-Contracts — Six-day evidence-integrity sprint

> Historical record (2026-09-05/06). The repository was renamed `uav-failsafe-composition` on 2026-09-10 ([identity](REPOSITORY_IDENTITY.md)); checkout paths and the remote below are as they were then. Current status lives in [SPRINT_TASKS.csv](SPRINT_TASKS.csv).

Prepared: 2026-09-05. Budget: 30 focused hours; optional Day 7 adds at most 4 hours for owner review only. Days are effort groupings, not unattended calendar commitments. Status lives only in [SPRINT_TASKS.csv](SPRINT_TASKS.csv).

## A. Outcome and baseline identity

A trustworthy research-design intake and conformance-protocol package: real nested schema validation, one consistent SITL-first critical path, and an explicit fleet-claim boundary; not a flying fleet.

Publication-state update (2026-09-06): the owner authorized local commits, branch
pushes, and pull requests for this sprint. This does not authorize deployment,
research publication, outreach, spending, or any blocked physical/data action.

Audience: engineering/research reviewer and graduate-application portfolio reader.
Canonical sprint checkout: `/Users/redhose/Developer/research-sprints/2026-09-05/UAV-Recovery-Contracts`.
Remote: https://github.com/500ft/UAV-Recovery-Contracts. Base: `55c6dd00b061da77dfb53e90c04e094ca4427d89`.
Branch: `sprint/evidence-integrity-20260905`. Prepared from the unmerged task PR head, not from original dirty drafts.
Original checkout: `/Users/redhose/UAV-Recovery-Contracts`; preserved. New sprint checkout was clean before evidence capture. No commit, push, publication, purchase, deployment or outreach is claimed or planned as an automatic action.

## B. Verified baseline and priority gaps

Verified: scripts/check_repo_contract.py compares top-level key sets but never evaluates JSON Schema constraints. ROADMAP.md blocks offline composition on HITL while docs/TASKS.md URC-S10 allows post-SITL work. No executed SITL/HITL traces exist.

Sources inspected: [scripts/check_repo_contract.py](../scripts/check_repo_contract.py), [protocols/configuration-manifest.schema.json](../protocols/configuration-manifest.schema.json), [tests/test_repo_contract.py](../tests/test_repo_contract.py), [ROADMAP.md](../ROADMAP.md), [docs/TASKS.md](../docs/TASKS.md), [docs/research-plan.md](../docs/research-plan.md).
[Actual baseline command outputs](../evidence/sprint-2026-09-05/baseline.json) record working directories, runtime versions, outputs and exit statuses. Alleged defects become reproduced failures only when the red tests record them. Test counts are not research performance.

Verified existing commands (repository root; local Python may need the recorded readline workaround):

```sh
python -m unittest discover -s tests -v
python scripts/check_repo_contract.py
```

No separately configured typechecker/linter was found in this scoped configuration. Use compileall for changed Python, relevant tests, existing CI commands and `git diff --check`; do not call syntax compilation a typecheck. Proposed test/CLI paths below do not exist until implemented.

## C. Scope, ownership and critical path

Must-haves: repaired claim/validation boundary; regression evidence including original failures; consistent operative scope; reproducible local delivery/check commands; review index identifying unresolved external work.
Exclusions: No autopilot installation, firmware flashing, flight, safety certification, claim of novelty clearance, fleet optimizer, or external push.
Owner/External dependencies: Owner configuration/resource choice and eventual lab/safety approval. This local branch includes the existing open PR head, not a merged default-branch change.
Critical path: baseline → regression failure → minimal correction → full affected checks → candidate identity/selection freeze → bounded evaluation → review packet. Prepare owner requests on Day1; replies do not block independent code fixes. External feedback is not presumed.

## D. Daily budget

September6 reconciliation: owner resource/reference actions start on Day1 rather
than after the evaluation packet. This moves two estimated hours forward; total
remains30. External turnaround is not compressed by this workload allocation.

| Day | Hours | Primary deliverable |
|---|---:|---|
| 1 | 7 | Baseline/scope (5 Agent hours), early resource/provenance action (2 Owner hours) |
| 2 | 5 | Enforce the declared configuration schema |
| 3 | 6 | Reconcile pilot, confirmation, composition and fleet limits |
| 4 | 4 | Package deterministic intake/negative fixtures |
| 5 | 6 | Evaluate previously uninspected metadata boundary cases |
| 6 | 2 | Review packet; external feedback remains conditional |
| Total | 30 | Local evidence-ready candidate or explicitly partial handoff |

## E. Ordered tasks and done conditions

### URC-S01 — Day 1: Capture baseline and reproduce audit hypotheses

Priority: P0 · Owner: Agent · Focused hours: 3 · Depends on: none.
Files: scripts/check_repo_contract.py; protocols/configuration-manifest.schema.json; tests/test_repo_contract.py; ROADMAP.md; docs/TASKS.md; docs/research-plan.md.
Deliverable / Done when: Record base identity, clean sprint start, versions, exact CI commands and observed outputs; preserve original worktree changes.
Verification: python -m unittest discover -s tests -v
python scripts/check_repo_contract.py
Evidence to retain: evidence/sprint-2026-09-05/baseline.json.

### URC-S02 — Day 1: Freeze scope and evidence-first execution design

Priority: P0 · Owner: Agent · Focused hours: 2 · Depends on: URC-S01.
Files: NEW docs/SPRINT_ROADMAP.md; NEW docs/SPRINT_TASKS.csv; NEW docs/SPRINT_PROGRESS.md; NEW docs/REVIEW_READY.md.
Deliverable / Done when: Six-day30h plan saved, requirements testable, user-provided plan-and-execute authorization recorded, external authority excluded.
Verification: Review this roadmap and parse task CSV; hours sum to30.
Evidence to retain: docs/SPRINT_ROADMAP.md.

### URC-S03 — Day 2: Enforce the declared configuration schema

Priority: P0 · Owner: Agent · Focused hours: 5 · Depends on: URC-S02.
Files: scripts/check_repo_contract.py; tests/test_repo_contract.py; .github/workflows/ci.yml; README.md; NEW requirements.txt.
Deliverable / Done when: Tests fail before the fix for invalid autopilot, battery fraction=2, negative logging rate and nested missing fields; valid example still passes; declared dialect is used and dependency installed in CI.
Verification: python -m unittest discover -s tests -v; python scripts/check_repo_contract.py
Evidence to retain: command, inputs, outputs and exit status under evidence/sprint-2026-09-05/; link from task ledger.

### URC-S04 — Day 3: Reconcile pilot, confirmation, composition and fleet limits

Priority: P0 · Owner: Agent · Focused hours: 6 · Depends on: URC-S03.
Files: ROADMAP.md; docs/TASKS.md; docs/research-plan.md; docs/experiment-01-authority-loss.md; README.md.
Deliverable / Done when: Pilot not called confirmation; offline simulated composition may follow positive SITL; HITL gates hardware claims; 5–10% uncertainty band has a decision; joint risk and common-mode limitations explicit.
Verification: python scripts/check_repo_contract.py; read all continuation gates side by side; no completed-trace language.
Evidence to retain: command, inputs, outputs and exit status under evidence/sprint-2026-09-05/; link from task ledger.

### URC-S05 — Day 4: Package deterministic intake/negative fixtures

Priority: P1 · Owner: Agent · Focused hours: 4 · Depends on: URC-S04.
Files: protocols/configuration-manifest.schema.json; NEW evidence/sprint-2026-09-05/candidate.json; docs/REVIEW_READY.md.
Deliverable / Done when: Clean consumer dependency install exercises validator; source/diff identity frozen; examples remain planned-example, not measured.
Verification: python -m pip install -r requirements.txt; python scripts/check_repo_contract.py; git diff --check
Evidence to retain: command, inputs, outputs and exit status under evidence/sprint-2026-09-05/; link from task ledger.

### URC-S06 — Day 5: Evaluate previously uninspected metadata boundary cases

Priority: P1 · Owner: Agent · Focused hours: 6 · Depends on: URC-S05.
Files: NEW evidence/sprint-2026-09-05/evaluation-plan.md; NEW evidence/sprint-2026-09-05/evaluation.json; tests/test_repo_contract.py.
Deliverable / Done when: Freeze fixture selection before candidate output; test valid boundaries and invalid types/NaN/missing fields; retain expected judgments and differences; no safety/generalization claim.
Verification: python -m unittest discover -s tests -v; reproduce changed examples and rejection reasons with recorded inputs.
Evidence to retain: command, inputs, outputs and exit status under evidence/sprint-2026-09-05/; link from task ledger.

### URC-S07 — Day 6: Assemble protocol review and harness handoff

Priority: P1 · Owner: Agent · Focused hours: 2 · Depends on: URC-S06.
Files: docs/REVIEW_READY.md; docs/SPRINT_PROGRESS.md; docs/SPRINT_TASKS.csv.
Deliverable / Done when: One reproducible record and exact next harness task; novelty closeout, simulator choices and missing hardware remain explicit.
Verification: python scripts/check_repo_contract.py; python -m unittest discover -s tests -v; git diff --check
Evidence to retain: command, inputs, outputs and exit status under evidence/sprint-2026-09-05/; link from task ledger.

### URC-S08 — Day 1: Owner chooses intended configurations and access path

Priority: P0 · Owner: Owner · Focused hours: 2 · Depends on: URC-S02.
Files: docs/experiment-01-authority-loss.md; docs/TASKS.md.
Deliverable / Done when: Owner confirms software/compute and advisor path; firmware identities verified from installed software before future traces; no purchase/outreach implied.
Verification: Review proposed equivalent Hold/Land/RTL intents and software resource availability; external novelty review remains pending.
Evidence to retain: command, inputs, outputs and exit status under evidence/sprint-2026-09-05/; link from task ledger.


## F. Evaluation and overrun policy

Existing audit counterexamples and all tests inspected while fixing are development evidence, not held-out evaluation. Before Day5, freeze a candidate source/diff identity and selection procedure; save expected judgments before predictions where meaningful. Any observed case used to fix the candidate becomes development material; record that and select new cases for a revised candidate. Hashes identify bytes, not independence. No AI peer is called an independent human reviewer.

If the implementation consumes extra time, cut optional model breadth, cosmetic changes and additional fixtures; never relax numerical thresholds, remove rejection checks or relabel missing measurements. Day7 may add up to4 owner-review hours (34 maximum) only by explicit rebaseline. Do not convert lab lead time into nominal coding hours. Stop affected work at missing authority; proceed with independent authorized tasks. Unavailable external evidence produces a partial handoff, not a completed empirical claim.

Follow-up review checks: reproduce original failures and repaired counterexamples, repeat real commands, inspect runtime and evidence provenance, distinguish local tests from hosted/deployed/physical outcomes, and assess scientific wording independently.

## G. Execution record and first action

[Ledger](SPRINT_TASKS.csv) · [Progress](SPRINT_PROGRESS.md) · [Review index](REVIEW_READY.md).
First behavior-changing action: URC-S03; write its regression input, observe failure on baseline, then make the minimal correction. User has authorized plan-and-execute now. No additional start confirmation is required for this bounded scope.
