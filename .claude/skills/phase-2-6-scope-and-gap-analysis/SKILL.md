---
name: phase-2-6-scope-and-gap-analysis
description: 'ใช้ skill นี้ก่อน sprint เริ่มเสมอ เพื่อ define ว่าอะไรอยู่ใน scope, อะไรไม่อยู่, อะไรที่ยัง assume โดยไม่มีใครยืนยัน, และอะไรที่ยังไม่รู้คำตอบ Skill นี้คือ "gate" สุดท้ายก่อน sprint — ถ้าข้าม step นี้ทีมจะ build โดยไม่มีใครตกลงกันก่อนว่าอะไรอยู่ใน scope และเกิด scope creep ระหว่าง sprint Trigger เมื่อ: ก่อน sprint planning, หลังเขียน AC ครบแล้วแต่รู้สึกว่ายังมีอะไรขาด, PM พูดถึง feature ที่ไม่ได้อยู่ใน AC, หรือทีมถกเถียงกันว่าอะไร "อยู่ใน scope" ไหม'
---

# Scope Boundary และ Gap Analysis

Define ว่าอะไรอยู่ใน scope, อะไรไม่อยู่, และอะไรที่ยังไม่รู้คำตอบ
ก่อน sprint เริ่มเพื่อไม่ให้เกิด scope creep หรือ assumption ที่ไม่มีใครยืนยัน

---

## หลักการพื้นฐาน

**"ไม่ได้พูดถึง" ≠ "out of scope"** ในหัว dev หรือ PM

ถ้าไม่ document ให้ชัด ทุกคนจะ assume ต่างกัน
แล้วมาเถียงกันตอน sprint review ว่าใคร "ผิด"
ทั้งที่จริงๆ ไม่มีใครตกลงกันก่อนเลย

Gap Analysis และ Scope Boundary แก้ปัญหานี้โดยบังคับให้ทุกคน
ตกลงกันล่วงหน้าก่อน sprint เริ่ม

---

## 5 สิ่งที่ต้อง define

### 1 — In Scope

สิ่งที่ทีมตกลงว่าจะ build ใน sprint นี้
ต้องระบุให้ชัดกว่า feature name เพราะ feature name คลุมเครือ

```
ไม่ชัด:
In scope: pending posts feature

ชัด:
In scope:
✓ View pending posts scoped to assigned communities
✓ Approve and decline individual posts
✓ Badge count show/hide
✓ Empty state
✓ Network error rollback
```

### 2 — Out of Scope

สิ่งที่รู้ว่ามี แต่ตัดสินใจไม่ build ใน release นี้
ต้อง document เสมอเพราะ "ไม่พูดถึง" ≠ "ทุกคนรู้ว่าไม่ทำ"

```
Out of scope (this release):
✗ Real-time sync — feed updates on refresh only
✗ Post owner notification when approved/declined
✗ Bulk approve/decline
✗ Filter by community
✗ Sort options other than created date
```

### 3 — Assumption

สิ่งที่ทีม assume ว่าจริงโดยไม่มีใครยืนยัน
**อันตรายที่สุดในสี่อย่างนี้** เพราะถ้า assumption ผิด
งานทั้งหมดอาจต้องแก้

```
ทุก assumption ต้องมี:
- สิ่งที่ assume
- Risk ถ้า assumption ผิด
- Owner ที่ต้องยืนยัน

ตัวอย่าง:
Assumption: Admin always has at least one assigned community
Risk: ถ้าไม่ใช่ → empty pending list misleads admin
      ว่า "ไม่มี pending" แทนที่จะ "ไม่ได้ assigned"
Owner: PM to confirm before sprint
```

### 4 — Constraint

ข้อจำกัดที่เปลี่ยนไม่ได้ ทีมต้องทำงานภายใต้นี้

```
ตัวอย่าง:
! iOS 15+ and Android 10+ only
! No real-time WebSocket in v1 architecture
! API response SLA ≤ 2 seconds
! Tablet layout not supported in v1
```

### 5 — Open Gap

