---
name: phase-1-2-three-layer-analysis
description: 'ใช้ skill นี้เมื่อได้รับ requirement ที่ต้องการแยกให้ออกว่าอะไรคือ Business Goal, User Need, และ System Behavior — และเมื่อต้องการตรวจสอบว่า requirement ที่ได้มา ครอบคลุมครบทั้ง 3 ชั้นหรือไม่ Skill นี้ไม่ใช่แค่ framework listing แต่รวม manual review step ที่ช่วยตั้งคำถามกลับไปหา PM เมื่อพบความคลุมเครือ หรือ assumption ที่ไม่มีใครเขียนออกมา Trigger เมื่อ: ได้รับ requirement ใหม่จาก PM หรือลูกค้า, story ดู implement ได้ แต่รู้สึกว่า "ยังมีอะไรขาด", AC ครบแต่ไม่แน่ใจว่า build ถูก goal หรือเปล่า'
---

# Three-Layer Requirement Analysis

แยก requirement ออกเป็น 3 ชั้น และทำ manual review เพื่อหา gap
ที่นำไปสู่คำถามที่ตั้งกลับไปหา PM ได้อย่างมีเหตุผล

## Artifacts
- **Consumes:** requirement + Relationship Map (จาก 1-1)
- **Produces:** 3-Layer trace (Business Goal ← User Need ← System Behavior) · gap questions (→ Clarification Register)
- **Called by:** process Layer 1 · STEP1. User Need ที่ผลิตถูก reuse โดย 2-6, 2-4

> Readiness เป็น **process-level gate** (ดู `process/README.md` → Gate catalog) — skill นี้แค่ผลิต gap questions

---

## ทำไมต้องแยก 3 ชั้น?

PM มักส่ง requirement มาในชั้นที่ผิด — ส่วนใหญ่คือ System Behavior
โดยข้าม Business Goal และ User Need ไป ทำให้ทีม build ได้ถูก spec
แต่ผิด goal และเมื่อ feature ไม่ได้ผล ไม่มีใครรู้ว่าต้องเปลี่ยนอะไร

```
Business Goal   "ทำแล้วได้อะไร?" ในระดับ business — วัดได้เป็น metric/outcome
      ↓
User Need       "user เจ็บปวดตรงไหน หรืออยากได้อะไร?" — ยังไม่มี solution
      ↓
System Behavior "system ทำอะไร เมื่อไหร่ ภายใต้เงื่อนไขอะไร?" — implement และ test ได้
```

**กฎสำคัญ:** ทุก System Behavior ต้องลาก line กลับขึ้นไปถึง User Need ได้
และทุก User Need ต้องลาก line กลับขึ้นไปถึง Business Goal ได้
ถ้าลากไม่ได้ = requirement ยังไม่สมบูรณ์

---

## Step 1 · ระบุชั้นของ requirement ที่ได้รับมา

อ่าน requirement แล้วถามตัวเองว่าประโยคนั้นตอบคำถามไหน

| ถ้าตอบได้ว่า... | ชั้นนั้นคือ |
|---|---|
| "ทำแล้ว business ได้อะไร?" | Business Goal |
| "user เจ็บปวดตรงไหน / อยากได้อะไร?" | User Need |
| "system ทำอะไร เมื่อไหร่ ภายใต้เงื่อนไขอะไร?" | System Behavior |
| "จะ build / implement ยังไง?" | Solution — ไม่ใช่ requirement |

**สัญญาณเตือนว่าอยู่ผิดชั้น:**
- พูดถึง platform หรือ technology เช่น "mobile", "email", "dashboard" → มักเป็น solution ไม่ใช่ goal
- พูดถึง feature โดยตรง เช่น "ทำ approve button" → System Behavior ไม่ใช่ goal
- พูดถึง capability เช่น "admin สามารถ..." → อาจเป็น Need หรือ Behavior แต่ยังไม่ใช่ Goal

---

## Step 2 · ขุดหา Business Goal ด้วย "Why ladder"

ถ้า requirement ที่ได้มาอยู่ชั้น System Behavior หรือ User Need
ให้ใช้ **Why Ladder** — ถาม "เพื่ออะไร?" ซ้ำๆ จนได้ metric หรือ outcome

```
ตัวอย่าง:

"ทำ approve/decline บนมือถือ"
      ↓ เพื่ออะไร?
"admin จัดการได้ทุกที่ ไม่ต้องรอถึง desktop"
      ↓ เพื่ออะไร?
"response time เร็วขึ้น pending post ไม่ค้างนาน"
      ↓ เพื่ออะไร?
"community มี content flow ที่ดี engagement ไม่ drop"
      ↑ นี่คือ Business Goal
```

**Business Goal ที่ถูกต้องจะ:**
- วัดได้เป็น metric เช่น response time, engagement rate, churn rate
- ยังคงเป็น goal เดิมแม้จะเปลี่ยน solution เช่น ถ้าเปลี่ยนจาก mobile เป็น SMS แล้ว goal ยังใช้ได้ = goal จริง
- ไม่ได้พูดถึง platform, feature, หรือ technology เลย

