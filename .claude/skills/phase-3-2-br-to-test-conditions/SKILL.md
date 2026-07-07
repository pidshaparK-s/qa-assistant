---
name: phase-3-2-br-to-test-conditions
description: 'ใช้ skill นี้เมื่อมี PRD, Jira story (AC จาก PM), หรือ Figma design และต้องการแปลงออกมาเป็น Business Rules พร้อม Test Conditions โดยไม่ต้องรอให้ AC ครบก่อน — รับ input หลายแหล่งพร้อมกันได้ Skill นี้ normalize source ก่อน จากนั้น extract BRs ด้วย 4 ประเภท แล้วแปลง BR แต่ละข้อเป็น Test Conditions ด้วย test technique ที่เหมาะกับ BR type นั้น (BVA, EP, Decision Table, State Transition) Trigger เมื่อ: ได้รับ PRD + Figma แต่ยังไม่มี AC ครบ, ต้องการ test coverage ก่อน sprint เริ่ม, หรือ AC จาก PM มี gap และต้องการขุด business logic ที่ซ่อนอยู่ออกมาก่อนเขียน test'
---

# BR Extraction → Test Conditions

รับ multi-source input (PRD + Jira AC + Figma) → สกัด Business Rules → แปลงเป็น Test Conditions พร้อม technique

---

## หลักการ — ทำไมต้องผ่าน BR ก่อนเขียน test

**Test condition ที่ดีต้องมาจาก rule ไม่ใช่จาก screen**

ถ้าเขียน test จาก Figma โดยตรง จะได้ test ที่ตรวจ "UI ถูกไหม" แต่ไม่ได้ตรวจ "business logic ถูกไหม"

```
❌ ถ้าเขียนจาก screen:
"ตรวจว่าปุ่ม Approve แสดงใน Pending Posts หน้า"
→ พลาด: ปุ่ม visible แต่ logic การ approve อาจผิด

✅ ถ้าผ่าน BR ก่อน:
BR-01 [Permission]: เฉพาะ Moderator เท่านั้นที่ approve pending post ได้
→ TC-01a: Moderator approve → post status = published
→ TC-01b: Member approve → blocked + error
→ TC-01c: Moderator approve post ที่ไม่ใช่ pending → blocked
```

---

## Input ที่รับได้

| Source | Format | บทบาท |
|---|---|---|
| PRD / requirement doc | paste text | intent หลัก + business context |
| Jira story + AC (PDT-XXXX) | issue key (MCP fetch) หรือ paste | PM's AC = source of truth แต่อาจมี gap |
| Figma design | URL หรือ screen description ที่ capture มา | visual behavior = implicit BRs ที่ไม่ได้เขียนใน doc |

**ไม่ต้องมีครบทั้ง 3** — 1 source ก็ run ได้ แต่ coverage จะน้อยกว่า

---

## STEP 1 · Source Normalization

แปลงทุก source เป็น "requirement statement" format เดียว พร้อม tag ที่มา

```
[PRD]    ผู้ใช้ที่มี role Moderator เท่านั้นที่ approve post ได้
[PRD]    Pending list แสดงสูงสุด 50 posts ต่อหน้า เรียงจากเก่าสุด
[AC-03]  Given moderator logged in, When tap Approve, Then post status = published AND pending count -1
[AC-03]  Given moderator, When approve, Then author gets push notification
[FIGMA]  หน้า Pending Posts มีปุ่ม Approve visible เฉพาะ Moderator role เท่านั้น
[FIGMA]  Empty state "No pending posts" แสดงเมื่อ list ว่าง
```

**กฎ:**
- ถ้า 2 source บอกสิ่งเดียวกัน → tag ทั้งคู่ใน BR เดียว
- ถ้า source ขัดแย้งกัน → flag `[CONFLICT]` ทันที ห้าม merge เอง ต้อง clarify ก่อน

```
[CONFLICT] PRD บอก "max 50 posts" แต่ FIGMA แสดง pagination ที่ 20 → ต้องถาม PM ก่อน proceed
```

---

## STEP 2 · BR Extraction

