---
name: phase-1-1-requirement-interrogation
description: 'ใช้ skill นี้เมื่อต้องการวิเคราะห์ requirement ที่ได้รับมาก่อนเริ่ม implement หรือ เขียน test case — ไม่ว่าจะเป็น requirement จาก PM, ลูกค้า, หรือ Jira story Skill นี้ช่วยตั้งคำถาม Who/What/Why อย่างมีโครงสร้าง โดยใช้ Relationship Map สำหรับ Who, State Machine สำหรับ What, และ Pain & Consequence Analysis สำหรับ Why Trigger เมื่อ: ได้รับ requirement ใหม่, กำลัง refinement session, ต้องการหา gap ใน AC, หรือต้องการตรวจสอบว่า story พร้อม implement หรือยัง'
---

# Requirement Interrogation

วิเคราะห์ requirement ที่ได้รับมาให้ครอบคลุมก่อนที่ทีมจะเริ่ม implement
โดยใช้ mental model 3 ชุดเพื่อถามคำถามที่ถูกทิศทางในแต่ละมิติ

## Artifacts
- **Consumes:** raw requirement (Jira story / PRD / PM draft)
- **Produces:** Relationship Map (Who) · State Machine (What) · Pain&Consequence "Why"
- **Called by:** process Layer 1 · STEP1 (Understand). artifact ที่ผลิตถูก reuse โดย 1-2, 1-3, 1-4, 2-2, 2-3, 2-6 — ดู `process/README.md` (reuse map)

> Skill นี้เป็น pure capability — ลำดับ/gate/การ loop อยู่ที่ `process/` ไม่ใช่ในนี้

---

## หลักการพื้นฐาน

Who, What, Why ไม่ใช่หัวข้อ — มันคือ **มุมมองการวิเคราะห์คนละชุดกัน**
แต่ละชุดใช้ mental model ที่ต่างกัน และต้องการทักษะการคิดที่ต่างกัน

| คำถาม | Mental model | เครื่องมือในหัว | สิ่งที่ค้นหา |
|---|---|---|---|
| Who | Actor & Relationship | Relationship map | ใครเกี่ยวข้อง และเกี่ยวข้องอย่างไร |
| What | State & Transition | State machine | object เปลี่ยน state ได้อย่างไร |
| Why | Pain & Consequence | "ถ้าไม่มี..." / "ถ้า implement ผิด..." | business risk ที่ซ่อนอยู่ |

---

## Step 1 · Who — วาด Relationship Map

**หลักการ:** ทุก feature มี actor มากกว่าหนึ่งคนเสมอ
คนที่มองแค่ผิวๆ จะนึกถึง actor หลักคนเดียว
BA+QA ต้องลาก relationship map ก่อนตั้งคำถาม

### วิธีวาด Relationship Map

1. วาง object หลักของ feature ไว้ตรงกลาง เช่น `pending post`
2. ระบุทุก actor ที่ interact กับ object นั้น ทั้งทางตรงและทางอ้อม
3. ระบุ relationship ระหว่าง actor กับ object เช่น creates, approves, receives notification
4. มองหา **concurrent actors** — actor ที่ทำ action เดียวกันพร้อมกันได้
5. มองหา **silent actors** — actor ที่ไม่ได้อยู่หน้าจอแต่ได้รับผลกระทบ

```
ตัวอย่าง: pending post feature

post owner → [pending post] ← admin A (mobile)
                  ↑
             admin B (desktop) ← concurrent
                  ↑
              system (auto-rules, timeout)
                  ↑
           super admin (can override?)
```

### Checklist Who

