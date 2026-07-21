---
name: phase-3-6-manual-runsheet
description: 'ใช้เมื่อมี executable test cases (phase-3-4) แล้วต้อง "รันมือ" และต้องได้ manual test case ที่ import Testmo ได้ ตาม convention ทีม (sc-console-playwright manual-test-case). ยุบ EC จุกจิกหลายตัว (setup เดียวกัน) เป็น 1 case แบบ team style: name "[ Category ] Verify …", expectedResults หลาย outcome/case, priority กระจาย P1 10% / P2 25% / P3 45% / P4 20%, folderPath = Section เดี่ยว (ไม่มี suite prefix), steps มี UI ใน [ ]. ไม่ตัด coverage — trace ทุก EC ใน covers[]. Trigger: เวลาน้อย/ต้อง manual, test case ไม่ friendly ต่อการกดมือ, ต้อง import Testmo ให้เหมือนทีม. Output: qa/<epic>/**/PDT-XXXX-manual-spec.json (qa-manual-spec-v1) + PDT-XXXX-manual-testmo.csv.'
---

# Phase 3.6 — Manual Test Cases (team Testmo convention)

ยุบ **EC ระดับ automation** (จุกจิก, 1 assertion/เคส) เป็น **manual test case ที่ import Testmo ได้ ตาม convention ทีม** — โดย **ไม่ตัด coverage** (trace ทุก EC). ใช้เมื่อต้องรันมือ + ส่งของให้เหมือนเพื่อน

> **Convention ต้นทาง:** repo `sc-console-playwright` `.claude/skills/manual-test-case/SKILL.md` (Step 6 priority distribution + Step 7 writing pattern). ตามนั้นเป๊ะ — เราแค่ derive จาก EC pipeline แทนการเขียนจาก Jira ตรงๆ

## Artifacts
- **Consumes:** `*-test-cases.json` (EC ทั้งหมดของ epic) + epic release date (`customfield_10860` → suiteTopLevel)
- **Produces:** `PDT-XXXX-manual-spec.json` (schema `qa-manual-spec-v1` — team spec.json + `_schema`/`covers`) + `PDT-XXXX-manual-testmo.csv` (team columns + `QA Responsibility`; Preconditions/Expected Results เป็น bullet `- `) วางที่ epic-level (`qa/<epic>/_epic/`)
- **Tool:** `tools/export_spec_testmo_csv.py <spec.json> -o <csv>` — spec → team CSV (mirror generator.ts)
- **Cross-check:** `qa/_shared/platform-behavior-registry.json` — ตั้ง `configurations`/platforms ของแต่ละ case ตาม divergence ที่ยืนยันแล้ว (เช่น mobile-web ไม่มี pause control) แทนที่จะเดาว่าเหมือนกันหมด

## Consolidation (ลด "งานกด" ไม่ลด "สิ่งที่ตรวจ")
EC ที่ **setup เดียวกัน** (success + guard + BVA-pair) → รวมเป็น **1 case ที่มี expectedResults หลาย outcome** (เพื่อนก็ทำแบบนี้ — 1 case มี expected 6 ข้อได้). re-tolerance เป็นค่าที่คนตัดสินได้ ("~1 วิ ไม่ใช่ 3", "~10s"). batch by setup. 109 EC → ~35 case

## Team writing pattern (Step 7 — บังคับ)
| field | กฎ |
|---|---|
| **name** | `[ Category ] Verify …` — prefix `[ Category ]` (มี space ใน bracket) = scope/aspect (เช่น `[ Reveal controls ]`, `[ Pause ]`, `[ Buffering ]`); ตามด้วย `Verify`/`Confirm`; sentence case (พิมพ์เล็กหมดยกเว้นคำแรก + UI ใน `[ ]` + acronym); ไม่มีจุดท้าย |
| **folderPath** | **Section เดี่ยว** เช่น `UC1a Reveal & pause (recorded)` — **ไม่ใส่ suiteTopLevel นำหน้า** (เลือก suite folder ใน Testmo ตอน import); suiteTopLevel เก็บเป็น top-level field. Section = UCn หรือ scope (Initial State / Core Happy Path / Validation / Edge Cases …) |
| **steps** | array, 1 step/ตัว, **ไม่ใส่เลข** (generator ใส่ให้), UI element ใน `[ ]` เช่น `"Tap the [ play button ]"` |
| **expectedResults** | array — 1 observable outcome/บรรทัด; CSV render เป็น bullet `- ` |
| **preconditions** | string, `\n` คั่นแต่ละ setup step; CSV render เป็น bullet `- `; `""` ถ้าไม่มี |
| **description** | test data/context note; `""` ถ้าไม่มี |
| **configurations** | platform ที่รันได้ (`["iOS","Android","web-desktop","mobile-web"]` หรือ subset); behavior ต่าง platform → เขียนใน expectedResults |
| **priority** | P1–P4 (ดู distribution ล่าง) |
| **qaResponsibility** | ผู้รับผิดชอบ manual — default `"Fai"` → column **QA Responsibility** ใน CSV |
| **covers** | (extra field ของเรา) `[ec_id …]` — trace + gate; generator เพื่อนไม่สนใจ. **ว่าง `[]` ได้** ถ้าเป็น edge case ที่ไม่มี EC รองรับ (manual-only → gate เตือน MANUAL_ONLY ไม่ fail) |
| **acs** | (derived จาก covers) `["UC1a AC-01", …]` — AC ที่ case นี้ครอบ; **qualify ด้วย UC** เพราะ AC-0x ซ้ำข้ามทุก UC. → column **AC Covered** ใน CSV (ทีมมักถามตอนรีวิว). gate ตรวจ AC_MISMATCH ไม่ให้ drift |

