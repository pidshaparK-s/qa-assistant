---
name: phase-2.5-prioritization
description: >
  ใช้ skill นี้เมื่อต้องการจัดลำดับ requirement ก่อน sprint planning
  หรือเมื่อต้องการ estimate effort จากมุม QA เพื่อ inform การตัดสินใจของ PM
  Skill นี้ครอบคลุม MoSCoW (ตัดสินว่าอะไรต้องมีใน release นี้),
  Impact vs Effort matrix (เรียงลำดับภายในกลุ่มที่ตกลงว่าต้องทำ),
  และ QA Effort Estimation framework ที่คิดจาก AC, BR, integration, และ regression risk
  Trigger เมื่อ: ก่อน sprint planning, PM บอกว่าทุกอย่างสำคัญเท่ากัน,
  หรือต้องการ estimate ว่า feature ไหน test ง่าย/ยากกว่ากัน
---

# Prioritization + QA Effort Estimation

จัดลำดับ requirement ก่อน sprint และ estimate effort จากมุม QA

---

## ทำไมต้อง Prioritize

ใน sprint จริงเวลาและ resource มีจำกัดเสมอ ถ้าไม่ prioritize จะเกิด 3 ปัญหา

```
1. Build ทุกอย่างพร้อมกันแล้วไม่เสร็จสักอย่าง
2. Build สิ่งที่ไม่ได้สำคัญก่อน ของจำเป็นไม่ทันปล่อย
3. PM และ dev เข้าใจ priority ต่างกัน ไม่มีใคร align กัน
```

**BA+QA ไม่ได้ prioritize แทน PM** แต่ช่วย 3 จุด:
- Flag เมื่อ Must มีเยอะเกินไป
- Estimate effort จากมุม QA ที่ PM และ dev มักไม่เห็น
- เชื่อม priority กับ AC coverage ที่ต้องเตรียม

---

## Technique 1 — MoSCoW

ใช้สำหรับ **ตัดสินว่า requirement ไหนต้องมีใน release นี้**
เหมาะกับ feature planning ก่อน sprint เริ่ม

### 4 ระดับ

**Must have** — ถ้าไม่มีนี้ product ใช้งานไม่ได้เลยหรือ launch ไม่ได้

```
วิธีทดสอบ: "ถ้าไม่มีนี้ release ได้ไหม?"
ถ้าตอบว่า "ได้ แต่ไม่ดี" = Should ไม่ใช่ Must
```

**Should have** — สำคัญมากแต่ยังมี workaround ชั่วคราวได้

```
วิธีทดสอบ: "มี workaround อื่นไหมถ้ายังไม่มีสิ่งนี้?"
ถ้าตอบว่า "มี แต่ไม่สะดวก" = Should
```

**Could have** — nice to have ตัดออกได้ถ้า scope ตึง

```
วิธีทดสอบ: "ถ้าตัดออก user จะเจ็บปวดไหม?"
ถ้าตอบว่า "ไม่มาก" = Could
```

**Won't have (this time)** — acknowledge ว่ารู้ว่ามี แต่ defer ออกไป release หน้า
ระบุให้ชัดใน AC ว่า "not supported in this release" เพื่อไม่ให้ dev assume

### กฎสำคัญของ MoSCoW

```
Must ต้องไม่เกิน 60% ของ scope ทั้งหมด
ถ้า Must มากเกินไป = BA/PM estimate ไม่ดี
หรือ = สิ่งที่เรียกว่า Must จริงๆ แค่ Should
```

### เชื่อม MoSCoW กับ AC Coverage

```
Must  → ต้องมี AC ครบทุก scenario (happy/alternative/error/edge)
Should → AC หลักก่อน edge case ค่อย follow-up
Could  → happy path AC อย่างเดียวก็พอ
Won't  → document ใน AC ว่า "[Out of scope for this release]"
```

---

## Technique 2 — Impact vs Effort Matrix

ใช้สำหรับ **เรียงลำดับภายใน Must/Should** — ว่าจะ build อะไรก่อน
เหมาะหลังจากใช้ MoSCoW แยก scope แล้ว

