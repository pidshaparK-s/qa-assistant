---
name: qa-story-diff
description: 'ใช้ skill นี้เมื่อ Jira story มีการแก้ไขหลังจากทำ analysis ไปแล้ว Fetch story จาก Jira ผ่าน Atlassian MCP → compare กับ JSON ที่เก็บไว้ใน products/ → ระบุว่าอะไรเปลี่ยน → แนะนำว่า phase ไหนต้อง re-run → flag clarifications ที่ได้รับผลกระทบ → อัปเดต stored JSON Trigger เมื่อ: "story PDT-XXXX เปลี่ยนแล้ว", "re-check PDT-XXXX", "sync PDT-XXXX จาก Jira", หรือก่อน sprint planning ทุกครั้ง'
argument-hint: '<issue-key> — Jira issue key เช่น PDT-3562'
---

# QA Story Diff

Fetch Jira story ล่าสุด → เทียบกับ stored JSON → บอกว่าอะไรเปลี่ยนและต้อง re-run อะไร

---

## Input

| Source | Path |
|---|---|
| Jira story (live) | fetch ผ่าน Atlassian MCP ด้วย issue key |
| Stored story JSON | `products/<epic>/stories/<key>-*.json` |
| Clarifications (ถ้ามี) | `qa/<feature>/1_clarifications.json` |

---

## STEP 1 — Fetch Jira story ปัจจุบัน

ใช้ Atlassian MCP ดึง issue key ที่ระบุ:
- Summary, description, status, priority, labels
- Acceptance criteria ทุกข้อพร้อม AC ID
- Comments ที่เกี่ยวข้องกับ requirement

แล้วอ่าน stored JSON จาก `products/` เพื่อเปรียบเทียบ

---

## STEP 2 — Diff: เปรียบเทียบ field by field

ตรวจทุก field ตามลำดับ:

### 2a — Metadata fields

| Field | เปลี่ยนไหม? | Impact |
|---|---|---|
| `summary` | ตรวจ | informational |
| `status` | ตรวจ | informational |
| `priority` | ตรวจ | → phase-2-5 (prioritization) |
| `label` / `note` | ตรวจ | informational |
| `user_story` | ตรวจ | → phase-1-1, phase-1-2 |
| `preconditions` | ตรวจ | → phase-1-3 |
| `entry_points` | ตรวจ | → phase-1-3 |

### 2b — Acceptance Criteria diff

เปรียบเทียบทีละ AC โดยใช้ `ac_id` เป็น key:

| เหตุการณ์ | ตรวจสอบ | Impact |
|---|---|---|
| **AC เพิ่มใหม่** | ac_id ไม่มีใน stored JSON | → phase-1-3 (happy path) + phase-1-4 (edge/error) |
| **AC แก้ไข** | `given` / `when` / `then` เปลี่ยน | → phase-1-3 หรือ 1.4 ตาม field ที่เปลี่ยน + ตรวจ clarifications |
| **AC ถูกลบ** | ac_id อยู่ใน stored JSON แต่ไม่อยู่ใน Jira | → mark deprecated + ลบออกจาก clarifications |
| **AC ไม่เปลี่ยน** | identical | ไม่ต้อง re-run |

สำหรับ AC ที่แก้ไข ระบุ field ที่เปลี่ยนให้ชัด:
```
AC-03 [MODIFIED]
  given: เปลี่ยน — เดิม: "controls overlay is visible" → ใหม่: "video is playing"
  then:  เปลี่ยน — เดิม: "overlay dismisses after ~1s" → ใหม่: "overlay dismisses after 3s"
```

---

## STEP 3 — Impact Assessment

สรุป re-run ที่จำเป็นเป็น table:

```
## Impact Summary

| Phase | Re-run ไหม? | เหตุผล |
|---|---|---|
| phase-1-1 Requirement Interrogation | ❌ / ✅ | user_story เปลี่ยน / ไม่เปลี่ยน |
| phase-1-2 Three-Layer Analysis      | ❌ / ✅ | ... |
| phase-1-3 Happy Path AC Enrichment  | ✅ (AC-01, AC-03) | AC เหล่านี้เปลี่ยน |
| phase-1-4 Edge & Error AC           | ✅ (AC-03) | given/when เปลี่ยนกระทบ edge |
| phase-2-5 Prioritization            | ❌ / ✅ | priority เปลี่ยน / ไม่เปลี่ยน |
| Clarification Gate                  | ✅ | มี clarifications ที่ต้อง re-check |
```

