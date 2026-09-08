# URC-D01 — First-pass priority-one source review

Date: 2026-09-08. Base `f9cbc81439c9a6f81a30e6187aa2150d5580935a`; branch `task/priority-one-20260908`.
Clean main-derived worktree at start. Candidate identity is the containing PR head.
Runtime: Python 3.11.8 from the existing /Users/redhose/ENTER environment.

## Why now

The prior software-integrity sprint is implemented. The first long-term research
task is still exact-gap closeout, before configuration, metrology or new apparatus
is chosen. Today's bounded deliverable is the
[dated source review](../../docs/prior-art-search-2026-09-08.md): exact executed
queries, 12 selected primary records, source-access limits, evidence grades,
claim boundaries and concrete next-task implications. This is a completed
first-pass subtask, **not completion of the parent novelty or owner gates**.

## Acceptance and reproducibility

Review the source table against the linked records; repeat the search strings
and record changed retrieval rather than expecting search ranks to be immutable.
The report distinguishes inspected primary material from indexed abstracts and
failed full-text access. It makes no global absence claim, installation claim,
physical result, patent clearance or independent reviewer claim.

Before edits, both commands passed: seven tests and repository contract.
Rerun from the repository root:

```sh
python -m unittest discover -s tests -v
python scripts/check_repo_contract.py
git diff --check
```

Final command results are retained in [checks.json](checks.json).
No behavior changed, so no artificial red regression or new scientific output
was created. No standalone lint/typecheck/build is configured. Existing schema,
evidence labels and disclosure boundaries remain unchanged.

The original eight sprint ledger rows remain byte-preserved; the appended task
is a separate daily follow-up estimate, not an expansion of the historical 30h
sprint. Full-text/library access and author review remain outstanding. The review
index below the latest-follow-up notice preserves historical evidence.

Next: obtain and review the specifically listed close-competitor full texts and
broader-search exports before full parent-task closeout. Do not start a simulator,
fabrication or hardware campaign based only on this review.
