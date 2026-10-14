# goldfish/ — QA-in-Solution experiment

**สถานะ: ทดลองส่วนตัว (pidshapar) ไม่ใช่ process ของทีม** — ยังไม่เสนอให้ใครแก้อะไร
เริ่ม 2026-10-04

## สมมติฐานที่ทดสอบ

> ถ้า QA ทำงานวิเคราะห์ตอน Solution ยังเป็น draft (สถานะ 02–04) แทนที่จะ analyse spec ที่เสร็จแล้ว
> (หลัง 06 ใน test-factory) คำถามที่ออกมาจะน้อยลง ตรงจุดกว่า และเปลี่ยน spec ได้ก่อนเริ่ม build
> แทนที่จะกลายเป็น "as built / as it does today" clarification หรือ bug หลัง build

ค่าเปรียบเทียบ (baseline): post-content ใน test-factory — 24 clarification หลัง 06
(~9 ข้อเป็นคำถามเรื่อง "as it does today / as built") + BUGS-TO-RAISE #1–34

## สอง skill

| Skill | ใช้ตอน | อ่าน | เขียน |
|---|---|---|---|
| `/gf-day0-intake` | Day 0 (ก่อน alignment) | frame **หรือ** PRD + Figma (ทางเลือกเมื่อไม่มี frame) | `<product>/<feature>/day0.md` |
| `/gf-solution-review` | 02 (`--sketch`) · 04 (`--detail [§n]`) | sketch.md / spec.md ที่ยังเป็น draft | `<product>/<feature>/review-<mode>-<date>.md` |

ทั้งสองตัว **อ่านอย่างเดียว** จาก console-next — ไม่เขียน `docs/solution/` ไม่ commit ที่นั่น
ข้อเสนอแก้ spec ส่งเข้าห้องเป็น PR comment / ticket chat / huddle ในฐานะ QA ของห้องตามปกติ

## สองโหมดการทดลอง

| โหมด | ทำอย่างไร | กติกา |
|---|---|---|
| **Replay** | รัน skill บน artefact ในอดีตจาก git history (`git show <sha>:docs/solution/<f>/…`) แล้วเทียบกับสิ่งที่เจอจริงทีหลัง | **Blind**: ตอนรัน ห้ามอ่านสิ่งที่เกิดหลัง sha นั้น — clarifications.json, BUGS-TO-RAISE, analysis.md, spec.md ที่ HEAD, tracker — และห้ามใช้ entry ใน knowledge ที่ `source` มาจาก feature เดียวกัน เทียบผลทีหลังเท่านั้น |
| **Shadow** | feature ถัดไปที่เข้า Solution จริง: รันคู่ไปกับงานจริง ถามในช่องทางปกติ | ทุกคำถามที่ถามจริงลง `question-log.md` |

## สิ่งที่วัด (ต่อ feature)

จาก `question-log.md`:
- จำนวนคำถามที่ถาม · ถามที่สถานะไหน (00/02/04/05/Delivery)
- **% ที่ทำให้ spec เปลี่ยน** (คำถามที่ไม่เปลี่ยนอะไร = ไม่ควรถาม)
- เวลาจนได้คำตอบ
- จาก `day0.md`: ช่องใน QA frame card ที่ `derived` แล้ว PM แก้ — ตัวชี้ความพร้อมของ frame

Replay เพิ่ม: finding ของ review ตรงกับ clarification / bug ที่เกิดจริงทีหลังกี่ข้อ (hit) · finding ที่ไม่มีคู่ (miss หรือ noise — ตัดสินทีละข้อ)

## โครงสร้าง

```
goldfish/
  README.md                 ← ไฟล์นี้
  templates/                ← day0.md · review.md · question-log.md
  knowledge/
    testability-catalogue.md  ← สิ่งที่ test ยาก/ไม่ได้ และวิธีรับมือ (QA-owned, ต้องมี source)
  <product>/<feature>/      ← output ต่อ feature
```

## เกณฑ์คำถาม (ใช้ทั้งสอง skill)

คำถามหนึ่งข้อถามได้ก็ต่อเมื่อผ่าน **ทั้ง 4**:
1. **เปลี่ยนอะไร** — คำตอบเปลี่ยน rule / state / ช่อง permission / expected ของ case ได้
2. **หาเองไม่ได้** — ไม่มีคำตอบใน frame, spec, S-CAT, knowledge, โค้ด core / console
3. **ถูกคน** — `[product]` → PM · `[system]` → Eng/Architect · หน้าจอ/copy → Design
4. **ตัดสินใจเดียว** — หนึ่ง decision ต่อข้อ ตอบได้ในไม่ถึงนาที

ไม่ผ่าน → QA ตัดสินเอง (เขียนเป็น case / assumption) หรือทิ้ง ไม่ถาม

## ถ้าได้ผล

port ทีละชิ้น: `solution-review` → test-factory (แทน solution-analysis + scope-analysis) ·
ข้อเสนอ section QA ใน sketch template → เจ้าของ console-next ·
knowledge ที่เป็นความจริงของ product → Architect (masters)
