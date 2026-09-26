# Results

**No study result is available.** The confirmation campaign is held, and nothing in this repository is a finding
about PX4 recovery behaviour.

What does exist, since 2026-09-20, is a working SIH/SITL apparatus and a small number of **diagnostic
development runs**: an autopilot was built, armed, flown, and injected with a hazard, and the captures are kept
outside git under `~/.cache/uav-failsafe-composition/runs/`. Their derived traces are re-derivable from the raw
captures with `python -m harness.normalize <run directory>`. They were run to find out why no failsafe action is
selected, so they are development evidence about the apparatus, never held-out confirmation and never a measured
result. The [2026-09-24 critique](../docs/specs/formal-composition/critique-2026-09-24.md) records why their
timing and verdicts needed repair before anything is concluded from them.

Since 2026-09-26 there is also one **executed component result**: PX4's own failsafe unit tests, nine of nine
passing at the pinned commit on an ordinary Ubuntu runner, from a hash-pinned binary
([evidence](../evidence/task-oracle-2026-09-26/README.md)). That is a statement about the framework's own test
suite. It is not a study result, it says nothing about why the integrated runtime commits no recovery mode, and
it does not validate this repository's model of the framework.

When a study result is generated, each one must link to its protocol, inputs, generator, uncertainty treatment,
and evidence state.
