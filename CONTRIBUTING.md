# Contributing

Contributions should make the research easier to audit, reproduce, or falsify.

## Evidence rules

- Label every artifact as `literature`, `planned`, `simulation`, `HITL`, or `measured`.
- Do not convert a planned threshold into a result.
- Pin firmware versions, parameter files, airframe identity, and test-environment metadata for every trace.
- Keep generated outputs out of the repository until their generator and input provenance are documented.
- Preserve negative results and failed hypotheses.
- Do not use “safe,” “validated,” or “guaranteed” without evidence explicitly supporting that scope.

## Before opening a pull request

```bash
python scripts/check_repo_contract.py
python -m unittest discover -s tests -v
```

Physical experiments additionally require approval from the responsible laboratory or facility. A contribution to this repository is not flight authorization.
