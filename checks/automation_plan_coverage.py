#!/usr/bin/env python3
"""
Automation-plan coverage gate — Layer 3.6 (Automation Plan)  [phase-3-5]

Pairs each executable-cases file (qa-test-cases-v1) with its automation-plan
file (qa-automation-plan-v1) by filename stem and verifies EVERY EC has a
deliberate automation disposition — automate vs manual — with a consistent
lifecycle status and (for automatable ones) a spec-keying target.

The model (user's vocabulary):
  AT status  "cannot automated"                 -> status "Manual"
  AT status  "wait for automated" | "automated" -> status "Automate"
  livestream / live-broadcast cases             -> MUST be Manual (cannot automate)

Every EC is accounted for (Dropout Rule): plan entries ⋈ test-cases is a
bijection. No EC may silently vanish into "unclassified".

Hard rules (exit 1):
  STRUCT          _schema != qa-automation-plan-v1 / missing ids / plan not a list /
                  an entry missing ec_id / at_status / status
  DUP_EC          duplicate ec_id in the plan
  MISSING_EC      an EC in the test-cases file has no plan entry (unclassified)
  PHANTOM_EC      a plan entry's ec_id is not in the paired test-cases file
  AT_ENUM         at_status not in {cannot automated, wait for automated, automated}
  STATUS_ENUM     status not in {Manual, Automate}
  INVARIANT       at_status<->status inconsistent (cannot automated<->Manual;
                  wait for automated/automated<->Automate)
  MANUAL_FIELDS   status=Manual but blocker not in the blocker enum OR reason empty
  MANUAL_TARGET   status=Manual but a non-null target is set (don't plan a spec for it)
  AUTOMATE_TARGET status=Automate but target missing repo/spec/tag
  TAG_KEY         Automate target.tag != "@"+ec_id (breaks EC<->test bijection/keying)
  AUTOMATE_BLOCKER status=Automate but a blocker is set (contradiction)
  LIVE_RULE       blocker=live-broadcast but status != Manual (livestream must be manual)

Advisory (exit 0):
  NO_PLAN         a test-cases file with no paired *-automation-plan.json (phase-3-5 not run)
  ORPHAN_PLAN     a plan file with no paired test-cases file
  SC_DRIFT        entry sc_id != the EC's sc_id (inherited field drifted)
  AC_DRIFT        entry ac_id != the EC's ac_id

Invocation: python3 checks/automation_plan_coverage.py qa/PDT-3418
Stdlib only, deterministic, no network.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EC_SUFFIX = "-test-cases"
AP_SUFFIX = "-automation-plan"
AT_ENUM = {"cannot automated", "wait for automated", "automated"}
STATUS_ENUM = {"Manual", "Automate"}
BLOCKER_ENUM = {"live-broadcast", "observe-only", "wallclock-duration", "web-platform-timing"}
AT_MANUAL = {"cannot automated"}
AT_AUTOMATE = {"wait for automated", "automated"}


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
        print("usage: python3 checks/automation_plan_coverage.py qa/<epic>")
        return 2
    epic = Path(args[0].rstrip("/")).name

    ec_files = {f.name[: -len(".json")].replace(EC_SUFFIX, ""): f
                for f in collect(epic, "test-cases")}
    ap_files = {f.name[: -len(".json")].replace(AP_SUFFIX, ""): f
                for f in collect(epic, "automation-plan")}

    violations, advisories = [], []
    print(f"Automation-plan coverage gate — epic {epic}")
    print(f"  test-cases files: {len(ec_files)} · automation-plan files: {len(ap_files)}")
    if not ec_files:
        print(f"\n❌ FAIL — no *-test-cases.json found for {epic} (run phase-3-4 first)")
        return 1

    for stem in sorted(ap_files):
        if stem not in ec_files:
            advisories.append((stem, "ORPHAN_PLAN", "automation-plan file has no paired test-cases file"))

    tally = {"Automate": 0, "Manual": 0}
    blocker_tally = {}
    print()
    for stem in sorted(ec_files):
        try:
            ecd = json.loads(ec_files[stem].read_text(encoding="utf-8"))
        except Exception as e:
            violations.append((stem, "PARSE", f"cannot parse test-cases: {e}"))
            continue
        # {ec_id: {sc_id, ac_id}}
        ec_map = {}
        for c in ecd.get("cases", []) or []:
            if c.get("ec_id"):
                ec_map[c["ec_id"]] = {"sc_id": c.get("sc_id"), "ac_id": c.get("ac_id")}

        if stem not in ap_files:
            advisories.append((stem, "NO_PLAN", f"{stem}: no *-automation-plan.json (phase-3-5 not run)"))
            print(f"  {stem}: {len(ec_map)} EC — no automation-plan (skipped)")
            continue

        try:
            apd = json.loads(ap_files[stem].read_text(encoding="utf-8"))
        except Exception as e:
            violations.append((stem, "PARSE", f"cannot parse automation-plan: {e}"))
            continue
        if apd.get("_schema") != "qa-automation-plan-v1":
            violations.append((stem, "STRUCT", f"_schema={apd.get('_schema')!r} (expected qa-automation-plan-v1)"))
        plan = apd.get("plan")
        if not isinstance(plan, list):
            violations.append((stem, "STRUCT", "plan[] missing or not a list"))
            continue

        seen, unit_auto, unit_manual = [], 0, 0
        for e in plan:
            eid = e.get("ec_id")
            if not eid:
                violations.append((stem, "STRUCT", f"a plan entry has no ec_id (status={e.get('status')!r})"))
                continue
            seen.append(eid)
            at, st = e.get("at_status"), e.get("status")
            if eid not in ec_map:
                violations.append((stem, "PHANTOM_EC", f"{eid} not in test-cases file"))
                continue
            if at not in AT_ENUM:
                violations.append((stem, "AT_ENUM", f"{eid} at_status={at!r} not in {sorted(AT_ENUM)}"))
            if st not in STATUS_ENUM:
                violations.append((stem, "STATUS_ENUM", f"{eid} status={st!r} not in {sorted(STATUS_ENUM)}"))
            # invariant
            if at in AT_MANUAL and st != "Manual":
                violations.append((stem, "INVARIANT", f"{eid} at_status='cannot automated' but status={st!r} (must be Manual)"))
            if at in AT_AUTOMATE and st != "Automate":
                violations.append((stem, "INVARIANT", f"{eid} at_status={at!r} but status={st!r} (must be Automate)"))
            blocker = e.get("blocker")
            target = e.get("target")
            if st == "Manual":
                unit_manual += 1
                if blocker not in BLOCKER_ENUM:
                    violations.append((stem, "MANUAL_FIELDS", f"{eid} Manual but blocker={blocker!r} not in {sorted(BLOCKER_ENUM)}"))
                else:
                    blocker_tally[blocker] = blocker_tally.get(blocker, 0) + 1
                if not (isinstance(e.get("reason"), str) and e["reason"].strip()):
                    violations.append((stem, "MANUAL_FIELDS", f"{eid} Manual but reason empty"))
                if target:
                    violations.append((stem, "MANUAL_TARGET", f"{eid} Manual but has a target (don't plan a spec for an un-automatable case)"))
            elif st == "Automate":
                unit_auto += 1
                if blocker:
                    violations.append((stem, "AUTOMATE_BLOCKER", f"{eid} Automate but blocker={blocker!r} set"))
                if not (isinstance(target, dict) and target.get("repo") and target.get("spec") and target.get("tag")):
                    violations.append((stem, "AUTOMATE_TARGET", f"{eid} Automate but target missing repo/spec/tag"))
                elif target.get("tag") != "@" + eid:
                    violations.append((stem, "TAG_KEY", f"{eid} target.tag={target.get('tag')!r} != '@{eid}' (spec-keying must equal the EC id)"))
            # livestream rule
            if blocker == "live-broadcast" and st != "Manual":
                violations.append((stem, "LIVE_RULE", f"{eid} blocker=live-broadcast but status={st!r} (livestream must be Manual)"))
            # inherited drift (advisory)
            if e.get("sc_id") and e["sc_id"] != ec_map[eid]["sc_id"]:
                advisories.append((stem, "SC_DRIFT", f"{eid} sc_id={e['sc_id']} != EC {ec_map[eid]['sc_id']}"))
            if e.get("ac_id") and e["ac_id"] != ec_map[eid]["ac_id"]:
                advisories.append((stem, "AC_DRIFT", f"{eid} ac_id={e['ac_id']} != EC {ec_map[eid]['ac_id']}"))

        dup = sorted({x for x in seen if seen.count(x) > 1})
        if dup:
            violations.append((stem, "DUP_EC", f"duplicate ec_id(s): {', '.join(dup)}"))
        missing = sorted(set(ec_map) - set(seen))
        if missing:
            violations.append((stem, "MISSING_EC", f"{len(missing)} EC unclassified: {', '.join(missing[:8])}{' …' if len(missing) > 8 else ''}"))

        tally["Automate"] += unit_auto
        tally["Manual"] += unit_manual
        print(f"  {stem}: {len(ec_map)} EC → {unit_auto} Automate / {unit_manual} Manual")

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
    covered = sum(1 for s in ec_files if s in ap_files)
    print(f"✅ PASS — {covered}/{len(ec_files)} units planned; "
          f"{tally['Automate']} Automate / {tally['Manual']} Manual "
          f"(blockers: {blocker_tally or '—'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
