---
name: phase-1.4-edge-and-error-ac
description: >
  ใช้ skill นี้หลังจากเขียน Happy Path AC แล้ว (phase-1.3) เมื่อต้องการ
  หา Edge Case และ Error Case ที่ยังขาดอยู่ใน story
  Skill นี้เน้นที่ "วิธีหา" ก่อน ไม่ใช่แค่ "วิธีเขียน" เพราะ Edge Case
  ไม่ได้โผล่ออกมาชัดเจนเหมือน Happy Path — ต้องใช้ mental model
  เพื่อขุดออกมาจาก boundary, environment, และ timing ของ system
  Trigger เมื่อ: เขียน Happy Path AC ครบแล้วแต่รู้สึกว่ายังไม่ครอบคลุม,
  ต้องการตรวจสอบ AC ก่อน sprint เริ่ม, หรือกำลังทำ gap analysis กับ story จริง
---

# Edge Case และ Error Case AC

หา Edge และ Error case ที่ซ่อนอยู่ใน requirement แล้วเขียนเป็น AC ที่ใช้ได้จริง

---

## ทำความเข้าใจ 3 มุมมองก่อน

มุมมองที่ถูกต้องในการมอง AC ทั้งหมดของ feature คือ

```
Success path    — ทุกอย่างเป็นไปตาม plan, input valid, environment ปกติ
    ↓
Alternative     — input ไม่ valid หรือ action ไม่สำเร็จ แต่ system รู้ว่าเกิดอะไร
    ↓
Edge            — สภาพแวดล้อมหรือ input ที่อยู่ขอบขีดจำกัด
                  คนปกติไม่ได้ตั้งใจทำ แต่เกิดขึ้นได้จริง
                  engineer ต้อง handle ไม่งั้น system พัง
```

**ความแตกต่างที่สำคัญ:**

Alternative ยังอยู่ใน "โลกที่ system ควบคุมได้" — เช่น password ผิด, field ว่าง
Edge อยู่ใน "โลกที่ environment ควบคุม" — เช่น network หาย, สองคนกดพร้อมกัน,
server ล่ม, permission เปลี่ยนกลางคัน, data corrupt

End user ไม่รู้ว่าทำไมมันพัง แต่ engineer ต้องรู้และ handle ทุก case

---

## ทำไม Edge ยากกว่า Error

**Error case** มักมี trigger ที่ชัด เช่น network ล้ม → แสดง error message
คนส่วนใหญ่นึกถึงได้ เพราะมันคือ "อะไรผิดพลาด"

**Edge case** ไม่มี trigger ที่ชัด เพราะมันคือ "ทุกอย่างถูก แต่ environment อยู่ที่ขอบ"
เช่น approve post ที่ 100 ในระบบที่รับได้ 100 — ถูกต้อง valid แต่อยู่ที่ขีดจำกัด
คนส่วนใหญ่ไม่นึกถึงเพราะไม่มี explicit "อะไรผิด"

---

## 4 Mental Models สำหรับหา Edge Case

### Model 1 — Boundary Analysis

ทุก field, limit, หรือ constraint ใน AC มี boundary เสมอ
Edge case ซ่อนอยู่ที่ขอบของ boundary ทุกแห่ง

```
วิธีใช้:
หา constraint ทุกอย่างใน story → ถามว่า "ถ้าอยู่พอดีขอบ จะเกิดอะไร?"

ตัวอย่าง UC8 — Pending posts:
  "badge count decrements by 1"
  → boundary: ถ้า count อยู่ที่ 1 แล้ว decline → count เป็น 0 → badge หาย ✓
  → boundary: ถ้า count เป็น 0 แล้วมี approve อีก (race condition) → เป็น -1?

ตัวอย่าง UC14 — Schedule post:
  "max 30 days in future"
  → boundary: schedule พอดีวันที่ 30 → ได้ ✓
  → boundary: schedule วันที่ 30 แต่ timezone ต่างกัน → อาจกลายเป็นวันที่ 31?
  → boundary: schedule 1 ชั่วโมงพอดี (minimum) → ได้ ✓
```

