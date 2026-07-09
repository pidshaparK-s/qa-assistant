# BA+QA Hybrid — Skills Package

ระบบ workflow สำหรับ BA+QA ที่ทำงานทั้งหมดใน Claude Code session
ใช้ Atlassian MCP ดึง Jira story โดยตรง ไม่มี CLI, ไม่มี API แยก

---

## Project context

- Platform: Social+ (Amity)
- Jira: `socialplus.atlassian.net` — project key **PDT**
- Epic หลัก: **PDT-2636** (Mod on the go — mobile console)
- UC format: UC-01 ถึง UC-15 อยู่ใน epic นี้
- MCP: Atlassian connected — ดึง story ด้วย issue key ได้เลย

---

## Workflow triggers

| Workflow | พิมพ์ใน Claude Code | Output |
|---|---|---|
| **A** — AC Analysis | `วิเคราะห์ PDT-XXXX` | `output/PDT-XXXX-enriched-ac.md` |
| **B** — Complete Jira Story JSON | `สร้าง story JSON PDT-XXXX` | `output/PDT-XXXX-complete-jira-story.json` |
| **C** — User Flow JSON | `สร้าง flow JSON PDT-XXXX` | `output/PDT-XXXX-user-flow.json` |
| **D** — Meeting Mode | `meeting mode` หรือ `โหมดประชุม` | ไม่มี file — conversational |

ดู workflow steps ละเอียดได้ที่ skill `run-analysis` (A/B/C) และ `meeting-mode` (D)

---

## Skills index

Skills เป็น Claude skills อยู่ที่ `.claude/skills/<name>/SKILL.md` — Claude Code โหลดให้อัตโนมัติ เรียกด้วย `/<name>` หรือปล่อยให้ match จาก description เอง

| Skill | Workflow | หน้าที่ |
|---|---|---|
| `run-analysis` | A, B, C | orchestrator หลัก + gates |
| `meeting-mode` | D | real-time PM interrogation |
| `phase-1-1-requirement-interrogation` | A, D | Who/What/Why, Relationship Map, State Machine |
| `phase-1-2-three-layer-analysis` | A, D | Business Goal / User Need / System Behavior |
| `phase-1-3-happy-path-ac-enrichment` | A, B | Given gap, Then gap, enriched AC |
| `phase-1-4-edge-and-error-ac` | A, B | 4 mental models, edge/error AC |
| `phase-2-1-user-story-invest` | B | INVEST check, when to split |
| `phase-2-2-acceptance-criteria` | B | 4 scenario types, AC structure |
| `phase-2-3-business-rule-extraction` | B, C | 4 BR types, consolidate across UC |
| `phase-2-4-elicitation-techniques` | D | 5 techniques, PM challenge patterns |
| `phase-2-5-prioritization` | B | MoSCoW + QA effort scoring |
| `phase-2-6-scope-and-gap-analysis` | B | scope, assumptions, open gaps |
| `phase-3-1-automation-judgment` | — | 6 criteria: automate vs manual, suggested tools |
| `phase-3-2-br-to-test-conditions` | — | multi-source (PRD+Jira+Figma) → BR → Test Conditions |
| `phase-3-3-scenarios` | — | AC + BR + conditions → functional scenarios (1 success + alternative[]); 1 SC/AC (split per precondition-state); 1 owning scenario per BR (no re-test) |
| `qa-clarifications-review` | — | review answered clarifications → resolved/followup/ac-change/still-ambiguous |
| `qa-story-diff` | — | Jira story เปลี่ยน → diff กับ stored JSON → แนะนำ re-run phases |

---

## Clarification Gate (ใหม่)

หลังทำ phase 1.x analysis และรวบรวม open items แล้ว ให้สร้าง `qa/<feature>/1_clarifications.json`
แล้ว run `qa-clarifications-review` **ก่อน** ไปทำ BR Extraction หรือ Test Conditions

```
Phase 1.x analysis (PRD + Jira + Figma)
    ↓ open items → qa/<feature>/1_clarifications.json
    ↓ ตอบคำถาม
    ↓ qa-clarifications-review  ← gate: ต้องไม่มี still-ambiguous medium+
    ↓ phase-3-2 BR Extraction / Test Conditions
```

Output: `qa/<feature>/1_clarifications.json` (+ resolution blocks), `qa/<feature>/FOLLOWUPS.md`

---

