#!/usr/bin/env python3
"""
Manual test-case coverage gate — Layer 3.7 (Manual Execution)

Validates the team-format manual spec (qa-manual-spec-v1 — the sc-console-playwright
manual-test-case convention) and verifies it still covers EVERY EC from the
test-cases files — i.e. consolidating 109 fiddly automation-grade EC into ~35
human-runnable cases did NOT silently drop coverage (Dropout Rule).

One epic-level file: qa/<epic>/**/[*-]manual-spec.json with cases[], each having a
covers[] list of the ec_id(s) it exercises in one pass.

Hard rules (exit 1):
  STRUCT        _schema != qa-manual-spec-v1 / cases not a list / a case missing
                name / steps / expectedResults / covers not a list
  DUP_NAME      duplicate case name
  PRIORITY_ENUM priority not in {P1,P2,P3,P4}          (team rule)
  PHANTOM_EC    a covers[] ec_id not present in any test-cases file
  AC_MISMATCH   a case's acs[] != the AC set derived from its covers[] (stale review field)
  MISSING_EC    an EC in the test-cases files is covered by no case (dropped)

Advisory (exit 0):
  NAME_FORMAT   a case name not of the form "[ Category ] Verify|Confirm ..."  (team rule)
  MANUAL_ONLY   a case with covers=[] (manual-only edge case, no EC backing)
  MULTI_COVER   an EC covered by >1 case (fine for manual — observed twice)
  NO_TESTCASES  no *-test-cases.json (nothing to check against)

Invocation: python3 checks/manual_runsheet_coverage.py qa/PDT-3418
Stdlib only, deterministic, no network.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PRIORITIES = {"P1", "P2", "P3", "P4"}
NAME_RE = re.compile(r"^\[ .+ \] (Verify|Confirm) .+")


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("usage: python3 checks/manual_runsheet_coverage.py qa/<epic>")
        return 2
    epic = Path(args[0].rstrip("/")).name
    base = REPO / "qa" / epic

    all_ec = set()
    ec2ac = {}
    tc_files = 0
    for f in sorted(base.rglob("*-test-cases.json")) if base.is_dir() else []:
        if f.name.startswith("."):
            continue
        tc_files += 1
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception as ex:
            print(f"❌ cannot parse {f.name}: {ex}")
            return 1
        uc = d.get("ids", {}).get("uc_id", "?")
        for c in d.get("cases", []) or []:
            if c.get("ec_id"):
                all_ec.add(c["ec_id"])
                ec2ac[c["ec_id"]] = (uc, c.get("ac_id"))

    print(f"Manual test-case coverage gate — epic {epic}")
    print(f"  test-cases files: {tc_files} · EC total: {len(all_ec)}")
    if not all_ec:
        print("\n· [NO_TESTCASES] no EC found — nothing to check")
        return 0

    matches = sorted(base.rglob("*manual-spec.json")) if base.is_dir() else []
    if not matches:
        print(f"\n❌ FAIL — no manual-spec.json under qa/{epic}/ (run the team-format builder first)")
        return 1
    spec_path = matches[0]
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except Exception as ex:
        print(f"\n❌ FAIL — cannot parse {spec_path.name}: {ex}")
        return 1

    violations, advisories = [], []
    if spec.get("_schema") != "qa-manual-spec-v1":
        violations.append(("STRUCT", f"_schema={spec.get('_schema')!r} (expected qa-manual-spec-v1)"))
    cases = spec.get("cases")
    if not isinstance(cases, list):
        print("\n❌ FAIL — cases[] missing or not a list")
        return 1

    names, cover_count = [], Counter()
    for c in cases:
        nm = c.get("name")
        if not nm:
            violations.append(("STRUCT", f"a case has no name (folderPath={c.get('folderPath')!r})"))
            continue
        names.append(nm)
        covers = c.get("covers")
        if not isinstance(covers, list):
            violations.append(("STRUCT", f"{nm!r} covers is not a list"))
            covers = []
        elif not covers:
            advisories.append(("MANUAL_ONLY", f"{nm!r} has no EC backing (manual-only edge case)"))
        if not (isinstance(c.get("steps"), list) and c["steps"]):
            violations.append(("STRUCT", f"{nm!r} steps empty"))
        if not (isinstance(c.get("expectedResults"), list) and c["expectedResults"]):
            violations.append(("STRUCT", f"{nm!r} expectedResults empty"))
        if c.get("priority") not in PRIORITIES:
            violations.append(("PRIORITY_ENUM", f"{nm!r} priority={c.get('priority')!r} not in {sorted(PRIORITIES)}"))
        if not c.get("folderPath"):
            violations.append(("STRUCT", f"{nm!r} has no folderPath"))
        if not NAME_RE.match(nm):
            advisories.append(("NAME_FORMAT", f"{nm!r} not '[ Category ] Verify …'"))
        for eid in covers or []:
            cover_count[eid] += 1
            if eid not in all_ec:
                violations.append(("PHANTOM_EC", f"{nm!r} covers {eid} — not in any test-cases file"))
        derived_acs = {f"{ec2ac[ec][0]} {ec2ac[ec][1]}" for ec in (covers or []) if ec in ec2ac}
        if set(c.get("acs", []) or []) != derived_acs:
            violations.append(("AC_MISMATCH", f"{nm!r} acs={sorted(c.get('acs', []) or [])} != AC derived from covers {sorted(derived_acs)}"))

    dup = sorted({x for x in names if names.count(x) > 1})
    if dup:
        violations.append(("DUP_NAME", f"duplicate case name(s): {', '.join(dup)}"))
    missing = sorted(all_ec - set(cover_count))
    if missing:
        violations.append(("MISSING_EC", f"{len(missing)} EC covered by no case: {', '.join(missing[:10])}{' …' if len(missing) > 10 else ''}"))
    multi = sorted(x for x, n in cover_count.items() if n > 1)
    if multi:
        advisories.append(("MULTI_COVER", f"{len(multi)} EC covered by >1 case (ok for manual)"))

    n = len(names)
    dist = Counter(c.get("priority") for c in cases)
    print(f"  cases: {n} · EC covered: {len(set(cover_count) & all_ec)}/{len(all_ec)}")
    if n:
        print("  priority: " + " · ".join(f"{p} {dist.get(p,0)} ({round(100*dist.get(p,0)/n)}%)" for p in ["P1", "P2", "P3", "P4"]))
    print()
    if advisories:
        print("advisories:")
        for r, m in advisories:
            print(f"  · [{r}] {m}")
        print()
    if violations:
        print(f"❌ FAIL — {len(violations)} violation(s):")
        for r, m in violations:
            print(f"  ✗ [{r}] {m}")
        return 1
    print(f"✅ PASS — {n} manual cases cover all {len(all_ec)} EC (nothing dropped)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
