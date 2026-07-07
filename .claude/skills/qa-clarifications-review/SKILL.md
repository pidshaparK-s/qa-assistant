---
name: qa-clarifications-review
description: 'ใช้ skill นี้หลังจากที่ผู้ใช้ตอบคำถามใน qa/<feature>/1_clarifications.json แล้ว Re-reads คำตอบแต่ละข้อในบริบท — ดึง design screenshots ใหม่เป็น ground truth — และ classify แต่ละ medium+ clarification เป็น resolved / followup / ac-change / still-ambiguous เขียน resolution block กลับเข้า 1_clarifications.json Route follow-ups ไปที่ FOLLOWUPS.md และ AC changes ไปที่ products/ (หรือ qa/new-product/ac/) Trigger เมื่อ: "review the clarification answers for <feature>", "are the answers clear enough", หลังตอบ 1_clarifications.json และก่อนทำ BR Extraction หรือ Test Conditions'
argument-hint: '<feature-slug> — must match an existing qa/<feature-slug>/ folder with an answered 1_clarifications.json'
---

# Clarification Review Gate

คุณเป็น Senior QA Engineer ทบทวนคำตอบ clarification ก่อนให้ pipeline ดำเนินต่อ

> **หลักการหลัก: "Answering is not resolving"**
> คำตอบที่ได้อาจยังคลุมเครือ อ้าง screenshot ที่ไม่ได้ดู หรือเปลี่ยน AC โดยไม่รู้ตัว
> Skill นี้พิสูจน์ว่า ambiguity ปิดจริง ก่อนให้ไปต่อ

Run นี้ **ระหว่าง phase 1.x analysis กับ phase 3.x test conditions** ทุกครั้งที่มีคำตอบใหม่

---

## Inputs (read-only ยกเว้น outputs ด้านล่าง)

| Source | Path |
|--------|-------|
| Answered clarifications | `qa/<feature>/1_clarifications.json` |
| Design screenshots (ground truth) | `products/<epic>/design/**` หรือ `qa/design-screenshot/**` |
| Stories + acceptance criteria | `products/<epic>/stories/<story>.json` |
| Existing follow-ups | `qa/<feature>/FOLLOWUPS.md` |

**Gate**: เฉพาะ `medium` / `high` / `critical` severity เท่านั้นที่ block pipeline
`low` severity เป็น advisory — skip ได้

---

## Workflow

### Step 1 — Re-read ทุก medium+ คำตอบในบริบท

สำหรับ clarification แต่ละข้อ severity medium+:

- **คำตอบตอบคำถามที่ถามจริงไหม?** คำตอบที่บอก "maybe / TBD / ไม่แน่ใจ"
  หรือตอบคนละประเด็น **ไม่ถือว่า resolve**
- **คำตอบอ้าง screenshot ไหม?** ถ้าใช่ → **เปิด screenshot ดู** และ extract
  specifics ที่ ambiguity ถาม (timeout value, layout state, behavior ที่แน่ชัด)
  ถ้า screenshot ที่อ้างไม่แสดงสิ่งที่ claim → item นั้น `still-ambiguous`
- **คำตอบเปลี่ยน AC ไหม?** เช่น "ควรจะเทส..." หรือ "AC ไม่ได้อัปเดต แต่ควรจะ..."
  → ต้อง classify เป็น `ac-change`

### Step 2 — Classify แต่ละข้อเป็น resolution.status

| status | ใช้เมื่อ | Side-effect ที่ต้องทำ |
|--------|----------|----------------------|
| `resolved` | คำตอบ (+ screenshot ที่ดูแล้ว) ปิด ambiguity ได้จริง | ระบุ `verified_refs` ทุก screenshot ที่อ้าง |
| `followup` | คำตอบ defer ไป PM/Designer ยังสรุปไม่ได้ | เพิ่ม `FU-N` ใน FOLLOWUPS.md; set `followup_ref` |
| `ac-change` | คำตอบเปลี่ยน/เพิ่ม rule ใน AC | แก้ criterion ใน `products/<epic>/stories/<story>.json`; set `ac_change_ref` |
| `still-ambiguous` | คำตอบคลุมเครือ นอกประเด็น หรือ screenshot ไม่ตรง | **Blocks pipeline** — รายงานให้ user re-clarify |

คำตอบเดียวอาจมีทั้ง AC edit และ screenshot verified — ใช้ status ที่ dominant ที่สุด

### Step 3 — เขียน resolution block (additive เท่านั้น)

Edit `qa/<feature>/1_clarifications.json` — **ห้ามเขียนทับ `answer`** — เพิ่ม `resolution` object:

```jsonc
{
  "id": "uc1-C1",
  "severity": "high",
  "answer": "Engineering confirm 3s timeout",
  "resolution": {
    "status": "resolved",
    "rationale": "Engineering confirmed auto-dismiss timeout = 3 seconds.",
    "verified_refs": [],
    "ac_change_ref": null,
    "followup_ref": null
  }
}
```

Field rules:
- `status` — `resolved | followup | ac-change | still-ambiguous`
- `rationale` — หนึ่งประโยค: อะไรปิด ambiguity หรือทำไมถึง block
- `verified_refs` — ทุก screenshot path ที่อ้างในคำตอบ (ต้อง exist บน disk)
- `followup_ref` — required ถ้า `status == followup`; FU-N id ใน FOLLOWUPS.md
- `ac_change_ref` — required ถ้า `status == ac-change`; path ของ story JSON ที่แก้

### Step 4 — Propagate side-effects

- **followup** → เพิ่ม `FU-N` section ใน `qa/<feature>/FOLLOWUPS.md`
  (source = clarification id; blocked item; action ที่ต้องทำ)
- **ac-change** → แก้ criterion ใน story JSON (products/ หรือ qa/new-product/ac/)
  และ note ว่า BC ที่เกี่ยวข้องจะ reference file นั้น

### Step 5 — Gate + รายงาน

หลัง classify ครบ รายงาน:
- จำนวนต่อ status (resolved N / followup N / ac-change N / still-ambiguous N)
- รายการ `still-ambiguous` ที่ user ต้อง re-answer (block pipeline)
- FOLLOWUPS.md entries ที่เพิ่ม
- Story JSON files ที่แก้

ถ้ามี `still-ambiguous` → **หยุด** ห้ามไปต่อ phase 3.x

---

## Quality bar

- **คำตอบที่อ้าง screenshot = ยังไม่ verify จนกว่าจะเปิดดูจริง**
  resolve หมายถึง transcribe specifics เข้า rationale ไม่ใช่แค่ link ไว้
- **ห้าม mark `resolved` เพื่อให้ผ่าน gate** คำตอบคลุมเครือ = `still-ambiguous`
- **Additive only** — preserve คำตอบของ user verbatim; `resolution` block เป็นของ QA

---

## Output paths

```
qa/<feature-slug>/
├── 1_clarifications.json    # + resolution block ต่อ medium+ item (answer preserved)
└── FOLLOWUPS.md             # FU-N entries สำหรับ deferred items

products/<epic>/stories/<story>.json  # AC edits สำหรับ ac-change items
```