- [ ] ใครเป็น actor หลักที่ trigger action?
- [ ] ใครได้รับผลกระทบโดยตรงจาก action นั้น?
- [ ] ใครได้รับผลกระทบโดยอ้อม (notification, count, state change)?
- [ ] มี concurrent actors ที่ทำ action เดียวกันพร้อมกันได้ไหม? ใครชนะ?
- [ ] permission แตกต่างกันอย่างไรในแต่ละ actor?
- [ ] มี actor ที่ถูกลบ/deactivate ระหว่าง session ได้ไหม?
- [ ] actor ที่เป็นเจ้าของ object มีสิทธิพิเศษอะไร หรือถูกจำกัดอะไร?

---

## Step 2 · What — วาด State Machine

**หลักการ:** ทุก object ใน software มี state เสมอ
คนที่ถามแค่ "feature ทำอะไรได้บ้าง" จะพลาด edge case เกือบทั้งหมด
BA+QA ต้องวาด state machine ก่อนถามคำถาม

### วิธีวาด State Machine

1. ระบุ object หลักของ feature เช่น `post`, `comment`, `user`
2. ระบุ state ทั้งหมดที่ object นั้นเป็นได้
3. วาด transition ระหว่าง state พร้อม trigger ที่ทำให้เกิด transition
4. มองหา **invalid transitions** — อะไรที่ไม่ควรเกิดแต่อาจเกิดได้
5. มองหา **external transitions** — state เปลี่ยนจากภายนอก session ปัจจุบัน

```
ตัวอย่าง: post state machine

[Draft] → [Pending] → [Approved] → [Published]
                ↓                       ↓
           [Declined]              [Deleted]
                ↓
           [Re-submit?]

คำถามที่ต้องถาม:
- Approved → Pending ได้ไหม? (ถ้า community setting เปลี่ยน)
- Published → Pending ได้ไหม? (ถ้ามีการ report)
- Deleted เป็น soft หรือ hard delete?
```

### Checklist What

- [ ] object นี้มี state อะไรได้บ้างตลอด lifecycle?
- [ ] แต่ละ transition มี trigger อะไร และมีเงื่อนไขอะไร?
- [ ] state ไหนที่ย้อนกลับได้? ย้อนกลับได้เมื่อไหร่?
- [ ] ถ้า state เปลี่ยนจาก external (คนอื่น / system) จะเกิดอะไรกับ UI?
- [ ] มี data ที่เปลี่ยนตาม state ไหม เช่น count, badge, timestamp?
- [ ] มี constraint เชิง business ไหม เช่น max limit, timeout, quota?
- [ ] ถ้า setting ของ parent (community, network) เปลี่ยน state ของ object จะเป็นอย่างไร?

---

## Step 3 · Why — วิเคราะห์ Pain และ Consequence

**หลักการ:** Why ที่ดีไม่ใช่ "feature นี้มีประโยชน์อะไร"
แต่คือ "pain อะไรที่มันแก้ และจะเกิดอะไรถ้า implement ผิดทิศ"
คำตอบของ Why จะบอก scope, priority, และ design decision ที่ต้องชัดเจน

### สองแบบของ Why ที่ต้องถาม

**Why แบบ Pain** — ถามว่า "ถ้าไม่มีฟีเจอร์นี้ เจ็บปวดตรงไหน?"
คำตอบจะบอก use case จริง, context การใช้งาน, และ priority ของ feature

```
ตัวอย่าง:
ถาม: "ทำไมต้อง approve บนมือถือ ทั้งๆ ที่ desktop ทำได้?"
Pain: admin อยู่ในงาน event ไม่มี laptop — pending post ค้างนาน
      community เงียบ engagement หาย
Implication: latency คือ pain หลัก → design ต้องเน้น speed ไม่ใช่ feature richness
```

**Why แบบ Consequence** — ถามว่า "ถ้า implement ผิดแบบ จะกระทบ business ยังไง?"
คำตอบจะบอก decision ที่ต้อง explicit ไม่ใช่ assume

```
ตัวอย่าง:
ถาม: "ถ้า approve แล้ว post delay 5 นาทีค่อย publish — acceptable ไหม?"
Consequence: ถ้า use case คือ live event → ไม่ acceptable
             ถ้า use case คือ content planning → อาจ acceptable
Implication: ต้องระบุ publish timing ใน AC ให้ชัด ไม่ใช่ assume "ทันที"
```

