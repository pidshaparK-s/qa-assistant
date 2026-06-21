---
name: run-analysis
description: >
  Orchestrator สำหรับ Workflow A, B, C ทั้งหมดรันใน Claude Code session
  แต่ละ workflow มี Readiness Gate, AC Manifest, progress counter, และ Completion Gate
  Trigger: "วิเคราะห์ PDT-XXXX" / "สร้าง story JSON PDT-XXXX" / "สร้าง flow JSON PDT-XXXX"
---

# run-analysis — Workflow Orchestrator (A / B / C)

---

## ═══════════════════════════════════════════
## WORKFLOW A — AC Analysis
## Trigger: "วิเคราะห์ PDT-XXXX" / "analyze PDT-XXXX"
## Output: output/PDT-XXXX-enriched-ac.md
## ═══════════════════════════════════════════

### STEP 0 — Fetch story

ใช้ Atlassian MCP (`getJiraIssue`) ดึง issue key ที่ได้รับ
แสดงก่อนดำเนินการต่อ:
```
✅ Fetched: PDT-XXXX — [summary]
   Status: [status]
```

---

### STEP 1 — AC Manifest [GATE 1]

**ทำก่อนวิเคราะห์เสมอ — ห้ามข้าม**

อ่าน description แล้ว list ทุก AC:
```
📋 AC Manifest — PDT-XXXX
─────────────────────────
AC-1: [scenario name]
AC-2: [scenario name]
...
─────────────────────────
Total: N ACs

⚠️ จะวิเคราะห์ทั้ง N ข้อ — ไม่มีข้อใดถูกข้าม
```

ถ้าไม่พบ AC ใด → หยุดและแจ้ง:
```
❌ ไม่พบ AC ใน story นี้ กรุณาตรวจสอบ description
```

---

### STEP 2 — อ่าน skills

อ่าน `skills/phase-1.3-happy-path-ac-enrichment.md` และ `skills/phase-1.4-edge-and-error-ac.md`
ก่อนเริ่ม loop เสมอ

---

### STEP 3 — วิเคราะห์ทีละ AC

วนลูปทุก AC จาก Manifest ตามลำดับ แสดง progress ก่อนเริ่มทุกข้อ:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 [X/N] กำลังวิเคราะห์: AC-X — [scenario]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

สำหรับแต่ละ AC ทำ 3 phases ตามลำดับ:

**Phase 1.3 — Happy Path Enrichment** (อิงจาก `phase-1.3-happy-path-ac-enrichment.md`)
1. ดึง Given จาก Preconditions ของ story
2. วาด state machine — ตรวจว่า Then ครอบคลุมทุก state change
3. ตรวจ silent actors
→ Output: enriched AC (Given/When/Then สมบูรณ์) + clarification questions (observation → consequence → question)

**Phase 1.4a — Edge Case Detection** (อิงจาก `phase-1.4-edge-and-error-ac.md`)
รัน 4 mental models: Boundary → Timing → Environment → Data Integrity
→ Output: edge cases พร้อม priority (high/medium/low) + state หลัง action ทุกข้อ

**Phase 1.4b — Error Case Detection** (อิงจาก `phase-1.4-edge-and-error-ac.md`)
ตอบ 3 คำถามต่อ error: trigger → user เห็นอะไร → state หลัง error
→ Output: error cases พร้อม priority + state หลัง error ทุกข้อ

---

### STEP 4 — Completion Gate [GATE 2]

**ห้ามข้ามไม่ว่ากรณีใด**

```
✅ Completion Check — PDT-XXXX
──────────────────────────────
AC-1: [scenario] ✓
AC-2: [scenario] ✓
...
──────────────────────────────
ครอบคลุม: N/N ACs
```

ถ้ามี AC ที่ไม่ได้วิเคราะห์:
```
❌ AC ที่หลุด:
- AC-X: [scenario] ✗

กำลังวิเคราะห์ส่วนที่ขาดหายก่อน...
[วิเคราะห์ทันที]
[re-check gate]
```

---

### STEP 5 — เขียน output

เขียน `output/PDT-XXXX-enriched-ac.md` ตาม format ใน CLAUDE.md
แจ้งเมื่อเสร็จ:
```
📄 เขียนแล้ว: output/PDT-XXXX-enriched-ac.md
```

---

## ═══════════════════════════════════════════
## WORKFLOW B — Complete Jira Story JSON
## Trigger: "สร้าง story JSON PDT-XXXX" / "generate story PDT-XXXX"
## Output: output/PDT-XXXX-complete-jira-story.json
## ═══════════════════════════════════════════

### READINESS GATE [GATE 0]

ก่อนเริ่ม ตรวจ inputs ครบหรือยัง ถ้าขาดข้อใด → แจ้งและหยุด ห้ามดำเนินการต่อ:

