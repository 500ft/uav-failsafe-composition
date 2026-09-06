# Bounded metadata evaluation — 2026-09-06

Candidate hashes and [exact cases with original judgments](evaluation-cases.json)
are saved before predictions. Run `python evidence/sprint-2026-09-05/evaluate_candidate.py`.
Every one of the seven cases is retained; no exclusions. These are development
spot checks derived from declared schema boundaries, not independent validation.
If a disagreement informs a fix, invalidate this candidate and relabel the case
as development evidence; freeze a new candidate before additional evaluation.

Manual protocol counterexample: ten marginal tubes at 0.95 coverage do not imply
0.95 joint coverage. Even under independence the all-contained probability is
0.95**10 ≈0.599; common-mode dependence needs a joint model. The updated plan
requires fleet-event/horizon/risk allocation before any composed-safety claim.
