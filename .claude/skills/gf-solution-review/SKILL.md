---
name: gf-solution-review
description: 'Goldfish experiment (goldfish/) — QA review ของ Solution ที่ยังเป็น draft: --sketch (สถานะ 02 อ่าน sketch.md → testability flags, effort drivers, คำถามสำหรับ direction & scope) หรือ --detail [§n] (สถานะ 04 อ่าน spec.md ทีละ section → finding ต่อ R/ST/F พร้อม fix ที่เสนอและช่องทางส่ง) ไม่ตรวจซ้ำสิ่งที่ solution:check ทำแล้ว ใช้เกณฑ์คำถาม 4 ข้อ Output goldfish/<product>/<feature>/review-<mode>-<date>.md อ่านอย่างเดียว Trigger: "/gf-solution-review <product>/<feature> --sketch|--detail", "review sketch", "review spec draft", "QA review solution" ไม่ใช่ analysis หลัง Solution Ready (นั่นคือ test-factory)'
user-invocable: true
argument-hint: "<product>/<feature> --sketch|--detail [§1..§7] [--ref <branch|sha>] [--replay]"
---

# gf-solution-review — QA in the room, not after it

ส่วนหนึ่งของการทดลองใน `goldfish/` — อ่าน `goldfish/README.md` ก่อน
Template: `goldfish/templates/review.md` · Knowledge: `goldfish/knowledge/testability-catalogue.md`
Day 0 ของ feature นี้ (ถ้ามี): `goldfish/<product>/<feature>/day0.md`
S-CAT + Gate 02: console-next `.claude/skills/solution/reference/goldfish.md` (branch `next`)

## Contract
1. **อ่านอย่างเดียว** artefact ที่ `--ref` (branch ของ Solution PR หรือ sha) ด้วย `git show <ref>:docs/solution/<dir>/<file>` เขียนเฉพาะ `goldfish/`
2. **ไม่ตรวจซ้ำ `solution:check`** — flow ไม่มี rule, rule ไม่มี test case, n/a ไม่มีเหตุผล, ช่อง permission ว่าง, id ไม่มีจริง ถ้าเห็นให้รัน `pnpm run solution:check -- <feature>` ใน console แทน
3. **Finding ต้องมี fix ที่เสนอ** — ประโยค rule ใหม่, state ที่ขาด, ตัวเลขที่ต้องระบุ ไม่ใช่แค่ "ไม่ชัด"
4. **เกณฑ์ 4 ข้อ** (README) — finding ที่ไม่ผ่านไป *QA decided*
5. **ห้องเป็นคนตัดสิน** — QA เสนอ ไม่เขียน spec.md เอง
6. **Replay** (`--replay`): อ่านแค่ที่ sha; ห้ามอ่าน clarifications / bugs / analysis / spec ที่ HEAD / tracker ของ feature นี้ และข้าม knowledge entry ของ feature นี้
   - **เลือก sha**: commit แรกที่ไฟล์ถึงสถานะที่จำลอง (`git log --reverse --format=%h -- <file>` แล้ว `git show <sha>:<file> | grep Status:`) ถ้า commit แรกเป็น 06 หรือมี Delivery amendment แล้ว → replay **ไม่ blind** บอกตั้งแต่หัวไฟล์ และติด † ทุก finding ที่แตะข้อความที่ถูก amend
   - ห้าม `git show --stat` / `git log` แบบมี message ของ commit หลัง sha (message สรุป amendment)
7. **Core ref** สำหรับ `[system]`: ใช้ core ที่ commit ใกล้วันที่ของ artefact (`git -C ../social-plus-core log --before=<date> -1`) จด sha ไว้หัวไฟล์ — line number ใน spec อาจเลื่อน ให้เทียบที่ชื่อ function

## --sketch (สถานะ 02 → ก่อน direction & scope check)

อ่าน sketch.md (+ day0.md) แล้วตอบสามอย่าง:
1. **Testability flags** — capability / draft rule / flow ไหนที่ verify ยากหรือไม่ได้ ทำไม และขออะไรได้ตอนนี้ (test hook, env setting, seeded data, stub) เทียบ catalogue + generic lenses
2. **Effort drivers** — ไม่ใส่ตัวเลข (console-next ไม่ size ใน Solution) บอกตัวขับ: roles × configurations, rule ที่ขึ้นกับเวลา, cross-product check, env ที่ต้องมีคนตั้ง, จำนวน surface
3. **Scope option ที่ test ไม่ได้** — option ใน §5 ที่เลือกแล้วจะเหลือสิ่งที่ verify ไม่ได้ → บอก PM ก่อน 03
คำถามที่นี่มีแค่ที่ **เปลี่ยน direction หรือ scope** รายละเอียดที่เห็นแล้วจดใน *Held for Detailing* ไม่ถามตอนนี้

