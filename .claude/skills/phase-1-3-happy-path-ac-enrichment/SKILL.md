---
name: phase-1-3-happy-path-ac-enrichment
description: 'ใช้ skill นี้เมื่อได้รับ AC จาก PM แล้วต้องการเติมให้สมบูรณ์ก่อน test หรือ implement โดยเฉพาะ Happy Path AC ที่เขียนมาในรูปแบบ Given-When-Then แต่ยังกว้างเกินไป ขาด precondition, side effect, หรือ state change ที่ชัดเจน Skill นี้ไม่ได้เขียนทับ AC ของ PM แต่ผลิต QA-enriched AC version ที่ต่อยอดออกมา พร้อม clarification questions ที่ต้องถาม PM ก่อนที่จะ finalize AC ได้ Trigger เมื่อ: ได้รับ AC จาก PM แล้วรู้สึกว่า "ยังไม่พอ test", ไม่แน่ใจว่า dev จะ implement ตรงกับที่ต้องการ, หรือต้องการ review AC ก่อน sprint เริ่ม'
---

# Happy Path AC Enrichment

รับ AC กว้างๆ จาก PM มาแล้วเติมให้สมบูรณ์ด้วย 3 ขั้น
พร้อม clarification process ก่อนที่จะ finalize เป็น QA-enriched AC

## Artifacts
- **Consumes:** PM's happy-path AC + story Preconditions + Relationship Map (จาก 1-1)
- **Produces:** QA-enriched happy-path AC (bound to ac_id) + clarification questions (→ Register)
- **Called by:** process Layer 1 · STEP2 (Specify) — loop ต่อ ac_id, ก่อน 1-4

> Skill นี้เป็น pure capability — การ loop ต่อ AC + gate อยู่ที่ `process/layer-1-ba-requirement-analysis.md`

---

## หลักการสำคัญ — ไม่เขียนทับ ต่อยอด

AC ของ PM และ AC ของ QA มีจุดประสงค์ต่างกัน

| | PM's AC | QA-enriched AC |
|---|---|---|
| จุดประสงค์ | บอก intent และ business expectation | บอก exact behavior ที่ verify ได้ |
| ผู้อ่านหลัก | dev, stakeholder | tester, dev ที่ต้องการ detail |
| ระดับ detail | business language | technical + UI behavior |
| เมื่อขัดแย้ง | PM's AC คือ source of truth | QA ต้องถาม clarification ก่อน |

**กฎ:** ถ้าสิ่งที่จะเขียนใหม่ขัดแย้งหรือตีความต่างจาก PM's AC
ห้าม assume — ต้องเปลี่ยนเป็น clarification question ก่อนเสมอ

---

## โครงสร้างของ Happy Path AC ที่สมบูรณ์

AC ที่ดีต้องตอบคำถามสี่ข้อนี้ครบในทุก scenario

```
Given  [role ของ actor]
       [state ของ object หลัก]
       [context / entry point]
When   [action ที่ trigger — ระบุ UI element ให้ชัด]
Then   [primary outcome — สิ่งที่เปลี่ยนโดยตรง]
       [side effects — state อื่นที่เปลี่ยนตามมา]
       [UI feedback — สิ่งที่ user เห็นบนหน้าจอ]
```

**สัญญาณว่า AC ยังไม่สมบูรณ์:**
- Given ไม่ระบุ permission หรือ role ของ actor
- Given ไม่ระบุ state ของ object ก่อน action
- Then บอกแค่ primary outcome ไม่มี side effect
- Then ใช้คำกว้างๆ เช่น "is approved", "is processed" โดยไม่บอกว่าหมายถึงอะไรบน UI

---

## Step 1 · ตีความ AC ที่ได้มา

อ่าน AC ของ PM แล้วระบุให้ชัดว่าแต่ละส่วน Given/When/Then
ครอบคลุมอะไร และขาดอะไร

### Checklist การตีความ Given

- [ ] ระบุ role / permission ของ actor ไหม?
- [ ] ระบุ state ของ object หลักก่อน action ไหม?
  เช่น post ต้องอยู่ใน pending state, field ต้องไม่ว่าง
- [ ] ระบุ context หรือ entry point ไหม?
  เช่น admin กำลังอยู่หน้าไหน, มาจาก flow ไหน
- [ ] มี AND condition ที่ซ่อนอยู่ใน preconditions ของ story ไหม?
  ที่ PM ลืมใส่ใน Given แต่จำเป็นต้อง setup ก่อน test

### Checklist การตีความ When

- [ ] action ชัดพอที่จะ map ไปหา UI element เดียวได้ไหม?
- [ ] ถ้า action เดียวกันเกิดได้จากหลาย entry point
  ต้อง split เป็นหลาย AC หรือระบุ entry point ให้ชัด

### Checklist การตีความ Then

- [ ] primary outcome คืออะไร — state อะไรที่เปลี่ยนโดยตรง?
- [ ] side effects คืออะไร — state อื่นที่ควรเปลี่ยนตามมา?
  เช่น count, badge, list, log