```
              Low Effort            High Effort
          ┌─────────────────────┬─────────────────────┐
High      │  Quick Wins         │  Major Projects     │
Impact    │  ทำก่อนเลย          │  plan ดีๆ แล้วทำ   │
          ├─────────────────────┼─────────────────────┤
Low       │  Fill-ins           │  Thankless Tasks    │
Impact    │  ทำถ้ามีเวลา        │  หลีกเลี่ยง         │
          │                     │  หรือ re-scope      │
          └─────────────────────┴─────────────────────┘
```

### ใช้สองเทคนิคร่วมกัน

```
Step 1 — MoSCoW ก่อน:
แยกว่าอะไร Must / Should / Could / Won't
→ ได้ scope ของ release นี้

Step 2 — Impact vs Effort กับ Must+Should:
เรียงลำดับว่าจะ build อะไรก่อน
→ ได้ sprint order

ผลลัพธ์:
Sprint 1: Must + Quick Wins
Sprint 2: Must + Major Projects ที่เหลือ
Sprint 3: Should ที่ยัง defer ได้
```

---

## QA Effort Estimation

QA estimate ต่างจาก dev — dev นับว่า code เยอะแค่ไหน
แต่ QA นับว่า "ต้อง verify อะไรบ้างและยากแค่ไหน"

QA ดู 3 ชั้นพร้อมกัน:

```
UC  → บอกว่า scope กว้างแค่ไหน
AC  → บอกว่ามี scenario กี่ข้อที่ต้อง test
BR  → บอกว่า logic ซับซ้อนแค่ไหน และ reuse ข้าม UC ไหม
```

### 5 Criteria สำหรับ QA Estimate

**Criteria 1 — จำนวนและประเภทของ AC**

```
Happy path AC   → test ง่าย setup ตรงไปตรงมา       weight: 1
Alternative AC  → ต้องสร้าง invalid input           weight: 1.5
Error AC        → ต้องจำลอง network fail, timeout   weight: 2
Edge case AC    → ต้องสร้าง environment พิเศษ       weight: 2.5

ยิ่งมี edge/error AC มาก effort ยิ่งสูง
```

**Criteria 2 — จำนวน BR และความซับซ้อน**

```
BR น้อย + ง่าย       → effort ต่ำ
BR มาก + ซับซ้อน     → effort สูง
BR ที่ reuse ข้าม UC → ต้อง regression test ทุก UC ที่ใช้ BR นั้น

ตัวอย่าง:
BR-01 (permission) ปรากฏใน UC7, UC8, UC9, UC10, UC12, UC13
→ ถ้า implementation ของ BR-01 เปลี่ยน ต้อง test ทุก UC ที่เกี่ยวข้อง
```

**Criteria 3 — Dependency และ Integration point**

```
Internal only (call API ตัวเอง) → effort ปกติ
Third-party integration         → effort สูงขึ้น เพราะ mock ยาก
  Google SSO → ต้องมี test account, token expiry, revoke scenarios
Multi-platform (iOS + Android)  → effort คูณสอง
Real device required            → setup time สูง
```

**Criteria 4 — Test environment complexity**

บางกรณี setup environment นานกว่า test จริงด้วยซ้ำ

```
ง่าย: happy path สร้าง data แล้ว test ได้เลย
ยาก: ต้องจำลองเงื่อนไขพิเศษ เช่น
  - Offline mode → ต้องจำลอง network drop
  - Concurrent action → ต้องเปิดสอง session พร้อมกัน
  - Soft/hard delete → ต้องมี data ใน state นั้น
  - Permission revoke mid-session → ต้องมี admin account พิเศษ
```

**Criteria 5 — Regression risk**

feature ใหม่กระทบ feature เดิมแค่ไหน

```
ต่ำ: feature ใหม่ standalone ไม่ touch core logic
สูง: แตะ BR ที่ share ข้าม UC หลายอัน เช่น
  - แก้ permission logic → regression ทุก UC ที่ require permission
  - แก้ count format BR-03 → regression ทุกที่ที่มี count display
  - แก้ sorting → regression ทุก list view
```

