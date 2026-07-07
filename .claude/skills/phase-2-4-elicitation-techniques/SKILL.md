---
name: phase-2-4-elicitation-techniques
description: 'ใช้ skill นี้เมื่อต้องการดึง requirement ที่ซ่อนอยู่ออกมาจาก stakeholder หรือ PM ก่อนเขียน User Story หรือ AC — เพราะคนส่วนใหญ่พูดสิ่งที่ตัวเองคิดอยู่ ไม่ใช่สิ่งที่จำเป็นต้องรู้ Skill นี้ครอบคลุม 5 techniques: Stakeholder Interview, 5 Whys, Context Diagram, Observation, Document Analysis พร้อมวิธีเลือก technique ที่เหมาะกับสถานการณ์ และวิธีพูดกับ PM ที่ไม่ค่อยเปิดรับ Trigger เมื่อ: requirement ที่ได้มาไม่ชัดหรือดูตื้นเกินไป, ไม่เข้าใจ business context, stakeholder พูดถึง solution โดยไม่บอก problem, หรือ requirement ขัดแย้งกันระหว่างคน'
---

# Elicitation Techniques

ดึง requirement จริงออกมาจาก stakeholder — ไม่ใช่แค่สิ่งที่พวกเขาบอกว่าต้องการ

---

## หลักการพื้นฐาน — ทำไม Elicitation ถึงยาก

ปัญหาไม่ได้อยู่ที่ "ถามอะไร" แต่อยู่ที่ **คนที่ถูกถามมักไม่รู้คำตอบ** หรือรู้แต่บอกไม่ถูก

```
สิ่งที่ stakeholder พูด:
"อยากได้ระบบที่ง่ายขึ้น"

สิ่งที่จริงๆ ต้องการ:
"ตอนนี้ต้องคลิก 7 ครั้งเพื่อ approve post หนึ่งอัน อยากให้เหลือ 2 ครั้ง"
```

งาน elicitation คือการขุดจาก "อยากได้ระบบที่ง่าย"
ไปถึง "2 คลิก" โดยไม่ทำให้ stakeholder รู้สึกว่าถูก interrogate

**สาเหตุที่ stakeholder พูดไม่ตรง:**
- Curse of knowledge — รู้เรื่องมากเกินจนอธิบายไม่ถูกว่าอะไรซับซ้อน
- Solution bias — นึกถึง solution ก่อนที่จะ articulate problem
- Social desirability — บอกสิ่งที่คิดว่าคนถามอยากได้ยิน
- Unknown unknowns — ไม่รู้ตัวว่าไม่รู้อะไร

---

## 5 Elicitation Techniques

### Technique 1 — Stakeholder Interview

เทคนิคพื้นฐานที่ใช้บ่อยที่สุด แต่คนส่วนใหญ่ทำผิดวิธี

**หลักการสำคัญ: ถามปัญหา ไม่ถาม solution**

```
ผิด (ถาม solution):
"อยากได้ mobile app ไหม?"
→ stakeholder ตอบ "ใช่" แต่ไม่รู้ว่าทำไม

ถูก (ถามปัญหา):
"ตอนนี้ถ้าอยากจัดการ post นอกออฟฟิศ ทำยังไง?"
→ stakeholder อธิบาย pain จริงๆ ออกมา
```

**โครงสร้าง interview ที่ดี:**

```
Phase 1 — Context setting (2-3 นาที)
"วันทำงานปกติเป็นยังไง? ใช้เวลาส่วนไหนกับ community มากที่สุด?"
→ เป้าหมาย: เข้าใจ workflow จริงก่อนถาม

Phase 2 — Pain discovery (10-15 นาที)
"อะไรที่ทำให้งานช้าที่สุดในตอนนี้?"
"เคยเจอสถานการณ์ไหนที่รู้สึกว่าทำไม่ได้ทั้งที่ควรทำได้?"
"ถ้าแก้ได้อย่างเดียว จะแก้อะไรก่อน?"
→ เป้าหมาย: หา pain ที่ใหญ่ที่สุด ไม่ใช่ wishlist

Phase 3 — Validation (5-10 นาที)
ทวน requirement ที่ได้ยินกลับให้ฟัง
"ที่เข้าใจคือ... ถูกไหม?"
→ เป้าหมาย: ยืนยันว่าเข้าใจตรงกัน

Phase 4 — Prioritization (5 นาที)
"ถ้ามีเวลาทำได้อย่างเดียว อยากได้อะไรก่อน?"
→ เป้าหมาย: รู้ priority จริงๆ ไม่ใช่ทุกอย่างสำคัญเท่ากัน
```