**Checklist Boundary:**
- [ ] max value — ถ้าใส่พอดี max ระบบรับไหม?
- [ ] min value — ถ้าใส่พอดี min ระบบรับไหม?
- [ ] count = 0 — ถ้า list ว่างเปล่า UI แสดงอะไร?
- [ ] count = 1 — ถ้ามีแค่ 1 item แล้วลบออก UI แสดงอะไร?
- [ ] ค่าที่เป็น null หรือ empty string ต่างกับ 0 ยังไง?

---

### Model 2 — Timing Analysis

Edge case จำนวนมากเกิดจาก timing ที่ไม่คาดคิด
ทั้ง concurrent users, session ที่ค้างอยู่, และ state ที่เปลี่ยนระหว่างรอ

```
วิธีใช้:
ถามว่า "ถ้า state เปลี่ยนระหว่างที่ user กำลังทำอยู่ จะเกิดอะไร?"

ตัวอย่าง UC8:
  admin A กำลังดู pending list อยู่
  → admin B approve post เดียวกันก่อน → admin A เห็น post นั้นหายไปไหม?
  → admin B delete community → post ใน pending list หายไปไหม?
  → admin A ถูก revoke permission กลางคัน → ยัง submit ได้ไหม?

ตัวอย่าง UC12 — Create post:
  admin เปิด community selector ไว้
  → community ถูกลบระหว่างที่ selector เปิดอยู่ → submit ได้ไหม?
```

**Checklist Timing:**
- [ ] สองคน action เดียวกันพร้อมกัน → ใครชนะ?
- [ ] state เปลี่ยนระหว่าง session เปิดอยู่ → UI อัปเดตไหม?
- [ ] permission ถูก revoke กลางคัน → action ที่ค้างอยู่จะเกิดอะไร?
- [ ] object ถูกลบระหว่าง action → error message ชัดเจนไหม?
- [ ] session timeout ระหว่าง long form → data หายไหม?

---

### Model 3 — Environment Analysis

Edge case อีกกลุ่มคือ environment ที่ผิดปกติ
end user ไม่รู้ว่าเกิดอะไร แต่ system ต้อง handle ได้

```
วิธีใช้:
ถามว่า "ถ้า infrastructure หรือ external dependency ทำงานผิดปกติ จะเกิดอะไร?"

กลุ่มที่ต้องถามเสมอ:
  Network     → ช้า, หาย, กลับมา
  Server      → ล่ม, timeout, response ช้า
  Storage     → เต็ม, corrupt, ขนาดเกิน limit
  Device      → battery ต่ำ, memory เต็ม, background kill app
  External    → third-party API ล่ม (Google auth, push notification)
```

**Checklist Environment:**
- [ ] network หาย กลางคัน → data ที่กรอกไปหายไหม?
- [ ] network กลับมา → reload อัตโนมัติไหม หรือต้อง manual?
- [ ] API timeout → แสดงอะไร? retry อัตโนมัติไหม?
- [ ] third-party ล่ม (Google SSO, push notification) → fallback ทำงานไหม?
- [ ] file ขนาดเกิน limit → error ก่อน upload หรือหลัง?

---

### Model 4 — Data Integrity Analysis

Edge case กลุ่มสุดท้ายคือ data ที่อยู่ใน state ที่ไม่คาดคิด
เกิดจาก soft delete, orphaned records, หรือ data migration

```
วิธีใช้:
ถามว่า "ถ้า data ที่เกี่ยวข้องอยู่ใน state ผิดปกติ จะเกิดอะไร?"

ตัวอย่าง UC7 — View Posted posts:
  author account ถูก soft delete → post card แสดง placeholder ✓ (ระบุใน AC)
  author account ถูก hard delete → post card หายไปเลย หรือแสดง broken state?
  community ถูกลบ → post ที่อยู่ใน community นั้นหายไปจาก feed ไหม?
  post ถูก hard delete กลางคัน → feed อัปเดตไหม หรือต้อง refresh?
```

**Checklist Data Integrity:**
- [ ] soft deleted object — ยังแสดงผลได้ด้วย placeholder?
- [ ] hard deleted object — หายไปจาก list ทันทีไหม?
- [ ] orphaned record — record ที่ parent ถูกลบแล้วจะ render ยังไง?
- [ ] data ที่ถูกแก้โดยคนอื่นกลางคัน — อ่านเวอร์ชันล่าสุดหรือเปล่า?

---

## Error Case — หลักการและ Checklist

