# Layer 1 — BA Requirement Analysis (Process)

**เป้าหมาย:** เข้าใจ + enrich requirement (draft ของ PM) ให้ครบ ก่อน commit เข้า sprint
**Input:** story key (Jira) + PRD (`products/<epic>/prd/`) + Figma (`products/<epic>/design/`)
**Output:** enriched AC + Clarification Register + readiness verdict ที่ `qa/<epic>/`
**Skills ที่เรียก:** `phase-1-1`, `phase-1-2`, `phase-1-3`, `phase-1-4` (+ `qa-story-diff` ที่ STEP0)
**Source of truth:** PM's AC — ห้ามเขียนทับ, QA ต่อยอดเป็น enriched version แยก

> Gate นิยามกลางที่ `process/README.md` (Gate catalog). Skill เป็น pure function — ดู "Artifacts" header ในแต่ละ SKILL.md

---

## STEP 0 · Ingest & Manifest

**calls:** Atlassian MCP `getJiraIssue` (+ `qa-story-diff` ถ้าเคย analyze แล้ว)

1. ดึง story ล่าสุด (description + comments) + อ่าน PRD + Figma screens
2. Sync `products/<epic>/stories/*.json` ให้ตรง Jira (AC, preconditions, platforms)
3. สร้าง **AC Manifest** จาก `products/<epic>/stories/*.json` — list `ac_id` ทุกตัว + count ต่อ story
   → นับจาก **structured JSON เท่านั้น** (ไม่ eyeball Jira free-text)

⛒ **Readiness gate:** PRD + Figma + AC ครบไหม (ถ้าขาด → แจ้งและหยุด)
⛒ **Freshness gate:** diff Manifest vs snapshot `qa/<epic>/.ac-manifest.json` → `added / removed / changed / unchanged`
   changed/added ต้อง re-analyze; removed ต้อง prune

**artifacts produced:** AC Manifest (+ snapshot)

---

## STEP 1 · Understand

**calls:** `phase-1-1` (Relationship Map · State Machine · Pain&Consequence) + `phase-1-2` (3-Layer)

1. `phase-1-1` → วาด **Relationship Map** (Who + concurrent/silent actors), **State Machine** (What + invalid/external transitions), **Pain&Consequence** (Why)
2. `phase-1-2` → trace **Business Goal ← User Need ← System Behavior**; หา gap 5 ประเภท
3. gap/ความคลุมเครือทุกจุด → **append เข้า Clarification Register** (observation → consequence → question + ask→who)

**artifacts produced:** Relationship Map, State Machine, 3-Layer trace, (append) Clarification Register
**artifacts consumed:** AC Manifest

---

## STEP 2 · Specify (loop ต่อ ac_id ใน Manifest)

**calls:** `phase-1-3` (happy-path enrich) → `phase-1-4` (edge/error)
**reads (ไม่ทำซ้ำ):** State Machine + Relationship Map จาก STEP1

สำหรับแต่ละ `ac_id` (แสดง progress `[X/N]`):
1. `phase-1-3` → interpret Given/When/Then, ดึง Given จาก preconditions, เช็ค Then ครบ state change (ใช้ State Machine), เช็ค silent actor (ใช้ Relationship Map) → **Enriched AC** (bound to ac_id) + `[PENDING]` markers
2. `phase-1-4` → run 4 mental models (Boundary/Timing/Environment/Data) → edge cases + priority + state-after; error cases (trigger → user sees → state-after) → **Edge/Error AC**
3. clarification ที่เจอ → append เข้า Register

⛒ **Coverage + Content gate:** ทุก `ac_id` ถูก enrich **และ** fingerprint(given+when+then) ตรง snapshot (ไม่ STALE)

**artifacts produced:** Enriched AC (`qa/<epic>/<story>-analysis.md`), (append) Clarification Register

---

## STEP 3 · Consolidate & Route

1. รวม Clarification Register: group by **category** (Conflict / Unclear / Ambiguous) + tag **ask→(PM/Design/Eng)** + priority + source
2. เขียน readiness verdict ต่อ story (ready / partial / not-ready + blocking items)
3. filter view ตาม audience ได้ (เช่น "คำถาม PM ทั้งหมด")

⛒ **Completion gate:** ✓/✗ ทุก `ac_id` เทียบ Manifest = **N/N** (มี ✗ → กลับไป STEP2)
⛒ **Dropout rule:** ห้าม AC หลุดเงียบตลอดทาง

**artifacts produced:** Clarification Register (final, `qa/<epic>/PDT-XXXX-clarifications-for-pm-design.md`), readiness verdict

---

## Exit → handoff to Layer 2

เข้า **Layer 2 (QA Story Authoring)** ได้เมื่อ Clarification Register **ไม่เหลือ still-ambiguous ระดับ medium+**
(gate นี้ = `qa-clarifications-review` ตรวจว่า answered clarifications เคลียร์พอ)

---

## Gate enforcement (automated)
```
python3 checks/ac_coverage.py qa/<epic>        # เช็ค Coverage + Content + Completion + Freshness
python3 checks/ac_coverage.py qa/<epic> --update   # refresh snapshot หลัง sync AC ใหม่
```

## ตัวอย่างจริง (PDT-3418)
- STEP0: sync 3 story, Manifest = UC1 6 / UC2 3 / UC3 6 = 15 ac_id
- STEP1–2: `qa/PDT-3418/PDT-356{2,3,4}-*-analysis.md` (1.1→1.4 + Completion N/N)
- STEP3: `qa/PDT-3418/PDT-3418-clarifications-for-pm-design.md` (+ `-en.md`) — 22 → 7 resolved, 17 open, group by category + ask
- Freshness จับได้: UC2 AC-01/02 ถูกเขียนใหม่ 2026-07-06 (count 3→3 เท่าเดิม แต่ content เปลี่ยน) → re-analyze
