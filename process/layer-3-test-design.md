# Layer 3 — Test Design (Process)

> **สถานะ:** gate `br_tc_coverage` ใช้งานจริงแล้ว (proven บน PDT-3418 — 105 TCs, BR+AC coverage 100%) · เหลือ strip orchestration ออกจาก phase-3-* skills (S1 รอบถัดไป)

**เป้าหมาย:** เปลี่ยน story/BR ที่ final เป็น test conditions/cases + คำตัดสิน automate vs manual
**Input:** Schema 1 (canonical) — หรือ multi-source (PRD+Jira+Figma) ถ้า AC ยังไม่ครบ
**Output:** test conditions + (optional) test cases + automation judgment table
**Skills:** `phase-3-1` (automation judgment), `phase-3-2` (BR → test conditions)

---

## STEP 0 · Input select
- **มี Schema 1** (จาก L2) → path ปกติ (BR + AC พร้อม)
- **AC ยังไม่ครบ** → path `phase-3-2` multi-source (รับ PRD/Jira/Figma อย่างน้อย 1 แหล่ง) — เป็นทางลัดข้าม L2

## STEP 1 · Test conditions
**calls:** `phase-3-2` — normalize source → extract BR (4 types) → แปลงเป็น Test Conditions ด้วย technique ตาม BR type:
- constraint → **BVA / EP**, permission → **Decision Table**, state → **State Transition** (**reuses State Machine concept จาก 1-1**), computation → **BVA + EP**
→ produces: Test Conditions table (TC-ID → BR-ID → condition → technique → priority) + `[CONFLICT]`/`[AI-INFERRED]` list

> ⚠️ **reconcile กับ L2:** `phase-3-2` มี BR extraction ของตัวเอง (self-contained) ซ้ำกับ `phase-2-3`.
> ถ้ามาจาก Schema 1 (มี br_id แล้ว) → ใช้ BR จาก L2, ให้ 3-2 ทำแค่ BR→Test Condition
> ถ้าเป็น path ทางลัด → 3-2 extract BR เอง

## STEP 2 · (optional) User Flow
ถ้ายังไม่มี Schema 2 → build user-flow (`02-user-flow.json`) เพื่อ trace test → flow → ac_id

## STEP 3 · Automation judgment
**calls:** `phase-3-1` — 6 criteria (blocker ก่อน) → verdict **automate / manual / QA-decides** + suggested tool
→ produces: Judgment Table + "QA Must Confirm" section

⛒ **Gates:** BR → Test-Condition coverage (ทุก BR มี ≥1 test condition) · Completion
**note:** ทับซ้อนกับ `00-schema-process-guide.md` PHASE 6 (generate test cases) → รอบ final ต้อง unify ถ้อยคำ

---

## ID traceability (ทั้ง 3 layer)
```
epic_id → story_id → uc_id → br_id / ac_id → flow_id → TC-ID
                                    ↑ L1/L2            ↑ L3
test case → flow_id → ac_id → story_id → uc_id   (ตรวจย้อนกลับได้)
```