- [ ] UI feedback คืออะไร — user เห็นอะไรบนหน้าจอ?
  เช่น toast, loading indicator, redirect, disabled state
- [ ] outcome วัดได้ไหม — verify ได้จาก UI หรือ API response?

---

## Step 2 · ตั้ง Clarification Questions ก่อนเติม

**กฎสำคัญ:** ทุกจุดที่ยัง assume อยู่ต้องถาม PM ก่อน
ห้ามเติม AC โดย assume เองในสิ่งที่มีความเป็นไปได้มากกว่าหนึ่งแบบ

### วิธีตั้ง Clarification Question ที่ดี

คำถามที่ดีต้องมีสองส่วนเสมอ

```
1. Observation  — "AC ไม่ได้ระบุว่า..."
2. Consequence  — "ถ้าไม่ชัดตรงนี้ อาจเกิด A หรือ B ซึ่งจะกระทบ..."
3. คำถาม        — "ลูกค้า / PM expect behavior แบบไหน?"
```

### ประเภทของ Clarification ที่พบบ่อย

**Missing precondition:**
```
Observation:  AC ไม่ได้ระบุว่า admin ต้องมี permission อะไรถึงจะ approve ได้
Consequence:  ถ้าไม่ระบุ dev อาจ implement ให้ admin ทุกคน approve ได้
              หรืออาจ restrict เฉพาะ role สูงสุด ซึ่งต่างกันมาก
คำถาม:        permission tier ไหนที่สามารถ approve pending post ได้?
```

**Ambiguous Then:**
```
Observation:  Then บอกว่า "the post is approved" แต่ไม่ได้ระบุว่า
              publish ทันทีหรือมี intermediate state
Consequence:  dev อาจ implement แค่เปลี่ยน status flag
              โดยไม่ publish ออก feed จนกว่าจะมี trigger อื่น
คำถาม:        เมื่อ approve แล้ว post ควร publish ทันทีบน community feed เลยไหม?
```

**Missing side effect:**
```
Observation:  Then ไม่ได้ระบุว่า badge count บน Pending tab จะเปลี่ยนไหม
Consequence:  ถ้า badge ไม่ update admin จะไม่รู้ว่า pending list เปลี่ยนไป
              ต้อง refresh เองทุกครั้ง
คำถาม:        badge count ควร decrement ทันทีหลัง approve หรือ refresh เมื่อกลับมาหน้านี้?
```

---

## Step 3 · เติม AC ด้วย 3 ขั้น

หลังจากได้คำตอบ clarification กลับมาแล้ว ให้เติม AC ด้วย 3 ขั้นนี้

### ขั้นที่ 1 — ดึง Given จาก Preconditions ของ story

ทุก story มี Preconditions section — นั่นคือ Given ที่หายไปจาก AC

```
วิธีทำ:
1. อ่าน Preconditions ทุกข้อของ story
2. เช็คว่าข้อไหนที่ AC ข้อนั้นต้องการแต่ยังไม่มีใน Given
3. เพิ่มเข้าไปเป็น AND condition ใน Given

ตัวอย่าง UC8:
Preconditions: "Admin has 'Can manage posts & comments' permission"
               "At least one post is pending approval"

AC เดิม Given: "the admin taps Approve on a post"
AC ใหม่ Given: "the admin has 'Can manage posts & comments' permission
               AND the post is in pending state
               AND the admin is viewing the Pending tab"
```

### ขั้นที่ 2 — วาด State Machine แล้วดูว่า Then ครอบคลุมทุก state change ไหม

```
วิธีทำ:
1. ระบุ object หลักที่ action นี้กระทบ
2. ระบุทุก state ที่ object นั้นเปลี่ยนหลัง action
3. ระบุ dependent objects ที่เปลี่ยนตาม เช่น count, list, log
4. เช็คว่า Then ในปัจจุบันครอบคลุมทุกบรรทัดไหม

ตัวอย่าง UC8 — หลัง approve:
├── post status:      pending → published          → มีใน Then ไหม?
├── pending list:     มี post นี้ → ไม่มี          → มีใน Then ไหม?
├── badge count:      N → N-1                      → มีใน Then ไหม?
├── posted list:      ไม่มี post นี้ → มี          → มีใน Then ไหม?
├── UI feedback:      ไม่มี toast → มี success toast → มีใน Then ไหม?
└── approve button:   enabled → disabled (loading) → มีใน Then ไหม?

บรรทัดไหนที่ยังไม่มีใน Then = สิ่งที่ต้องเพิ่ม
```

### ขั้นที่ 3 — ถามว่า "ใครอีกที่รู้เรื่องนี้?"

```
วิธีทำ:
1. ดึง Relationship Map จาก Phase 1.1 มาดู
2. สำหรับทุก actor ที่ไม่ใช่ผู้ทำ action — ถามว่า
   "เขารู้เรื่อง action นี้ไหม? รู้ได้ยังไง?"
3. ถ้ารู้ → ต้องมี Then ที่ระบุ notification หรือ state change ของเขาด้วย
4. ถ้าไม่มีใน AC → เพิ่มเป็น clarification question

ตัวอย่าง UC8:
Actor: post owner
ถาม: post owner รู้ว่า post ถูก approve ไหม? รู้ได้ยังไง?
ใน AC: ไม่มีการระบุเลย
→ เพิ่มเป็น clarification question:
  "post owner ควรได้รับ notification เมื่อ post ถูก approve ไหม?"
```