ใช้คำถาม trigger ต่อไปนี้กับ requirement statements ทุกข้อ:

| BR Type | Trigger คำถาม | ตัวอย่าง |
|---|---|---|
| **Permission** | "ใครทำได้บ้าง? ใครทำไม่ได้?" | เฉพาะ Moderator approve ได้ |
| **Constraint** | "มีตัวเลข limit, boundary, หรือ format จำกัดไหม?" | max 50 posts/page, max 200 chars |
| **Computation** | "ระบบคำนวณค่านี้ยังไง? แสดงผลยังไง?" | pending count -1 หลัง approve |
| **State/Lifecycle** | "state ก่อน action คืออะไร? หลัง action เปลี่ยนเป็นอะไร?" | pending → published หลัง approve |

**Format เขียน BR:**

```
BR-01 [Permission]
Rule: เฉพาะ Moderator role เท่านั้นที่ approve หรือ reject pending post ได้
Source: [PRD], [AC-03], [FIGMA]

BR-02 [Constraint]
Rule: Pending Posts list แสดงสูงสุด 50 posts ต่อหน้า เรียงจากเก่าสุดขึ้นก่อน
Source: [PRD]

BR-03 [State]
Rule: Post ที่ถูก approve เปลี่ยน status จาก pending → published ทันที
      pending count ของ community ลด 1
      author ได้รับ push notification
Source: [AC-03]

BR-04 [Computation]
Rule: pending count แสดงในรูป UIKIT numeric format (1K+ ถ้า ≥ 1000)
Source: [FIGMA]
```

**สิ่งที่ไม่ใช่ BR:**
- "ตรวจว่าปุ่มสีถูกต้อง" → visual test (ไม่ใช่ business rule)
- "หน้าโหลดเร็ว" → performance test
- "user เข้าใจ label ไหม" → usability test

---

## STEP 3 · Test Condition Derivation

ทุก BR → Test Conditions ตาม technique ที่เหมาะกับ type:

---

### Permission BR → Decision Table

สร้าง condition ครอบทุก combination ของ role + state:

```
BR-01 [Permission]: เฉพาะ Moderator approve ได้

TC-01a [P1] Moderator + post status=pending → approve visible, action succeeds
TC-01b [P1] Member role + post status=pending → approve hidden/disabled
TC-01c [P1] Moderator + post status=published → approve blocked (wrong state)
TC-01d [P2] Moderator ถูก revoke permission กลางทาง → action fails gracefully
```

---

### Constraint BR → BVA (Boundary Value Analysis)

สร้าง condition ที่ boundary และรอบ boundary:

```
BR-02 [Constraint]: max 50 posts/page

TC-02a [P1] 0 posts → empty state แสดง "No pending posts"
TC-02b [P2] 1 post → แสดง 1 post, ไม่มี pagination
TC-02c [P2] 49 posts → แสดงทั้งหมด, ไม่มี pagination
TC-02d [P1] 50 posts → แสดงทั้งหมด, ไม่มี pagination (boundary)
TC-02e [P1] 51 posts → แสดง 50 posts, pagination แสดง page 2
```

---

### Computation BR → EP + Sample Values

สร้าง condition ครอบ equivalence class หลัก:

```
BR-04 [Computation]: pending count แสดงด้วย UIKIT format

TC-04a [P1] count = 0 → แสดง "0" (หรือ empty/hidden ตาม design)
TC-04b [P1] count = 1 → แสดง "1"
TC-04c [P2] count = 999 → แสดง "999"
TC-04d [P1] count = 1000 → แสดง "1K"
TC-04e [P2] count = 1500 → แสดง "1.5K"
TC-04f [P2] count = 1,000,000 → แสดง "1M"
```

---

### State/Lifecycle BR → State Transition Table

สร้าง condition ครอบทุก valid/invalid transition:

```
BR-03 [State]: approve post: pending → published

TC-03a [P1] post=pending + Moderator approve → status=published, count-1, notification sent
TC-03b [P1] post=pending + Moderator approve → pending list refresh ทันที (post หายออก)
TC-03c [P2] approve แล้ว approve ซ้ำอีกครั้ง → blocked (idempotency)
TC-03d [P2] 2 Moderator approve post เดียวกันพร้อมกัน → first wins, second gets conflict error
TC-03e [P1] approve สำเร็จแต่ push notification fail → post ยัง published (notification failure ไม่ rollback)
```

---

## Output Format

```markdown
## Source Summary

| Source | รายการที่ดึงมา |
|---|---|
| PRD | 8 requirements |
| Jira PDT-2880 (AC จาก PM) | AC-01 ถึง AC-06 |
| Figma screen capture | 4 screens |
| [CONFLICT] | BR-02 — ต้องได้คำตอบจาก PM ก่อน proceed |

---

## BR Catalog

| BR-ID | Type | Rule | Source |
|---|---|---|---|
| BR-01 | Permission | เฉพาะ Moderator approve/reject pending post ได้ | [PRD][AC-03][FIGMA] |
| BR-02 | Constraint | Pending list สูงสุด 50 posts/page เรียงเก่าสุดก่อน | [PRD] ⚠️ CONFLICT กับ FIGMA |
| BR-03 | State | approve: pending → published, count-1, notification | [AC-03] |
| BR-04 | Computation | pending count ใช้ UIKIT format (1K+) | [FIGMA] |

---

## Test Conditions

| TC-ID | BR-ID | Condition | Technique | Priority |
|---|---|---|---|---|
| TC-01a | BR-01 | Moderator + pending post → approve succeeds | Decision Table | P1 |
| TC-01b | BR-01 | Member role → approve hidden/blocked | Decision Table | P1 |
| TC-01c | BR-01 | Moderator + non-pending post → approve blocked | Decision Table | P1 |
| TC-02a | BR-02 | 0 posts → empty state | BVA | P2 |
| TC-02d | BR-02 | 50 posts → all shown, no pagination | BVA | P1 |
| TC-02e | BR-02 | 51 posts → pagination appears | BVA | P1 |
| TC-03a | BR-03 | approve → status=published, count-1, notification | State Transition | P1 |
| TC-03d | BR-03 | 2 Moderators approve same post → first wins | State Transition | P2 |
| TC-04d | BR-04 | count=1000 → แสดง "1K" | EP | P2 |

---

## Conflicts & Clarifications ที่ต้องได้คำตอบก่อน proceed

1. **BR-02 [CONFLICT]** — PRD บอก max 50 posts แต่ Figma แสดง pagination ที่ 20  
   → ถาม PM: limit จริงคือเท่าไหร่?

2. **TC-03e [AI-INFERRED]** — ไม่มี source ระบุ behavior ของ notification failure  
   → ถาม PM: ถ้า push notification fail ต้อง rollback approval ไหม?
```

---

## หลังได้ Test Conditions แล้ว

Test Conditions ที่ได้จาก skill นี้ต่อกับ pipeline ถัดไปได้เลย:

```
TC list นี้ → เขียน Scenarios + Test Cases (phase-3-3 ถ้ามี)
TC list นี้ → ป้อนเข้า phase-3-1 เพื่อ Automation Judgment
```

ห้ามข้าม BR — ถ้าเขียน test cases จาก screen โดยตรงโดยไม่ผ่าน BR จะพลาด business logic ที่ซ่อนอยู่

---

## Checklist ก่อน output

```
☐ ทุก requirement statement มี source tag ([PRD]/[AC-XX]/[FIGMA])
☐ ทุก [CONFLICT] ถูก flag และหยุดรอ clarification
☐ ทุก [AI-INFERRED] ถูก flag และระบุคำถามที่ต้องถาม PM
☐ BR ทุกข้อระบุ type ถูกต้อง (Permission/Constraint/Computation/State)
☐ Test Conditions ใช้ technique ตรงกับ BR type
☐ Priority P1 ครอบ happy path + hard blockers ครบ
☐ State BRs มี TC ที่ตรวจ concurrent action ด้วย (ถ้าเกี่ยวข้อง)
```
