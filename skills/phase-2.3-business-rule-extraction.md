---
name: phase-2.3-business-rule-extraction
description: >
  ใช้ skill นี้หลังจากได้ AC มาแล้ว เมื่อต้องการแยก logic ที่ซ่อนอยู่ใน AC
  ออกมาเป็น Business Rule ที่ทีมใช้อ้างอิงร่วมกันได้
  Skill นี้ใช้เทคนิค "Why" จาก phase-1.1 เป็นเครื่องมือหลักในการขุด BR
  แล้วจัดประเภทเป็น 4 ชนิด (permission, constraint, computation, state)
  พร้อมรูปแบบการเขียนที่ใช้ได้จริงใน Jira
  Trigger เมื่อ: มี AC ที่ logic เดียวกันปรากฏในหลาย story,
  dev ถามว่า "แล้วกฎนี้ใช้ที่ไหนบ้าง?", หรือก่อน sprint เริ่มเพื่อ consolidate rules
---

# Business Rule Extraction

แยก logic ที่ซ่อนใน AC ออกมาเป็น Business Rule ที่ทีมทั้งหมดใช้อ้างอิงร่วมกันได้

---

## หลักการพื้นฐาน — BR ต่างจาก AC ยังไง

**AC** ผูกกับ scenario เฉพาะ — "ถ้า X แล้ว Y เกิดขึ้น"
**Business Rule** จริงเสมอข้าม scenario — "กฎที่ระบบต้องปฏิบัติตามในทุกบริบท"

```
AC (ผูกกับ scenario):
"Given admin เปิด Pending tab, Then เห็นแค่ post ของ community ที่ตัวเอง assigned"

Business Rule (จริงเสมอ):
BR-01: An admin can only view and manage content from communities
       they are assigned to, across all content views.
```

**ทำไมต้องแยก:**
ถ้าไม่แยก logic เดียวกันจะกระจายอยู่ใน AC หลายข้อและเขียนต่างกันทุกที่
dev อ่านแล้วไม่รู้ว่า "เหมือนหรือต่าง" อาจ implement ไม่สอดคล้องกัน
แยกแล้ว AC อ้างถึง BR เดียวกัน — implement ครั้งเดียว test ครั้งเดียว

---

## ความสัมพันธ์ระหว่าง AC กับ BR — ไม่ใช่ 1:1 เสมอ

```
แบบที่ 1 — 1 AC : 1 BR
AC: "admin เห็นแค่ post ของ community ที่ assigned"
→ BR-01: admin can only manage assigned communities

แบบที่ 2 — 1 AC : หลาย BR
AC: "post card แสดง author name, reaction count, community name"
→ BR-03: count format ใช้ UIKIT format
→ BR-07: soft deleted author ใช้ placeholder
→ BR-01: แสดงแค่ community ที่ assigned
สัญญาณ: AC เดียวที่อธิบาย behavior หลายอย่างพร้อมกัน มักซ่อน BR มากกว่าหนึ่ง

แบบที่ 3 — หลาย AC : 1 BR ← นี่คือสิ่งที่ extraction ต้องหาให้เจอ
UC7 AC: "เห็นแค่ post ของ community ที่ assigned"
UC8 AC: "เห็นแค่ pending post ของ community ที่ assigned"
UC10 AC: "จัดการ action ได้เฉพาะ community ที่ assigned"
→ ทั้งสามใช้ BR-01 เดียวกัน
```

**กฎตัดสิน:**
ถ้า AC เดียวอธิบาย behavior หลายอย่างพร้อมกัน → อาจซ่อน BR หลายข้อ
ถ้า AC แคบและเจาะจง → มักมี BR เดียว
ถ้า logic เดิมซ้ำในหลาย story → BR เดียวที่ต้อง consolidate

---

## เครื่องมือหลัก — "Why" จาก Phase 1.1

BR extraction ใช้ "Pain & Consequence Analysis" จาก phase-1.1 เป็น trigger

**วิธีใช้:** อ่าน AC แต่ละข้อแล้วถามว่า
"ทำไม behavior นี้ถึงต้องเป็นแบบนี้?"
"ถ้า implement ต่างออกไปจะกระทบอะไร?"

คำตอบที่เป็น **กฎที่จริงในทุก context** = Business Rule
คำตอบที่เป็น **เหตุผลเฉพาะ scenario** = อยู่ใน AC ต่อไป

```
ตัวอย่าง:
AC: "reaction count แสดงเป็น 1.2K"
ถาม Why: "ทำไมต้องแสดงแบบนี้?"
→ "เพราะ UIKIT กำหนด count format ไว้ทั้ง platform"
→ กฎนี้จริงในทุก count ทุก screen = Business Rule

AC: "admin เห็น empty state เมื่อไม่มี post"
ถาม Why: "ทำไมต้องแสดง empty state?"
→ "เพราะ UX ต้องการ feedback เมื่อ list ว่าง"
→ นี่คือ UI behavior เฉพาะ scenario ไม่ใช่ BR ที่ใช้ข้าม context
```

---

## 4 ประเภทของ Business Rule

จัดประเภทก่อนเขียนเพื่อให้รู้ว่า subject และ condition ควรเป็นอะไร

### ประเภท 1 — Permission / Authorization

ใครทำอะไรได้ ในขอบเขตไหน

```
สัญญาณใน AC: "admin ที่มี X permission เท่านั้น", "เฉพาะ role Y"

ตัวอย่าง:
BR-01: An admin can only view and manage content from communities
       they are assigned to, across all content views.
BR-10: Only admins with "Can manage posts & comments" permission
       can approve or decline pending posts.
```

