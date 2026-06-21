---
name: meeting-mode
description: >
  Real-time conversational interrogation ระหว่าง meeting กับ PM
  ไม่ใช่ pipeline — ไม่มี phases ไม่มี output file ไม่มี completion gate
  พิมพ์ requirement มา → ได้คำถามกลับทันที พร้อม gaps และ PM challenge phrases
  Trigger: "meeting mode" หรือ "โหมดประชุม"
  ออก: "end meeting" หรือ "โหมดออก"
---

# meeting-mode — Real-time PM Interrogation

---

## Entry

เมื่อ trigger ทันที ไม่มี preamble ไม่มีการ announce ว่า "กำลังอ่าน skills":

```
🎯 Meeting Mode — พร้อมแล้ว
paste requirement หรือ AC จาก PM ได้เลย
พิมพ์ "end meeting" เมื่อต้องการออก
```

---

## เมื่อได้รับ requirement/AC text

อ่านแล้วทำ 4 ส่วนนี้ทันที เรียงลำดับนี้เสมอ:

---

### ส่วนที่ 1 — คำถามสำหรับ PM ตอนนี้

ใช้ mental model จาก `phase-1.1` (Who/What/Why) แต่ปรับ format ให้กระชับ ใช้ได้ทันทีในการประชุม

**รูปแบบ:** numbered, conversational, ภาษาที่ PM จะไม่รู้สึกว่าถูกจับผิด

```
คำถามสำหรับ PM ตอนนี้:

1. [Who] ...
2. [Who] ...
3. [What] ...
4. [Why] ...
```

**หมายเหตุ:** ไม่ใช่ format observation+consequence+question (นั่นคือ async format สำหรับเขียนลงใน AC)
ในประชุมใช้ประโยคสั้น ถามตรง ๆ

---

### ส่วนที่ 2 — Gaps ที่เห็น

bullet สั้น ๆ ว่าขาดอะไรใน requirement นี้

```
Gaps ที่เห็น:
• Given ไม่ระบุ permission tier ของ actor
• Then บอกแค่ "is processed" ไม่รู้ว่า state เปลี่ยนอะไร
• ไม่มี error state เลย
```

---

### ส่วนที่ 3 — Silent actors ที่ PM ลืม

ถ้ามี actor ที่ได้รับผลกระทบแต่ไม่ถูกพูดถึงในข้อความที่ paste มา

```
Silent actors ที่น่าจะลืม:
• [actor] — ได้รับผลกระทบตรงนี้แต่ไม่มีใน requirement
```

ถ้าไม่มี → ข้ามส่วนนี้

---

### ส่วนที่ 4 — State machine ช่องโหว่

ถ้า requirement พูดถึง state หรือ action ที่เกี่ยวกับ object ใด แล้วมี transition ที่ไม่ครบ

```
State machine ช่องโหว่:
• [object] มี state X แล้วจะเกิดอะไรถ้า [condition]?
• ไม่ชัดว่า state กลับไปได้ไหมถ้า [scenario]
```

ถ้าไม่มี → ข้ามส่วนนี้

---

## PM Challenge Patterns

ใช้ตอนที่ PM ให้คำตอบที่ไม่ครบหรือคลุมเครือ เลือก pattern ที่เหมาะกับสถานการณ์:

**เมื่อ PM พูดถึงเฉพาะ happy path:**
> "Happy path ครอบคลุมแล้ว แต่ถ้า network ล้มตอน [action] เราจะ handle หรือปล่อยให้ fail เงียบ ๆ?"

**เมื่อ PM ลืม silent actor:**
> "[Actor] จะรู้ว่า [event] เกิดขึ้นได้ยังไง ถ้าไม่มี notification หรือ state update?"

**เมื่อ PM ตอบกำกวม:**
> "ถ้าผมเข้าใจถูก คุณหมายความว่า [X] — แปลว่า [Y] อยู่นอก scope หรือแค่ยังไม่ได้พูดถึง?"

**เมื่อมี concurrent scenario:**
> "คุณบอกว่า state เป็น [X] — ถ้ามีสองคนทำ [action] พร้อมกันจะเกิดอะไร ใครชนะ?"

**เมื่อต้องการ business goal:**
> "feature นี้วัด success ยังไง — มี metric ไหนที่บอกได้ว่ามันทำงานถูก?"

**เมื่อ PM ตอบสั้นเกิน:**
> "ถ้า implement แบบนั้นแล้ว [actor] ที่อยู่ใน [context] จะ experience ยังไง — ยังโอเคไหม?"

---

## Conversation state

Track ใน context ระหว่าง meeting (ไม่ใช่ file) ว่า:
- Requirements ที่พูดถึงแล้ว: list สั้น ๆ
- Gaps ที่ identify ได้: running list
- คำถามที่ยิงไปแล้ว + ตอบหรือยัง
- สิ่งที่ยัง PENDING

---

## Exit — "end meeting" หรือ "โหมดออก"

แสดง Meeting Summary ทันที:

```
📋 Meeting Summary
─────────────────────────────────────────────

✅ Confirmed decisions:
• [requirement/decision ที่ PM ตอบชัดแล้ว]

⚠️ ยัง PENDING (ต้องได้คำตอบก่อน Sprint):
• [item] — suggested owner: PM / dev / design
• [item] — suggested owner: PM

─────────────────────────────────────────────
→ Next step:
  พอได้คำตอบ PENDING แล้ว:
  • รัน "วิเคราะห์ PDT-XXXX" เพื่อ enrich AC (Workflow A)
  • รัน "สร้าง story JSON PDT-XXXX" เมื่อ clarification ครบ (Workflow B)
```

---

## สิ่งที่ไม่ควรทำใน Meeting Mode

- ห้ามรัน phase pipeline — นั่นคือ Workflow A/B/C ซึ่งใช้หลัง meeting
- ห้ามเขียน output file ระหว่าง meeting mode
- ห้ามใช้ format observation+consequence+question — นั่น async format ไม่ใช่ meeting format
- ห้าม announce "กำลังอ่าน skills" — ทำทุกอย่างเบื้องหลัง แสดงเฉพาะ output
