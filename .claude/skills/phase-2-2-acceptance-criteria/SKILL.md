---
name: phase-2-2-acceptance-criteria
description: 'ใช้ skill นี้เมื่อต้องเขียน Acceptance Criteria ใหม่ตั้งแต่ต้นสำหรับ User Story (ต่างจาก phase-1-3 ที่เติม AC ของ PM ที่มีอยู่แล้ว — skill นี้เขียนจากศูนย์) Skill นี้สอนโครงสร้าง Given-When-Then ที่ครบ สอนวิธีคิด 3 คำถามก่อนเขียน และสอนให้ครอบคลุม 4 ประเภท scenario เสมอ (default state, happy path, alternative/validation, error state) ไม่ใช่แค่ happy path Trigger เมื่อ: เขียน AC ใหม่สำหรับ story, story ที่มีแต่ happy path, ต้องการตรวจว่า AC ครอบคลุมทุก scenario type ไหม, หรือก่อนสร้าง test case'
---

# Acceptance Criteria — Given-When-Then

เขียน AC ตั้งแต่ต้นที่ implement และ test ได้ ครอบคลุมทุกประเภท scenario

---

## หลักการพื้นฐาน — AC คืออะไรจริงๆ

AC ไม่ใช่ "คำอธิบาย feature" — มันคือ **สัญญาที่วัดได้** ระหว่าง PM, dev, และ QA
ว่า "done" หมายความว่าอะไร

**กฎทดสอบ:** ถ้าเขียน AC แล้ว dev อ่านแล้วยังต้องถาม "แล้วถ้า... จะเกิดอะไร?"
แสดงว่า AC ยังไม่สมบูรณ์

> หมายเหตุ: skill นี้เน้นการเขียน AC จากศูนย์ ถ้าต้องการเติม AC ที่ PM
> เขียนมาแล้ว ให้ใช้ phase-1-3-happy-path-ac-enrichment ควบคู่กัน

---

## โครงสร้างที่ต้องครบ

```
Given  [role + permission]
       [state ของ object ก่อน action]
       [context / entry point]
When   [action + UI element ที่ชัดเจน]
Then   [primary outcome]
  AND  [side effect 1 — state อื่นที่เปลี่ยน]
  AND  [side effect 2 — data ที่เปลี่ยนตาม]
  AND  [UI feedback — สิ่งที่ user เห็น]
```

Then มักต้องการ AND หลายอัน เพราะ action เดียวมักทำให้เกิดหลายอย่างพร้อมกัน
ถ้า Then มีบรรทัดเดียว ให้สงสัยไว้ก่อนว่ายังไม่ครบ

---

## 3 คำถามก่อนเขียน AC ทุกข้อ

**1. "Setup ก่อน action คืออะไร?"** → Given
ระบุ role, permission, state ของ object, และ context ให้ครบ

**2. "User ทำอะไรกันแน่?"** → When
ต้องระบุถึงระดับ "แตะปุ่มไหนบนหน้าไหน" ไม่ใช่แค่ "กด submit"

**3. "เกิดอะไรทุกอย่างหลัง action?"** → Then
นึกถึงทุก state ที่เปลี่ยน ไม่ใช่แค่ผลลัพธ์หลัก — ใช้ State Machine ช่วย

---

## 4 ประเภท Scenario ที่ต้องเขียนครบ

AC ที่สมบูรณ์ของ feature หนึ่งต้องครอบคลุม 4 ประเภทนี้ ไม่ใช่แค่ happy path

### ประเภท 1 — Default state

ก่อนที่ user จะทำอะไรเลย หน้าจอแสดงอะไร

```
Given the admin navigates to the Pending tab
When the page loads
Then a loading indicator is shown
  AND no empty state is displayed until data returns
```

### ประเภท 2 — Happy path

ทุกอย่างถูกต้อง ผลลัพธ์ที่ควรได้

```
Given the admin has "Can manage posts & comments" permission
  AND the post is in pending state
When the admin taps Approve AND the request succeeds
Then the post is removed from the Pending tab
  AND the post appears in the Posted tab
  AND the badge count decrements by 1
  AND a success toast is shown
```