**Priority ของ re-run:**
- `high` — AC ที่เปลี่ยนมี clarification เดิมที่ยัง open อยู่
- `medium` — AC ที่เปลี่ยนแต่ clarification เดิม resolved แล้ว
- `low` — metadata เปลี่ยน, AC ไม่เปลี่ยน

---

## STEP 4 — Clarification Impact Check

ถ้ามี `qa/<feature>/1_clarifications.json` ให้ตรวจว่า clarification ไหนได้รับผลกระทบ:

```
## Clarifications ที่ต้อง re-check

| ID | ผลกระทบ | Action |
|---|---|---|
| uc1-C1 | AC-03 (timeout) แก้ไขแล้ว — คำตอบเดิมอาจ stale | Re-open หรือ verify คำตอบยังถูกต้อง |
| uc2-G1 | AC ที่เกี่ยวข้องไม่เปลี่ยน | ไม่กระทบ |
```

**กฎ:**
- ถ้า AC ที่ clarification อ้างถึงเปลี่ยน → flag clarification ว่า `needs-recheck`
- ถ้า AC ที่ clarification อ้างถึงถูกลบ → mark clarification ว่า `deprecated`
- ถ้า resolved clarification ยังถูกต้องอยู่ → ไม่ต้องทำอะไร

---

## STEP 5 — อัปเดต Stored JSON

ถามผู้ใช้ก่อนว่าต้องการ update stored JSON ไหม:

```
Jira story PDT-3562 มีการเปลี่ยนแปลง 2 จุด:
- AC-03 then[] เปลี่ยน (timeout value)
- AC-06 เพิ่มใหม่

อัปเดต products/PDT-3418/stories/PDT-3562-uc1-tap-to-reveal-controls.json ไหม? [y/n]
```

ถ้า y → เขียน stored JSON ใหม่จาก Jira data ล่าสุด พร้อม:
- เพิ่ม `fetched_at` field บันทึก timestamp วันที่ sync
- เก็บ `clarifications_needed` เดิมไว้ (ไม่ overwrite)
- เพิ่ม AC ใหม่, แก้ AC ที่เปลี่ยน, mark AC deprecated ที่ถูกลบ

---

## Output Format

```markdown
# Story Diff — PDT-3562 (2026-06-30)

## Metadata
- summary: ไม่เปลี่ยน
- priority: ไม่เปลี่ยน
- user_story: ไม่เปลี่ยน

## Acceptance Criteria Changes

### AC-03 [MODIFIED]
given: เดิม "controls overlay is visible" → ใหม่ "controls overlay is visible AND video is playing"
then[0]: เดิม "overlay auto-dismisses after a short timeout" → ใหม่ "overlay auto-dismisses after 3 seconds"

### AC-07 [ADDED]
scenario: Double-tap → skip 10s forward
...

## Impact Summary
| Phase | Re-run? | เหตุผล |
|---|---|---|
| phase-1-3 Happy Path AC Enrichment | ✅ | AC-03 then[] เปลี่ยน |
| phase-1-4 Edge & Error AC | ✅ | AC-03 เปลี่ยน + AC-07 เพิ่มใหม่ |

## Clarifications ที่ต้อง re-check
| ID | ผลกระทบ |
|---|---|
| uc1-C1 | AC-03 timeout ถูก confirm ใน Jira แล้ว — อาจ resolve clarification นี้ได้ |
```

---

## หลักการสำคัญ

- **ห้ามเขียนทับ stored JSON โดยไม่ถาม** — ต้องขอ confirm ก่อนทุกครั้ง
- **ห้ามลบ clarifications_needed เดิม** — merge เท่านั้น
- **ถ้า AC ถูกลบใน Jira แต่มี clarification open อยู่** → แจ้งผู้ใช้ก่อน อย่า auto-deprecate
- **`fetched_at` บันทึกเสมอ** — ให้รู้ว่า JSON sync มาเมื่อไหร่
