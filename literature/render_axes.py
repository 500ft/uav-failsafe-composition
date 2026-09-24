"""Render literature/axes.md from register.json.

    python literature/render_axes.py            # rewrite axes.md
    python literature/render_axes.py --check    # axes.md is current (used by the test suite)

axes.md used to be maintained by hand, which is how L32 stayed a cell-biology thesis in the prose after the
register was in doubt. The register is now the only place an entry is edited.
"""
from __future__ import annotations
import sys
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from search_plan import AXES  # noqa: E402

TITLES = {"A_failsafe_testing": "Failsafe Testing", "B_formal_autopilot": "Formal Autopilot",
          "C_timed_hybrid": "Timed & Hybrid", "D_runtime_assurance": "Runtime Assurance",
          "E_contingency_ops": "Contingency Ops", "F_feature_interaction": "Feature Interaction",
          "G_sim_fidelity": "Simulation Fidelity", "H_fleet_composition": "Fleet Composition"}

HEADER = """# Annotated reading list, by axis

Generated from [register.json](register.json) by `render_axes.py`; edit the register, not this file. Access is
stated for every entry: **read** means the full text was inspected during the prior-art packet and its findings
live in `docs/day3-reading-records.json`; **not read** means an identifier was recorded but the text has not
been inspected, so nothing here claims anything about its contents. "Why it is on the list" is a reason for
reading, never a finding.

Identity is a separate question from access. An identifier that resolves still need not name the work the entry
was selected for, which is how L32 spent two days as a cell-biology thesis standing in for the Simplex paper.
Entries whose identity a person has checked against the reason for selection are marked *identity checked*;
the rest are marked *identity unverified*, which is the honest default. `identity-audit.json` records the
machine-checkable half. Corrected entries keep the record of what was wrong under `quarantined_identifier`.
"""


def render(reg: dict) -> str:
    out = [HEADER]
    for axis, description in AXES.items():
        entries = [e for e in reg["entries"] if e["axis"] == axis]
        out.append(f"\n## {TITLES[axis]} — {description}\n\n{len(entries)} entries.\n")
        for e in entries:
            venue, year = e.get("venue") or "", e.get("year")
            where = ", ".join([venue or "venue unrecorded", str(year) if year else "year unrecorded"])
            bits = [where, f"`{e['identifier']}`" if e["identifier"] else "no identifier resolved",
                    {"inspected_earlier": "**read**", "identifier_unresolved": "**identifier unresolved**"}
                    .get(e["access"], "not read")]
            matched = e["identity"]["intended_work_matched"]
            bits.append("identity checked" if matched in ("verified", "corrected") else "identity unverified")
            if e.get("relates_to_repository_record"):
                bits.append(f"repository record: `{e['relates_to_repository_record']}`")
            out.append(f"\n**{e['id']}. {e['title']}**  \n{' · '.join(bits)}  ")
            if e.get("quarantined_identifier"):
                q = e["quarantined_identifier"]
                out.append(f"\n*Corrected {e['identity']['checked_on']}.* This entry previously read "
                           f"`{q['identifier']}` / \"{q['title']}\" — {q['what_it_actually_is']}. "
                           f"{q['how_it_got_here'].capitalize()}; found by {q['found_by']}.  ")
            out.append(f"\n*Why it is on the list.* {e['why_selected']}  \n"
                       f"*What reading it would settle.* {e['what_it_would_settle']}\n")
    return "".join(out)


def main(argv: list[str]) -> int:
    text = render(json.loads((HERE / "register.json").read_text()))
    target = HERE / "axes.md"
    if "--check" in argv:
        if target.read_text() != text:
            print("axes.md is stale; run python literature/render_axes.py", file=sys.stderr)
            return 1
        print("axes.md is current")
        return 0
    target.write_text(text)
    print(f"wrote {target} ({len(text.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