---

## QA Effort Score — Relative Estimation

ใช้ score นี้เปรียบเทียบ relative effort ระหว่าง feature ไม่ใช่ตัวเลขสัมบูรณ์

```
Criteria                       Low (1)     Medium (2)    High (3)
─────────────────────────────────────────────────────────────────
จำนวน AC                       1-3         4-7           8+
ประเภท AC ที่ยากสุด            happy       alternative   edge/error
จำนวน BR ที่ relate            0-1         2-3           4+
BR reuse ข้าม UC ไหม           ไม่         บางส่วน       มาก
Dependency / Integration       none        internal API  third-party
Environment complexity         simple      data setup    device/network
Regression risk                ต่ำ         กลาง          สูง
─────────────────────────────────────────────────────────────────
รวม:  7-10  = Low effort
      11-15 = Medium effort
      16-21 = High effort
```

### ตัวอย่างจริง — UC8 Approve/Decline Post

```
จำนวน AC: 8 AC                               → score 2
ประเภทที่ยากสุด: edge case (concurrent)       → score 3
BR ที่ relate: BR-01, BR-03, BR-04, BR-07     → score 3
BR reuse ข้าม UC: BR-01 ใช้ทุก UC            → score 3
Dependency: internal API + real device        → score 2
Environment: concurrent session จำลองยาก     → score 3
Regression: BR-01 กระทบทุก UC               → score 3

รวม: 19 → High effort

แปลว่า: ถ้า PM บอกว่า UC8 "ง่าย" QA ต้องอธิบายว่า
มี 8 scenario + concurrent edge case +
regression risk ข้าม UC ทั้งหมด ใช้เวลาจริงกว่าที่คิด
```

---

## วิธีสื่อสาร QA Effort กับ PM

```
แบบที่ PM ไม่เข้าใจ:
"UC8 effort สูง ต้องใช้เวลา 5 วัน"

แบบที่ PM เข้าใจและ respect:
"UC8 มี 8 AC รวม edge case ที่ต้องจำลอง concurrent session
 และ BR-01 ที่ใช้ ถ้าแก้อะไรใน permission logic ต้อง regression
 ทุก UC ใน epic — estimate 5 วัน test รวม regression"
```

**Pattern ที่ใช้ได้เสมอ:**
```
"feature นี้มี [X] AC รวม [Y] edge case..."  → บอก scope จริง
"BR-[N] ที่ใช้ใน feature นี้ยังใช้ใน [UC...]..."  → บอก regression risk
"ถ้าต้องการลด effort ตัด [edge case/Could AC] ออกได้..."  → ให้ choice
```

---

## Mistake ที่พบบ่อย

**Must inflation** — ทุกอย่างเป็น Must เพราะกลัวถูกตัด
แก้ด้วย: "ถ้าไม่มีนี้ user เจ็บปวดยังไงจริงๆ?"

**Effort inflation โดย PM** — PM มักประเมิน effort ต่ำเกินไป
เพราะไม่เห็น environment setup, regression risk, และ edge case
แก้ด้วย: อธิบาย AC count + BR reuse + environment complexity

**Impact assumption** — assume ว่า feature ที่ PM excited คือ high impact เสมอ
แก้ด้วย: validate ด้วย usage data, user research, หรือ support tickets

---

## Output format

เมื่อใช้ skill นี้กับ epic หรือ sprint backlog ให้ produce output 3 ส่วน

**ส่วนที่ 1 — MoSCoW classification**
จัด feature/UC แต่ละอันเข้า Must/Should/Could/Won't พร้อมเหตุผลสั้นๆ

**ส่วนที่ 2 — Impact vs Effort mapping**
วาง Must+Should ลงใน 4 quadrant พร้อมระบุว่าอะไรคือ Quick Wins

**ส่วนที่ 3 — QA Effort Score**
score ทีละ criteria สำหรับแต่ละ feature พร้อม highlight จุดที่ PM อาจ underestimate
