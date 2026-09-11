# Presentation migration verification

Date: September 10, 2026. Base commit: `76b4e5a10f62a62b3c890bda2eeea582ae987378`.
New identity: [500ft/uav-failsafe-composition](https://github.com/500ft/uav-failsafe-composition).

## Scope

The README, reviewer entry points, conceptual overview and contribution templates
were updated. CI now checks local navigation, anchors, identity and SVG accessibility,
with four offline positive/negative-control tests. The diagrams are hand-authored
concepts, not new simulation results or hardware photographs.

[Repository identity and design references](../../docs/REPOSITORY_IDENTITY.md)
explain the rename and intentionally retained historical names. See
[checks.json](checks.json) for the local baseline and comparison outputs,
commands, runtime and preservation check. Source/candidate identity and hosted
CI are verified separately on this change's pull request.

## Reproduce navigation checks

```sh
python tools/check_presentation.py . "UAV Failsafe Composition" uav-failsafe-composition
python tools/test_presentation.py
```

Run from the root after cloning and installing the repository's documented
requirements. Existing project checks are in the [CI workflow](../../.github/workflows/ci.yml)
and [reading guide](../../docs/START_HERE.md).

## Boundaries

The scientific datasets, paper sources, frozen protocols, site/parameter
registers and existing release artifacts were not altered. No existing research
gate was closed by presentation work. This is a software/documentation review,
not independent human or physical validation. Repository-license terms were
preserved, including the absence of an open-source license for Enclosure.
