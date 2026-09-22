# Literature

A reading list for this project, with verified identifiers, organised by the question each axis has to settle.
It is **not** a set of findings. Of 55 entries, 9 were read in full during the prior-art packet and their
findings live in `docs/day3-reading-records.json`; 45 have a verified identifier and have **not** been read;
1 is unresolved. Every entry states which, and a test fails if an unread entry is described as establishing
anything.

| file | what it is |
|---|---|
| [axes.md](axes.md) | the annotated list, grouped by axis, with why each work is on it and what reading it would settle |
| [register.json](register.json) | the machine-readable register; edit this, not `axes.md` |
| [search_plan.py](search_plan.py) | the frozen query plan, 21 queries across 8 axes |
| [`evidence/task-literature-2026-09-22/`](../evidence/task-literature-2026-09-22/README.md) | how the search was run, its audit, and its limits |

## Why these axes

The project's own question axes account for four of them. Two more exist because the prior-art packet closed
with them unsearched, and they are where the current programme actually lives:

| axis | entries | why it is here |
|---|---|---|
| A, failsafe and configuration testing | 14 | the field this project sits next to, and the one it must distinguish itself from |
| B, formal verification of autopilot software | 9 | **never searched before this task.** The programme's spine is an extracted, checkable model |
| C, timed automata and hybrid reachability | 8 | the formalism and tooling the check would use, including where decidability stops |
| D, run-time assurance | 8 | monitor, switch, recovery function: the pattern PX4's failsafe framework instantiates |
| E, contingency operations and lost link | 5 | the operational meaning of the behaviour being modelled |
| F, feature interaction and mode confusion | 7 | **never searched before this task,** and the closest thing to a name for this project's question |
| G, simulation fidelity | 2 | what a SITL result is worth |
| H, fleet composition | 2 | deferred scope, tracked so it is not rediscovered later |

## The three entries to read first

1. **L15, extracting verification models from source code.** The method paper for Study A, and the one that
   states the fidelity problem this project has to solve rather than assume away.
2. **L45, the feature-interaction benchmark.** Individually correct mechanisms that misbehave in combination
   is a studied problem with a detection contest behind it. If that literature transfers, it reframes the
   contribution; if it does not, the reason why is itself worth writing down.
3. **L36, multi-layered run-time assurance.** Several monitors and the arbitration between them is the
   priority-consistency property stated in someone else's vocabulary.

Then **L46** (model checking for mode confusion) and **L31** (bounded model checking combined with fuzzing),
because between them they set the bar for what "predict, then confirm by replay" can claim as distinct.

## Rules this list follows

- An identifier is recorded with the route that produced it. Nothing is cited from memory.
- Access is stated per entry. A work that was not read cannot support a claim about its contents, and the
  phrasing of every unread entry is constrained to why it was chosen and what reading it would settle.
- A work that could not be resolved stays on the list marked unresolved. It is not dropped and it is not
  given a plausible-looking identifier.
- **This list does not change URC-01.** The prior-art packet's denominators, eligibility register and
  coverage numbers are untouched. Where an entry corresponds to a row the earlier intake left unread, the
  mapping is recorded so a later task can resolve it deliberately.
- The repository's standing rule of no new broad search was lifted by the owner for this task only, on
  2026-09-22. It stands for everything else.

## What this list does not do

It does not establish novelty, and it does not close URC-01, which remains partial. Reading 45 works would
change that; listing them does not.