```
🔎 Readiness Check — PDT-XXXX
──────────────────────────────────────────────
[ ] User Story ในรูปแบบ As a/I want/So that
[ ] Preconditions ของ story ครบ
[ ] PM's happy path AC ทุกข้อ confirmed (ไม่มี ambiguity)
[ ] คำตอบ clarification ทุกข้อที่ถามไป (ไม่มี PENDING)
[ ] BR list พร้อม br_id extract แล้ว
──────────────────────────────────────────────
```

ถ้ามีข้อที่ [ ] ยังไม่ครบ:
```
❌ ยังไม่พร้อมสร้าง Schema 1 เพราะ:
- [สิ่งที่ขาด]
→ แก้ไขก่อนแล้วรัน Workflow B ใหม่
```

---

### STEP 0 — Fetch story

ดึง story ล่าสุดผ่าน `getJiraIssue`

---

### STEP 1 — อ่าน skills

อ่าน `phase-2.1-user-story-invest.md`, `phase-2.2-acceptance-criteria.md`, `phase-2.3-business-rule-extraction.md`

---

### STEP 2 — INVEST check

รัน INVEST check ตาม `phase-2.1-user-story-invest.md`:

```
INVEST Check — User Story
─────────────────────────
I — Independent:  ✓/✗
N — Negotiable:   ✓/✗
V — Valuable:     ✓/✗
E — Estimable:    ✓/✗
S — Small:        ✓/✗
T — Testable:     ✓/✗
```

ถ้า fail ข้อใด → แจ้งปัญหาและคำแนะนำก่อนดำเนินการต่อ

---

### STEP 3 — BR consolidation

รัน `phase-2.3-business-rule-extraction.md`:
- Extract BR จาก AC ทั้งหมด
- Assign br_id (BR-01, BR-02, ...)
- ตรวจ duplicate ข้าม UC — ถ้า BR เหมือนกันข้าม UC ให้ใช้ br_id เดิม ไม่สร้างใหม่
- ระบุ `also_used_in` สำหรับทุก BR ที่ reuse

```
📌 Business Rules — PDT-XXXX
─────────────────────────────
BR-01 [permission]: ...
BR-02 [constraint]: ...
...
Total: N BRs
```

---

### STEP 4 — AC Manifest [GATE 1]

List ทุก AC ทั้ง PM source และ QA-enriched พร้อม type และ count:

```
📋 AC Manifest — PDT-XXXX
──────────────────────────────────────────────────
AC-1:  [scenario] — type: default_state  — source: PM
AC-2:  [scenario] — type: happy_path    — source: PM
AC-11: [scenario] — type: error_state   — source: QA
AC-12: [scenario] — type: edge_case     — source: QA
...
──────────────────────────────────────────────────
Total: N ACs (PM: X, QA: Y)
```

---

### STEP 5 — Loop [X/N] — assign metadata

สำหรับแต่ละ AC วนลูปตาม Manifest แสดง progress:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 [X/N] กำหนด metadata: AC-X — [scenario]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Assign ให้ครบ:
- `ac_id` — ตามลำดับ
- `type` — default_state / happy_path / alternative / error_state / edge_case
- `source` — PM หรือ QA
- `br_ids` — list br_id ที่ apply กับ AC นี้
- `given[]`, `when`, `then[]` — structured array
- `clarifications_needed[]` — คำถามที่ยังค้าง (status: PENDING, answer: null)

---

### STEP 6 — Completion Gate [GATE 2]

```
✅ Completion Check — PDT-XXXX
──────────────────────────────────────────────────
AC-1:  type ✓  source ✓  br_ids ✓  given ✓  then ✓
AC-2:  type ✓  source ✓  br_ids ✓  given ✓  then ✓
...
──────────────────────────────────────────────────
ครอบคลุม: N/N ACs
```

ถ้า AC ใดขาด field → assign ทันที แล้ว re-check ก่อนเขียน output

---

### STEP 7 — เขียน JSON

เขียน `output/PDT-XXXX-complete-jira-story.json` โดย match ทุก field จาก `01-complete-jira-story.json`:
- `_schema`, `_purpose`, `_status`
- `ids` (epic_id, story_id, uc_id)
- `title`
- `user_story` (role, action, value, invest_check)
- `preconditions[]`
- `business_rules[]` (br_id, type, statement, also_used_in[])
- `acceptance_criteria[]` (ทุก field ตามที่ assign ใน STEP 5)
- `open_questions[]` (list CQ-ID ทุกอันที่ status PENDING)

```
📄 เขียนแล้ว: output/PDT-XXXX-complete-jira-story.json
```

---

## ═══════════════════════════════════════════
## WORKFLOW C — User Flow JSON
## Trigger: "สร้าง flow JSON PDT-XXXX" / "generate flow PDT-XXXX"
## Output: output/PDT-XXXX-user-flow.json
## ═══════════════════════════════════════════

### READINESS GATE [GATE 0]

ตรวจ 3 เงื่อนไขก่อน ถ้าขาดข้อใด → แจ้งและหยุด:

