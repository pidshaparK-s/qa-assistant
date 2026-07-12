#!/usr/bin/env python3
"""
Testmo CSV exporter — team convention (sc-console-playwright manual-test-factory).

Reads a qa-manual-spec-v1 spec.json and emits the SAME Testmo CSV that their
generator.ts produces:
  columns: ID, Key, Name, Folder Path, Description, Preconditions, Steps,
           Expected Results, Priority, AC Covered, QA Responsibility
  - ID / Key left blank (Testmo assigns on import)
  - Steps numbered "1. …\n2. …"; Preconditions + Expected Results as "- " bullets
  - QA Responsibility from case.qaResponsibility (default "Fai")
  - QUOTE_MINIMAL, '\n' line terminator
  (Variant of sc-console generator.ts: adds QA Responsibility + bulleted pre/expected;
   Folder Path is section-only — pick the suite folder at Testmo import time.)

Extra spec fields (_schema, covers, configurations) are ignored on export — they
drive our coverage gate / traceability, not the Testmo import.

Usage:
  python3 tools/export_spec_testmo_csv.py qa/PDT-3418/_epic/PDT-3418-manual-spec.json \
      -o qa/PDT-3418/_epic/PDT-3418-manual-testmo.csv

Stdlib only, deterministic, no network.
"""
import csv
import json
import sys
from pathlib import Path

HEADER = ["ID", "Key", "Name", "Folder Path", "Description",
          "Preconditions", "Steps", "Expected Results", "Priority", "AC Covered", "QA Responsibility"]


def main() -> int:
    argv = sys.argv[1:]
    out_path = None
    for flag in ("-o", "--output"):
        if flag in argv:
            out_path = Path(argv[argv.index(flag) + 1])
    args = [a for a in argv if not a.startswith("-") and a != (str(out_path) if out_path else None)]
    if not args:
        print("usage: python3 tools/export_spec_testmo_csv.py <manual-spec.json> [-o out.csv]")
        return 2

    spec_path = Path(args[0])
    if not spec_path.is_file():
        print(f"error: {spec_path} not found")
        return 2
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if spec.get("_schema") != "qa-manual-spec-v1":
        print(f"error: {spec_path} _schema={spec.get('_schema')!r} (expected qa-manual-spec-v1)")
        return 2

    cases = spec.get("cases", []) or []
    if out_path is None:
        out_path = spec_path.parent / (spec_path.stem.replace("-manual-spec", "-manual-testmo") + ".csv")

    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        w.writerow(HEADER)
        for c in cases:
            steps = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(c.get("steps", [])))
            expected = "\n".join(f"- {x}" for x in c.get("expectedResults", []))
            pre = "\n".join(f"- {ln}" for ln in (c.get("preconditions", "") or "").split("\n") if ln.strip())
            acs = ", ".join(c.get("acs", []))
            w.writerow(["", "", c.get("name", ""), c.get("folderPath", ""),
                        c.get("description", ""), pre,
                        steps, expected, c.get("priority", ""), acs, c.get("qaResponsibility", "Fai")])

    print(f"✅ wrote {len(cases)} case row(s) → {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
