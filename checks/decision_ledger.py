#!/usr/bin/env python3
"""
Decision-ledger gate — Layer 2 (QA Story Authoring)  [R2]

Validates qa/<epic>/decisions.json — the record of every JUDGMENT call in L2
(split / priority / scope / pending-resolution / spec-correction / policy) — and
reports which decisions are still OPEN (awaiting a human).

This is the HALT-and-flag surface for AUTONOMOUS runs: a mechanical run can
assemble schema + traceability itself (G1/G2), but must never silently pick a
side on a judgment call. In autonomous mode any open human decision is a hard
stop.

Invocation:
    python3 checks/decision_ledger.py qa/PDT-3418               # manual: open items are advisory
    python3 checks/decision_ledger.py qa/PDT-3418 --autonomous  # open human decisions → exit 1 (HALT)

Hard rules — always exit 1:
    STRUCT      missing decisions[] / a decision missing id|type|decision|decided_by|status
    DUP_ID      duplicate decision id
    BAD_TYPE    type not in type_vocab
    BAD_STATUS  status not in status_vocab
    NO_SOURCE   a pending-resolution with no source_ref (an unsourced "answer" = a guess)

Autonomous-only (exit 1 with --autonomous; advisory otherwise):
    OPEN_HUMAN  a {split, priority, scope, policy} decision still {proposed, pending-human}

Manual mode reports OPEN decisions as advisories and exits 0 (open items are
expected while sign-off is pending). Stdlib only, deterministic, no network.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

TYPES = {"split", "priority", "scope", "pending-resolution", "spec-correction", "policy"}
STATUSES = {"confirmed", "resolved-by-code", "proposed", "pending-human"}
OPEN_STATUSES = {"proposed", "pending-human"}
HUMAN_TYPES = {"split", "priority", "scope", "policy"}
REQUIRED = ("id", "type", "decision", "decided_by", "status")


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    autonomous = "--autonomous" in sys.argv or "--strict" in sys.argv
    if not args:
        print("usage: python3 checks/decision_ledger.py qa/<epic> [--autonomous]")
        return 2

    epic = Path(args[0].rstrip("/")).name
    ledger = REPO / "qa" / epic / "decisions.json"

    mode = "AUTONOMOUS (open human decision = HALT)" if autonomous else "manual (open = advisory)"
    print(f"Decision-ledger gate — epic {epic}  ·  mode: {mode}")

    if not ledger.exists():
        msg = f"no decision ledger: qa/{epic}/decisions.json"
        if autonomous:
            print(f"\n❌ HALT — {msg} (autonomous L2 requires a ledger)")
            return 1
        print(f"\n· [NO_LEDGER] {msg} (advisory — create one before an autonomous run)")
        return 0

    try:
        data = json.loads(ledger.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"\n❌ FAIL — cannot parse {ledger.relative_to(REPO)}: {e}")
        return 1

    decisions = data.get("decisions")
    if not isinstance(decisions, list):
        print("\n❌ FAIL — [STRUCT] decisions[] missing or not a list")
        return 1

    violations, advisories, open_human = [], [], []
    seen_ids, settled = [], 0

    for i, d in enumerate(decisions):
        did = d.get("id") or f"<#{i}>"
        for f in REQUIRED:
            if not d.get(f):
                violations.append((did, "STRUCT", f"missing '{f}'"))
        seen_ids.append(d.get("id"))
        typ, status = d.get("type"), d.get("status")
        if typ not in TYPES:
            violations.append((did, "BAD_TYPE", f"type={typ!r} not in {sorted(TYPES)}"))
        if status not in STATUSES:
            violations.append((did, "BAD_STATUS", f"status={status!r} not in {sorted(STATUSES)}"))
        if typ == "pending-resolution" and not d.get("source_ref"):
            violations.append((did, "NO_SOURCE", "pending-resolution with no source_ref (an unsourced answer is a guess)"))

        is_open = status in OPEN_STATUSES
        if is_open and typ in HUMAN_TYPES:
            open_human.append((did, typ, status, d.get("decision", "")[:70]))
        elif is_open:
            advisories.append((did, "OPEN", f"{typ}/{status} — {d.get('decision','')[:60]}"))
        elif status in ("confirmed", "resolved-by-code"):
            settled += 1

    dup = sorted({x for x in seen_ids if x and seen_ids.count(x) > 1})
    if dup:
        violations.append(("*", "DUP_ID", f"duplicate id(s): {', '.join(dup)}"))

    total = len(decisions)
    print(f"  {total} decisions · settled {settled} · open-human {len(open_human)} · other-open {len(advisories)}\n")

    if open_human:
        head = "❌ open human decisions (HALT):" if autonomous else "· open human decisions (need sign-off):"
        print(head)
        for did, typ, status, txt in open_human:
            print(f"    [{typ}/{status}] {did}: {txt}")
        print()
    if advisories:
        print("advisories:")
        for did, r, msg in advisories:
            print(f"  · [{r}] {did}: {msg}")
        print()

    if violations:
        print(f"❌ FAIL — {len(violations)} structural violation(s):")
        for did, r, msg in violations:
            print(f"  ✗ [{r}] {did}: {msg}")
        return 1
    if autonomous and open_human:
        print(f"❌ HALT — {len(open_human)} judgment call(s) need a human before an autonomous L2 may proceed")
        return 1
    print(f"✅ PASS — ledger well-formed"
          + (f"; {len(open_human) + len(advisories)} open item(s) flagged (manual mode)" if (open_human or advisories) else "; all decisions settled"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