---

## Step 4 · เขียน QA-enriched AC

หลังจากผ่าน Step 1–3 และได้รับ clarification กลับมาแล้ว
ให้เขียน AC เวอร์ชันใหม่โดยใช้โครงสร้างนี้

```
[ชื่อ scenario — ระบุให้ชัดว่า happy path หรือ scenario ไหน]

Given [role + permission ของ actor]
  AND [state ของ object หลัก]
  AND [context / entry point]
When  [action + UI element ที่ชัดเจน]
Then  [primary outcome]
  AND [side effect 1]
  AND [side effect 2]
  AND [UI feedback]

Note: [assumption หรือ dependency ที่ต้อง aware — ถ้ามี]
```

**กฎการเขียน:**
- ทุก Then ต้องระบุสิ่งที่ verify ได้จริง ห้ามใช้คำกว้างเช่น "is processed"
- ถ้ามีหลาย Then ที่เกิดพร้อมกัน ใช้ AND
- ถ้า Then มีลำดับ เช่น loading แล้วค่อย success ให้แยก scenario

---

## ตัวอย่างเต็ม — UC8 Approve Post

### Input: AC จาก PM

```
Given the admin taps Approve on a post
When the request is in progress
Then the Approve button is disabled to prevent double submission

Given the user taps Approve, when the action succeeds
Then the post is immediately removed from the pending list,
     and the badge count decrements by one
```

### Step 1 · ตีความ

Given: ไม่ระบุ permission, ไม่ระบุ state ของ post
When: "request is in progress" กับ "action succeeds" เป็นคนละ scenario
Then: บอก primary outcome แต่ขาด posted list, UI feedback, และ post owner

### Step 2 · Clarification Questions

```
Q1: permission tier ไหนที่ approve ได้?
    → เพราะถ้าไม่ระบุ dev อาจให้ admin ทุก role approve ได้

Q2: เมื่อ approve สำเร็จ post จะปรากฏใน Posted tab ทันทีไหม?
    → Then ระบุว่าหายจาก pending แต่ไม่บอกว่าไปอยู่ที่ไหน

Q3: post owner ได้รับ notification ไหมเมื่อ post ถูก approve?
    → ไม่มีใน AC เลย แต่ post owner เป็น actor ที่ได้รับผลกระทบ
```

### Step 3 · 3 ขั้น

**ขั้นที่ 1 — ดึง Given จาก Preconditions:**
```
+ Admin has "Can manage posts & comments" permission
+ At least one post is pending approval
```

**ขั้นที่ 2 — State Machine:**
```
post status:    pending → published      ✓ มีบางส่วนใน Then
pending list:   มี → ไม่มี              ✓ มีใน Then
badge count:    N → N-1                 ✓ มีใน Then
posted list:    ไม่มี → มี              ✗ ไม่มีใน Then → เพิ่ม
approve button: enabled → disabled       ✓ มีใน Then (loading scenario)
success toast:  ไม่มี → มี              ✗ ไม่มีใน Then → เพิ่ม
post owner:     ไม่รู้ → รู้ผล          ✗ ไม่มีใน Then → clarification
```

**ขั้นที่ 3 — Silent actor:**
```
post owner → ยังไม่มี notification ระบุใน AC → clarification question
```

### Output: QA-enriched AC

```
[Happy path — Approve post: loading state]

Given the admin has "Can manage posts & comments" permission
  AND the post is in pending state
  AND the admin is viewing the Pending tab
When the admin taps Approve
Then the Approve button is immediately disabled
  AND a loading indicator is shown
  AND no further taps on Approve are registered

[Happy path — Approve post: success]

Given the admin has "Can manage posts & comments" permission
  AND the post is in pending state
  AND the admin is viewing the Pending tab
When the admin taps Approve
  AND the request succeeds
Then the post is immediately published to the community feed
  AND the post is removed from the Pending tab list
  AND the post appears in the Posted tab
  AND the badge count on the Pending tab decrements by 1
  AND a success toast is shown to the admin

Note: ยังรอ clarification เรื่อง post owner notification
      ก่อน finalize AC ข้อนี้
```

---

## Output format สรุป

เมื่อใช้ skill นี้กับ AC จริง ให้ produce output 3 ส่วนเสมอ

**ส่วนที่ 1 — Interpretation notes**
สรุปสั้นๆ ว่า Given/When/Then เดิมขาดอะไร

**ส่วนที่ 2 — Clarification questions**
คำถามที่ต้องถาม PM ก่อน finalize
พร้อม observation และ consequence ทุกข้อ

**ส่วนที่ 3 — QA-enriched AC (draft)**
AC ที่เติมแล้ว โดยทำเครื่องหมาย [PENDING CLARIFICATION]
ในส่วนที่ยังรอคำตอบจาก PM อยู่