---

## Step 3 · ขยาย User Need ให้ครบทุก actor

User Need มักมีมากกว่าหนึ่งข้อ และมักมี **silent user** ที่ถูกลืม

**วิธีหา User Need ทั้งหมด:**
1. ดึง actor ทุกคนจาก Relationship Map (จาก Phase 1.1)
2. ถามสำหรับแต่ละ actor ว่า "เขาต้องการอะไรจาก feature นี้?"
3. มองหา Need ที่แตกต่างกันจริงๆ — ไม่ใช่แค่พูดเรื่องเดิมต่างคำ

```
ตัวอย่าง UC8:

Actor: admin (mobile)
Need: จัดการ pending post ได้โดยไม่ต้องอยู่หน้าคอม ✓

Actor: admin (desktop, concurrent)
Need: รู้ว่ามี pending รออยู่เท่าไหร่โดยไม่ต้อง refresh เอง ✓

Actor: post owner  ← silent user ที่ลืมบ่อย
Need: รู้ผลของ post ตัวเองโดยเร็ว ไม่ต้องมาเช็คเอง ✗ (ไม่มีใน AC)
```

---

## Step 4 · ลาก Line จาก Need → Behavior

สำหรับแต่ละ User Need ให้ถามว่า "System Behavior อะไรที่ทำให้ Need นี้ได้รับการ address?"
และตรวจสอบว่า AC ที่มีอยู่ cover ครบไหม

```
Need: admin รู้ว่ามี pending รออยู่เท่าไหร่
   → Behavior: badge count บน Pending tab แสดงจำนวน ✓ (มีใน AC)
   → Behavior: badge decrement ทันทีเมื่อ action ✓ (มีใน AC)

Need: post owner รู้ผลเร็ว
   → Behavior: notification ไปหา post owner เมื่อ approved/declined ✗ (ไม่มีใน AC)
   → Behavior: post owner เห็น status change บน post ตัวเอง ✗ (ไม่มีใน AC)
```

**Gap ที่พบ = สิ่งที่ต้องถามกลับไปหา PM**

---

## Step 5 · Manual Review — ตั้งคำถามกลับหา PM

นี่คือหัวใจของ skill นี้ — gap ที่พบใน Step 4 ต้องถูกแปลงเป็นคำถามที่มีเหตุผล
ไม่ใช่แค่ "ขาดอะไร" แต่ต้องบอกได้ว่า "ถ้าไม่ชัดตรงนี้จะกระทบอะไร"

### 5 ประเภทของ Gap ที่ต้องถาม

**ประเภท 1 — Missing Business Goal**
เมื่อ requirement มีแต่ System Behavior โดยไม่รู้ว่า goal คืออะไร

```
สัญญาณ: "ทำ X ได้" โดยไม่บอกว่าทำไป
คำถามที่ตั้งกลับ: "feature นี้ตั้งใจให้ช่วย metric ไหนของ business?
                   เราจะรู้ได้อย่างไรว่า feature นี้ประสบความสำเร็จ?"
```

**ประเภท 2 — Ambiguous User Need**
เมื่อ Need ที่เขียนมามี solution แฝงอยู่แล้ว ทำให้ไม่รู้ว่า Need จริงๆ คืออะไร

```
สัญญาณ: "user ต้องการ mobile app" แทนที่จะเป็น "user ต้องการจัดการได้ทุกที่"
คำถามที่ตั้งกลับ: "ถ้าเราทำ web responsive แทน native app
                   use case ที่ลูกค้าบอกมายังได้รับการ address ไหม?"
```

**ประเภท 3 — Silent User Need**
เมื่อมี actor ที่ได้รับผลกระทบแต่ไม่มี Need หรือ Behavior รองรับ

```
สัญญาณ: พบ actor ใหม่จาก Relationship Map แต่ไม่มีใน AC เลย
คำถามที่ตั้งกลับ: "post owner จะรู้ได้ยังไงว่า post ตัวเองถูก approve หรือ decline?
                   ถ้าไม่มี notification ลูกค้า expect ว่า user จะรู้ได้ยังไง?"
```

**ประเภท 4 — Orphaned System Behavior**
เมื่อ System Behavior บาง item ลาก line กลับขึ้นไปหา Need หรือ Goal ไม่ได้

```
สัญญาณ: มี AC ที่เขียนไว้ แต่อ่านแล้วไม่รู้ว่ามันแก้ pain อะไร
คำถามที่ตั้งกลับ: "AC ข้อนี้ exist เพื่อ support use case ไหน?
                   ถ้า user ไม่ได้ใช้ feature นี้ เขาจะ miss อะไร?"
```

**ประเภท 5 — Assumed Context**
เมื่อ requirement assume บริบทบางอย่างที่ไม่มีใครพูดออกมา

