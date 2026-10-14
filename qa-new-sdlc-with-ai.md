# QA in the New SDLC with AI

## ความเห็นต่อแนวคิด New SDLC

ผมเห็นด้วยกับแก่นของบทความค่อนข้างมาก แต่มีจุดหนึ่งที่อยากขยายให้ชัดขึ้น:

> **AI ไม่ได้ทำให้ QA หายไป แต่ทำให้ “QA แบบรอรับของไป test ตอนท้าย” เริ่มไม่เวิร์ก**

AI ทำให้ Implementation เร็วขึ้นมาก แต่คอขวดจะย้ายไปอยู่ที่ **Specification → Review → Testing/Evaluation** เพราะ AI สามารถสร้าง User Story, Test Case และ Code ได้เร็วมาก แต่ไม่ได้แปลว่าสิ่งที่สร้างนั้น “ถูก”

ปัญหาสำคัญคือ defect จำนวนหนึ่งไม่ได้เกิดจาก code แต่เกิดจาก requirement/specification ที่ผิดตั้งแต่ต้น

```text
Business requirement ผิด
        ↓
Specification ผิด
        ↓
AI generate code ได้ถูกต้องตาม specification
        ↓
Code ทำงาน "ถูก"
        ↓
แต่ product ผิด
```

ดังนั้น Quality ต้องถูกจัดการตั้งแต่ต้น lifecycle

---

# 1. จาก SDLC แบบเดิมสู่ New SDLC

## SDLC แบบเดิม

```text
Requirement
    ↓
Design
    ↓
Development
    ↓
QA
    ↓
Deploy
    ↓
Production
```

QA มักจะเข้มข้นตรงช่วง Development → QA

```text
Requirement → Design → Development → [ QA ] → Deploy
                                      ↑
                                จุดที่ QA รับงาน
```

ถ้า Developer + AI สามารถ generate implementation ได้เร็วขึ้นหลายเท่า แต่ QA ยังทำงานแบบเดิม QA จะกลายเป็น bottleneck

---

# 2. QA ควรอยู่ตรงไหนใน New SDLC?

คำตอบคือ:

> **QA ไม่ควรอยู่จุดเดียวอีกต่อไป แต่ควรกระจายตัวเป็น Quality Engineering ตลอด lifecycle**

```text
                 ┌───────────────────────────┐
                 │       REQUIREMENT         │
                 └─────────────┬─────────────┘
                               │
                         QA / QE Review
                               │
                               ▼
                 ┌───────────────────────────┐
                 │    SPECIFICATION / PRD    │
                 └─────────────┬─────────────┘
                               │
                      AI generates
                stories / scenarios / tests
                               │
                         QA validates
                               │
                               ▼
                 ┌───────────────────────────┐
                 │     DESIGN / ARCHITECTURE │
                 └─────────────┬─────────────┘
                               │
                       Quality / Risk review
                               │
                               ▼
                 ┌───────────────────────────┐
                 │       IMPLEMENTATION      │
                 │       Human + AI          │
                 └─────────────┬─────────────┘
                               │
                    AI generates tests
                               │
                       QA validates
                               │
                               ▼
                 ┌───────────────────────────┐
                 │      TEST / EVALUATE      │
                 └─────────────┬─────────────┘
                               │
                     Automation / AI
                               │
                               ▼
                 ┌───────────────────────────┐
                 │       DEPLOY / PROD       │
                 └─────────────┬─────────────┘
                               │
                      Observability
                      Quality monitoring
                               │
                               └──────► Feedback
```

สรุปสั้น ๆ:

> **QA ต้องขยับไปทางซ้าย และขยายไปทางขวา**

ไม่ใช่แค่เพิ่ม automation ตรงกลาง

---

# 3. QA ตั้งแต่ Requirement

นี่คือจุดที่สำคัญที่สุดจุดหนึ่ง

สมมติ Product Manager บอก AI:

> “สร้างระบบให้ user สามารถ tag product ใน post ได้”

AI สามารถสร้าง:

- User Story
- Acceptance Criteria
- Test Cases
- API
- UI
- Automation

ได้หมด

แต่ใครเป็นคนกำหนดว่า:

