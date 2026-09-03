# Decision Log

## 2026-09-03 — Use the configured vehicle as the experimental identity

**Decision:** analyze autopilot + firmware + airframe + complete parameters rather than “PX4 versus ArduPilot.”

**Reason:** both platforms expose configurable failsafe actions and delays. A brand comparison would confound software, tuning, airframe, and intention.

## 2026-09-03 — Narrow the candidate contribution

**Decision:** focus on empirical post-authority-loss recovery contracts.

**Rejected framing:** generic capability-aware fleet safety, health contracts, or recovery reservations.

**Reason:** those ingredients have close prior art. The more defensible question concerns native mode transitions and recovery trajectories after companion authority disappears.

## 2026-09-03 — Start with a conformance benchmark

**Decision:** run a matched SITL pilot before building a fleet allocator.

**Reason:** if individualized native behaviors do not materially change the recovery envelope, fleet optimization would add complexity without evidence of value.

## 2026-09-03 — Keep physical flight contingent

**Decision:** physical testing is a later, facility-approved gate.

**Reason:** the present repository contains no flight evidence, approved test plan, or demonstrated operating envelope.