## --detail [§n] (สถานะ 04 — ทีละ section ขณะห้องเขียน)

ทำเฉพาะ section ที่สั่ง (ไม่สั่ง = ทุก section ที่มีเนื้อหา) lens ต่อ section:

| § | Lens |
|---|---|
| 1 Flows | branch ที่ไม่มีใครวาด: cancel / back / submit ซ้ำ / object ถูกแก้หรือลบระหว่างทำ / สิทธิ์หายระหว่างทำ — แต่ละ Alt มีปลายทาง |
| 2 States | S-CAT ต่อ surface — `[n/a]` ที่เหตุผลไม่จริง (เช่น quota ที่มีจริง) · state ที่ staging สร้างไม่ได้ → testability flag |
| 3 Rules | **observable**: tester เห็นอะไรเมื่อ rule ทำงาน · **numbers**: หน่วย, ขอบรวม/ไม่รวม, นาฬิกาไหน · **conditional**: decision table ครบทุก combination · **decider**: tag `[product|system]` ถูกคน · `[system]` อ้าง core จริง · **cross-feature**: object นี้ถูก feature อื่นแตะไหม (ลบ, ซ่อน, ย้าย) · **today**: ถ้าเป็นพฤติกรรมเดิมของ console ให้ rule พูดตรง ๆ ไม่ใช่ "as today" — และ surface ที่ Figma เขียน `Follow existing` หรือ action ที่ console today มีแต่ spec ไม่พูดถึง (ปุ่ม, ค่าเริ่มต้น, ล็อกตอน edit, filter) → diff กับ console today แล้วเสนอเป็น rule หรือ out-of-scope |
| 4 Permissions | ทุก role × action มี account บน staging ทดสอบได้จริงไหม · ✓ แปลว่า "เห็น" หรือ "ทำสำเร็จ" · denied look ระบุ · revoke ระหว่าง session มีผลเมื่อไร · **dependency**: action ที่เรียก API ของ module อื่น (เช่น mention → member search) ต้องการ permission ของ module นั้นด้วย — ระบุใน matrix |
| 5 API | error ทุกตัว map ไป rule ที่ tester เห็นได้ · ordering / page size / limit ระบุ |
| 6 Test cases | Then สังเกตได้ด้วยตา (ไม่ใช่ request body) · boundary ทั้งสองฝั่ง · negative ต่อ rule ที่มีเงื่อนไข — case ที่ขาด QA เขียนเอง (*QA decided*) ไม่ใช่คำถาม |
| 7 Instrumentation | event แต่ละตัว QA verify อย่างไร |

แต่ละ finding: `QF<n>` · ref (R/ST/F/§) · lens · finding · fix ที่เสนอ · route · **blocks** (03 / 05 / —)

- **รวม ไม่แตก**: rule เดียวที่ขาดหลายเรื่อง (หน่วย + ขอบ + นาฬิกา) = finding เดียว เสนอเป็น **ประโยค rule เดียว** ที่ตอบครบ — เกณฑ์ "ตัดสินใจเดียว" หมายถึงคนตัดสินรับ/ไม่รับประโยคนั้น
- **Tag + citation** เป็น lens เดียว: tag ผิดคน หรือ `[system]` ไม่มี/อ้าง core ผิด
- **dev S-R ที่ Then มองไม่เห็น**: PR comment เสนอ Then ที่มองเห็นได้ (ไม่ใช่ QA decided — case เป็นของ dev)
- **§2 n/a**: "n/a ไม่มีเหตุผล" = solution:check · "n/a เหตุผลไม่จริง" = ของเรา ต้องมีหลักฐาน (core / knowledge)
- **ตัดเสียงรบกวน**: ส่งห้องเฉพาะ finding ที่ block 05 หรือเปลี่ยน expected ของ case P1–P2 ที่เหลือ (copy TBD, rate limit ทั่วไป) รวมเป็นรายการเดียวท้าย PR comment ไม่ถามทีละข้อ

Route: `PR comment → Eng|Design` · `chat → PM` ([product]) · `chat → Architect` (platform truth, core) · `huddle` (สองฝ่ายเห็นต่าง) · `QA decides`
Testability flag ที่ต้องขออะไร (hook, network เฉพาะ) มี route ด้วย

## Output
เขียน `goldfish/<product>/<feature>/review-<sketch|detail>-<YYYY-MM-DD>.md` (replay: `review-<mode>-replay-<sha>.md`) ตาม template
สรุปในแชทไม่เกิน 15 บรรทัด: จำนวน finding (ส่งห้อง / QA decides), ตัวที่ block 03 หรือ 05, flags สำคัญ
Shadow mode: เตือนให้ลง `question-log.md` เมื่อส่งจริง
