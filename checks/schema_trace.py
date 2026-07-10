#!/usr/bin/env python3
"""
Schema-1 <-> Schema-2 traceability gate — Layer 2 (QA Story Authoring)  [G2]

Pairs each Complete Jira Story (complete-jira-story-v1) with its User Flow
(user-flow-v1) by FILENAME STEM — `<story>-<unit>-complete-jira-story.json`
pairs with `<story>-<unit>-user-flow.json`. (Stem, not ids: UC1a and UC1b share
story_id PDT-3562 and only differ by unit.)

Verifies the flows fully + faithfully cover the story — the checks that during
the PDT-3418 run were only done by a throwaway script:

Hard rules (any → exit 1):
  AC_COVERAGE       an ac_id in Schema 1 appears in NO flow (flow.ac_ids or step.ac_ids)
  PHANTOM_AC        a flow/step cites an ac_id not in the paired Schema 1
  PHANTOM_BR        a flow/step cites a br_id not in the paired Schema 1's business_rules[]
  UNDECLARED_ACTOR  a step.actor not in the file's actors{} (prefix before '-' allowed, e.g. admin-A)
  STRUCT            a user-flow file missing actors{} / flows[]

Advisory (reported, exit 0):
  NO_FLOWS      a Schema 1 unit has no paired Schema 2 (flows not built yet)
  ORPHAN_FLOWS  a Schema 2 file with no paired Schema 1
  ACTOR_VOCAB   an actor outside the canonical vocab (viewer/app/player/sdk/network/system)
  UNKNOWN_ENTRY entry_from that resolves to no known flow_id across the epic
  IDS_MISMATCH  paired files disagree on ids.story_id / ids.uc_id

Invocation:
    python3 checks/schema_trace.py qa/PDT-3418
    python3 checks/schema_trace.py PDT-3418

Scans qa/<epic>/ (always) + output/ (files whose ids.epic_id == epic).
Stdlib only, deterministic, no network.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CANON_ACTORS = {"viewer", "app", "player", "sdk", "network", "system"}

S1_SUFFIX = "-complete-jira-story"
S2_SUFFIX = "-user-flow"


def collect(epic: str, needle: str):
    found = {}
    for base in (REPO / "qa" / epic, REPO / "output"):
        if base.is_dir():
            for f in sorted(base.rglob("*.json")):  # recurse into per-UC subfolders
                if f.name.startswith(".") or needle not in f.name:
                    continue
                found[f.resolve()] = f
    return list(found.values())


def parse_relevant(epic: str, needle: str):
    """{stem_key: (path, data)} for files that belong to the epic."""
    qa_dir = (REPO / "qa" / epic).resolve()
    out = {}
    errs = []
    for f in collect(epic, needle):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            errs.append((f.name, "PARSE", f"cannot parse: {e}"))
            continue
        fe = data.get("ids", {}).get("epic_id") if isinstance(data.get("ids"), dict) else None
        in_qa = str(f.resolve()).startswith(str(qa_dir))
        if not in_qa and fe != epic:
            continue
        suffix = S1_SUFFIX if needle == "complete-jira-story" else S2_SUFFIX
        key = f.name[: -len(".json")].replace(suffix, "")
        out[key] = (f, data)
    return out, errs


def flow_and_step_ids(flows, field):
    """All values of `field` (ac_ids/br_ids) from flow level + step level."""
    vals = set()
    for fl in flows:
        for x in fl.get(field, []) or []:
            vals.add(x)
        for st in fl.get("steps", []) or []:
            for x in st.get(field, []) or []:
                vals.add(x)
    return vals


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("usage: python3 checks/schema_trace.py qa/<epic>")
        return 2
    epic = Path(args[0].rstrip("/")).name

    s1, e1 = parse_relevant(epic, "complete-jira-story")
    s2, e2 = parse_relevant(epic, "user-flow")

    violations = list(e1) + list(e2)
    advisories = []

    print(f"Schema-1<->2 traceability gate — epic {epic}")
    print(f"  Schema 1: {len(s1)} unit(s) · Schema 2: {len(s2)} unit(s)")
    if not s1:
        print(f"\n❌ FAIL — no complete-jira-story files found for {epic}")
        return 1

    # global flow_id set for entry_from resolution (across the whole epic)
    all_flow_ids = set()
    for _, data in s2.values():
        for fl in data.get("flows", []) or []:
            if fl.get("flow_id"):
                all_flow_ids.add(fl["flow_id"])

    for key in sorted(s2):
        if key not in s1:
            advisories.append((key, "ORPHAN_FLOWS", "user-flow file has no paired complete-jira-story"))

    print()
    for key in sorted(s1):
        _, d1 = s1[key]
        label = d1.get("ids", {}).get("uc_id") or key
        ac_def = {ac.get("ac_id") for ac in d1.get("acceptance_criteria", []) or [] if ac.get("ac_id")}
        br_def = {br.get("br_id") for br in d1.get("business_rules", []) or [] if br.get("br_id")}

        if key not in s2:
            advisories.append((label, "NO_FLOWS", f"{key}: Schema 1 has no paired user-flow (flows not built?)"))
            print(f"  {label}: {len(ac_def)} ACs — no paired flows (skipped)")
            continue

        _, d2 = s2[key]
        flows = d2.get("flows") if isinstance(d2.get("flows"), list) else None
        actors = d2.get("actors") if isinstance(d2.get("actors"), dict) else None
        if flows is None:
            violations.append((label, "STRUCT", f"{key} user-flow missing flows[]"))
            continue
        if actors is None:
            violations.append((label, "STRUCT", f"{key} user-flow missing actors{{}}"))
            actors = {}

        # ids agreement (advisory)
        for fld in ("story_id", "uc_id"):
            a1 = d1.get("ids", {}).get(fld)
            a2 = d2.get("ids", {}).get(fld)
            if a1 and a2 and a1 != a2:
                advisories.append((label, "IDS_MISMATCH", f"{key}: Schema1 ids.{fld}={a1} != Schema2 {a2}"))

        cited_ac = flow_and_step_ids(flows, "ac_ids")
        cited_br = flow_and_step_ids(flows, "br_ids")

        # AC_COVERAGE
        missing = sorted(ac_def - cited_ac)
        if missing:
            violations.append((label, "AC_COVERAGE", f"ac_id(s) in no flow: {', '.join(missing)}"))
        # PHANTOM_AC / PHANTOM_BR
        for x in sorted(cited_ac - ac_def):
            violations.append((label, "PHANTOM_AC", f"flow cites {x} — not in Schema 1 acceptance_criteria"))
        for x in sorted(cited_br - br_def):
            violations.append((label, "PHANTOM_BR", f"flow cites {x} — not in Schema 1 business_rules"))

        # actors
        declared = set(actors.keys())
        bad_actor = set()
        for fl in flows:
            for st in fl.get("steps", []) or []:
                act = st.get("actor")
                if not act:
                    continue
                base = act.split("-")[0]
                if act not in declared and base not in declared:
                    bad_actor.add(act)
                elif base not in CANON_ACTORS and act not in CANON_ACTORS:
                    advisories.append((label, "ACTOR_VOCAB", f"actor {act!r} outside canonical vocab"))
        for act in sorted(bad_actor):
            violations.append((label, "UNDECLARED_ACTOR", f"step actor {act!r} not in actors{{}}"))

        # entry_from resolution (advisory — may point cross-unit)
        for fl in flows:
            ef = fl.get("entry_from")
            if ef and ef not in all_flow_ids:
                advisories.append((label, "UNKNOWN_ENTRY", f"{fl.get('flow_id')} entry_from={ef} not a known flow_id"))

        cov = len(ac_def)
        print(f"  {label}: {cov}/{cov} ACs covered · {len(flows)} flows · "
              f"{len(cited_br)} BRs cited · {len(declared)} actors")

    # de-dup advisories (ACTOR_VOCAB can repeat per step)
    advisories = list(dict.fromkeys(advisories))

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
    print(f"✅ PASS — {len(s1)} units fully traceable Schema 1 → Schema 2 "
          f"(coverage complete, no phantom ac/br, all actors declared)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
