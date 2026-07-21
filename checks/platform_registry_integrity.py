#!/usr/bin/env python3
"""
Platform Behavior Registry integrity gate — cross-epic (not epic-scoped)

Validates qa/_shared/platform-behavior-registry.json stays well-formed as it
grows across epics. This is a STRUCTURAL check, not a coverage gate — there is
no fixed universe of "all platform behaviors" to cover; the point is to catch
rot (dup ids, phantom epic refs, entries that don't actually diverge) as the
registry accumulates entries from many epics over time.

Hard rules (exit 1):
  STRUCT        _schema != platform-behavior-registry-v1 / entries not a list /
                an entry missing id / feature_area / summary / platforms /
                divergence_type / evidence / first_confirmed
  DUP_ID        duplicate entry id
  ID_FORMAT     id not PB-NNN
  PLATFORM_ENUM a platforms{} key not in {ios, android, web-desktop, mobile-web}
  NOT_DIVERGENT platforms{} has < 2 keys, or all values are identical text
                (that's uniform behaviour, not a divergence — doesn't belong here)
  DIVERGENCE_ENUM divergence_type not in {interaction-steps, not-supported, timing,
                control-visibility, other}
  STATUS_ENUM   status not in {confirmed, needs-reverification}
  PHANTOM_EPIC  first_confirmed.epic or an also_seen_in[] entry has no folder
                under qa/<epic>/ (dangling reference)

Advisory (exit 0):
  STALE_CANDIDATE status=needs-reverification (flagged for re-check, not a failure)

Invocation: python3 checks/platform_registry_integrity.py
Stdlib only, deterministic, no network.
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REGISTRY = REPO / "qa" / "_shared" / "platform-behavior-registry.json"
PLATFORM_ENUM = {"ios", "android", "web-desktop", "mobile-web"}
DIVERGENCE_ENUM = {"interaction-steps", "not-supported", "timing", "control-visibility", "other"}
STATUS_ENUM = {"confirmed", "needs-reverification"}
ID_RE = re.compile(r"^PB-\d{3}$")


def known_epics():
    qa_dir = REPO / "qa"
    if not qa_dir.is_dir():
        return set()
    return {p.name for p in qa_dir.iterdir() if p.is_dir() and not p.name.startswith("_")}


def main() -> int:
    print("Platform Behavior Registry integrity gate")
    if not REGISTRY.is_file():
        print(f"\n❌ FAIL — {REGISTRY.relative_to(REPO)} not found")
        return 1
    try:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"\n❌ FAIL — cannot parse: {e}")
        return 1

    violations, advisories = [], []
    if data.get("_schema") != "platform-behavior-registry-v1":
        violations.append(("STRUCT", f"_schema={data.get('_schema')!r} (expected platform-behavior-registry-v1)"))
    entries = data.get("entries")
    if not isinstance(entries, list):
        print("\n❌ FAIL — entries[] missing or not a list")
        return 1

    epics = known_epics()
    ids = []
    for e in entries:
        eid = e.get("id")
        if not eid:
            violations.append(("STRUCT", f"an entry has no id (feature_area={e.get('feature_area')!r})"))
            continue
        ids.append(eid)
        if not ID_RE.match(eid):
            violations.append(("ID_FORMAT", f"{eid} does not match PB-NNN"))

        for field in ("feature_area", "summary", "divergence_type", "evidence"):
            if not (isinstance(e.get(field), str) and e[field].strip()):
                violations.append(("STRUCT", f"{eid} missing/empty {field!r}"))

        platforms = e.get("platforms")
        if not isinstance(platforms, dict) or not platforms:
            violations.append(("STRUCT", f"{eid} missing platforms{{}}"))
            platforms = {}
        for k in platforms:
            if k not in PLATFORM_ENUM:
                violations.append(("PLATFORM_ENUM", f"{eid} platform key {k!r} not in {sorted(PLATFORM_ENUM)}"))
        vals = [v.strip() for v in platforms.values() if isinstance(v, str)]
        if len(platforms) < 2 or (vals and len(set(vals)) < 2):
            violations.append(("NOT_DIVERGENT", f"{eid} platforms{{}} has < 2 genuinely different behaviours — not a divergence"))

        if e.get("divergence_type") not in DIVERGENCE_ENUM:
            violations.append(("DIVERGENCE_ENUM", f"{eid} divergence_type={e.get('divergence_type')!r} not in {sorted(DIVERGENCE_ENUM)}"))
        status = e.get("status")
        if status not in STATUS_ENUM:
            violations.append(("STATUS_ENUM", f"{eid} status={status!r} not in {sorted(STATUS_ENUM)}"))
        elif status == "needs-reverification":
            advisories.append(("STALE_CANDIDATE", f"{eid} flagged needs-reverification — re-check before relying on it"))

        fc = e.get("first_confirmed", {})
        fc_epic = fc.get("epic") if isinstance(fc, dict) else None
        if not fc_epic:
            violations.append(("STRUCT", f"{eid} missing first_confirmed.epic"))
        elif epics and fc_epic not in epics:
            violations.append(("PHANTOM_EPIC", f"{eid} first_confirmed.epic={fc_epic!r} has no qa/{fc_epic}/ folder"))
        for also in e.get("also_seen_in", []) or []:
            if epics and also not in epics:
                violations.append(("PHANTOM_EPIC", f"{eid} also_seen_in includes {also!r} — no qa/{also}/ folder"))

    dup = sorted({x for x in ids if ids.count(x) > 1})
    if dup:
        violations.append(("DUP_ID", f"duplicate id(s): {', '.join(dup)}"))

    print(f"  entries: {len(entries)}")
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
    print(f"✅ PASS — {len(entries)} platform-behavior entries, well-formed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