## Priority distribution (Step 6 — approximate)
- **P1 ~10%** — critical path, พังคือใช้ feature ไม่ได้
- **P2 ~25%** — important, flow ที่ใช้บ่อย
- **P3 ~45%** — standard coverage (ส่วนใหญ่)
- **P4 ~20%** — edge cases, nice-to-have

## suiteTopLevel
`"D M YY - Feature Name"` จาก epic `customfield_10860` (Production Release Date) — `"2026-07-31"` → `"31 Jul 26"` (ไม่มี 0 นำหน้าวัน, เดือน 3 ตัว, ปี 2 หลัก). ดึงด้วย `getJiraIssue(<epic>, fields=["customfield_10860","summary"])`

## Schema `qa-manual-spec-v1` (per case)
```json
{
  "name": "[ Reveal controls ] Verify first tap reveals the controls overlay without toggling playback",
  "folderPath": "UC1a Reveal & pause (recorded video / LS)",
  "description": "",
  "preconditions": "A recorded video or recorded live stream (VOD) is open on the target device\nThe video is playing",
  "configurations": ["iOS","Android","web-desktop","mobile-web"],
  "steps": ["Observe the player before tapping", "Tap the center of the screen once"],
  "expectedResults": ["Before the first tap, no controls overlay is shown", "The first tap reveals the controls overlay", "Playback is unaffected"],
  "priority": "P1",
  "qaResponsibility": "Fai",
  "covers": ["EC-UC1a-001","EC-UC1a-002","EC-UC1a-003","EC-UC1a-019","EC-UC1a-020"]
}
```
Top-level: `_schema`, `featureSlug`, `suiteTopLevel`, `sources{jira,figma,notes}`, `cases[]`

## Workflow
1. รวม EC ทั้งหมดจาก `*-test-cases.json`; ดึง release date → suiteTopLevel.
2. ยุบ EC (setup เดียวกัน) เป็น case; เขียนตาม team pattern (name/steps/expectedResults/preconditions).
3. กระจาย priority ให้ใกล้ 10/25/45/20; ทุก EC ต้องอยู่ใน `covers[]` ของ ≥1 case (Dropout Rule).
4. Emit `PDT-XXXX-manual-spec.json` → run `tools/export_spec_testmo_csv.py` → CSV.
5. Gate: `python3 checks/manual_runsheet_coverage.py qa/<epic>`

## Quality bar
- **Coverage bijection:** ทุก EC ∈ ≥1 `covers[]`; ไม่มี phantom (gate: MISSING_EC / PHANTOM_EC)
- **Team rules (gate):** priority ∈ P1–P4 · folderPath present · name = `[ Category ] Verify …`
- **Human tolerances:** ห้าม assertion ที่คนวัดไม่ได้ (ms เป๊ะ) — เป็นช่วงที่คนตัดสินได้
- **ไม่แต่งพฤติกรรมใหม่:** expectedResults มาจาก EC/scenario — ขาดให้ย้อนแก้ต้นทาง

## Gate
`checks/manual_runsheet_coverage.py qa/<epic>` — อ่าน `*-manual-spec.json` เทียบ EC จาก `*-test-cases.json`: ทุก EC ถูก cover, no phantom, แต่ละ case มี name/covers/steps/expectedResults, priority enum, folderPath present.
