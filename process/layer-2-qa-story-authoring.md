# Layer 2 — QA Story Authoring (Process) · 🚧 DRAFT

> **DRAFT เพื่อเทียบภาพรวม** — ยังไม่ strip orchestration ออกจาก phase-2-* skills (จะทำรอบถัดไปเมื่อ process นี้ final)

**เป้าหมาย:** เปลี่ยน requirement ที่เข้าใจ+enrich แล้ว (จาก L1) เป็น story artifact ที่ final สำหรับ sprint
**Input:** output ของ Layer 1 (enriched AC + Clarification Register clean)
**Output:** Schema 1 (`output/PDT-XXXX-complete-jira-story.json`) → Schema 2 (`output/PDT-XXXX-user-flow.json`)
**Skills:** `phase-2-1` … `phase-2-6`
**ต่างจาก L1:** L1 = interrogate draft ของคนอื่น (ห้ามเขียนทับ) · L2 = author artifact final (re-decompose ได้)

---

## STEP 0 · Readiness gate
⛒ ต้องมี: enriched AC (L1), Clarification Register ไม่เหลือ still-ambiguous medium+, preconditions ครบ, user story รูป As a/I want/So that
(= Readiness Gate เดิมของ Workflow B — ถ้าไม่ครบ หยุด)
- **write boundary (R1):** L2 เขียนแค่ `qa/` + `output/` · `products/<epic>/stories/*.json` = READ-ONLY (แก้ได้เฉพาะ L1 sync) — กันเขียนทับ PM AC
- **decision ledger (R2):** เปิด/ต่อ `qa/<epic>/decisions.json` — judgment ใน STEP 1/4/5 append ที่นี่ (type + decided_by + status + source_ref)

## STEP 1 · Story shape
**calls:** `phase-2-1` (INVEST — split by **mechanism** ไม่ใช่ role; role นอก scope → เป็น AC)
(+ `phase-2-4` elicitation ถ้าเจอ gap ใหม่ที่ต้องถาม stakeholder)
→ produces: user story + invest_check · **ถ้า split → log `decisions.json`** (type=split, decided_by, status)

## STEP 2 · AC authoring
**calls:** `phase-2-2` (4 scenario types: default / happy / alternative / error)
**reuses:** State Machine (1-1) เพื่อ verify Then ครอบทุก state change · complement กับ enriched AC จาก L1 (1-3/1-4)
→ produces: AC set ครบ 4 type (PM + QA source)

## STEP 3 · Business Rules
**calls:** `phase-2-3` (**reuses Pain&Consequence "Why" จาก 1-1** เป็น extraction engine)
→ produces: BR catalog (4 types: permission/constraint/computation/state) + `br_id` + consolidate ข้าม UC (`also_used_in`)
> canonical BR path (มี AC แล้ว). ถ้า AC ยังไม่ครบ → ใช้ `phase-3-2` แทน (L3 entry)

## STEP 4 · Scope gate
**calls:** `phase-2-6` (**reuses Relationship Map จาก 1-1 + User Need จาก 1-2**)
→ produces: Scope Boundary doc (In/Out/Assumption/Constraint/Open-Gap + owner) + User-Need→AC coverage map
→ feeds `open_questions[]` / `clarifications_needed[]` เข้า Schema 1
→ **log scope in/out → `decisions.json`** (type=scope, owner, status)

## STEP 5 · Prioritize
**calls:** `phase-2-5` (MoSCoW → Impact/Effort → QA Effort Score 7 criteria)
**reuses:** BR reuse info จาก 2-3 (regression risk)
→ **log MoSCoW → `decisions.json`** (type=priority, status=pending-human จนกว่า PM confirm)

## STEP 6 · Emit Schema 1 → Schema 2
- ประกอบ **Schema 1** ตาม `01-complete-jira-story.json` (ทุก field: story_id/uc_id/br_id/ac_id)
- ถ้า AC ไม่มี PENDING → build **Schema 2** user-flow (`02-user-flow.json`) ตาม flow
- **⛒ machine gates (บังคับ — ต้อง exit 0 ทั้งคู่ ก่อน commit / exit ไป L3):**
  - `python3 checks/schema1_integrity.py qa/<epic>` — [G1] br_ids ทุกตัวมี def (no **DANGLING_BR**) · ไม่มี BR ตายซาก (no **DEAD_BR**) · ไม่มี ac_id/br_id ซ้ำ
  - `python3 checks/schema_trace.py qa/<epic>` — [G2] ทุก ac_id ถูก flow ครอบ (**AC_COVERAGE**) · ไม่มี ac/br ผี (**PHANTOM**) · step actor ประกาศครบ (Schema 1↔2)
  - `python3 checks/decision_ledger.py qa/<epic> [--autonomous]` — [R2] judgment ทุกตัว log + settled · autonomous: open human decision = HALT
  - exit 1 = หยุด แก้ก่อน ห้าม commit. G1/G2 codify script ที่จับ error จริงตอนรัน PDT-3418 (dangling BR, orphan BR, phantom ref); R2 กัน silent judgment ตอน autonomous

⛒ **Gates:** Readiness (STEP0) · AC Manifest (list ac_id + type + source PM/QA, `Total N (PM:X, QA:Y)`) · Completion (ทุก ac_id มี type/source/br_ids/given/then) · **Schema-1 Integrity [G1]** · **Schema-1↔2 Traceability [G2]** · Dropout

**artifacts consumed จาก L1:** Enriched AC · State Machine · Relationship Map · User Need · Clarification Register
**Exit → Layer 3** เมื่อ Schema 1 สมบูรณ์ (ทุก ac_id/br_id assigned, ไม่มี PENDING)
