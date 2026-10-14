---
name: gf-day0-intake
description: 'Goldfish experiment (goldfish/) — QA Day 0 สำหรับ feature ที่กำลังจะเข้า Solution: อ่าน frame หรือ (ถ้าไม่มี frame) PRD + Figma ที่ยังไม่ครบ แล้วทำ QA frame card 8 ช่อง ทุกช่องมี source tag (frame/PRD/Figma/console/derived/UNKNOWN) + rule candidates + state walk + testability flags + คำถามที่ผ่านเกณฑ์ 4 ข้อ แยก ต้องตอบก่อน 03 / รอได้ Output goldfish/<product>/<feature>/day0.md อ่านอย่างเดียว ไม่เขียน console-next Trigger: "/gf-day0-intake <product>/<feature>", "day 0 <feature>", "อ่าน frame ก่อนเข้า solution", "ไม่มี frame มีแต่ PRD กับ figma" ไม่ใช่สำหรับ Jira AC analysis (นั่นคือ run-analysis)'
user-invocable: true
argument-hint: "<product>/<feature> [frame link | PRD link] [figma page] [--replay <sha>]"
---

# gf-day0-intake — QA Day 0

ส่วนหนึ่งของการทดลองใน `goldfish/` — อ่าน `goldfish/README.md` ก่อน (เกณฑ์คำถาม 4 ข้อ, โหมด replay/shadow)
Template: `goldfish/templates/day0.md` · Knowledge: `goldfish/knowledge/testability-catalogue.md`
Process reference: `process/goldfish.md` · S-CAT: console-next `.claude/skills/solution/reference/goldfish.md` (branch `next`)

## Contract
1. **อ่านอย่างเดียว** จาก console-next, Figma, PRD เขียนเฉพาะ `goldfish/<product>/<feature>/`
2. **ทุกค่ามี source** — ไม่มี source = `UNKNOWN` ห้ามเติมเอง อนุมานได้ = `derived` (PM ยืนยันที่ 03)
3. **AC ไม่ใช่ rule** — AC ใน PRD เป็นแค่ rule candidate (RC) ห้องเป็นคนตัดสิน ห้ามเรียกว่า R
4. **ถามเฉพาะที่ผ่าน 4 ข้อ** (README) ที่ไม่ผ่านไป §6 QA decided — ยกเว้น **frame gap** (ช่อง 1–8 ที่ frame ควรมีแต่ไม่มี เช่น rank, appetite, events): ไม่ต้องผ่านเกณฑ์ ไม่ถามทีละข้อ รวมเป็นโน้ตเดียวถึง PM ใน §5 "Frame gaps"
5. **Replay mode** (`--replay <date>`): ห้ามอ่านสิ่งที่เกิดทีหลัง (ดู README) และข้าม knowledge entry ที่ `feature` ตรงกับ feature นี้
   - console today และ core อ่านที่วันนั้น: `C=$(git rev-list -1 --before=<date> main)` แล้ว `git show "${C}:src/…"` (zsh ต้องมี `${}` และ quote) — `main` หลัง 2026-10-01 มีโค้ด console-next ที่สร้างจาก spec แล้ว
   - Figma ย้อนเวอร์ชันไม่ได้ (`figma:explore` อ่านแค่ปัจจุบัน) → จดวัน last-modified ไว้หัวไฟล์ว่าอาจมีการตัดสินใจหลังวัน replay ปนอยู่

## Steps

