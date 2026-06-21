---
name: phase-2.1-user-story-invest
description: >
  ใช้ skill นี้เมื่อต้องเขียน User Story ใหม่จาก requirement หรือ feature idea
  หรือเมื่อต้องตรวจสอบ/ปรับ User Story ที่มีอยู่ให้ผ่าน INVEST
  Skill นี้สอนวิธีเขียนโครงสร้าง As a/I want/So that ให้ "So that" บอก business value จริง
  สอนวิธีทดสอบแต่ละตัวอักษรของ INVEST และสอนว่าเมื่อไหรควรแตก story
  (แตกตาม method ไม่ใช่ตาม role) รวมถึงกรณีพิเศษที่ role out-of-scope เป็น AC ไม่ใช่ story
  Trigger เมื่อ: เขียน story ใหม่, story ดูใหญ่หรือกว้างเกินไป, ไม่แน่ใจว่าควรแตกไหม,
  หรือต้องการ review story ก่อนเข้า backlog
---

# User Story & INVEST

เขียน User Story ที่ผ่าน INVEST และรู้ว่าเมื่อไหรควรแตก story

---

## หลักการพื้นฐาน

User Story คือหน่วยที่เล็กที่สุดของ requirement ที่ยังมีคุณค่าในตัวเอง
INVEST ไม่ใช่แค่ checklist ตอนจบ แต่คือ **วิธีทดสอบว่า story พร้อมสำหรับทีมจริงหรือเปล่า**

ปัญหาที่พบบ่อย: คนเขียน story ในรูปแบบถูก (As a/I want/So that)
แต่ผ่าน INVEST ไม่ได้ เพราะรูปแบบกับคุณภาพคือคนละเรื่องกัน

---

## โครงสร้างพื้นฐาน

```
As a [role]
I want [action]
So that [outcome — business value]
```

ทั้งสามบรรทัดมีน้ำหนักไม่เท่ากัน — **"So that" สำคัญที่สุด**

**กฎทดสอบ "So that":**
ถ้าลบ "So that" ออกแล้วทีมยังเข้าใจว่าทำไปทำไม = เขียนได้ดีพอ
ถ้าลบแล้วไม่รู้ว่าทำไปทำไม = "So that" ยังไม่ดีพอ ต้องเขียนใหม่

"So that" ต้องบอก pain ที่ feature แก้ ไม่ใช่ restate action ที่เพิ่งเขียนไป

---

## INVEST — ทีละตัวอักษร พร้อมวิธีทดสอบ

### I — Independent

story implement ได้โดยไม่ต้องรอ story อื่น

**วิธีทดสอบ:** "ถ้า story อื่นยังไม่เริ่ม story นี้ทำได้ไหม?" ถ้าไม่ได้ = dependent

```
dependent (ผิด):
"As an admin, I want to approve posts, so that content is published"
→ ต้องรอ story "view pending posts" ก่อน

แก้: merge หรือ sequence ให้ชัด ไม่เขียนเป็น story ที่ต้องรอกัน
```

### N — Negotiable

scope ของ story ยังปรับได้ก่อน sprint lock

**วิธีทดสอบ:** "ถ้า PM บอกให้ cut บางส่วนออก cut ได้ไหม?"
ถ้าทุกอย่างเป็น must-have หมด = ยังแตก story ต่อได้อีก

```
ยัดทุกอย่าง (ผิด):
"As an admin, I want to create posts with text, images, video,
 scheduled posting, brand identity, and blocklist validation"
→ ตัดไม่ได้สักชิ้น

แก้: แตกเป็นหลาย story — core create / scheduled / brand identity
```

### V — Valuable

deliver คุณค่าให้ user หรือ business ได้จริง ไม่ใช่ technical task

**วิธีทดสอบ:** "ถ้า story นี้ไม่มี ใครเสียอะไร?" ถ้าตอบไม่ได้ = ไม่ valuable พอ

```
technical task (ผิด):
"As a developer, I want to refactor the pending posts API
 so that the code is cleaner"
→ user ไม่ได้รับอะไร

แก้: story ต้องมี actor ที่เป็น user หรือ business
     technical task เขียนเป็น task แยก ไม่ใช่ story
```

### E — Estimable

team ประเมิน effort ได้

**วิธีทดสอบ:** ถาม dev "ประเมินได้ไหม?" ถ้าตอบ "ต้องรู้เพิ่มก่อน" = ยังไม่ชัดพอ

สาเหตุที่ estimate ไม่ได้มักมีสองอย่าง: story ใหญ่เกินไปต้องแตกย่อย
หรือ requirement ยังไม่ชัดต้องถาม PM ก่อน

### S — Small

ทำเสร็จได้ใน sprint เดียว (โดยทั่วไป 1–2 สัปดาห์)

**วิธีทดสอบ:** "ทำเสร็จภายใน sprint เดียวได้ไหม?" ถ้าไม่ได้ = ต้องแตก

S คือเหตุผลหลักที่ต้องแตก story และเป็นตัวที่ trigger การแตกบ่อยที่สุด

### T — Testable

