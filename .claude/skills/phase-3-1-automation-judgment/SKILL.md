---
name: phase-3-1-automation-judgment
description: 'ใช้ skill นี้เมื่อมี test cases list แล้วต้องการรู้ว่าอันไหน automate ได้ อันไหน manual เท่านั้น และอันไหนต้อง QA ตัดสินเอง Skill นี้ตรวจตาม 6 criteria เรียงตาม blocker ก่อน แล้ว produce judgment table พร้อม verdict, reason, และ suggested tool Trigger เมื่อ: มี test cases แล้วต้องแบ่ง automate vs manual, กำลังวางแผน automation suite, ต้องการ prioritize test cases สำหรับ CI/CD, หรือต้องการ justify ว่าทำไมบาง test ถึงต้อง manual เสมอ'
---
 
# Automation Judgment
 
ตรวจ test cases ทีละข้อว่า automate ได้หรือไม่ได้ พร้อมเหตุผลที่ชัดเจน
 
---
 
## Context ที่ต้องได้รับก่อนตรวจ
 
ก่อนเริ่ม judgment ให้ถามหรือตรวจสอบว่ามี context ครบหรือเปล่า
ถ้าไม่มีให้ถามก่อน — ถ้า assume เองจะ mark automate ผิดพลาด
 
```
สิ่งที่ต้องรู้:
 
1. Platform          : Web / Android / iOS / ครบทั้งสาม
2. Feature stability : stable / might-change / A-B test / redesign planned
3. External deps     : none / payment-gateway / SMS-OTP / third-party-webhook / etc.
4. Test environment  : stable / flaky / sandbox-only
```
 
ถ้า user ไม่ได้บอก ให้ default เป็น:
- platform = Web (conservative)
- stability = stable
- external deps = none
- environment = stable
แล้วระบุ assumption ใน output ด้วยว่า assume อะไรไป
 
---
 
## 6 Criteria — ตรวจตามลำดับนี้เสมอ
 
ตรวจ sequential ถ้าติด blocker (criteria 1, 2, 6) หยุดทันที — ไม่ต้องตรวจต่อ
 
---
 
### Criteria 1 — Expected result assert ได้ด้วย code ไหม? `[BLOCKER]`
 
**assert ได้** = observable output ที่ code เช็คได้โดยไม่ต้องให้คนดู
 
```
assert ได้:
  ✓ text content ของ element ("Email is required")
  ✓ element visible / hidden / disabled
  ✓ URL / route change ("/dashboard")
  ✓ HTTP status code (200, 422, 401)
  ✓ response body field ("error": "Min 8 characters")
  ✓ element count (แสดง 3 items)
  ✓ attribute value (aria-label, data-testid)
  ✓ navigation / redirect
 
assert ไม่ได้ด้วย Playwright ธรรมดา:
  ✗ "ดูดีไหม" / "สวยไหม" / "เหมาะสมไหม"
  ✗ "error message อ่านแล้วเข้าใจง่ายไหม" (usability)
  ✗ "สีตรงกับ Figma ไหม" (visual — ต้อง Percy/Chromatic)
  ✗ "animation smooth ไหม"
  ✗ "layout พังไหม" (ต้อง visual regression tool)
```
 
**ถ้า assert ไม่ได้ → verdict = Manual (blocker) หยุดตรวจข้ออื่น**
 
---
 
### Criteria 2 — ต้องการ physical sensor ไหม? `[BLOCKER]`
 
```
physical sensor ที่ simulator บน CI ไม่มี:
  ✗ Face ID / Touch ID / fingerprint
  ✗ Camera (scan QR, take photo, AR)
  ✗ NFC tap
  ✗ GPS real location (ไม่ใช่ mock location)
  ✗ Accelerometer / shake gesture
  ✗ Barometer / microphone จริง
```
 
**ถ้าต้องการ physical sensor → verdict = Manual (blocker)**
 
หมายเหตุ: real device farm (BrowserStack/Sauce Labs) automate sensor บางอย่างได้
แต่ราคาแพงและ setup ซับซ้อน — ให้ระบุ `Manual (or real-device-farm)` แทน
 
---
 
### Criteria 3 — จะรันซ้ำกี่ครั้ง? `[REQUIRED]`
 
```
กฎ:
  < 3 ครั้งตลอด lifetime → ไม่คุ้ม automate
  ≥ 3 ครั้ง (เช่น regression ทุก sprint) → คุ้มค่า
 
test ที่มักรันน้อยครั้ง:
  - one-time migration test
  - test สำหรับ hotfix ที่จะไม่ถูก touch อีก
  - test สำหรับ feature ที่จะถูก sunset เร็วๆ นี้
```
 
**ถ้ารันน้อยกว่า 3 ครั้ง → verdict = Manual (low ROI)**
 
---
 
### Criteria 4 — Feature นี้ UI จะเปลี่ยนบ่อยไหม? `[REQUIRED]`
 
