#!/usr/bin/env python3
"""
Scenario coverage gate — Layer 3.5 (Functional Scenarios)  [phase-3-3]

Pairs each Complete Jira Story (Schema 1) with its scenarios file
(qa-scenarios-v1) by filename stem and verifies the scenario set is COMPLETE
and honours the two locked rules:

  RULE 1 (split per precondition-state) — structural: scenarios may carry
          precondition_state; not machine-verifiable beyond shape.
  RULE 2 (one owning scenario per BR)   — every BR is owns_br in >=1 scenario;
          a BR owned by >1 scenario is flagged advisory (confirm contexts differ).

Hard rules (any -> exit 1):
  STRUCT        _schema != qa-scenarios-v1 / missing ids / scenarios not a list /
                a scenario missing sc_id or ac_id
  DUP_SC        duplicate sc_id within a file
  AC_COVERAGE   an ac_id in Schema 1 is realized by NO scenario
  BR_UNOWNED    a br_id in Schema 1 is in no scenario's owns_br (rule never owned)
  PHANTOM_AC    a scenario.ac_id not in the paired Schema 1
  PHANTOM_BR    an owns_br/cites_br id not in the paired Schema 1
  NO_SUCCESS    expected.success missing or empty
  BAD_ALT       expected.alternative not a list
  BAD_ENUM      technique / test_layer outside the allowed set

Advisory (reported, exit 0):
  BR_MULTI_OWNER  a br in owns_br of >1 scenario (redundancy unless contexts differ)
  ALT_EMPTY_TECH  a BVA/EP/MultiCondition/StateTransition/Pairwise scenario with 0 alternatives
  PHANTOM_TC      a tc_id not found in the unit's *-test-design.md
  NO_SCENARIOS    a Schema 1 unit with no paired scenarios file (phase-3-3 not run)
  ORPHAN_SC       a scenarios file with no paired Schema 1

Invocation: python3 checks/scenario_coverage.py qa/PDT-3418
Scans qa/<epic>/ (always) + output/ (Schema 1 whose ids.epic_id == epic).
Stdlib only, deterministic, no network.
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
S1_SUFFIX = "-complete-jira-story"
SC_SUFFIX = "-scenarios"
TD_SUFFIX = "-test-design"
TECHNIQUES = {"BVA", "EP", "MultiCondition", "StateTransition", "Presence", "Pairwise"}
TEST_LAYERS = {"e2e", "api", "manual"}
ALT_TECHNIQUES = {"BVA", "EP", "MultiCondition", "StateTransition", "Pairwise"}  # expected >=1 alt


def collect(epic: str, glob: str, needle: str):
    found = {}
    for base in (REPO / "qa" / epic, REPO / "output"):
        if base.is_dir():
            for f in sorted(base.rglob(glob)):  # recurse into per-UC subfolders
                if f.name.startswith(".") or needle not in f.name:
                    continue
                found[f.resolve()] = f
    return list(found.values())


def parse_s1(epic: str):
    """{stem: (path, {ac_ids:set, br_ids:set})}"""
    qa_dir = (REPO / "qa" / epic).resolve()
    out, errs = {}, []
    for f in collect(epic, "*.json", "complete-jira-story"):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            errs.append((f.name, "PARSE", f"cannot parse: {e}"))
            continue
        fe = d.get("ids", {}).get("epic_id") if isinstance(d.get("ids"), dict) else None
        if not str(f.resolve()).startswith(str(qa_dir)) and fe != epic:
            continue
        stem = f.name[: -len(".json")].replace(S1_SUFFIX, "")
        out[stem] = (f, {
            "ac_ids": {a.get("ac_id") for a in d.get("acceptance_criteria", []) or [] if a.get("ac_id")},
            "br_ids": {b.get("br_id") for b in d.get("business_rules", []) or [] if b.get("br_id")},
        })
    return out, errs


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("usage: python3 checks/scenario_coverage.py qa/<epic>")
        return 2
    epic = Path(args[0].rstrip("/")).name

    s1, errs = parse_s1(epic)
    scen_files = {f.name[: -len(".json")].replace(SC_SUFFIX, ""): f
                  for f in collect(epic, "*.json", "scenarios")}
    td_files = {f.name[: -len(".md")].replace(TD_SUFFIX, ""): f
                for f in collect(epic, "*.md", "test-design") if f.name.endswith(TD_SUFFIX + ".md")}

    violations, advisories = list(errs), []
    print(f"Scenario coverage gate — epic {epic}")
    print(f"  Schema 1: {len(s1)} unit(s) · scenarios files: {len(scen_files)}")
    if not s1:
        print(f"\n❌ FAIL — no complete-jira-story files found for {epic}")
        return 1

    for stem in sorted(scen_files):
        if stem not in s1:
            advisories.append((stem, "ORPHAN_SC", "scenarios file has no paired complete-jira-story"))

    print()
    for stem in sorted(s1):
        _, spec = s1[stem]
        label = stem
        if stem not in scen_files:
            advisories.append((label, "NO_SCENARIOS", f"{stem}: no *-scenarios.json (phase-3-3 not run)"))
            print(f"  {label}: {len(spec['ac_ids'])} ACs · {len(spec['br_ids'])} BRs — no scenarios (skipped)")
            continue

        try:
            data = json.loads(scen_files[stem].read_text(encoding="utf-8"))
        except Exception as e:
            violations.append((label, "PARSE", f"cannot parse scenarios: {e}"))
            continue

        if data.get("_schema") != "qa-scenarios-v1":
            violations.append((label, "STRUCT", f"_schema={data.get('_schema')!r} (expected qa-scenarios-v1)"))
        scenarios = data.get("scenarios")
        if not isinstance(scenarios, list):
            violations.append((label, "STRUCT", "scenarios[] missing or not a list"))
            continue

        td_text = td_files[stem].read_text(encoding="utf-8") if stem in td_files else None
        sc_ids, realized_ac, owned_br, owner_count = [], set(), set(), {}
        for sc in scenarios:
            sid = sc.get("sc_id")
            if not sid:
                violations.append((label, "STRUCT", f"a scenario has no sc_id (ac={sc.get('ac_id')!r})"))
                continue
            sc_ids.append(sid)
            ac = sc.get("ac_id")
            if not ac:
                violations.append((label, "STRUCT", f"{sid} has no ac_id"))
            elif ac not in spec["ac_ids"]:
                violations.append((label, "PHANTOM_AC", f"{sid} references {ac} — not in Schema 1"))
            else:
                realized_ac.add(ac)

            if sc.get("technique") not in TECHNIQUES:
                violations.append((label, "BAD_ENUM", f"{sid} technique={sc.get('technique')!r} not in {sorted(TECHNIQUES)}"))
            if sc.get("test_layer") not in TEST_LAYERS:
                violations.append((label, "BAD_ENUM", f"{sid} test_layer={sc.get('test_layer')!r} not in {sorted(TEST_LAYERS)}"))

            exp = sc.get("expected", {}) if isinstance(sc.get("expected"), dict) else {}
            if not (isinstance(exp.get("success"), str) and exp.get("success").strip()):
                violations.append((label, "NO_SUCCESS", f"{sid} expected.success missing/empty"))
            alt = exp.get("alternative")
            if not isinstance(alt, list):
                violations.append((label, "BAD_ALT", f"{sid} expected.alternative not a list"))
                alt = []
            if sc.get("technique") in ALT_TECHNIQUES and len(alt) == 0:
                advisories.append((label, "ALT_EMPTY_TECH", f"{sid} ({sc.get('technique')}) has 0 alternatives — technique usually yields ≥1"))

            for b in sc.get("owns_br", []) or []:
                owned_br.add(b)
                owner_count[b] = owner_count.get(b, 0) + 1
            for b in list(sc.get("owns_br", []) or []) + list(sc.get("cites_br", []) or []):
                if b not in spec["br_ids"]:
                    violations.append((label, "PHANTOM_BR", f"{sid} references {b} — not in Schema 1 business_rules"))
            if td_text is not None:
                for tc in sc.get("tc_ids", []) or []:
                    if not re.search(rf"\b{re.escape(tc)}\b", td_text):
                        advisories.append((label, "PHANTOM_TC", f"{sid} tc_id {tc} not found in {td_files[stem].name}"))

        dup = sorted({x for x in sc_ids if sc_ids.count(x) > 1})
        if dup:
            violations.append((label, "DUP_SC", f"duplicate sc_id(s): {', '.join(dup)}"))

        # RULE completeness
        miss_ac = sorted(spec["ac_ids"] - realized_ac)
        for a in miss_ac:
            violations.append((label, "AC_COVERAGE", f"{a} realized by no scenario"))
        unowned = sorted(spec["br_ids"] - owned_br)
        for b in unowned:
            violations.append((label, "BR_UNOWNED", f"{b} is owns_br of no scenario (rule never authoritatively tested)"))
        for b, n in sorted(owner_count.items()):
            if n > 1:
                advisories.append((label, "BR_MULTI_OWNER", f"{b} owned by {n} scenarios — confirm contexts differ (else redundant)"))

        print(f"  {label}: {len(scenarios)} SC · AC {len(realized_ac)}/{len(spec['ac_ids'])} · BR owned {len(owned_br)}/{len(spec['br_ids'])}")

    print()
    if advisories:
        print("advisories:")
        for s, r, m in advisories:
            print(f"  · [{r}] {s}: {m}")
        print()
    if violations:
        print(f"❌ FAIL — {len(violations)} violation(s):")
        for s, r, m in violations:
            print(f"  ✗ [{r}] {s}: {m}")
        return 1
    covered = sum(1 for s in s1 if s in scen_files)
    print(f"✅ PASS — {covered}/{len(s1)} units have scenarios; every AC realized, every BR owned")
    return 0


if __name__ == "__main__":
    sys.exit(main())
