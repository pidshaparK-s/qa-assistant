#!/usr/bin/env python3
"""
BR -> Test-Condition coverage gate — Layer 3 (Test Design)  [L3]

Pairs each Complete Jira Story (complete-jira-story-v1) with its L3 test-design
doc (`<stem>-test-design.md`) by filename stem and verifies the test design
actually covers the spec:

Hard rules (any → exit 1):
  BR_COVERAGE  a br_id in Schema 1 appears in NO test-design doc for its unit
               (the process-doc L3 gate: every BR has >=1 test condition)
  AC_COVERAGE  an ac_id in Schema 1 appears nowhere in its test-design doc

Advisory (reported, exit 0):
  NO_TESTDESIGN  a Schema 1 unit has no paired *-test-design.md (L3 not done yet)
  ORPHAN_TD      a test-design doc with no paired Schema 1

Coverage is checked by substring presence of the id in the doc text (same
approach as ac_coverage.py) — it proves the id is addressed, not that the
technique is correct (that is the skill's job). Pair key = filename stem with
`-complete-jira-story` / `-test-design` stripped.

Invocation:
    python3 checks/br_tc_coverage.py qa/PDT-3418
    python3 checks/br_tc_coverage.py PDT-3418

Scans qa/<epic>/ (always) + output/ (Schema 1 whose ids.epic_id == epic).
Stdlib only, deterministic, no network.
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
S1_SUFFIX = "-complete-jira-story"
TD_SUFFIX = "-test-design"


def collect(epic: str, glob: str, needle: str):
    found = {}
    for base in (REPO / "qa" / epic, REPO / "output"):
        if base.is_dir():
            for f in sorted(base.glob(glob)):
                if f.name.startswith(".") or needle not in f.name:
                    continue
                found[f.resolve()] = f
    return list(found.values())


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("usage: python3 checks/br_tc_coverage.py qa/<epic>")
        return 2
    epic = Path(args[0].rstrip("/")).name
    qa_dir = (REPO / "qa" / epic).resolve()

    # Schema 1 (spec) by stem
    specs = {}
    violations, advisories = [], []
    for f in collect(epic, "*.json", "complete-jira-story"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            violations.append((f.name, "PARSE", f"cannot parse: {e}"))
            continue
        fe = data.get("ids", {}).get("epic_id") if isinstance(data.get("ids"), dict) else None
        if not str(f.resolve()).startswith(str(qa_dir)) and fe != epic:
            continue
        stem = f.name[: -len(".json")].replace(S1_SUFFIX, "")
        specs[stem] = (f, data)

    # test-design docs by stem (exact `<stem>-test-design.md`, not `-test-design-overview.md`)
    tds = {}
    for f in collect(epic, "*.md", "test-design"):
        if not f.name.endswith(TD_SUFFIX + ".md"):
            continue
        stem = f.name[: -len(".md")].replace(TD_SUFFIX, "")
        tds[stem] = f

    print(f"BR->TC coverage gate — epic {epic}")
    print(f"  Schema 1: {len(specs)} unit(s) · test-design docs: {len(tds)}")
    if not specs:
        print(f"\n❌ FAIL — no complete-jira-story files found for {epic}")
        return 1

    for stem in sorted(tds):
        if stem not in specs:
            advisories.append((stem, "ORPHAN_TD", "test-design doc has no paired complete-jira-story"))

    print()
    for stem in sorted(specs):
        _, d = specs[stem]
        label = d.get("ids", {}).get("uc_id") or stem
        br_ids = [br.get("br_id") for br in d.get("business_rules", []) or [] if br.get("br_id")]
        ac_ids = [ac.get("ac_id") for ac in d.get("acceptance_criteria", []) or [] if ac.get("ac_id")]

        if stem not in tds:
            advisories.append((label, "NO_TESTDESIGN", f"{stem}: no *-test-design.md (L3 not run for this unit)"))
            print(f"  {label}: {len(br_ids)} BRs · {len(ac_ids)} ACs — no test-design doc (skipped)")
            continue

        text = tds[stem].read_text(encoding="utf-8")
        # word-boundary match so BR-1 does not spuriously match BR-15
        miss_br = [b for b in br_ids if not re.search(rf"\b{re.escape(b)}\b", text)]
        miss_ac = [a for a in ac_ids if not re.search(rf"\b{re.escape(a)}\b", text)]
        for b in miss_br:
            violations.append((label, "BR_COVERAGE", f"{b} has no test condition in {tds[stem].name}"))
        for a in miss_ac:
            violations.append((label, "AC_COVERAGE", f"{a} not addressed in {tds[stem].name}"))
        print(f"  {label}: BR {len(br_ids) - len(miss_br)}/{len(br_ids)} · AC {len(ac_ids) - len(miss_ac)}/{len(ac_ids)}")

    print()
    if advisories:
        print("advisories:")
        for s, r, msg in advisories:
            print(f"  · [{r}] {s}: {msg}")
        print()
    if violations:
        print(f"❌ FAIL — {len(violations)} violation(s):")
        for s, r, msg in violations:
            print(f"  ✗ [{r}] {s}: {msg}")
        return 1
    covered = sum(1 for s in specs if s in tds)
    print(f"✅ PASS — {covered}/{len(specs)} units test-designed; every BR + AC covered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