```
signal ที่บอกว่าจะเปลี่ยน:
  - PM บอกว่า "อาจ redesign"
  - อยู่ใน A/B test
  - feature ใหม่ที่ยังไม่ validate กับ user จริง
  - onboarding / landing page ที่ปรับบ่อย
 
ผลถ้า UI เปลี่ยน:
  - selector พัง (element ย้ายที่ / เปลี่ยน class)
  - automation ต้อง rewrite ทุก sprint
  - maintain cost > manual test cost
```
 
**ถ้า UI จะเปลี่ยนบ่อย → verdict = Manual (unstable, high maintain cost)**
ถ้าไม่แน่ใจ → verdict = Partial — ระบุ "automate เมื่อ design stable แล้ว"
 
---
 
### Criteria 5 — Setup ซับซ้อนกว่า test เอง หรือเปล่า? `[REQUIRED]`
 
```
setup ที่ซับซ้อน:
  - real payment gateway (Stripe, Omise sandbox unstable)
  - OTP จาก SMS จริง (ต้องมี SIM/phone number)
  - third-party webhook ที่ timing ไม่แน่นอน
  - email confirmation จาก inbox จริง
  - external API ที่ rate limit ต่ำ
 
ผล:
  - flaky test (รัน 10 ครั้ง ผ่าน 7)
  - เวลา debug automation > เวลา manual test
  - CI pipeline พังบ่อยโดยไม่ใช่ fault ของ app
```
 
**ถ้า setup ซับซ้อน → verdict = Manual (flaky risk)**
ถ้ามี stable mock/stub → verdict = Automate (with mock) ระบุว่า mock อะไร
 
---
 
### Criteria 6 — เป็น exploratory หรือ usability test ไหม? `[BLOCKER]`
 
```
exploratory test:
  - ไม่มี predetermined steps
  - ไม่มี expected result ที่กำหนดล่วงหน้า
  - QA improvise ระหว่าง test เพื่อหา bug ที่ไม่ได้คาดไว้
  - "ลองใช้แบบ user จริงๆ แล้วดูว่ามีอะไรแปลก"
 
usability test:
  - "flow นี้ confusing ไหม"
  - "user เข้าใจ label ไหม"
  - "ขั้นตอนนี้มากเกินไปไหม"
```
 
**ถ้าเป็น exploratory หรือ usability → verdict = Manual (blocker) หยุดตรวจ**
 
---
 
## Verdict Options
 
| Verdict | ความหมาย |
|---------|----------|
| `Automate` | ผ่านทุก criteria — ควร automate เลย |
| `Automate (with mock)` | ผ่าน แต่ต้อง mock external dependency |
| `Automate (when stable)` | ผ่าน แต่ UI ยังไม่ stable รอก่อน |
| `Partial` | automate ได้บางส่วน ส่วนที่เหลือ manual |
| `Manual` | ติด blocker หรือ ROI ต่ำ |
| `Manual (real-device-farm)` | ต้องการ physical sensor แต่ทำได้ด้วย real device farm |
 
---
 
## Suggested Tools
 
ระบุ tool ที่เหมาะสมสำหรับแต่ละ verdict
 
```
Web functional/interaction   → Playwright
Android functional           → Detox หรือ Appium
iOS functional               → Detox หรือ XCUITest
API / integration            → Supertest หรือ Postman/Newman
Visual regression            → Percy หรือ Chromatic (ไม่ใช่ Playwright)
Real device (sensor)         → BrowserStack / Sauce Labs
Unit test (Dev ทำ)           → Jest / Vitest / JUnit / XCTest
```
 
---
 
## Step 1 · รับ input และ validate context
 
```
รับ:
  - test cases list (TC-ID, scenario, expected result)
  - platform
  - feature stability
  - external dependencies
 
ถ้าขาด context → ถามก่อน
ถ้า user บอกว่า "ข้ามไปเลย" → assume default และระบุไว้ใน output
```
 
---
 
## Step 2 · ตรวจแต่ละ test case
 
สำหรับแต่ละ TC ให้ตรวจตาม 6 criteria ตามลำดับ:
 
```
1. Expected result assert ได้ไหม?
   → ถ้าไม่ได้ = Manual (blocker) หยุด
 
2. ต้องการ physical sensor ไหม?
   → ถ้าใช่ = Manual (blocker) หยุด
 
3. รันซ้ำน้อยกว่า 3 ครั้งไหม?
   → ถ้าใช่ = Manual (low ROI)
 
4. UI จะเปลี่ยนบ่อยไหม? (จาก stability context)
   → ถ้าใช่ = Manual หรือ Automate (when stable)
 
5. Setup ซับซ้อนกว่า test เอง?
   → ถ้าใช่ = Manual หรือ Automate (with mock)
 
6. เป็น exploratory หรือ usability?
   → ถ้าใช่ = Manual (blocker) หยุด
 
ถ้าไม่ติดข้อไหนเลย → Automate
ระบุ suggested tool ด้วยเสมอ
```
 