**คำถามที่ห้ามถาม:**

```
"ต้องการ feature นี้ไหม?"
→ คนตอบ "ใช่" เสมอถ้าได้ฟรี

"feature นี้ดีไหม?"
→ คนตอบ "ดี" เสมอถ้าคุณดูตั้งใจ

"อยากได้อะไรเพิ่ม?"
→ คนจะบอก wishlist ไม่ใช่ priority
```

---

### Technique 2 — 5 Whys

ถาม "ทำไม" ซ้ำๆ จนถึง root cause จริง
ใช้ร่วมกับ Pain & Consequence จาก phase-1-1 เสมอ

```
เริ่มจาก: "อยากได้ approve post บน mobile"

Why 1: "ทำไมต้องเป็น mobile?"
→ "เพราะไม่ได้อยู่หน้าคอมตลอด"

Why 2: "ทำไมต้อง approve เร็ว?"
→ "เพราะ post รอ approve นานทำให้ community เงียบ"

Why 3: "ทำไม community เงียบถึงเป็นปัญหา?"
→ "เพราะ engagement ลดลง KPI ไม่ผ่าน"

Root cause: admin response time ช้า กระทบ community engagement KPI
Solution จริง: mobile console ที่ approve ได้เร็ว ไม่ใช่แค่ "อยากได้ mobile app"
```

**กฎการใช้ 5 Whys:**
- หยุดเมื่อได้ **metric หรือ business outcome** ไม่ใช่หยุดเมื่อถามครบ 5 ครั้ง
- ถ้าคำตอบ Why เป็น "ก็แค่อยากได้" หรือ "ก็มันดีกว่า" = ยังไม่ถึง root cause
- ถ้า Why ที่ n นำไปสู่ "แต่ทำไมถึงต้องเป็นแบบนั้น?" = ยังขุดต่อได้

---

### Technique 3 — Context Diagram

วาดก่อนคุยเสมอเพื่อให้เห็น boundary และ external dependencies
ก่อน interview จะได้รู้ว่า "ยังขาด actor ไหน" และ "dependency ไหนที่ไม่ได้ถาม"

```
วาด 3 อย่าง:
1. System ที่จะ build (วงกลมตรงกลาง)
2. External actors ทั้งหมดที่ interact
3. ทิศทาง data/action ที่ไหลระหว่างกัน

ตัวอย่าง Mobile Console:

[Admin] ──sends action──→ [Mobile Console] ──calls──→ [API Server]
                                ↑                           ↓
                          [PM dashboard]           [Community Database]
                                                          ↓
                                                   [Post Owner]
                                                          ↓
                                                 [Push Notification]
```

**สิ่งที่ diagram ช่วยบอก:**
- มี actor ไหนที่ยังไม่ได้คุยด้วย? (เช่น Post Owner ที่เป็น silent actor)
- มี dependency ไหนที่อาจกระทบ scope? (เช่น Push Notification ต้อง integrate อะไร?)
- boundary ของ system อยู่ที่ไหน? อะไรอยู่ใน out of scope?

---

### Technique 4 — Observation (Job Shadowing)

ดู workflow จริงแทนที่จะ assume
เพราะ **สิ่งที่คนทำจริงกับสิ่งที่คนบอกว่าทำมักต่างกันเสมอ**

```
สิ่งที่ stakeholder บอก:
"approve post ก็แค่กดปุ่มเดียว ง่ายมาก"

สิ่งที่เห็นจากการ observe จริง:
1. เปิด browser
2. navigate ไป console
3. login ใหม่เพราะ session หมด
4. หา community ที่ต้องการ
5. filter pending
6. อ่าน post
7. กด approve
→ จริงๆ คือ 7 steps ไม่ใช่ "กดปุ่มเดียว"
```

**วิธี observe อย่างมีประสิทธิภาพ:**
- ดูเงียบๆ ก่อน อย่าแนะนำระหว่าง observe
- จดทุก step ที่เห็น ไม่ว่าจะดูเล็กน้อยแค่ไหน
- สังเกต workaround ที่คนทำ — มักบอกถึง pain ที่ไม่ได้พูดถึง
- ถามหลัง observe เสร็จว่า "ทำแบบนี้เพราะอะไร?"