- Product tag ได้สูงสุด 5 ตัวหรือไม่?
- ถ้า product ถูก disable หลังจาก post ถูก publish แล้วต้องแสดงอะไร?
- User ที่ไม่มีสิทธิ์ขายสินค้าสามารถ tag ได้หรือไม่?
- Product ที่หมด stock สามารถ tag ได้หรือไม่?
- Error handling ต้องเป็นอย่างไร?

สิ่งเหล่านี้คือ **Business Context**

AI ไม่รู้เองทั้งหมด

ดังนั้น QA ควรเข้ามาทำ:

## QA → Requirement Quality

ตรวจสอบว่า:

- Requirement testable หรือไม่?
- Acceptance criteria complete หรือไม่?
- มี ambiguity หรือไม่?
- Missing negative cases หรือไม่?
- Business rules ครบหรือไม่?
- Boundary conditions คืออะไร?
- Permission / role มีอะไรบ้าง?
- Dependency คืออะไร?
- Failure behavior คืออะไร?
- Non-functional requirements มีหรือไม่?

ตรงนี้คือการทำ **Specification Testing**

---

# 4. AI สร้าง Test Case ได้ แล้ว QA ยังต้องเขียน Test Case หรือไม่?

ควรเปลี่ยนวิธีคิด

ไม่ควรให้ QA ใช้เวลาส่วนใหญ่กับการเขียน:

```text
TC001
TC002
TC003
...
TC157
```

ด้วยมือ

AI ทำงานนี้ได้เร็วกว่า

แต่ QA ควรทำ:

```text
          Requirement
               ↓
             AI
               ↓
       Generate scenarios
               ↓
             QA
       ┌───────┼────────┐
       ↓       ↓        ↓
   Validate  Challenge  Risk
       │       │        │
       └───────┼────────┘
               ↓
       Approved Test Model
               ↓
             AI
               ↓
      Generate Test Cases
               ↓
             QA
               ↓
          Automation
```

บทบาทจึงเปลี่ยนจาก:

> **Test Case Writer**

เป็น:

> **Test Strategy / Test Model Designer**

---

# 5. QA ต้องทำ AI Testing เพิ่มอีกชั้น

ถ้า Developer ใช้ AI generate code คำถามสำคัญคือ:

> **เราจะรู้ได้อย่างไรว่า AI generate code ถูก?**

จึงเกิด testing อย่างน้อย 2 layers

## Layer 1 — Test the Product

```text
AI-generated code
       ↓
Functional Testing
API Testing
UI Testing
Integration Testing
Performance
Security
```

## Layer 2 — Test the AI-generated Artifact

```text
AI output
   ↓
Specification compliance
Business rule compliance
Security
Reliability
Maintainability
Test coverage
Hallucination
Unintended behavior
```

เช่น AI generate test case มา 100 cases

ไม่ได้หมายความว่า:

> 100 test cases = good coverage

QA ต้องถามว่า:

> “100 test cases นี้ cover risk ที่สำคัญจริงหรือเปล่า?”

---

# 6. QA Automation จะเปลี่ยนอย่างไร?

## แบบเดิม

```text
Requirement
   ↓
QA writes test cases
   ↓
QA writes automation
   ↓
Run CI
   ↓
Report
```

## New SDLC

```text
PRD
 ↓
AI
 ↓
Generate
 ├── Test scenarios
 ├── Test cases
 ├── Automation
 └── Test data
       ↓
     QA validates
       ↓
   Automated Test Suite
       ↓
      CI/CD
       ↓
 ┌─────┴────────┐
 ↓              ↓
Pass           Fail
 ↓              ↓
Deploy       AI analysis
                 ↓
             Root cause
                 ↓
             Auto-heal?
                 ↓
              QA review
```

ดังนั้น Automation Engineer จะไม่ได้มีหน้าที่แค่:

> “เขียน Playwright/Appium script”

แต่จะกลายเป็นคนสร้าง:

> **Quality Automation System**

---

# 7. Agent ที่ควรเพิ่ม: Quality Gate Agent

จาก workflow ที่มี Story Generator, Test Scenario, Test Suite Generator และ Test Healer ผมคิดว่าควรมี Agent สำคัญเพิ่มอีกตัว:

## `quality-gate-agent`

วางไว้ก่อน Development

```text
PRD
 ↓
Quality Gate Agent
 ↓
"Requirement นี้พร้อมให้ AI coding หรือยัง?"
```

ตรวจเรื่อง:

- ambiguity
- missing acceptance criteria
- missing error scenarios
- missing boundary conditions
- missing NFR
- inconsistent business rules
- untestable requirements
- missing observability
- missing security considerations