team รู้ว่า done หมายความว่าอะไร — มี AC ที่ verify ได้

**วิธีทดสอบ:** "QA จะรู้ได้ยังไงว่า story นี้ pass?" ถ้าตอบไม่ได้ = ยังไม่ testable

```
วัดไม่ได้ (ผิด):
"As an admin, I want a good experience viewing pending posts"
→ "good experience" วัดไม่ได้

วัดได้ (ถูก):
"As an admin, I want to see all pending posts in one list
 so that I can approve or decline without missing any"
→ list แสดงครบ, approve/decline ทำงาน, ไม่มี post หาย
```

---

## วิธีแตก Story — แตกตาม Method ไม่ใช่ตาม Role

นี่คือหลักการที่คนมักเข้าใจผิดมากที่สุด

**กฎ:** เมื่อ story ใหญ่เกินไป ให้แตกตาม **method / mechanism** ที่ implementation ต่างกัน
ไม่ใช่แตกตาม role ที่ใช้ feature

```
requirement: "รองรับ sign in หลายรูปแบบ — email/password, Google SSO,
              SSO องค์กร, และ forgot password"

แตกตาม method (ถูก):
- Story 1: Sign in with email/password
- Story 2: Sign in with Google SSO
- Story 3: Sign in with SSO องค์กร
- Story 4: Forgot password

เหตุผล: แต่ละ method มี implementation คนละชุดกัน
        email/password ต้อง build validation logic
        Google SSO ต้อง integrate OAuth
        SSO องค์กร ต้อง handle domain validation
        → dev คนละคนทำพร้อมกันได้
```

```
แตกตาม role (ผิด):
- Story 1: Super Admin sign in
- Story 2: Admin sign in
- Story 3: Analyst sign in

เหตุผลที่ผิด: ทุก role ใช้ sign-in mechanism เดียวกัน
             stories จะ overlap กันทุกอัน
             สิ่งที่ต่างคือ "เห็นอะไรหลัง login" ซึ่งเป็น AC ไม่ใช่ story
```

---

## กรณีพิเศษ — Role ที่ Out of Scope เป็น AC ไม่ใช่ Story

เมื่อเจอ role ที่ไม่มีส่วนเกี่ยวข้องกับ feature เช่น role ที่เข้าได้แค่หน้าอื่น
นั่นไม่ใช่ User Story แยก แต่คือ **Acceptance Criteria** ของ story หลัก
ที่บอกว่า permission boundary คืออะไร

```
สถานการณ์: Analyst role เข้าได้แค่ dashboard ไม่ใช่ mobile console

เขียนเป็น story แยก (ผิด):
"As an Analyst, I should not see the applications..."
→ Analyst ไม่ได้ value อะไรจากการ "ไม่เห็น" — ไม่ใช่ story

เขียนเป็น AC ของ Login story (ถูก):
Given the user has Analyst role
When they sign in successfully
Then they are NOT redirected to the Applications page
  AND they cannot access the mobile console
```

**กฎตัดสิน:** ถาม "actor นี้ได้ value อะไรจาก story นี้?"
ถ้าตอบไม่ได้ → ไม่ใช่ story ของเขา เป็น permission boundary (AC) ของ story อื่น

---

## Pattern ที่ทำให้ Story ดีขึ้นทันที

| จุด | อ่อน | แข็ง |
|---|---|---|
| So that | "so that I can see applications list" | "so that I can manage communities from anywhere without being at my desk" |
| Role | "As a user" | "As an admin with 'Can manage posts & comments' permission" |
| Action | "I want a mobile console" | "I want to manage my communities from my phone" |

**So that ต้องบอก business value:**
```
อ่อน:  "I want to see pending posts so that I can see pending posts"
แข็ง:  "I want to see pending posts so that I can act on them quickly
        without switching to desktop"
```

---

## Output format

เมื่อใช้ skill นี้ ให้ produce output ตามนี้

**ถ้าเขียน story ใหม่:**
1. story ในรูปแบบ As a/I want/So that
2. INVEST check ทีละตัว — ผ่าน/ไม่ผ่าน พร้อมเหตุผลสั้นๆ
3. ถ้าไม่ผ่านข้อไหน ให้เสนอวิธีแก้

**ถ้า review story ที่มีอยู่:**
1. ระบุว่า INVEST ข้อไหนไม่ผ่าน
2. ถ้าต้องแตก story บอกว่าแตกยังไง (ตาม method)
3. ถ้ามี role ที่ควรเป็น AC ไม่ใช่ story ให้ flag

---

## สัญญาณว่า Story ยังไม่พร้อม

- "So that" restate action แทนที่จะบอก pain
- ยัดหลาย action เข้าไปใน story เดียว (see/write/delete พร้อมกัน)
- Role กว้างเกินไป เช่น "user" โดยไม่ระบุ permission
- มี role ที่เขียนเป็น story แต่จริงๆ คือ permission boundary
- estimate ไม่ได้เพราะกว้างหรือไม่ชัด
- ไม่มี AC ที่ verify ได้ — ไม่รู้ว่า done คืออะไร
