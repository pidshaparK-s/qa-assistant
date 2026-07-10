#!/usr/bin/env python3
"""
Testmo CSV exporter — converts qa-test-cases-v1 executable cases (+ optional
paired qa-automation-plan-v1 disposition) into a Testmo-importable CSV.

Columns (exact order):
  Folder, Test Title, Pre-condition, Steps, Expected, Priority, Test Data,
  AT Status, QA Responsibility

One CSV row per EC (executable case). Folder = "<epic_id>/<uc_id>" from the
test-cases file's ids{}. If a paired *-automation-plan.json exists (same
filename stem, "-test-cases" -> "-automation-plan"), AT Status is that EC's
at_status and QA Responsibility is derived from status/blocker; otherwise
both default to "QA (manual)" (nothing planned yet).

Usage:
  python3 tools/export_testmo_csv.py qa/PDT-3418 -o qa/PDT-3418/PDT-3418-testmo.csv
  python3 tools/export_testmo_csv.py qa/PDT-3418/PDT-3562-uc1a-test-cases.json

Stdlib only, deterministic, no network.
"""
import csv
import json
import sys
from pathlib import Path

HEADER = ["Folder", "Test Title", "Pre-condition", "Steps", "Expected",
          "Priority", "Test Data", "AT Status", "QA Responsibility"]
EC_SUFFIX = "-test-cases"
AP_SUFFIX = "-automation-plan"


def find_test_case_files(target: Path):
    if target.is_file():
        return [target]
    return sorted(target.rglob("*-test-cases.json"))  # recurse into per-UC subfolders


def paired_automation_plan(tc_file: Path):
    stem = tc_file.name[: -len(".json")]
    if not stem.endswith(EC_SUFFIX):
        return None
    ap_file = tc_file.parent / (stem[: -len(EC_SUFFIX)] + AP_SUFFIX + ".json")
    return ap_file if ap_file.is_file() else None


def fmt_list(items):
    if not items:
        return ""
    return "\n".join(f"- {i}" for i in items)


def fmt_steps(steps):
    if not steps:
        return ""
    return "\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1))


def fmt_test_data(data):
    if not isinstance(data, dict) or not data:
        return ""
    lines = []
    for k, v in data.items():
        if isinstance(v, list):
            v = ", ".join(str(x) for x in v)
        lines.append(f"{k}: {v}")
    return "\n".join(lines)


def qa_responsibility(plan_entry):
    if plan_entry is None:
        return "QA (manual)"
    status = plan_entry.get("status")
    if status == "Manual":
        blocker = plan_entry.get("blocker") or "manual"
        return f"QA (manual — {blocker})"
    if status == "Automate":
        if plan_entry.get("at_status") == "automated":
            return "Automation"
        return "QA (manual until automated)"
    return "QA (manual)"


def build_rows(tc_file: Path):
    tcd = json.loads(tc_file.read_text(encoding="utf-8"))
    if tcd.get("_schema") != "qa-test-cases-v1":
        print(f"  ! {tc_file}: _schema={tcd.get('_schema')!r}, skipping (expected qa-test-cases-v1)", file=sys.stderr)
        return []
    ids = tcd.get("ids", {})
    epic_id, uc_id = ids.get("epic_id", ""), ids.get("uc_id", "")
    folder = f"{epic_id}/{uc_id}" if epic_id or uc_id else tc_file.stem

    ap_file = paired_automation_plan(tc_file)
    plan_by_ec = {}
    if ap_file:
        apd = json.loads(ap_file.read_text(encoding="utf-8"))
        for e in apd.get("plan", []) or []:
            if e.get("ec_id"):
                plan_by_ec[e["ec_id"]] = e

    rows = []
    for c in tcd.get("cases", []) or []:
        ec_id = c.get("ec_id", "")
        plan_entry = plan_by_ec.get(ec_id)
        rows.append([
            folder,
            f"[{ec_id}] {c.get('name', '')}",
            fmt_list(c.get("preconditions")),
            fmt_steps(c.get("steps")),
            c.get("expected_result", ""),
            c.get("priority", ""),
            fmt_test_data(c.get("test_data")),
            plan_entry.get("at_status", "") if plan_entry else "",
            qa_responsibility(plan_entry),
        ])
    return rows


def main() -> int:
    argv = sys.argv[1:]
    out_path = None
    for flag in ("-o", "--output"):
        if flag in argv:
            out_path = Path(argv[argv.index(flag) + 1])
    args = [a for a in argv if not a.startswith("-")]
    args = [a for a in args if a != (str(out_path) if out_path else None)]

    if not args:
        print("usage: python3 tools/export_testmo_csv.py <qa/EPIC dir | path/to/*-test-cases.json> [-o out.csv]")
        return 2

    target = Path(args[0].rstrip("/"))
    if not target.exists():
        print(f"error: {target} not found")
        return 2

    tc_files = find_test_case_files(target)
    if not tc_files:
        print(f"error: no *-test-cases.json found under {target}")
        return 2

    all_rows = []
    for f in tc_files:
        rows = build_rows(f)
        print(f"  {f}: {len(rows)} case(s)")
        all_rows.extend(rows)

    if out_path is None:
        if target.is_dir():
            out_path = target / f"{target.name}-testmo.csv"
        else:
            out_path = target.parent / (target.name[: -len(".json")] + "-testmo.csv")

    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(HEADER)
        writer.writerows(all_rows)

    print(f"\n✅ wrote {len(all_rows)} row(s) → {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
