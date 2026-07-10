#!/usr/bin/env python3
"""
Schema-1 integrity gate — Layer 2 (QA Story Authoring)  [G1]

Validates every Complete Jira Story (complete-jira-story-v1) under an epic for
INTERNAL referential integrity — the class of error that slipped through the
manual PDT-3418 run and was only caught by throwaway scripts:

  - an AC cites a br_id that is NOT defined in the file        → DANGLING_BR
    (real: UC1a AC-10 cited BR-15 before it was defined)
  - a business_rule is defined but referenced by ZERO ACs      → DEAD_BR
    (real: UC2/UC3 carried an orphan BR-09)
  - duplicate ac_id / br_id within one file                    → DUP_AC / DUP_BR
  - structural / field gaps                                    → STRUCT / *_FIELDS

Every BR in a unit must be cited by >=1 AC, and every br_id an AC cites must be
defined — this is the AC<->BR traceability contract from business-rules.md.

Invocation:
    python3 checks/schema1_integrity.py qa/PDT-3418
    python3 checks/schema1_integrity.py PDT-3418

Hard rules (any → exit 1):
  SCHEMA       _schema != "complete-jira-story-v1"
  STRUCT       missing ids.{epic_id,story_id,uc_id} / business_rules[] / acceptance_criteria[]
  BR_FIELDS    a BR missing br_id or statement
  AC_FIELDS    an AC missing ac_id / given / when / then / br_ids(list)
  DUP_BR/DUP_AC duplicate id within a file
  DANGLING_BR  ac.br_ids references a br_id not in business_rules[]
  DEAD_BR      a business_rule referenced by zero ACs in the unit

Advisory (reported, exit 0):
  *_ENUM       unknown type/source value
  ALSO_USED_IN a br's also_used_in names a unit whose file does not define that br

Scans qa/<epic>/ (always) + output/ (files whose ids.epic_id == epic).
Stdlib only, deterministic, no network.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

BR_TYPES = {"permission", "constraint", "computation", "state"}
AC_TYPES = {"default_state", "happy_path", "alternative", "error_state", "edge_case"}
SOURCES = {"PM", "QA", "PM+QA"}


def collect(epic: str, needle: str):
    """Files in qa/<epic>/ (always) + output/ (epic-matched later), deduped by real path."""
    found = {}
    for base in (REPO / "qa" / epic, REPO / "output"):
        if base.is_dir():
            for f in sorted(base.rglob("*.json")):  # recurse into per-UC subfolders
                if f.name.startswith(".") or needle not in f.name:
                    continue
                found[f.resolve()] = f
    return list(found.values())


def check_unit(path: Path, data: dict):
    """Return (label, violations, advisories, info)."""
    v, a = [], []
    ids = data.get("ids", {}) if isinstance(data.get("ids"), dict) else {}
    label = ids.get("uc_id") or path.stem

    if data.get("_schema") != "complete-jira-story-v1":
        v.append((label, "SCHEMA", f"_schema={data.get('_schema')!r} (expected 'complete-jira-story-v1')"))
    for k in ("epic_id", "story_id", "uc_id"):
        if not ids.get(k):
            v.append((label, "STRUCT", f"ids.{k} missing"))
    if not data.get("title"):
        a.append((label, "STRUCT", "title missing"))

    brs = data.get("business_rules")
    acs = data.get("acceptance_criteria")
    if not isinstance(brs, list):
        v.append((label, "STRUCT", "business_rules[] missing or not a list"))
        brs = []
    if not isinstance(acs, list):
        v.append((label, "STRUCT", "acceptance_criteria[] missing or not a list"))
        acs = []

    # --- BR definitions ---
    br_ids = []
    also_used = {}  # br_id -> [unit ...]
    for br in brs:
        bid = br.get("br_id")
        if not bid:
            v.append((label, "BR_FIELDS", f"a business_rule has no br_id: {br.get('statement', br)!r}"))
            continue
        if not br.get("statement"):
            v.append((label, "BR_FIELDS", f"{bid} has no statement"))
        if br.get("type") not in BR_TYPES:
            a.append((label, "BR_ENUM", f"{bid} type={br.get('type')!r} not in {sorted(BR_TYPES)}"))
        br_ids.append(bid)
        if isinstance(br.get("also_used_in"), list):
            also_used[bid] = br["also_used_in"]
    dup_br = sorted({x for x in br_ids if br_ids.count(x) > 1})
    if dup_br:
        v.append((label, "DUP_BR", f"duplicate br_id(s): {', '.join(dup_br)}"))
    br_def = set(br_ids)

    # --- AC definitions + referential integrity ---
    ac_ids = []
    referenced_br = set()
    for ac in acs:
        aid = ac.get("ac_id")
        if not aid:
            v.append((label, "AC_FIELDS", f"an AC has no ac_id (scenario={ac.get('scenario', '?')!r})"))
            continue
        ac_ids.append(aid)
        for fld in ("given", "when", "then"):
            if fld not in ac:
                v.append((label, "AC_FIELDS", f"{aid} missing '{fld}'"))
        if ac.get("type") not in AC_TYPES:
            a.append((label, "AC_ENUM", f"{aid} type={ac.get('type')!r} not in {sorted(AC_TYPES)}"))
        if ac.get("source") not in SOURCES:
            a.append((label, "AC_ENUM", f"{aid} source={ac.get('source')!r} not in {sorted(SOURCES)}"))
        brl = ac.get("br_ids")
        if not isinstance(brl, list):
            v.append((label, "AC_FIELDS", f"{aid} br_ids missing or not a list"))
        else:
            for b in brl:
                referenced_br.add(b)
                if b not in br_def:
                    v.append((label, "DANGLING_BR", f"{aid} references {b} — not defined in business_rules[]"))
    dup_ac = sorted({x for x in ac_ids if ac_ids.count(x) > 1})
    if dup_ac:
        v.append((label, "DUP_AC", f"duplicate ac_id(s): {', '.join(dup_ac)}"))

    # --- DEAD_BR: defined but cited by no AC in this unit ---
    for b in sorted(br_def - referenced_br):
        v.append((label, "DEAD_BR", f"{b} defined but referenced by zero ACs in this unit"))

    info = {"label": label, "acs": len(ac_ids), "brs": len(br_def),
            "dangling": sum(1 for _, r, _ in v if r == "DANGLING_BR"),
            "dead": sum(1 for _, r, _ in v if r == "DEAD_BR"),
            "br_def": br_def, "also_used": also_used, "uc": ids.get("uc_id")}
    return label, v, a, info


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("usage: python3 checks/schema1_integrity.py qa/<epic>")
        return 2
    epic = Path(args[0].rstrip("/")).name
    qa_dir = REPO / "qa" / epic

    files = collect(epic, "complete-jira-story")
    parsed = []
    violations, advisories = [], []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            violations.append((f.name, "PARSE", f"cannot parse: {e}"))
            continue
        fe = data.get("ids", {}).get("epic_id") if isinstance(data.get("ids"), dict) else None
        in_qa = str(f.resolve()).startswith(str(qa_dir.resolve()))
        if not in_qa and fe != epic:
            continue  # unrelated file living under output/
        parsed.append((f, data))

    print(f"Schema-1 integrity gate — epic {epic}")
    print(f"  scanning: qa/{epic}/ + output/ for *complete-jira-story*.json")
    if not parsed:
        print(f"\n❌ FAIL — no complete-jira-story files found for {epic}")
        return 1
    print()

    infos = []
    for f, data in parsed:
        label, v, a, info = check_unit(f, data)
        violations += v
        advisories += a
        infos.append(info)
        print(f"  {label}: {info['acs']} ACs · {info['brs']} BRs · "
              f"dangling {info['dangling']} · dead {info['dead']}")

    # cross-file: also_used_in must point at units that actually define the br
    defined_by_uc = {i["uc"]: i["br_def"] for i in infos if i.get("uc")}
    for i in infos:
        for bid, units in i.get("also_used", {}).items():
            for u in units:
                if u in defined_by_uc and bid not in defined_by_uc[u]:
                    advisories.append((i["label"], "ALSO_USED_IN",
                                       f"{bid}.also_used_in lists {u}, but {u} does not define {bid}"))

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
    total_ac = sum(i["acs"] for i in infos)
    total_br = sum(i["brs"] for i in infos)
    print(f"✅ PASS — {len(infos)} units, {total_ac} ACs, {total_br} BRs — "
          f"no dangling/dead br_id, no dup id")
    return 0


if __name__ == "__main__":
    sys.exit(main())
