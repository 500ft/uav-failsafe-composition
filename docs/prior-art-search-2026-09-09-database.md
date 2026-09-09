# URC-D02 — native-database search export, 2026-09-09

Follow-up named by [URC-D01](prior-art-search-2026-09-08.md): "run a native scholarly-database
search where access is available; retain a screened export." This is the **export and recall
check**, not a screen. Nothing here closes the parent novelty gate or any owner gate.

## What was run

Three native databases through their public APIs, with the day-1 web-index queries rewritten as
plain keyword queries (no `site:` operators; patents excluded — no patent database is reachable
from this environment). Retrieved 2026-09-09T02:28:22Z.

| database | queries attempted | succeeded | unique records retained |
| --- | ---: | ---: | ---: |
| Crossref | 5 | 5 | 182 |
| OpenAlex | 5 | 5 | 130 |
| arXiv search API | 6 | 1 | 90 |

**arXiv's search endpoint throttled this run** (HTTP 429 on 5 of 6 queries despite 4–32 s
spacing and retries). Its id-lookup endpoint worked, so the arXiv leg is **incomplete, not
absent** — re-run `evidence/task-2026-09-09/rerun_search.py` from a network that arXiv does
not rate-limit. Raw export: [`database-export.json`](../evidence/task-2026-09-09/database-export.json)
/ [`.csv`](../evidence/task-2026-09-09/database-export.csv) (402 unique records, every one tagged with the query that produced it).

## Recall check against the day-1 screened set — the finding

Day 1 screened 12 sources, 6 of them resolvable to a database identifier. This run
retrieved **0 of 6**.

Diagnosis, done rather than assumed: all five day-1 arXiv items resolve by id at arXiv; OpenAlex
indexes 3 of the 5 by DOI; and **none** of them appears in the top 100 OpenAlex results for
`PX4 ArduPilot`, `PX4 ArduPilot failsafe` or `ArduPilot PX4 bug fuzzing`. So this is not a
query-wording accident. Native-database keyword ranking and web-index discovery surface different
populations for this topic, and the day-1 set was found by the latter. Neither leg substitutes for
the other; the complete novelty gate needs both, plus the full-text reads day 1 already lists.

## New candidates — UNSCREENED

[`candidates-unscreened.csv`](../evidence/task-2026-09-09/candidates-unscreened.csv) lists the 25 highest-scoring records not in the
day-1 set, ranked by a **keyword triage** over title and abstract (weights in `rerun_search.py`).
This is a reading order, not a relevance judgement: no candidate has been read against the
day-1 rubric, and none is asserted to be prior art or to be irrelevant. Top five by score:

| # | id | year | title (truncated) | score |
| --- | --- | --- | --- | ---: |
| 1 | [arxiv:2606.22289](https://arxiv.org/abs/2606.22289) | 2026 | Control-Aware Manipulation of ArduPilot via Legitimate MAVLink Commands: Simulation and Ha | 8 |
| 2 | [doi:10.1016/j.compeleceng.2026.111144](https://doi.org/10.1016/j.compeleceng.2026.111144) | 2026 | Flight log analysis and recovery for open-source drones: Focusing on ArduPilot, PX4, and B | 8 |
| 3 | [arxiv:1905.00265](https://arxiv.org/abs/1905.00265) | 2019 | MAVSec: Securing the MAVLink Protocol for Ardupilot/PX4 Unmanned Aerial Systems | 7 |
| 4 | [doi:10.3846/mla.2012.66](https://doi.org/10.3846/mla.2012.66) | 2012 | ERROR ANALYSIS OF INS ARRANGED IN ARDUPILOT MEGA / „ARDUPILOT MEGA“ AUTOPILOTO INERCINIO N | 6 |
| 5 | [arxiv:1811.06948](https://arxiv.org/abs/1811.06948) | 2018 | Closing the Gap in Swarm Robotics Simulations: An Extended Ardupilot/Gazebo plugin | 6 |


## What this does and does not change

- Adds a dated, reproducible native-database export with per-query provenance. Retained.
- Establishes that the two discovery routes diverge on this topic, so the day-1 web-index set
  cannot be assumed complete and the database set cannot be assumed to contain it.
- Does **not** screen anything, close the novelty gate, touch patents, or read a full text. The
  day-1 "Next" items — close-competitor full texts, native search where *institutional* access
  exists (Scopus/WoS/IEEE Xplore), patent claims with qualified help — all remain open.
- Does not authorise a simulator, fabrication or hardware campaign.
