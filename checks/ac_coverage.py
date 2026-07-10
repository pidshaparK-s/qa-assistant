#!/usr/bin/env python3
"""
AC-coverage gate — Layer 1 (BA Requirement Analysis)

Verifies that the per-story analysis under qa/<epic>/ actually covers every
acceptance criterion in the stored story JSON, and that it is not STALE relative
to the AC content (catches reworded ACs that keep the same count — e.g. PDT-3563
UC2 AC-01/02 rewritten 2026-07-06 while count stayed 3).

Anchors on ac_id + a content fingerprint (sha1 of given+when+then) — NOT on count.

Invocation:
    python3 checks/ac_coverage.py qa/PDT-3418          # verify
    python3 checks/ac_coverage.py qa/PDT-3418 --update # bless current AC state (write snapshot)
    python3 checks/ac_coverage.py PDT-3418             # epic key also accepted

Rules (hard → exit 1):
  - COVERAGE : every ac_id in the story JSON appears in its analysis .md
  - COMPLETION: the "ครอบคลุม: N/N" line, if present, equals the ac_id count
  - STALE    : an ac_id's fingerprint differs from the blessed snapshot
               (AC changed since last verification → re-analyze then --update)
  - NO-ANALYSIS: a story JSON has no matching analysis .md in qa/<epic>/

Advisory (reported, exit 0): missing completion line; added/removed ac_id vs snapshot.
Stdlib only, deterministic, no network. First run with no snapshot auto-establishes a baseline.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SNAPSHOT_NAME = ".ac-manifest.json"
COMPLETION_RE = re.compile(r"ครอบคลุม[:\s]*?(\d+)\s*/\s*(\d+)")


def fingerprint(ac: dict) -> str:
    payload = json.dumps(
        {"given": ac.get("given", []), "when": ac.get("when", ""), "then": ac.get("then", [])},
        ensure_ascii=False, sort_keys=True,
    )
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:12]


def build_manifest(stories_dir: Path):
    """{story_key: {"file": rel, "acs": {ac_id: fp}}}"""
    manifest = {}
    for jf in sorted(stories_dir.glob("*.json")):
        if jf.name.startswith("."):
            continue
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except Exception as e:
            manifest[f"<unparseable:{jf.name}>"] = {"file": str(jf.relative_to(REPO)), "acs": {}, "error": str(e)}
            continue
        key = data.get("key") or jf.stem
        acs = {}
        for ac in data.get("acceptance_criteria", []):
            ac_id = ac.get("ac_id")
            if ac_id:
                acs[ac_id] = fingerprint(ac)
        manifest[key] = {"file": str(jf.relative_to(REPO)), "acs": acs}
    return manifest


def find_analysis(qa_dir: Path, story_key: str):
    # rglob: analysis .md may live in a per-UC subfolder (qa/<epic>/uc*/)
    hits = sorted(qa_dir.rglob(f"{story_key}*.md"))
    # prefer a file explicitly named *analysis* over sibling .md (test-design, etc.)
    analysis = [p for p in hits if "analysis" in p.name]
    return (analysis or hits or [None])[0]


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    update = "--update" in sys.argv
    if not args:
        print("usage: python3 checks/ac_coverage.py qa/<epic> [--update]")
        return 2

    epic = Path(args[0].rstrip("/")).name
    qa_dir = REPO / "qa" / epic
    stories_dir = REPO / "products" / epic / "stories"

    if not stories_dir.is_dir():
        print(f"❌ stories dir not found: {stories_dir.relative_to(REPO)}")
        return 2
    if not qa_dir.is_dir():
        print(f"❌ qa dir not found: {qa_dir.relative_to(REPO)}")
        return 2

    manifest = build_manifest(stories_dir)
    snap_path = qa_dir / SNAPSHOT_NAME

    # --update: bless current AC state
    if update:
        snap = {k: v["acs"] for k, v in manifest.items() if "error" not in v}
        snap_path.write_text(json.dumps(snap, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        total = sum(len(a) for a in snap.values())
        print(f"✅ snapshot updated: {snap_path.relative_to(REPO)} — {len(snap)} stories, {total} ACs blessed")
        return 0

    baseline = {}
    baseline_exists = snap_path.exists()
    if baseline_exists:
        try:
            baseline = json.loads(snap_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"⚠️  snapshot unreadable ({e}) — treating as no baseline")
            baseline_exists = False

    violations = []   # (story, rule, message)
    advisories = []
    total_acs = 0

    print(f"AC-coverage gate — epic {epic}")
    print(f"  stories: {stories_dir.relative_to(REPO)}  |  analysis: {qa_dir.relative_to(REPO)}")
    print(f"  baseline: {'yes' if baseline_exists else 'NONE (will auto-establish)'}\n")

    for story_key, info in manifest.items():
        if "error" in info:
            violations.append((story_key, "PARSE", f"cannot parse {info['file']}: {info['error']}"))
            continue
        acs = info["acs"]
        total_acs += len(acs)
        md = find_analysis(qa_dir, story_key)
        if md is None:
            violations.append((story_key, "NO-ANALYSIS", f"no analysis .md in qa/{epic}/ for story {story_key}"))
            continue
        text = md.read_text(encoding="utf-8")
        rel_md = md.relative_to(REPO)

        # COVERAGE
        missing = [ac_id for ac_id in acs if ac_id not in text]
        if missing:
            violations.append((story_key, "COVERAGE", f"{rel_md} missing ac_id(s): {', '.join(missing)}"))

        # COMPLETION line
        m = COMPLETION_RE.search(text)
        if m:
            got, tot = int(m.group(1)), int(m.group(2))
            if tot != len(acs) or got != len(acs):
                violations.append((story_key, "COMPLETION",
                                   f"{rel_md} completion line {got}/{tot} != ac count {len(acs)}/{len(acs)}"))
        else:
            advisories.append((story_key, "COMPLETION", f"{rel_md} has no 'ครอบคลุม: N/N' completion line"))

        # STALE / freshness vs baseline
        if baseline_exists:
            base = baseline.get(story_key, {})
            added = [a for a in acs if a not in base]
            removed = [a for a in base if a not in acs]
            changed = [a for a in acs if a in base and acs[a] != base[a]]
            unchanged = [a for a in acs if a in base and acs[a] == base[a]]
            for a in changed:
                violations.append((story_key, "STALE",
                                   f"{a} content changed since snapshot — re-analyze then --update"))
            if added:
                advisories.append((story_key, "ADDED", f"new ac_id(s) since snapshot: {', '.join(added)}"))
            if removed:
                advisories.append((story_key, "REMOVED", f"ac_id(s) gone from JSON (prune analysis?): {', '.join(removed)}"))
            print(f"  {story_key}: {len(acs)} ACs | unchanged {len(unchanged)} · changed {len(changed)} · added {len(added)} · removed {len(removed)}")
        else:
            print(f"  {story_key}: {len(acs)} ACs | (baseline established)")

    # auto-establish baseline on first run
    if not baseline_exists:
        snap = {k: v["acs"] for k, v in manifest.items() if "error" not in v}
        snap_path.write_text(json.dumps(snap, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        advisories.append(("*", "BASELINE", f"established {snap_path.relative_to(REPO)} ({total_acs} ACs)"))

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
    print(f"✅ PASS — {len(manifest)} stories, {total_acs} ACs covered, no STALE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