### 1 Gather inputs — เลือกทาง
- **มี frame** → อ่าน frame header + section; ช่อง 1–8 มาจาก frame เป็นหลัก
- **ไม่มี frame (ทางเลือก)** → ใช้ตามลำดับความน่าเชื่อ (ไม่มี PRD ก็ได้ — ใช้ copy ใน Figma + console today แทน):
  1. PRD (user stories, AC, non-goals) → capabilities, rule candidates, boundaries
  2. Figma page + `⤷` sub-pages + `🌏 Generic cases: All` → surfaces, flows, states ที่วาด
     (ใน social-plus-console: `npx -y tsx governance/design/figma/explore.ts pages|tree|text <node>` —
     `pnpm run figma:explore` ใช้ไม่ได้ถ้าไม่มี node_modules · `text` ทั้ง page ใหญ่จะ error "Invalid string length"
     ให้ดึงทีละ section · FIGMA_TOKEN อยู่ใน social-plus-test-factory/.env ส่งเป็น env var ห้ามพิมพ์ค่า)
  4. core (`../social-plus-core`) — ใช้ตอบคำถาม `[system]` เองก่อนถาม Architect (เกณฑ์ข้อ 2)
  3. console today (`src/pages/**`) เมื่อ Figma เขียน `Follow existing / …`
- จด inputs + mode ที่หัวไฟล์

### 2 QA frame card (§1)
เติม 8 ช่องตาม template แต่ละช่องมี source tag ช่องที่ derive เขียนเหตุผลสั้น ๆ ว่าอนุมานจากอะไร
- Capabilities: รูป `C<n> A <role> <verb> …` ระดับ "user can X" ไม่ใช่หน้าจอ ไม่มี rank → `UNKNOWN` (ถาม PM)
- Actors → role: ใช้ role จริงของระบบ (console `src/config/sitePermissions.ts`) คนที่ไม่มี role เขียน `no account`

### 3 Rule candidates (§2)
จาก AC/PRD แตกเป็นประโยค subject–condition–result หนึ่งเรื่องต่อบรรทัด เดา tag `[product|system]`
ตัวเลขทุกตัว (limit, เวลา, ความยาว) ต้องมีหน่วยและบอกว่าขอบรวมหรือไม่ — ไม่บอก = คำถาม

### 4 State walk (§3)
ต่อ surface: S-CAT 17 ข้อ ข้อไหน Figma วาด / ไม่วาด ไม่วาด ≠ ถาม — ถ้า standing look ใน S-CAT ตอบได้ ใช้มันแล้วจดไว้
Figma วาด **ต่างจาก** S-CAT (เช่น quota เป็น toast ตอน submit แทน disabled + tooltip) → ยึด Figma และจดเป็นคำถาม "รอได้" ถึง Design ว่าตั้งใจแหวก standing look

### 5 Testability flags (§4)
เทียบ RC + states กับ testability-catalogue และ generic lenses (time, limits, cross-product, async, third party)
แต่ละ flag บอกสิ่งที่ทำให้ test ได้ (hook / env / data) — นี่คือสิ่งที่ขอได้ถูกที่สุดตอน 02

### 6 Questions (§5) + QA decided (§6)
รวม `UNKNOWN` + `derived` ที่สำคัญ + flag ที่ต้องการคำตัดสิน → ผ่านเกณฑ์ 4 ข้อทีละข้อ
แยก **ต้องตอบก่อน 03** (เปลี่ยน capability/scope/shape) กับ **รอได้** (รายละเอียดที่ Detailing ตอบ)

### 7 Verdict + chat summary
- `NO FRAME — n frame gaps` — ทางเลือกเมื่อไม่มี frame: แยกจาก NOT READY เพราะ rank/appetite/events ไม่มีเสมอ ตัดสินจากคำถามก่อน 03 ที่เหลือเท่านั้น
- `READY` — ช่อง 1–8 มี source จริงครบ
- `DERIVED — n` — ทำงานต่อได้ แต่ n ช่องต้องให้ PM ยืนยันที่ 03
- `NOT READY — n` — มีคำถามต้องตอบก่อน 03 ที่ไม่มีใครตอบ → frame defect ส่งกลับ PM
สรุปในแชทไม่เกิน 15 บรรทัด: verdict, คำถามก่อน 03, flags สำคัญ ถ้าเป็น shadow mode เตือนให้ลง `question-log.md` เมื่อถามจริง
