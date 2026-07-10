#!/usr/bin/env python3
"""
Test-case coverage gate — Layer 3.5 (Executable Test Cases)  [phase-3-4]

Pairs each scenarios file (qa-scenarios-v1) with its executable-cases file
(qa-test-cases-v1) by filename stem and verifies each scenario is expanded into
runnable cases COMPLETELY and WITHOUT over-testing:

  per scenario SC:  exactly  1+ EC  path="success"
                    AND      N  EC   path="alternative"   where N = len(SC.expected.alternative[])
                    AND      the alternative ECs' alt_index set == {0 .. N-1}

That "exactly N" is the anti-over-test teeth (mirrors admin-on-the-go's
test-cases check): fewer = a gap, more = redundant over-testing.

Hard rules (exit 1):
  STRUCT         _schema != qa-test-cases-v1 / missing ids / cases not a list /
                 an EC missing ec_id / sc_id / path
  DUP_EC         duplicate ec_id
  PATH_ENUM      path not in {success, alternative}
  PHANTOM_SC     an EC's sc_id not in the paired scenarios file
  NO_SUCCESS     a scenario has 0 success ECs
  ALT_COUNT      a scenario's alternative-EC count != len(expected.alternative[])
  ALT_INDEX      alternative ECs' alt_index set != {0..N-1} (dup / gap / out of range)
  EMPTY_FIELD    steps / test_data / expected_result empty on any EC

Advisory (exit 0):
  NO_TEST_CASES  a scenarios file with no paired *-test-cases.json (phase-3-4 not run)
  ORPHAN_EC      a *-test-cases.json with no paired scenarios file
  AC_MISMATCH    an EC's ac_id != the scenario's ac_id (inherited field drifted)

Invocation: python3 checks/test_case_coverage.py qa/PDT-3418
Stdlib only, deterministic, no network.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SC_SUFFIX = "-scenarios"
EC_SUFFIX = "-test-cases"
PATHS = {"success", "alternative"}


def collect(epic: str, needle: str):
    found = {}
    for base in (REPO / "qa" / epic, REPO / "output"):
        if base.is_dir():
            for f in sorted(base.rglob("*.json")):  # recurse into per-UC subfolders
                if f.name.startswith(".") or needle not in f.name:
                    continue
                found[f.resolve()] = f
    return list(found.values())


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("usage: python3 checks/test_case_coverage.py qa/<epic>")
        return 2
    epic = Path(args[0].rstrip("/")).name

    sc_files = {f.name[: -len(".json")].replace(SC_SUFFIX, ""): f
                for f in collect(epic, "scenarios")}
    ec_files = {f.name[: -len(".json")].replace(EC_SUFFIX, ""): f
                for f in collect(epic, "test-cases")}

    violations, advisories = [], []
    print(f"Test-case coverage gate — epic {epic}")
    print(f"  scenarios files: {len(sc_files)} · test-cases files: {len(ec_files)}")
    if not sc_files:
        print(f"\n❌ FAIL — no *-scenarios.json found for {epic} (run phase-3-3 first)")
        return 1

    for stem in sorted(ec_files):
        if stem not in sc_files:
            advisories.append((stem, "ORPHAN_EC", "test-cases file has no paired scenarios file"))

    print()
    for stem in sorted(sc_files):
        try:
            scen = json.loads(sc_files[stem].read_text(encoding="utf-8"))
        except Exception as e:
            violations.append((stem, "PARSE", f"cannot parse scenarios: {e}"))
            continue
        # {sc_id: {ac_id, alt_count}}
        sc_map = {}
        for sc in scen.get("scenarios", []) or []:
            if sc.get("sc_id"):
                alt = sc.get("expected", {}).get("alternative", []) if isinstance(sc.get("expected"), dict) else []
                sc_map[sc["sc_id"]] = {"ac_id": sc.get("ac_id"), "alt_count": len(alt) if isinstance(alt, list) else 0}

        if stem not in ec_files:
            advisories.append((stem, "NO_TEST_CASES", f"{stem}: no *-test-cases.json (phase-3-4 not run)"))
            print(f"  {stem}: {len(sc_map)} SC — no test-cases (skipped)")
            continue

        try:
            data = json.loads(ec_files[stem].read_text(encoding="utf-8"))
        except Exception as e:
            violations.append((stem, "PARSE", f"cannot parse test-cases: {e}"))
            continue
        if data.get("_schema") != "qa-test-cases-v1":
            violations.append((stem, "STRUCT", f"_schema={data.get('_schema')!r} (expected qa-test-cases-v1)"))
        cases = data.get("cases")
        if not isinstance(cases, list):
            violations.append((stem, "STRUCT", "cases[] missing or not a list"))
            continue

        ec_ids, by_sc = [], {}   # by_sc: sc_id -> {"success": n, "alt_idx": [..]}
        for ec in cases:
            eid = ec.get("ec_id")
            if not eid:
                violations.append((stem, "STRUCT", f"an EC has no ec_id (sc={ec.get('sc_id')!r})"))
                continue
            ec_ids.append(eid)
            sid, path = ec.get("sc_id"), ec.get("path")
            if not sid:
                violations.append((stem, "STRUCT", f"{eid} has no sc_id"))
                continue
            if sid not in sc_map:
                violations.append((stem, "PHANTOM_SC", f"{eid} references {sid} — not in scenarios file"))
                continue
            if path not in PATHS:
                violations.append((stem, "PATH_ENUM", f"{eid} path={path!r} not in {sorted(PATHS)}"))
            if ec.get("ac_id") and ec["ac_id"] != sc_map[sid]["ac_id"]:
                advisories.append((stem, "AC_MISMATCH", f"{eid} ac_id={ec['ac_id']} != scenario {sid} ac_id={sc_map[sid]['ac_id']}"))
            if not (isinstance(ec.get("steps"), list) and ec["steps"]):
                violations.append((stem, "EMPTY_FIELD", f"{eid} steps empty"))
            if not (isinstance(ec.get("test_data"), dict) and ec["test_data"]):
                violations.append((stem, "EMPTY_FIELD", f"{eid} test_data empty"))
            if not (isinstance(ec.get("expected_result"), str) and ec["expected_result"].strip()):
                violations.append((stem, "EMPTY_FIELD", f"{eid} expected_result empty"))

            rec = by_sc.setdefault(sid, {"success": 0, "alt_idx": []})
            if path == "success":
                rec["success"] += 1
            elif path == "alternative":
                rec["alt_idx"].append(ec.get("alt_index"))

        dup = sorted({x for x in ec_ids if ec_ids.count(x) > 1})
        if dup:
            violations.append((stem, "DUP_EC", f"duplicate ec_id(s): {', '.join(dup)}"))

        # per-scenario coverage
        for sid, info in sc_map.items():
            rec = by_sc.get(sid, {"success": 0, "alt_idx": []})
            if rec["success"] < 1:
                violations.append((stem, "NO_SUCCESS", f"{sid} has no path=success EC"))
            n = info["alt_count"]
            got = len(rec["alt_idx"])
            if got != n:
                violations.append((stem, "ALT_COUNT", f"{sid}: {got} alternative EC(s) but expected.alternative[] has {n} (must match exactly)"))
            # alt_index set must be exactly {0..n-1}
            expect_idx = set(range(n))
            got_idx = [i for i in rec["alt_idx"] if isinstance(i, int)]
            if set(got_idx) != expect_idx or len(got_idx) != len(rec["alt_idx"]):
                violations.append((stem, "ALT_INDEX", f"{sid}: alt_index set {sorted([i for i in rec['alt_idx'] if i is not None])} != required {sorted(expect_idx)}"))

        total_ec = len(ec_ids)
        print(f"  {stem}: {len(sc_map)} SC → {total_ec} EC")

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
    covered = sum(1 for s in sc_files if s in ec_files)
    print(f"✅ PASS — {covered}/{len(sc_files)} units expanded; every SC has 1+ success + exactly-N alternative ECs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