requirement ที่รู้ว่าต้องมีแต่ยังไม่รู้คำตอบ
ต่างจาก out of scope ตรงที่ out of scope คือ "ตัดสินใจแล้วว่าไม่ทำ"
แต่ open gap คือ "ยังไม่รู้จะทำยังไง"

**กฎ: Open gap ทุกอันต้องมี owner และ due date**
ถ้าไม่มี เจ้าของ gap จะไม่ถูกปิดจนกระทั่ง sprint เริ่มแล้ว

```
? CQ-1: Soft-deleted author placeholder spec
  Owner: PM, Due: ก่อน sprint day 1
? CQ-3: Approved post visibility in Posted tab
  Owner: PM, Due: ก่อน sprint day 1
```

---

## Gap vs Out of Scope — ความต่างที่ต้องชัด

```
Gap (ยังไม่รู้คำตอบ):
"post owner notification — ยังไม่มีใครตัดสินใจ"
→ ต้องหาคำตอบก่อน sprint เริ่ม
→ ถ้าหาไม่ทัน → escalate หรือ hold story

Out of scope (ตัดสินใจแล้ว):
"real-time sync — defer to v2"
→ ทีมตกลงแล้ว ไม่ต้องหาคำตอบ
→ document ใน AC ว่า "[Out of scope for this release]"
```

**กฎตัดสิน:** ถ้าทีมยังถกเถียงกันอยู่ว่าทำหรือไม่ทำ = Open Gap
ถ้าทุกคนเห็นด้วยแล้วว่าไม่ทำ release นี้ = Out of Scope

---

## 3 เทคนิคสำหรับหา Gap

### เทคนิคที่ 1 — ลาก line จาก User Need ไปหา System Behavior

เอา User Need แต่ละข้อจาก Phase 1.2 แล้วถามว่า
"มี AC ที่ cover need นี้ไหม?" — ที่ยังไม่มี = gap candidate

```
User Need: admin รู้ว่ามี pending post รอ review
→ AC-5 badge count                         ✓ covered
→ AC ที่ notify admin เมื่อมี post ใหม่    ✗ gap
  → ตัดสินใจ: out of scope (no real-time)
  → document ชัดว่าไม่มี push notification
```

### เทคนิคที่ 2 — เช็ค AC ทุกข้อว่ามี error state ไหม

```
ทุก happy path AC ต้องถาม:
"ถ้า network ล้มตอนนี้ ใครรับผิดชอบ?"
"ถ้า permission หมดตอนนี้ เกิดอะไร?"
"ถ้า object ถูกลบก่อนที่ action จะสำเร็จ เกิดอะไร?"

AC ที่ไม่มี corresponding error state = gap
ต้องตัดสินใจว่าเป็น in scope error handling
หรือ out of scope ที่จะ fail silently
```

### เทคนิคที่ 3 — เช็ค silent actor ทุกคน

```
ดึง Relationship Map จาก Phase 1.1 มา
แล้วถามทุก actor ว่า "เขามี AC ที่ cover เขาไหม?"

ตัวอย่าง UC8:
post owner = silent actor
→ ไม่มี AC ว่า post owner รู้ผลยังไง
→ gap — in scope? out of scope? defer?
→ ต้องตัดสินใจและ document ให้ชัด
```

---

## Scope Boundary Document — รูปแบบที่ใช้ได้จริง

```
SCOPE BOUNDARY — [Story title]
Sprint: [sprint name/number]
Agreed by: [PM], [Dev lead], [QA]
Date: [date]
Last updated: [date]

IN SCOPE
─────────────────────────────────────────
✓ [สิ่งที่ทำ — ระบุให้ละเอียดกว่า feature name]
✓ ...

OUT OF SCOPE (this release)
─────────────────────────────────────────
✗ [สิ่งที่ไม่ทำ] — [เหตุผลสั้นๆ]
✗ ...

ASSUMPTIONS
─────────────────────────────────────────
~ [สิ่งที่ assume]
  Risk: [ถ้า assume ผิดจะเกิดอะไร]
  Owner: [ใครต้องยืนยัน]

CONSTRAINTS
─────────────────────────────────────────
! [ข้อจำกัดที่เปลี่ยนไม่ได้]

OPEN GAPS — must close before sprint starts
─────────────────────────────────────────
? [สิ่งที่ยังไม่รู้คำตอบ]
  Owner: [ชื่อ], Due: [วันที่]
```