## Gates (ห้ามข้าม ไม่มีข้อยกเว้น)

**Readiness Gate** — ก่อนเริ่ม Workflow B หรือ C
ตรวจว่า input ครบก่อน ถ้าขาดอะไร → แจ้งและหยุด ห้ามดำเนินการต่อ

**AC Manifest** — เริ่มทุก workflow ที่มี AC
List ทุก AC พร้อม ID และจำนวนรวม ก่อนเริ่มวิเคราะห์

**Completion Gate** — หลัง loop ทุก workflow
Checklist ✓/✗ ทุก AC เทียบกับ Manifest ถ้ามี ✗ → วิเคราะห์ทันที ก่อนเขียน output

**Dropout Rule** — ตลอดทุก workflow
ห้าม AC หลุดโดยไม่แจ้ง ถือเป็น critical failure ของ workflow

---

## Schema reference

ดูเมื่อใช้ schema อ้างอิงที่ `00-schema-process-guide.md`

| Schema | ไฟล์ตัวอย่าง | สร้างเมื่อไหร่ |
|---|---|---|
| Complete Jira Story (Schema 1) | `01-complete-jira-story.json` | หลัง clarification ครบ ก่อน sprint |
| User Flow JSON (Schema 2) | `02-user-flow.json` | หลัง Schema 1 สมบูรณ์แล้วเท่านั้น |

Workflow B → Schema 1 → Workflow C → Schema 2 (ลำดับนี้ห้ามสลับ)

---

## Output format สรุป

**Workflow A** (`output/PDT-XXXX-enriched-ac.md`):
```markdown
# QA-Enriched AC — {key}: {summary}

## {AC-ID}: {scenario}

### Happy Path (enriched)
Given ...  AND ...
When  ...
Then  ...  AND ...

### Clarification questions
- Q1: [observation] → [consequence] → [question]

### Edge cases
[Edge — {model}, {priority}]
Given ...
When  ...
Then  ...  AND [state หลัง action]

### Error cases
[Error — {trigger}, {priority}]
Given ...
When  ...  AND [error condition]
Then  ...  AND [state หลัง error]  AND [action ที่ทำต่อได้]

---
```

**Workflow B** (`output/PDT-XXXX-complete-jira-story.json`):
Match schema ใน `01-complete-jira-story.json` ทุก field

**Workflow C** (`output/PDT-XXXX-user-flow.json`):
Match schema ใน `02-user-flow.json` ทุก field

---

## หมายเหตุสำคัญ

- **PM's AC คือ source of truth** — ห้ามเขียนทับ ให้ต่อยอดเป็น QA-enriched version แยก
- **Write boundary (R1)** — Layer 2 เขียนเฉพาะ `qa/` + `output/` เท่านั้น · `products/<epic>/stories/*.json` เป็น **READ-ONLY input** (เขียนได้เฉพาะตอน L1 STEP 0 Jira-sync แล้ว re-bless ด้วย `checks/ac_coverage.py --update`) — บังคับกฎ source-of-truth ข้างบน การเผลอเขียนทับ PM AC จะโผล่เป็น **STALE** ใน `ac_coverage.py`
- **Judgment → ledger (R2)** — ทุก judgment call ใน L2 (split / priority / scope / วิธีตอบ PENDING) ต้อง log ลง `qa/<epic>/decisions.json` · autonomous run หยุด (HALT) ถ้ามี open human decision — `checks/decision_ledger.py --autonomous`
- **Clarification questions** ต้องมี 3 ส่วนเสมอ: observation → consequence → question
- **Edge case** ทุกข้อต้องระบุ state หลัง action ไม่ใช่แค่ UI ที่เห็น
- **Error case** ทุกข้อต้องตอบ: trigger + user เห็นอะไร + **state หลัง error** (ส่วนที่ขาดมากที่สุด)
- **ห้ามสร้าง User Flow** จาก AC ที่ยัง PENDING — ให้ใช้ Option A หรือ B จาก `00-schema-process-guide.md`

---

## Bootstrap command

Skills โหลดอัตโนมัติจาก `.claude/skills/` — ไม่ต้อง read เองแล้ว
เปิด Claude Code แล้วเรียก workflow ได้เลย เช่น `/run-analysis`, `/meeting-mode`
หรือพิมพ์ trigger เช่น `วิเคราะห์ PDT-XXXX` แล้ว Claude จะ match skill ให้เอง