### Checklist Why

- [ ] ถ้าไม่มีฟีเจอร์นี้ ใครเจ็บปวดตรงไหน?
- [ ] context ที่ user ใช้ฟีเจอร์นี้คืออะไร — เวลา, สถานที่, อุปกรณ์?
- [ ] ฟีเจอร์นี้ต่างจาก solution เดิมอย่างไร และทำไมถึงต้องต่าง?
- [ ] ถ้า implement ผิดทิศ (เร็วเกิน/ช้าเกิน/ซับซ้อนเกิน) business เสียอะไร?
- [ ] success ของฟีเจอร์นี้วัดจากอะไร?
- [ ] มี assumption ที่ทีม assume ร่วมกันแต่ไม่เคยพูดออกมาชัดๆ ไหม?

---

## Step 4 · Gap Check ก่อนสรุป

หลังจากตั้งคำถามครบทั้ง 3 มิติแล้ว ให้ทำ gap check ด้วยคำถาม 3 ข้อนี้

**1. ยังมี actor ที่ไม่ได้ถามถึงไหม?**
ย้อนกลับไปดู relationship map — มี silent actor หรือ system actor ที่ลืมไป?

**2. ยังมี state transition ที่ไม่ได้ cover ไหม?**
ย้อนกลับไปดู state machine — มี path ที่วาดแล้วแต่ยังไม่ได้ตั้งคำถาม?

**3. Why ที่ตั้งไปมัน lead ไปถึง business decision ไหม?**
ถ้า Why ที่ตั้งยังจบแค่ "อธิบาย feature" แสดงว่ายังไม่ลึกพอ
ต้องต่อด้วย "แล้วถ้าเป็นแบบนั้น เราต้องตัดสินใจอะไร?"

---

## สัญญาณว่า Requirement ยังไม่พร้อม

requirement ที่ยังไม่พร้อม implement มักแสดงอาการเหล่านี้

- มี actor ใหม่โผล่ขึ้นมาเมื่อวาด relationship map แต่ไม่มีใน AC
- มี state transition ที่ไม่มีคำตอบว่าจะ handle อย่างไร
- Why ตอบได้แค่ "เพราะ PM บอก" หรือ "เพราะ competitor ทำ" โดยไม่มี pain ที่ชัดเจน
- มี concurrent scenario ที่ยังไม่ตกลงกันว่าใครชนะ
- มี assumption ที่ทุกคน assume แต่ไม่มีใครเขียนไว้ใน AC

เมื่อพบอาการเหล่านี้ ให้หยุดและ clarify ก่อน อย่า proceed ต่อ

---

## ตัวอย่างการใช้ skill นี้กับ Requirement จริง

**Input:** "เพิ่มฟีเจอร์ approve/decline pending posts บน mobile"

**Who — วาด Relationship Map:**
```
post owner → [pending post] ← admin (mobile)
                  ↑
             admin (desktop) ← concurrent
                  ↑
              system (timeout?)
```
คำถามที่ได้: permission tier ไหนที่ approve ได้?, self-approve ได้ไหม?,
ถ้า admin สองคน approve พร้อมกันใครชนะ?, admin ที่ถูก deactivate กลางคัน?

**What — วาด State Machine:**
```
[Pending] → [Approved] → [Published]
         ↓
      [Declined]
```
คำถามที่ได้: publish ทันทีไหม?, badge count sync real-time ไหม?,
ถ้า community setting เปลี่ยน pending post กลายเป็นอะไร?,
notification ไปหา post owner ไหม?

**Why — Pain & Consequence:**
คำถามที่ได้: ทำไม mobile แทน desktop? (pain = latency ใน field),
ถ้า delay 5 นาที acceptable ไหม? (consequence = depends on use case),
success วัดจาก? (approve rate? response time?)