```
🔎 Readiness Check — PDT-XXXX User Flow
──────────────────────────────────────────────────
[ ] output/PDT-XXXX-complete-jira-story.json exists
[ ] ทุก ac_id และ br_id ถูก assign ใน Schema 1 แล้ว
[ ] open_questions ไม่มี PENDING (ถ้ามี → เลือก Option A/B ก่อน)
──────────────────────────────────────────────────
```

ถ้า open_questions ยัง PENDING → แจ้งตัวเลือกจาก `00-schema-process-guide.md`:
```
⚠️ มี clarification ที่ยังค้าง:
Option A — Hold flow ที่อ้างอิง AC นั้นเป็น placeholder ก่อน
Option B — สร้าง flow แต่ mark step ที่ไม่ชัดว่า "assumption": "..."
เลือก Option ไหน?
```

---

### STEP 0 — อ่าน Schema 1

อ่าน `output/PDT-XXXX-complete-jira-story.json`

---

### STEP 1 — อ่าน skills และ Build actor map

อ่าน `phase-2.3-business-rule-extraction.md` สำหรับ BR cross-reference

Build actor map ตาม schema ใน `02-user-flow.json`:
```json
"actors": {
  "admin":   "User with permission",
  "app":     "Mobile console frontend",
  "api":     "Social+ backend API",
  "network": "Network layer",
  "system":  "Server-side background process"
}
```

---

### STEP 2 — Flow Manifest [GATE 1]

จัดกลุ่ม AC จาก Schema 1 เป็น flows โดยดูจาก type และ entry_from:

```
📋 Flow Manifest — PDT-XXXX
──────────────────────────────────────────────────
F01: [name] — type: happy_path    — AC: AC-1,2,3  — entry_from: null
F02: [name] — type: happy_path    — AC: AC-7,8    — entry_from: F01
F03: [name] — type: error_state   — AC: AC-11     — entry_from: F01
F04: [name] — type: alternative   — AC: AC-10     — entry_from: F01
F05: [name] — type: edge_case     — AC: AC-13     — entry_from: F01
F06: [name] — type: default_state — AC: AC-6,12   — entry_from: null
──────────────────────────────────────────────────
Total: N flows
ทุก AC ถูก cover? [ตรวจ]
```

ถ้ามี AC ที่ไม่ถูก assign ใน flow ใด → flag ทันที

---

### STEP 3 — Loop — เขียน flow

สำหรับแต่ละ flow แสดง progress:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 [X/N] กำลังเขียน flow: F0X — [name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

สำหรับแต่ละ flow เขียน:
- `flow_id`, `name`, `type`, `source`, `ac_ids[]`, `br_ids[]`, `entry_from`, `summary`
- `assumptions[]` — ถ้ามี PENDING clarification mark ไว้ที่นี่
- `steps[]` — ทุก step ต้องมี `step_id`, `actor`, `action`
  - step ที่มี state change ต้องมี `state_change: { object, from, to }` หรือ `{ object, operation, ... }`
  - step ที่อ้างอิง BR ต้องมี `br_ids[]`
- `test_hints` — unit, scenario, e2e

---

### STEP 4 — Completion Gate [GATE 2]

ตรวจว่าทุก ac_id จาก Schema 1 ปรากฏอยู่ใน flow อย่างน้อย 1 flow:

```
✅ Completion Check — PDT-XXXX Flows
──────────────────────────────────────────────────
AC-1:  covered in F01 ✓
AC-2:  covered in F01 ✓
AC-7:  covered in F02 ✓
AC-11: covered in F03 ✓
...
──────────────────────────────────────────────────
ครอบคลุม: N/N ACs
```

ถ้ามี AC ที่ไม่ถูก cover → สร้าง flow สำหรับ AC นั้นทันที แล้ว re-check

---

### STEP 5 — เขียน JSON

เขียน `output/PDT-XXXX-user-flow.json` โดย match ทุก field จาก `02-user-flow.json`:
- `_schema`, `_purpose`, `_status`, `_warning`
- `ids` (epic_id, story_id, uc_id)
- `actors` (map)
- `flows[]` (ทุก flow จาก STEP 3)

```
📄 เขียนแล้ว: output/PDT-XXXX-user-flow.json
```

---

## ═══════════════════════════════════════════
## Gate Rules — ใช้กับทุก Workflow
## ═══════════════════════════════════════════

```
RULE 1 — ห้ามข้าม AC โดยไม่แจ้ง
         ถ้า context ยาวมากจน Claude อาจ drop → pause ขอ confirm ก่อน

RULE 2 — ห้ามเขียน output ก่อน Completion Gate pass

RULE 3 — แสดง progress [X/N] ทุกครั้งที่เริ่ม AC หรือ flow ใหม่

RULE 4 — อ่าน skills ที่ระบุก่อน loop เสมอ

RULE 5 — ถ้าพบ AC ที่หลุดหลัง gate → วิเคราะห์ทันที แล้ว re-check gate
          ห้ามบันทึก output จนกว่า gate จะ pass
```
