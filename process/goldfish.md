# Goldfish — กระบวนการทำงานที่ใช้อยู่ (ตั้งแต่ 2026-09-28)

สรุปจาก 3 artifact (อ่านเมื่อ 2026-10-01):
- Goldfish playbook ฉบับเต็ม — https://claude.ai/code/artifact/8d6256d4-e5ee-402f-aaeb-4686430c2f45
- Goldfish process model (ภาพรวม) — https://claude.ai/code/artifact/12b09fdb-5b5c-4dce-84a5-51aed71080b5
- Goldfish QA Workflow (หน้าของ pidshapar) — https://claude.ai/artifact/QzV9WBXW1MdhMQUzSJ9rA8

Goldfish แทนที่โมเดลเดิม (Mickey Mouse: PM เขียน PRD + user story + AC แล้วส่งต่อ) ด้วย **Rule แทน AC**
และ **"Nothing is handed over. Everything is pulled."** — เฟสถัดไปดึงงานเมื่อมี capacity

## สามเฟส

| เฟส | อยู่ที่ไหน | ใครเป็นเจ้าของ | ผลลัพธ์ |
|---|---|---|---|
| **Frame** | นอก sprint (~1 สัปดาห์) | PM + Architect | frame doc: problem, outcome, capability ที่จัดลำดับ, metrics, appetite, complexity S/M/L/XL, technical direction |
| **Solution** | ใน sprint (1–2 สัปดาห์) | solution group = Engineer + QA (+ Design ถ้า frame บอก design required) · Engineer เป็นเจ้าของ sketch + common specs · แต่ละฝ่ายเป็นเจ้าของ domain spec ของตัวเอง | flows F, states ST, rules R (stable ID), permissions, API surface, test cases, design handoff, slices SL → Solution PR |
| **Delivery** | ใน sprint (~3 สัปดาห์) | Engineering สร้าง · QA ถือ verification gate | build ทีละ slice → Ship PR (entries `planned` → `shipped`) |

QA ใน Goldfish **เข้ามาตั้งแต่ rule แรก เป็นผู้เขียน ไม่ใช่ผู้รับ**: ให้ estimate (Detailing + Delivery) ใน Sketch PR,
ชี้ testability flags (อะไรยาก/ทดสอบไม่ได้), ท้าทาย rule ว่า test ได้ไหม, ใช้ state inventory คุม loading/empty/error/denied,
เขียน test case ของ QA, และยืนยัน readiness ที่ gate 05 ความรับผิดชอบเรื่อง "ครบไหม" อยู่ที่ Design + Eng + QA ไม่ใช่ PM

## สถานะของ Solution

01 To pick up → 02 Solutioning → **03 Pending direction & scope** (gate: PM ตอบ frame ไหม · Architect ขัด direction ไหม; ไม่ผ่านกลับ 02)
→ 04 Detailing → **05 Pending review** (gate: ไม่มี gap เปิด · ทุกฝ่ายยืนยัน) → 06 Solution ready (Delivery ดึงได้ · QA เขียน case ได้) · 07 Obsolete (ต้องมีเหตุผล)

เปลี่ยนก่อน 03 ถูก หลัง 03 แพง — อย่าวาดทุก state ก่อน direction ผ่าน

## Artefact ใน console-next `docs/solution/<feature>/`

| ไฟล์ | ตอบคำถาม | เจ้าของ |
|---|---|---|
| sketch.md | approach ให้ outcome ไหม · scope option | Engineer (Design ร่าง flow) |
| spec.md | §1 Flows F · §2 States ST (S-CAT 17 ข้อ) · §3 Rules R `[product]`/`[system]` · §4 Permissions · §5 API surface · §6 Test cases S-R (ของ dev) · §7 Instrumentation · Open | ห้อง Solution |
| handoff.md | state → component, copy | Design |
| slices.md | แบ่งเป็นงาน demo ได้ | Eng |
| delivery.md | build ต่างจาก spec ตรงไหน | Eng (Delivery) |
| test-cases.md | QA test case (QA-R) | QA — generated จาก test-factory `pnpm solution:export` ห้ามแก้มือ |

หลักการ: spec ต้องตอบได้ว่า "นี่คือ bug ไหม" โดยไม่ต้องอ่านโค้ด (ตรง Rn = ตั้งใจ · ขัด Rn = defect) · `[product]` PM ตัดสิน · `[system]` ต้องอ้าง code ใน core ·
state ที่ไม่ใช้เขียน `[n/a] — เหตุผล` · ไม่มีอะไรหายเงียบ

## ID chain

`R6` (rule) → `S-R6-1` (dev case ใน spec.md §6) → `QA-R6-1` (QA case, `derived_from: "S-R6-1"`) → `case_uid` (ถาวร) → Testmo project 5 → annotation ใน Playwright
gap case ที่ dev ไม่มีคู่ได้เลขถัดไป (`QA-R6-4`) ไม่มี `derived_from` · ไม่ renumber

## Clarification vs defect (ใช้ตั้งแต่ post-content)

- ไม่มี R สำหรับพฤติกรรมนี้ → **rule-request** ส่งห้อง (รวมเป็นรายการเดียว ไม่ block)
- มี R แต่ spec เองให้ผลที่คาดหวังไม่ได้ (spec ขัดกันเอง) → **clarification** block เฉพาะ case นั้น
- มี R และ build ไม่ตรง → **defect** (`open-bug-ticket`) หรือห้องแก้ rule

## qa-assistant อยู่ตรงไหนใน Goldfish

test-factory ทำงาน **หลัง 06** (import spec.md → QA-R → export test-cases.md) · qa-assistant ช่วยช่วง **02–05** ตอน spec ยังแก้ได้ถูก
skill ของ qa-assistant เขียนสำหรับ Jira story/AC — ใช้ใน Goldfish ต้องให้ output อ้าง F / ST / R / §4 แทน AC
Solution เป็นงานกลุ่มของ dev, QA และ designer (2026-10-14): dev สร้างไฟล์ก่อน · QA รีวิว ถามตอบ แล้ว**แก้ไฟล์ใน Solution เอง**ผ่าน docs PR ที่ dev รีวิว ก่อนเอาไป implement หรือเขียน test design · ใส่เฉพาะเรื่องที่ตกลงแล้ว ต่อท้ายด้วย "— amended <date>, see sketch.md §7" · S-R ใน §6 ยังเป็นของ dev (ขอใน PR)

| สถานะ | งาน QA | skill |
|---|---|---|
| 02 Solutioning | estimate, testability flags, เช็ค approach กับ outcome | phase-1-1, phase-1-2, meeting-mode |
| 04 Detailing | rule/state ที่ขาด, edge/error, boundary, ร่าง QA case | phase-1-4, phase-2-3, phase-2-6, phase-3-2, phase-3-3 |
| 05 Pending review | gap check รอบสุดท้าย | proposal-preimplementation-gap-checks.md |