เหตุผลสำคัญ:

> ถ้า input ห่วย AI + automation + 1,000 test cases ก็ยังผลิตของห่วยได้เร็วขึ้นเท่านั้น

AI เป็นเครื่องเร่ง ไม่ใช่เครื่องกรองขยะ

---

# 8. QA ใน New SDLC = 5 บทบาท

| Stage | QA / QE Role |
|---|---|
| Requirement | **Specification Quality** |
| Design | **Risk / Architecture Quality** |
| Implementation | **AI-generated Code/Test Review** |
| Testing | **Evaluation + Automation** |
| Production | **Quality Observability** |

และแต่ละช่วงใช้ AI ต่างกัน:

```text
Requirement
    ↓
AI: วิเคราะห์ ambiguity
QA: ตรวจ business correctness

Design
    ↓
AI: วิเคราะห์ scenario / risk
QA: challenge architecture

Implementation
    ↓
AI: generate code + tests
QA: validate behavior

Testing
    ↓
AI: execute / analyze / generate
QA: evaluate quality

Production
    ↓
AI: detect anomalies
QA: investigate quality signals
```

---

# 9. QA ในอนาคตไม่ใช่แค่ “คน Test”

เส้นทางสามารถเปลี่ยนจาก:

```text
QA Tester
   ↓
QA Engineer
   ↓
Automation Engineer
   ↓
Quality Engineer
   ↓
AI-Augmented Quality Engineer
   ↓
Quality Architect
```

สิ่งที่มีค่ามากขึ้นจะไม่ใช่:

> “เขียน automation ได้เร็วแค่ไหน”

แต่เป็น:

> **“ออกแบบระบบที่ทำให้ทีมสามารถรู้ได้เร็วว่า software ที่กำลังสร้างนั้นมีคุณภาพหรือไม่”**

นี่เป็น mindset ที่ต่างกันมาก

---

# 10. Architecture ที่น่าสนใจสำหรับ AI-Native QA

แนวคิดสามารถต่อยอดเป็น pipeline เดียว:

```text
                    PRD
                     │
                     ▼
             ┌───────────────┐
             │ Quality Gate  │
             │ Agent         │
             └───────┬───────┘
                     │
                     ▼
             ┌───────────────┐
             │ Story Agent   │
             └───────┬───────┘
                     │
                     ▼
             ┌───────────────┐
             │ Scenario Agent│
             └───────┬───────┘
                     │
                     ▼
             ┌───────────────┐
             │ Test Agent    │
             └───────┬───────┘
                     │
                     ▼
             ┌───────────────┐
             │ Automation    │
             │ Agent         │
             └───────┬───────┘
                     │
                     ▼
                   CI/CD
                     │
                     ▼
             ┌───────────────┐
             │ Test Results  │
             └───────┬───────┘
                     │
              ┌──────┴──────┐
              ▼             ▼
          Failure         Pass
              │             │
              ▼             ▼
        Test Healer      Deploy
              │
              ▼
          QA Review
```

---

# 11. สรุปความเห็น

ผมเห็นด้วยกับแนวคิด New SDLC ประมาณ **85–90%**

โดยเฉพาะประเด็น:

> AI ทำให้ implementation เร็วขึ้น แต่ bottleneck จะย้ายไปที่ specification, review และ evaluation

แต่ผมจะต่อยอดอีกขั้นว่า:

> **The New SDLC ไม่ได้ลดความสำคัญของ QA — มันบังคับให้ QA เลิกเป็นขั้นตอนหนึ่งใน SDLC แล้วกลายเป็น quality layer ที่ครอบทั้ง SDLC**

สำหรับ QA Automation Engineer จุดที่ควรลงทุนที่สุดจึงไม่ใช่:

> “ทำให้ AI เขียน Playwright ได้เก่งขึ้น”

แต่คือการสร้าง pipeline:

**PRD → Context → Risk → Scenario → Test → Automation → Evaluation → Quality Gate**

ถ้าทำสิ่งนี้ได้ คุณไม่ได้แค่ใช้ AI ช่วยทำงาน QA

แต่กำลังสร้าง:

> **AI-native QA Engineering Workflow**

ซึ่งมี leverage สูงกว่าการเป็นคนเขียน automation ได้เร็วเพียงอย่างเดียว