### ประเภท 3 — Alternative / Validation

input ไม่ valid หรือเงื่อนไขไม่ครบ แต่ system ยังรู้ว่าเกิดอะไร

```
Given another admin already approved this post
When the current admin taps Approve on the same post
Then a toast "Post has been reviewed" is shown
  AND no duplicate action is performed
```

### ประเภท 4 — Error state

network, permission, หรือ system ล้ม

```
Given the admin has permission AND post is pending
When the admin taps Approve AND the network request fails
Then an error toast is shown
  AND the post remains in the Pending tab — state unchanged
  AND the Approve button returns to enabled state
```

> สำหรับการขุดหา edge case และ error case ที่ลึกกว่านี้ด้วย 4 mental models
> ให้ใช้ phase-1-4-edge-and-error-ac ต่อยอด

---

## วิธีเขียนจากศูนย์ — 3 ขั้น

### ขั้นที่ 1 — เขียน happy path ก่อน

ถามว่า "ถ้าทุกอย่าง perfect จะเกิดอะไร?" แล้วเขียน Given-When-Then ให้ครบโครงสร้าง

### ขั้นที่ 2 — เช็ค Then ด้วย State Machine

วาด state machine ในหัวว่า action นี้เปลี่ยน state อะไรบ้าง เช็คว่า Then ครอบคลุมครบ

```
post status:      pending → published     ✓ อยู่ใน Then?
pending list:     มี → ไม่มี             ✓ อยู่ใน Then?
badge count:      N → N-1                ✓ อยู่ใน Then?
posted list:      ไม่มี → มี             ✗ ขาด → เพิ่ม
UI feedback:      ไม่มี → toast          ✗ ขาด → เพิ่ม
```

### ขั้นที่ 3 — เติมอีก 3 ประเภท scenario

จาก happy path ที่ได้ เติม default state, alternative/validation, และ error state
ให้ครบ 4 ประเภท

---

## Rule of Thumb

feature หนึ่งอย่างควรมี AC อย่างน้อย 3–5 ข้อเสมอ

```
1   default state
1–2 happy path
1   alternative / validation
1–2 error state
```

ถ้ามีแค่ข้อเดียว = คนเขียนคิดแค่ happy path แล้วถือว่าจบ

---

## สัญญาณว่า AC ยังไม่ดีพอ

- Then บอกแค่ "is approved" โดยไม่บอกว่าเกิดอะไรบน UI → Then ไม่สมบูรณ์
- Given ไม่มี permission หรือ state ของ object → dev ต้อง assume เอง
- When บอกแค่ "กด submit" ไม่บอกว่ากดปุ่มไหนบนหน้าไหน → QA เดา test เอง
- ไม่มี error scenario เลย → dev จะไม่ handle error
- มี AC แค่ข้อเดียว (happy path) → ขาด 3 ประเภทที่เหลือ

---

## คำเตือนเรื่อง wording

- ใช้คำที่ verify ได้ ห้ามใช้คำกว้างเช่น "is processed", "works correctly", "good experience"
- ทุก Then ต้องเป็นสิ่งที่ test ได้จาก UI หรือ API response
- ถ้า outcome มีลำดับ เช่น loading แล้วค่อย success ให้แยกเป็นคนละ scenario
- subject ของ Then ต้องชัด — "the post" ไม่ใช่ "it"

---

## Output format

เมื่อใช้ skill นี้กับ story ให้ produce output ตามนี้

1. ระบุ object หลักและ state machine สั้นๆ
2. เขียน AC ครบ 4 ประเภท scenario (default / happy / alternative / error)
3. ทุก AC ใช้โครงสร้าง Given-When-Then เต็ม
4. ถ้ามีจุดที่ยังต้อง clarify กับ PM ให้ mark [PENDING] ไว้
5. ตรวจ rule of thumb — มีอย่างน้อย 3–5 AC ไหม