**ใช้เมื่อ:**
stakeholder บอกว่า "ง่ายมาก" แต่รู้สึกว่าจริงๆ ไม่น่าง่าย
หรือมี workflow ที่ซับซ้อนและยากจะ describe ด้วยคำพูด

---

### Technique 5 — Document Analysis

อ่านเอกสารที่มีอยู่แล้วก่อนถาม เพื่อไม่เสีย interview time
กับข้อมูลที่หาเองได้

```
ควรอ่านก่อน interview:
- PRD ที่มีอยู่        → เข้าใจ context พื้นฐาน
- Existing AC/story    → รู้ว่าทีมคิดอะไรไว้แล้ว
- Bug reports          → เข้าใจ pain points ที่เกิดจริง
- Support tickets      → เห็น user problem ที่ real
- Analytics/usage data → รู้ว่า feature ไหนใช้จริง ไหนไม่ใช้
```

**ผลที่ได้จาก Document Analysis:**
ก่อน interview จะมี hypothesis เกี่ยวกับ pain points ที่ต้องการ validate
แทนที่จะเข้า interview มือเปล่าและถามกว้างๆ

---

## เลือก Technique ให้ถูกสถานการณ์

| สถานการณ์ | Technique ที่เหมาะ |
|---|---|
| ไม่รู้อะไรเลยเกี่ยวกับ domain | Document analysis → Interview |
| requirement ตื้น ไม่รู้ว่าทำไป | 5 Whys |
| ไม่เข้าใจ system boundary หรือ actor | Context diagram |
| stakeholder บอกว่า "ง่าย" แต่สงสัย | Observation |
| requirement ขัดแย้งกันระหว่างคน | Interview แยกกันก่อน แล้วค่อย reconcile |
| มี story แต่รู้สึกว่าขาด context | Document analysis + 5 Whys |

**กฎทั่วไป:** ใช้ Document Analysis ก่อนเสมอ แล้วค่อย Interview
ใช้ 5 Whys ระหว่าง Interview เมื่อได้คำตอบที่ดูตื้นเกินไป

---

## วิธีพูดกับ PM ที่ไม่ค่อยเปิดรับ

framing ที่ถูกต้องคือ **"ช่วย implement ให้ถูก"** ไม่ใช่ **"ตรวจงาน"**

```
แบบที่ทำให้ PM defensive:
"Story นี้ไม่ครบ ขาด error case"

แบบที่ทำให้ PM เปิดรับ:
"อยากยืนยันความเข้าใจก่อน sprint เริ่ม —
 ตอนที่ network ล้มระหว่าง approve dev จะ handle ยังไง
 อยากได้ให้ post กลับมา pending ไหม หรือ fail silently?"
```

คำถามแบบที่สองให้ choice แทนที่จะ expose gap
ทำให้ PM รู้สึกว่าถูกขอความคิดเห็น ไม่ใช่ถูกจับผิด

**Pattern ที่ใช้ได้เสมอ:**
```
"อยากยืนยันความเข้าใจก่อน..."  ← framing ว่าเป็นการ clarify
"ถ้า X เกิดขึ้น ต้องการให้ Y หรือ Z?"  ← ให้ choice
"เพื่อที่ dev จะได้ implement ได้ถูกตั้งแต่แรก"  ← บอก benefit
```

---

## Output format

เมื่อใช้ skill นี้ ให้ produce output 2 ส่วน

**ส่วนที่ 1 — Elicitation plan**
ระบุว่าจะใช้ technique ไหน กับ stakeholder ไหน และต้องการหาข้อมูลอะไร

**ส่วนที่ 2 — คำถามที่จะถาม**
เรียงตาม phase interview (context → pain → validation → priority)
แต่ละคำถามต้องถามปัญหา ไม่ถาม solution

---

## Checklist ก่อนเข้า Meeting / Interview

- [ ] อ่าน PRD และ story ที่มีแล้วทั้งหมด (Document analysis)
- [ ] วาด Context diagram เพื่อหา actor ที่อาจขาด
- [ ] รวม gap ที่พบจาก Phase 1.1–1.4 เป็น hypothesis
- [ ] เตรียมคำถาม Pain discovery ไม่ใช่ Solution discovery
- [ ] เตรียม 5 Whys สำหรับทุก requirement ที่ดูตื้นเกินไป
- [ ] frame คำถามเป็น "ช่วย clarify" ไม่ใช่ "ตรวจงาน"
- [ ] หลัง meeting — เขียน clarification questions ที่ยังไม่ได้ตอบ
  ด้วย Observation + Consequence + Question (phase-1-2)