---
 
## Step 3 · Produce output
 
### Primary output — Judgment Table
 
```
| TC-ID | Scenario (สั้น) | Verdict | Criteria ที่ติด | Suggested Tool | Note |
```
 
เรียง verdict: Automate → Partial → Manual
ภายในกลุ่มเดียวกัน เรียงตาม TC-ID
 
### Secondary output — QA Must Confirm
 
หลัง table ให้แสดง section นี้เสมอ:
 
```
## สิ่งที่ AI ตัดสินไม่ได้ — QA ต้อง confirm ก่อน implement
 
1. Feature stability ในอนาคต
   - TC ที่อาจได้รับผล: [list TC-IDs]
   - ต้องถาม: PM มีแผน redesign/A-B test feature นี้ไหม?
 
2. Automation budget ของ sprint นี้
   - AI recommend automate X cases แต่ทีมอาจมีเวลาแค่ Y cases
   - QA ต้อง prioritize จาก verdict = Automate ว่าจะเริ่มอันไหนก่อน
 
3. Flakiness risk จาก environment จริง
   - TC ที่มี external dependency: [list TC-IDs]
   - ต้องถาม: test environment ของ project นี้ stable แค่ไหน?
```
 
### Tertiary output — Summary Stats
 
```
## สรุป
- Automate:        X cases (X%)
- Manual:          Y cases (Y%)
- Partial/Pending: Z cases (Z%)
- Total:           N cases
```
 
---
 
## ตัวอย่าง output เต็ม
 
**Input:**
```
Feature: Registration form
Platform: Web + Android + iOS
Stability: stable
External deps: none
 
TC-007-01: Submit empty form → error ทั้ง 2 field
TC-007-02: Password 7 chars → error "Min 8 characters"
TC-007-03: Password 8 chars → submit สำเร็จ
TC-007-04: Error หายทันทีที่พิมพ์ตัวแรก
TC-007-05: iOS "Done" keyboard button → dismiss เท่านั้น ไม่ submit
TC-007-06: Error message อ่านแล้วเข้าใจง่ายไหม
TC-007-07: Face ID unlock ก่อน register (iOS)
TC-007-08: Explore ดูว่ามี edge case ที่ไม่ได้คาดไว้บ้าง
```
 
**Output:**
 
| TC-ID | Scenario | Verdict | Criteria ที่ติด | Suggested Tool |
|-------|----------|---------|-----------------|----------------|
| TC-007-01 | Submit empty → 2 errors | Automate | — | Playwright (Web), Detox (mobile) |
| TC-007-02 | PW 7 chars → error text | Automate | — | Playwright (Web), Detox (mobile) |
| TC-007-03 | PW 8 chars → submit OK | Automate | — | Playwright (Web), Detox (mobile) |
| TC-007-04 | Error ลายบน keystroke | Automate | — | Playwright (Web), Detox (mobile) |
| TC-007-05 | iOS Done → dismiss only | Partial | criteria 2 (iOS keyboard behavior) | Detox + real device confirm ครั้งแรก |
| TC-007-06 | Error อ่านแล้วเข้าใจไหม | Manual | criteria 1 (usability — assert ไม่ได้), criteria 6 | — |
| TC-007-07 | Face ID unlock | Manual | criteria 2 (physical sensor) | — |
| TC-007-08 | Exploratory testing | Manual | criteria 6 (exploratory) | — |
 
**สิ่งที่ AI ตัดสินไม่ได้ — QA ต้อง confirm:**
 
1. TC-007-05 — iOS keyboard Done behavior ควร confirm ด้วย real device ครั้งแรก simulator อาจ behave ต่างกัน
2. Budget — AI recommend automate 4 cases ถ้าทีมมีเวลาน้อยกว่าให้เริ่ม TC-007-01 และ TC-007-03 (happy path + critical error) ก่อน
**สรุป:**
- Automate: 4 cases (50%)
- Partial: 1 case (12.5%)
- Manual: 3 cases (37.5%)
- Total: 8 cases
---
 
## หมายเหตุสำหรับ mobile testing
 
iOS simulator บน CI:
- `keyboard.type()` ใน Detox ทำงานได้ แต่ IME action button (Done, Next, Go) อาจ behave ต่างจาก real device
- Face ID / Touch ID ต้อง real device เท่านั้น
- Safe area, gesture navigation ควร confirm บน real device ครั้งแรก
Android emulator บน CI:
- `typeText()` และ IME action ทำงานได้ดีกว่า iOS
- Back gesture / back button automate ได้ใน Detox
- Camera / NFC ต้อง real device
กฎง่ายๆ: ถ้าไม่แน่ใจว่า simulator handle ได้ → verdict = Partial แล้วระบุ "confirm on real device first"
