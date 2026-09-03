#!/usr/bin/env python3
"""Check the public research-concept contract without claiming study results."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "README.md",
    "ROADMAP.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "assets/recovery-contracts-overview.svg",
    "docs/research-plan.md",
    "docs/prior-art.md",
    "docs/experiment-01-authority-loss.md",
    "docs/claim-ledger.md",
    "docs/data-and-figures.md",
    "docs/decision-log.md",
    "protocols/configuration-manifest.schema.json",
    "protocols/example-configuration-manifest.json",
    "data/README.md",
    "results/README.md",
)
REQUIRED_MANIFEST_KEYS = {
    "manifest_version",
    "study_id",
    "run_id",
    "evidence_state",
    "autopilot",
    "firmware_identifier",
    "airframe_id",
    "configuration_hash",
    "recovery_intention",
    "test_environment",
    "authority_loss_event",
    "initial_condition",
    "recording",
}
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def local_markdown_links(path: Path) -> list[Path]:
    links: list[Path] = []
    for raw_target in MARKDOWN_LINK.findall(path.read_text(encoding="utf-8")):
        target = raw_target.strip().split(" ", 1)[0]
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = unquote(target.split("#", 1)[0])
        if target:
            links.append((path.parent / target).resolve())
    return links


def run_checks() -> list[str]:
    errors: list[str] = []

    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "No simulation, HITL, or flight results" not in readme:
        errors.append("README must state that no simulation, HITL, or flight results exist")

    result_notice = (ROOT / "results/README.md").read_text(encoding="utf-8")
    if "No experimental or simulation results are available" not in result_notice:
        errors.append("results/README.md must preserve the empty-results notice")

    schema = json.loads(
        (ROOT / "protocols/configuration-manifest.schema.json").read_text(encoding="utf-8")
    )
    example = json.loads(
        (ROOT / "protocols/example-configuration-manifest.json").read_text(encoding="utf-8")
    )
    schema_required = set(schema.get("required", []))
    if schema_required != REQUIRED_MANIFEST_KEYS:
        errors.append("configuration schema required keys differ from the repository contract")
    missing_example = REQUIRED_MANIFEST_KEYS - set(example)
    if missing_example:
        errors.append(f"example manifest missing keys: {sorted(missing_example)}")
    if example.get("evidence_state") != "planned-example":
        errors.append("example manifest must remain labeled planned-example")

    for markdown in ROOT.rglob("*.md"):
        if ".git" in markdown.parts:
            continue
        for target in local_markdown_links(markdown):
            if not target.exists():
                errors.append(f"broken local link in {markdown.relative_to(ROOT)}: {target}")

    return errors


def main() -> int:
    errors = run_checks()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Repository contract: PASS")
    print("Evidence state: research design; no study results")
    return 0


if __name__ == "__main__":
    sys.exit(main())