---

## เชื่อมกับ Schema — Complete Jira Story และ User Flow JSON

Gap Analysis เป็น input ให้กับทั้งสอง schema

**Complete Jira Story JSON** (01-complete-jira-story.json):
- `open_questions[]` มาจาก Open Gaps ของ Scope Boundary
- `clarifications_needed[]` ใน AC มาจาก Assumption ที่ยังรอยืนยัน
- `ac_ids` ที่ `source: "QA"` มาจากสิ่งที่ BA+QA ระบุว่า in scope แต่ PM ลืมเขียน

**User Flow JSON** (02-user-flow.json):
- flow ที่มี `assumptions[]` มาจาก Open Gap ที่ยังไม่ปิด
- flow ที่ไม่ควรสร้างจนกว่า gap จะถูกปิด ให้ใช้ placeholder:

```json
{
  "flow_id": "flow-UC08-PENDING-notification",
  "status": "BLOCKED",
  "blocked_by": "CQ-4 — post owner notification behavior not confirmed",
  "steps": []
}
```

---

## Workflow ทีละขั้น

### Step 1 — รวม User Need ทั้งหมดจาก Phase 1.2

อ่าน Why Ladder ที่ทำไว้แล้ว ดูว่ามี User Need ไหนที่ยังไม่มี AC cover

### Step 2 — ลาก line จาก User Need ไปหา AC

สร้าง mapping table ง่ายๆ

```
User Need                          | AC ที่ cover        | Status
──────────────────────────────────────────────────────────────────
review pending posts quickly       | AC-1,2,3,4,5,6     | ✓
act on posts without missing any   | AC-7,8,9,10        | ✓
know result of action immediately  | AC-8,9 (toast)     | ✓
know if action failed              | AC-11              | ✓ (QA added)
notify post owner of outcome       | —                  | ✗ gap → out of scope
```

### Step 3 — เช็ค silent actor และ error state

รัน checklist ด้านล่างกับ AC ทุกข้อ

### Step 4 — จัดกลุ่ม in/out/assumption/constraint/gap

### Step 5 — เขียน Scope Boundary Document และ get sign-off

PM, dev lead, QA ต้อง agree พร้อมกัน ก่อน sprint lock

---

## Checklist ก่อน Sprint

- [ ] ทุก User Need มี AC ที่ cover อย่างน้อยหนึ่งข้อ
- [ ] ทุก happy path AC มี corresponding error state (หรือ document ชัดว่า fail silently)
- [ ] ทุก silent actor ถูกระบุว่า in scope หรือ out of scope
- [ ] ทุก assumption มี owner และ risk ระบุชัด
- [ ] ทุก open gap มี owner และ due date ก่อน sprint day 1
- [ ] Out of scope ทุกอันถูก document ใน AC ที่เกี่ยวข้องว่า "[Out of scope]"
- [ ] PM, dev lead, QA sign off Scope Boundary Document แล้ว
- [ ] User Flow JSON ไม่มี flow ที่มาจาก gap ที่ยังไม่ปิด

---

## สัญญาณว่าควรรัน Gap Analysis ทันที

- PM พูดถึง feature ที่ไม่มีใน AC ระหว่าง sprint
  → Scope Boundary ไม่ชัดพอ
- Dev ถามว่า "feature X อยู่ใน scope นี้ไหม?"
  → ไม่มีใคร document out of scope
- QA พบ behavior ที่ไม่มีใน AC ระหว่าง test
  → มี gap ที่ไม่ถูกระบุ
- PM บอกว่า "ฉันคิดว่า notification ก็ต้องมีด้วย"
  → Assumption ที่ไม่มีใครยืนยัน กลายเป็น scope creep