### ประเภท 2 — Constraint / Limit

ขีดจำกัดเชิงปริมาณ เวลา หรือ format ที่เปลี่ยนไม่ได้

```
สัญญาณใน AC: "สูงสุด X", "ไม่เกิน Y", "อย่างน้อย Z"

ตัวอย่าง:
BR-02: Posts are sorted by created date in descending order by default.
BR-11: A scheduled post can be set at most 30 days in advance.
```

### ประเภท 3 — Computation / Display Format

วิธีคำนวณหรือแสดงผลที่ใช้สม่ำเสมอทั้ง system

```
สัญญาณใน AC: "แสดงตาม format X", "คำนวณจาก Y"

ตัวอย่าง:
BR-03: Counts (reactions, comments) follow UIKIT display format:
       1–999 → exact number
       1,000–999,999 → "X.XK" (e.g. 1.2K, 350.6K)
       1,000,000+ → "X.XM" (e.g. 1.2M)
```

### ประเภท 4 — State / Lifecycle

เงื่อนไขการเปลี่ยน state หรือ behavior ตาม lifecycle ของ object

```
สัญญาณใน AC: "ถ้า X ถูกลบ", "หลัง Y เกิดขึ้น", "เมื่อ Z อยู่ใน state นั้น"

ตัวอย่าง:
BR-07: When a post's author is soft-deleted, the post remains visible
       in the feed with a deleted-author placeholder — it must not
       disappear or render as broken.
BR-08: A hard-deleted post must not appear in any feed —
       no card, no placeholder, no trace.
```

---

## รูปแบบการเขียน BR ที่ใช้ได้จริง

```
BR-[เลข]: [subject] [must/must not/can/cannot] [condition]
           [ขอบเขต — across all / within / only when]
```

**กฎการเขียน:**
- ใช้ภาษา statement ไม่ใช่ scenario ("An admin can only..." ไม่ใช่ "When admin views...")
- ไม่ผูกกับ UI element — พูดถึง logic ไม่ใช่ปุ่มหรือหน้าจอ
- หนึ่ง BR หนึ่งกฎ ถ้ามีหลาย condition ให้แตก BR
- ให้เลขอ้างอิงเพื่อให้ AC อ้างถึงได้ [BR-XX]
- ระบุ scope ให้ชัด — กฎนี้ใช้กับทั้ง platform หรือเฉพาะ feature?

**ข้อผิดพลาดที่พบบ่อย:**
```
ผิด — เขียน behavior แทน rule:
BR-9: Refresh to see the latest post on the feed.
→ นี่คือ instruction ให้ user ไม่ใช่ rule ของระบบ

ถูก:
BR-09: The mobile console feed does not support real-time updates.
       Content changes are reflected only upon manual or triggered refresh.

ผิด — subject ไม่แม่น:
BR-8: The post from hard deleted author will not be displayed.
→ "hard deleted author" ต่างจาก "hard deleted post" — คนละ object

ถูก:
BR-08: A hard-deleted post must not appear in any feed —
       no card, no placeholder, no trace.
```

---

## Workflow ทีละขั้น

### Step 1 — รวม AC ทั้งหมดของ story ไว้ตรงหน้า

อ่านแล้วถามทุกข้อว่า "ทำไม behavior นี้ถึงเป็นแบบนี้?"

### Step 2 — แยกตามประเภท

จัด AC ที่ได้คำตอบเป็น "กฎที่จริงข้าม context" ออกเป็น 4 ประเภท
permission / constraint / computation / state

### Step 3 — เขียน BR ด้วยรูปแบบ

```
BR-[เลข]: [subject] [must/must not/can] [condition] [scope]
```

### Step 4 — มองหา BR ที่ซ้ำกันข้าม story

เทียบกับ BR จาก story อื่นใน epic เดียวกัน
ถ้า logic เดียวกัน → merge เป็น BR เดียว อย่าให้มีสอง BR ที่พูดถึงสิ่งเดียวกัน

### Step 5 — เชื่อม BR กลับเข้า AC

```
AC ที่อ้าง BR:
Given the admin views the Pending tab
When the page loads
Then only posts from communities the admin manages are shown [BR-01]
  AND counts display in UIKIT format [BR-03]
```

---

## Output format

เมื่อใช้ skill นี้กับ story ให้ produce output 3 ส่วน

**ส่วนที่ 1 — BR ที่พบ จัดตามประเภท**
แสดงให้เห็นว่าแต่ละ BR มาจาก AC ข้อไหน และเป็นประเภทอะไร

**ส่วนที่ 2 — BR ที่อาจซ้ำกับ story อื่น**
flag ว่า BR ไหนน่าจะ exist ใน story อื่นด้วย — ต้อง consolidate

**ส่วนที่ 3 — AC ที่เชื่อม BR แล้ว**
เขียน AC เดิมใหม่โดยมี [BR-XX] อ้างอิงในส่วนที่เกี่ยวข้อง

---

## Checklist ก่อน finalize BR

- [ ] แต่ละ BR เป็น statement ของกฎ ไม่ใช่ scenario
- [ ] subject ของ BR แม่น — "post ถูกลบ" ต่างจาก "author ถูกลบ"
- [ ] scope ระบุชัด — ใช้กับทั้ง platform หรือเฉพาะ feature?
- [ ] ไม่มี BR สองข้อที่พูดถึงสิ่งเดียวกัน
- [ ] AC ทุกข้อที่ใช้ logic เดียวกันอ้างถึง BR เดียวกัน
- [ ] BR ที่เกี่ยวกับ UI element → ตรวจว่าจริงๆ เป็น BR หรือแค่ AC detail
