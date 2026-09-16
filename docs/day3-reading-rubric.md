# Day-3 close-reading rubric

Prepared 2026-09-09 after the existing day-1 screen and day-2 export were known, before new day-3 close reading. This is a targeted follow-up, not a blind/systematic review or preregistered novelty proof.

Question axes: Equivalent recovery intention across explicitly pinned configurations; distinct liveness/setpoint failure injection; behavior when commands return; calibrated whole-trajectory coverage.

For each selected source record identifier/version, access date, exact sections/pages inspected, aboutness 0–3 (without citation/prestige inputs), evidence grade, and per-axis status: demonstrated / discussed / not established in inspected material / inaccessible. Record a source locator for every affirmative claim. Abstract-only sources cannot establish detailed negative conclusions about their full paper.

Decision rule: if an accessible competitor establishes an axis, remove that axis from the headline novelty claim. An uninspected or inaccessible competitor keeps the corresponding gap unresolved. Literature distinctions are conditional on the bounded inspected set; they never establish global absence or patent clearance.

Provenance rule: preserve every raw day-2 record and its reported route separately from verified query-log support. Do not repair missing historical query logs with a later acquisition. Keep screened citations and unscreened database hits distinguishable. No numeric recall until denominator eligibility, identities and acquisition provenance are complete.

Keep implementation-sensitive mechanism details withheld where disclosure approval is open. Public patent claim text may inform technical overlap only.

## 2026-09-15 clarification (plan `docs/specs/prior-art-closeout/plan.md`, T01)

Committed before the successor readings under that plan were judged; this is a targeted follow-up after earlier results were known, not a blind or independent preregistration. The original rubric above stands as historical context.

**Axis definitions used from this date.**

| Axis | What an affirmative finding must address |
| --- | --- |
| `equivalent_intent` | Equivalence of a stated recovery intention across identified configurations; sharing an interface or selecting one configured action is related work, not by itself this comparison. |
| `liveness_vs_setpoint_injection` | Separately identified liveness/heartbeat and setpoint-loss stimuli and their semantics; heartbeat loss alone does not establish the distinction. |
| `reconnection` | What happens to command acceptance/authority when the relevant input returns. Distinguish documented behaviour from a measured comparison. |
| `coverage` | Calibrated whole-recovery-trajectory containment over a specified horizon with separate evaluation; code coverage, policy-distance scores, per-mode oracles and static action tables are not this endpoint. |

**States.** `disclosed_or_addressed` (a discussion or specification counts, the rationale says which), `not_found_in_inspected` (a bounded reading result, never global absence), `not_applicable` (stated reason; not positive gap support), `unresolved`. Every record carries all four axes; a missing axis is unresolved.

**Access vocabulary.** Inspected: `full_text_sections`, `full_text_pdf`, `full_text_html`, `official_documentation`, `patent_claims`, `repository_files`. Not inspected (every axis unresolved in the consumers): `metadata_only`, `abstract_only`, `inaccessible`, `not_reinspected`, missing or unknown. A hash identifies bytes; the `axes` text must name the section or file that justifies each judgment.

**Identity map.** U1–U12 = the day-1 reference set (register byte-identical). S1 = UAVConfigFuzzer `10.14722/fuzzing.2026.23009`; S2 = ADGFuzz `10.14722/ndss.2026.231014`; S3 = PGPatch `10.1109/sp46214.2022.9833567` (S&P 2022; the earlier "2026 successors" label was wrong for S3). C-ids = canonical-export rows screened as relevant-unread or ambiguous, metadata only.

**Acquisition limit.** Exact identifier/title lookups and primary opens for named sources only; at most the primary route plus one lawful publisher/author/archive alternative; no new search legs, no export reruns, no native patent campaign. Canonical intake frozen at `evidence/task-2026-09-11-public/database-export.json`, SHA-256 `b523635bdc5bd08d9a41d017e9a782f184a5efa8d13e49ed3ca33cfae861775d`, 317 rows, 16 logged legs.

**Relevance screen.** Include cross-autopilot execution; timed safety/configuration policies; communication-loss recovery; trajectory reservations. Exclude tutorials, anecdotes, throughput-only work, unrelated domains, marketing. Missing abstract or unclear relevance is unresolved, never an exclusion.

**Conclusion rule.** URC-01 reports two fields: an evidence conclusion (`prior art found` / `supported candidate gap` / no conclusion when evidence is insufficient) and an independent gate status (`complete` / `partial` / `blocked`). Unread sources cannot support any conclusion about their contents.