Error case ง่ายกว่า Edge เพราะมี trigger ที่ชัด
แต่ที่คนมักพลาดคือ **"state หลัง error"** ไม่ใช่แค่ "แสดง error message"

**Error case ที่ดีต้องตอบสามข้อ:**

```
1. อะไรที่ trigger error?
   → input invalid, network ล้ม, permission ผิด, API fail

2. user เห็นอะไร?
   → error message, toast, inline error, failed state

3. data/state อยู่ที่ไหนหลัง error?
   → กลับสู่ state เดิม? ข้อมูลที่กรอกหายไหม? retry ได้ไหม?
```

**ข้อที่ 3 คือสิ่งที่ขาดมากที่สุดใน AC จริง**

```
ตัวอย่างที่ขาดบ่อย:

AC กว้าง:
"Given network fails, when admin taps Approve, then show error message"

สิ่งที่ขาด:
→ post ยังอยู่ใน pending state ไหม? หรือ state corrupted?
→ Approve button กลับมา enabled ไหม? หรือ disabled ค้าง?
→ retry อัตโนมัติไหม หรือต้อง tap ใหม่?
```

### Error Case Checklist ที่ต้องมีทุก feature

```
Network errors:
- [ ] request ล้มระหว่างส่ง → state กลับสู่ previous state ไหม?
- [ ] timeout → retry อัตโนมัติ หรือแสดง retry button?
- [ ] partial success (บางอย่างสำเร็จ บางอย่างไม่) → data อยู่ที่ไหน?

Permission errors:
- [ ] permission ถูก revoke ก่อน submit → แสดงอะไร?
- [ ] token หมดอายุระหว่าง session → redirect login หรือ refresh token อัตโนมัติ?

Validation errors:
- [ ] blocked word/link → content ถูกเก็บไว้ใน composer ไหม? หรือหาย?
- [ ] file format ไม่รองรับ → error ที่ thumbnail หรือ toast?
- [ ] duplicate action → ถ้ากด submit สองครั้ง ระบบ handle ยังไง?

Concurrency errors:
- [ ] object ถูกลบก่อน action สำเร็จ → error message บอกสาเหตุชัดไหม?
- [ ] action เดียวกันถูกทำโดยคนอื่นก่อน → แสดง stale state หรือ refresh?
```

---

## Step 1 · รัน 4 Models กับ Happy Path AC ที่มีอยู่

ให้อ่าน Happy Path AC แต่ละข้อแล้วรัน 4 models นี้ทีละอัน

```
สำหรับแต่ละ Happy Path AC ให้ถาม:

Boundary:  "มี limit หรือ constraint อะไรใน Given/When/Then นี้?
            ถ้าอยู่พอดีขอบ จะเกิดอะไร?"

Timing:    "ถ้ามีคนอื่นทำ action เดียวกันพร้อมกัน จะเกิดอะไร?
            ถ้า state เปลี่ยนระหว่างที่ user กำลังทำอยู่ จะเกิดอะไร?"

Environment: "ถ้า network หรือ server ทำงานผิดปกติตอนนี้ จะเกิดอะไร?
              state หลัง error คืออะไร?"

Data integrity: "ถ้า data ที่เกี่ยวข้องอยู่ใน state ที่ไม่คาดคิด จะเกิดอะไร?"
```

---

## Step 2 · เขียน Edge/Error AC

โครงสร้างเหมือน Happy Path แต่มีความแตกต่างสำคัญ

**Edge Case AC:**
```
Given [precondition ปกติ]
  AND [condition ที่อยู่ที่ขอบ — boundary/timing/environment]
When  [action เดิม]
Then  [outcome ที่ถูกต้องสำหรับ edge condition นั้น]
  AND [state ที่ควรเป็นหลัง action]

ตัวอย่าง:
Given the admin has "Can manage posts & comments" permission
  AND there is exactly 1 post remaining in the pending list
When the admin taps Decline on that post
Then the post is removed from the pending list
  AND the badge disappears entirely from the Pending tab
  AND an empty state is shown
```