```
สัญญาณ: requirement ดูสมเหตุสมผล แต่ถ้า environment เปลี่ยน มันอาจไม่ work
คำถามที่ตั้งกลับ: "ถ้า community setting เปลี่ยนจาก require approval เป็น open post
                   pending posts ที่มีอยู่แล้วจะเกิดอะไรขึ้น?"
```

### วิธีตั้งคำถามกลับที่ดี

คำถามที่ดีต้องมีสองส่วนเสมอ

1. **บอก observation** — "ใน AC ไม่มีการระบุว่า..."
2. **บอก consequence** — "ถ้าไม่ชัดตรงนี้ dev อาจ implement แบบ A หรือ B ซึ่งจะกระทบ..."

```
ตัวอย่างที่ไม่ดี:
"post owner จะได้รับ notification ไหม?"  ← ถามตรงแต่ไม่บอกว่าทำไมต้องถาม

ตัวอย่างที่ดี:
"AC ไม่ได้ระบุว่า post owner จะได้รับ notification เมื่อถูก approve/decline
ถ้าไม่ระบุ dev อาจ implement แบบไม่ส่ง notification เลย ซึ่งอาจกระทบ
experience ของ user ที่รอผล — ลูกค้า expect behavior แบบไหนตรงนี้?"
```

---

## Step 6 · Readiness Check (reference)

> เกณฑ์ด้านล่างเป็น **นิยามของ "ready"** ที่ **process ใช้เป็น Readiness gate** (`process/README.md` → Gate catalog)
> การ enforce gate เป็นหน้าที่ของ process layer — skill นี้แค่ผลิต gap questions

เกณฑ์ที่ process ใช้ตรวจว่า requirement พร้อม implement หรือยัง

**พร้อม implement เมื่อ:**
- [ ] Business Goal ชัดเจน วัดได้ และไม่ใช่ solution
- [ ] User Need ครอบคลุมทุก actor รวมถึง silent users
- [ ] ทุก User Need มี System Behavior รองรับอย่างน้อยหนึ่งข้อ
- [ ] ทุก System Behavior ลาก line กลับขึ้นไปหา Need ได้
- [ ] Gap ทุกข้อที่พบได้รับคำตอบจาก PM แล้ว หรือ explicit accept ว่า out of scope
- [ ] Assumption ที่ซ่อนอยู่ถูกเขียนออกมาเป็น constraint หรือ AC แล้ว

**ยังไม่พร้อม implement เมื่อ:**
- Business Goal ยังเป็น solution เช่น "ทำ mobile app"
- มี silent user ที่ยังไม่มี Need/Behavior รองรับ
- มี System Behavior ที่ลาก line กลับไม่ได้เลย
- Gap ที่พบยังไม่ได้รับคำตอบ และทีมยัง assume เอาเอง

---

## ตัวอย่างการใช้ skill นี้กับ UC8 จริง

**Input จาก PM:**
> "Admin ต้องดู pending posts ได้จากมือถือ กด Approve หรือ Decline ได้เลย"

**Step 1 — ชั้นของ requirement:**
System Behavior — พูดถึงสิ่งที่ system ทำบน platform ที่ระบุ

**Step 2 — Why Ladder:**
```
"ทำ approve/decline บนมือถือ"
→ เพื่ออะไร? admin จัดการได้โดยไม่ต้องอยู่หน้า desktop
→ เพื่ออะไร? pending post ไม่ค้างนาน community ยังมี content flow
→ เพื่ออะไร? engagement ไม่ drop, community staff ดู responsive
↑ Business Goal: community staff จัดการ community ได้ทุกที่
  ทำให้ response time เร็วและ community quality คงที่
```

**Step 3 — User Need ทุก actor:**
```
Admin (mobile)     → จัดการ pending ได้โดยไม่ต้องอยู่หน้าคอม
Admin (concurrent) → รู้จำนวน pending โดยไม่ต้อง refresh เอง
Post owner         → รู้ผลของ post ตัวเองโดยเร็ว  ← silent, ขาดใน AC
```

**Step 4 — Gap ที่พบ:**
```
Post owner Need ไม่มี System Behavior รองรับเลยใน AC
```

**Step 5 — คำถามกลับหา PM:**
> "AC ไม่ได้ระบุว่า post owner จะได้รับ notification เมื่อ post ถูก approve หรือ
> decline ถ้าไม่ระบุ dev จะไม่ implement notification ให้ post owner เลย
> ซึ่งอาจทำให้ user ต้องเข้ามาเช็คเองว่า post ตัวเองถูก approve หรือยัง
> ลูกค้า expect ให้มี notification กลับไปหา post owner ไหม?
> และถ้ามี จะส่งผ่าน channel ไหน — in-app, push notification, หรือทั้งคู่?"

**Step 6 — Readiness:**
ยังไม่พร้อม — Gap ของ post owner notification ยังไม่มีคำตอบ
