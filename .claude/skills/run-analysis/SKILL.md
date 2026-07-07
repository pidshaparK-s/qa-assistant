---
name: run-analysis
description: 'Dispatcher/entry-point สำหรับ BA+QA pipeline — map trigger phrase ไปยัง process definition ที่ process/ แล้วทำตามนั้น (orchestration + gates ย้ายไป process แล้ว) Trigger: "วิเคราะห์ PDT-XXXX" / "สร้าง story JSON PDT-XXXX" / "สร้าง flow JSON PDT-XXXX"'
---

# run-analysis — Pipeline Dispatcher

Skill นี้เป็น **thin dispatcher** เท่านั้น — orchestration จริง (steps · gates · shared artifacts)
ย้ายไปอยู่ที่ `process/` แล้ว. เมื่อ match trigger → **อ่าน process doc ที่ระบุ แล้วทำตามนั้น**

> ทำไมแยก: skill เป็น capability atomic ที่ถูก reuse ข้าม process (เช่น phase-1-1 ถูกเรียกโดย 1-2/1-3/1-4/2-2/2-3/2-6)
> — orchestration จึงอยู่นอก skill. ดูภาพรวม 3 layer + reuse map ที่ `process/README.md`

---

## Trigger → Process

| พิมพ์ว่า | ทำตาม process | Output | Skills ที่ process เรียก |
|---|---|---|---|
| `วิเคราะห์ PDT-XXXX` / `analyze PDT-XXXX` | **`process/layer-1-ba-requirement-analysis.md`** | `qa/<epic>/<story>-analysis.md` + Clarification Register | phase-1-1 … 1-4 |
| `สร้าง story JSON PDT-XXXX` | **`process/layer-2-qa-story-authoring.md`** (STEP 0–6) | `output/PDT-XXXX-complete-jira-story.json` (Schema 1) | phase-2-1 … 2-6 |
| `สร้าง flow JSON PDT-XXXX` | **`process/layer-2-qa-story-authoring.md`** (STEP 6 · Schema 2) | `output/PDT-XXXX-user-flow.json` (Schema 2) | phase-2-3 |
| test design / test conditions | **`process/layer-3-test-design.md`** | test conditions/cases + automation judgment | phase-3-1, 3-2 |
| `meeting mode` / `โหมดประชุม` | skill `meeting-mode` (conversational — ไม่มี process/output/gate) | — | — |

> ลำดับบังคับ: Layer 1 → Layer 2 (Schema 1 → Schema 2) → Layer 3. ห้ามสลับ Schema 1/2

---

## Gates

gate ทั้งหมด (Readiness · AC Manifest · Coverage+Content · Completion · Freshness/Dropout)
นิยามกลางที่ **`process/README.md` (Gate catalog)** — ไม่ซ้ำในแต่ละ workflow อีกต่อไป

AC-coverage บังคับใช้อัตโนมัติด้วย:
```
python3 checks/ac_coverage.py qa/<epic>            # verify (coverage + content-hash + freshness)
python3 checks/ac_coverage.py qa/<epic> --update   # bless AC state หลัง sync ใหม่
```

---

## หมายเหตุ paths
- skill อยู่ที่ `.claude/skills/<name>/SKILL.md` (path เดิม `skills/<name>.md` ผิด — แก้แล้ว)
- แต่ละ skill = pure capability — ดู **"## Artifacts"** header ในไฟล์ว่า consume/produce artifact อะไร
- Schema fields + ID traceability → `00-schema-process-guide.md`, `01-complete-jira-story.json`, `02-user-flow.json`