**Error Case AC:**
```
Given [precondition ปกติ]
When  [action]
  AND [error condition — network ล้ม, API fail, permission ผิด]
Then  [error message / failed state ที่ user เห็น]
  AND [state ของ data หลัง error — กลับสู่ previous state?]
  AND [action ที่ user ทำต่อได้ — retry? แก้ไข? ออกจากหน้า?]

ตัวอย่าง:
Given the admin has "Can manage posts & comments" permission
  AND the post is in pending state
When the admin taps Approve
  AND the network request fails
Then an error toast is shown
  AND the post remains in the pending list — state unchanged
  AND the Approve button returns to enabled state
  AND the admin can retry the action
```

---

## Step 3 · Prioritize — ไม่ต้อง test ทุก edge ที่หาได้

หลังจากหา edge/error cases ครบแล้ว ต้อง prioritize ว่าอันไหนควร test ก่อน
ไม่ใช่ทุก edge case มีความสำคัญเท่ากัน

**Priority สูง — ต้อง test เสมอ:**
- Data loss ถ้า handle ผิด เช่น content หายหลัง network error
- State corruption เช่น count กลายเป็น -1, post stuck ใน pending
- Security boundary เช่น permission bypass, unauthorized action
- Concurrent action บน critical resource เช่น approve/delete พร้อมกัน

**Priority กลาง — test ถ้ามีเวลา:**
- UI ที่ render ผิดเพราะ data อยู่ใน edge state
- Loading state ที่ค้างไม่ resolve
- Empty state ที่แสดงผิดเวลา

**Priority ต่ำ — log ไว้ แต่ skip ได้:**
- Edge ที่เกิดได้น้อยมากใน production
- Edge ที่ impact เฉพาะ cosmetic ไม่กระทบ data หรือ flow

---

## ตัวอย่างเต็ม — UC8 Approve Post

**Happy Path ที่มีอยู่:**
```
Given admin has permission AND post is in pending state
When admin taps Approve AND request succeeds
Then post removed from pending, appears in posted, badge -1, success toast
```

**รัน 4 Models:**

```
Boundary:
→ badge count = 1 แล้ว approve → badge ต้องหายไปทั้งหมด ไม่ใช่แสดง "0"
→ approve post สุดท้ายใน list → empty state ต้องโผล่

Timing:
→ admin B approve ก่อนที่ admin A จะ tap → admin A เห็น "Post has been reviewed"
→ admin permission ถูก revoke ก่อน tap → action fail gracefully
→ community ถูกลบระหว่าง pending → post หายออกจาก list ไหม?

Environment:
→ network ล้มหลัง tap → post ยังอยู่ใน pending, button กลับมา enabled
→ API timeout 30 วินาที → loading indicator ค้าง หรือ timeout ชัดเจน?

Data integrity:
→ post ถูก hard delete โดย admin อื่นระหว่าง session → approve fail, แสดงอะไร?
```

**Edge/Error AC ที่ได้:**

```
[Edge — badge clears when last post approved]
Given the admin has permission AND there is 1 post in the pending list
When the admin taps Approve AND request succeeds
Then the post is removed AND the empty state is shown
  AND the badge disappears from the Pending tab entirely

[Edge — concurrent approve by another admin]
Given two admins both view the same pending post
When admin A taps Approve first AND admin B taps Approve simultaneously
Then admin A sees a success toast
  AND admin B sees a toast: "Post has been reviewed"
  AND the post is approved only once — not duplicated

[Error — network fails on approve]
Given the admin has permission AND post is in pending state
When the admin taps Approve AND the network request fails
Then an error toast is shown
  AND the post remains in the pending list — state unchanged
  AND the Approve button returns to enabled — admin can retry

[Error — post deleted by another admin before approve]
Given the admin has permission AND post is in pending state
When the admin taps Approve AND the post has already been deleted
Then an error message is shown explaining the post no longer exists
  AND the post is removed from the current admin's pending list
```

---

## Output format

เมื่อใช้ skill นี้กับ story จริง ให้ produce output 3 ส่วน

**ส่วนที่ 1 — Edge cases found (จัดหมวดตาม 4 models)**
แสดงให้เห็นว่าแต่ละ edge มาจาก model ไหน

**ส่วนที่ 2 — Priority list**
แยก high/medium/low พร้อมเหตุผลสั้นๆ

**ส่วนที่ 3 — AC ใหม่**
เขียนเฉพาะ high priority ก่อน label ชัดว่า [Edge] หรือ [Error]
พร้อม mark [PENDING] ในส่วนที่ยังต้องถาม PM
