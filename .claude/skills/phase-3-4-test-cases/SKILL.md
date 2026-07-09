---
name: phase-3-4-test-cases
description: 'ใช้เมื่อมี scenarios (phase-3-3) แล้ว ต้องการแตกเป็น executable test cases ที่ tester/automation รันได้ทันที — ต่อ scenario ได้ 1 success case + 1 case ต่อ expected.alternative[] แต่ละข้อ (เป๊ะ N ตัว: ไม่ขาด=gap, ไม่เกิน=over-test), steps เป็น concrete (แทน [field] ด้วยค่าจริง), test_data ค่าจริง, expected_result คัดจาก scenario.success / alternative[i]. Trigger: มี *-scenarios.json แล้ว, อยากได้ test case พร้อมรัน/ส่งต่อ automation. Output: qa/<epic>/PDT-XXXX-ucN-test-cases.json (qa-test-cases-v1). id = EC-<unit>-NNN (Executable Case — แยกจาก TC=L3 condition และ SC=scenario).'
---

# Phase 3.4 — Executable Test Cases (from Scenarios)

แตก **scenario (SC)** เป็น **executable case (EC)** ที่ concrete พอให้ tester หรือ automation รันได้ทันที — พร้อมส่งต่อ `phase-3-5` automation

## Artifacts
- **Consumes:** scenarios (`*-scenarios.json` — SC ที่มี `expected.success` + `expected.alternative[]`, `steps`, `test_layer`)
- **Produces:** `qa/<epic>/PDT-XXXX-ucN-test-cases.json` (schema `qa-test-cases-v1`)

## What an EC is
Concrete runnable expansion of one scenario path: **1 `success` EC** + **1 `alternative` EC per entry in `expected.alternative[]`**. `steps` มีค่าจริง (แทน `[field]` แล้ว), `test_data` ค่าจริง, `expected_result` คัดตรงจาก scenario.

> **id เตือน:** `EC-` = Executable Case (this layer). อย่าสับสนกับ `TC-` (L3 test condition, phase-3-2) และ `SC-` (scenario, phase-3-3). chain: `AC → SC → EC`.

## Derivation rules (บังคับ — gate ตรวจ)
1. **นับให้เป๊ะ:** ต่อ SC → **1 EC `path:"success"`** (expected = `SC.expected.success`) **+ 1 EC `path:"alternative"` ต่อ 1 entry ใน `expected.alternative[]`** (expected = `alternative[i]`, ตั้ง `alt_index:i`). จำนวน alternative EC = `len(expected.alternative[])` **เป๊ะ** — ไม่ขาด (gap) ไม่เกิน (over-test). ถ้า `alternative:[]` → มีแค่ success EC.
2. **steps concrete:** เอา `SC.steps` มาแทน `[field]` ด้วยค่าใน `test_data`; ทุก assertion ต้อง observable (`Assert: <thing> is <state>`), ห้าม "should work".
3. **test_data ค่าจริง:** ค่าจริง (timecode / play-state / stream-type / role / viewport …) — ห้าม `{}`, ห้าม placeholder. ดึงจาก preconditions/steps ของ scenario.
4. **inherit:** `sc_id`, `ac_id`, `test_layer`, `priority` จาก scenario.
5. **pending SC (observe-only):** alternative EC ของ scenario ที่ `pending` ให้ `expected_result` ระบุ "observe/record — do NOT assert until FU-N closes" (ยังต้องมี EC เพื่อ traceability แต่ไม่ assert).

## id + name
- `ec_id`: `EC-<unit>-NNN` (running ต่อ unit).
- `name`: `[<surface>] Verify <behaviour> (<condition>)` — success = คำเชิงบวก; alternative = ระบุเงื่อนไข failure/edge สั้น ๆ. ห้าม "Check/Should/You".

## Schema `qa-test-cases-v1` (per case)
```json
{
  "ec_id": "EC-UC3-003",
  "sc_id": "SC-UC3-03a",            // → scenario (traceability)
  "ac_id": "AC-03",                  // inherited from scenario
  "path": "success",                 // success | alternative
  "alt_index": null,                 // path=alternative → 0-based index into scenario.expected.alternative[]; success → null
  "name": "[Video player] Verify skip-back at 0:05 while playing clamps to 0:00 and continues",
  "priority": "P1",                  // P1..P4 (inherit scenario)
  "test_layer": "e2e",               // inherit scenario
  "preconditions": ["...concrete..."],
  "test_data": { "position": "0:05", "play_state": "playing" },
  "steps": ["Navigate ...", "Tap ...", "Assert: ... is ..."],
  "expected_result": "single observable string (= scenario.expected.success OR .alternative[alt_index])"
}
```

## Workflow
1. Read `*-scenarios.json` ต่อ unit.
2. ต่อ SC → derive success EC + N alternative EC (rule 1).
3. แทน `[field]` ด้วย `test_data`, ทำ expected observable.
4. Emit `qa/<epic>/PDT-XXXX-ucN-test-cases.json`.
5. Gate: `python3 checks/test_case_coverage.py qa/<epic>`

## Quality bar
- **จำนวน alternative EC = จำนวน `expected.alternative[]` เป๊ะ** (gate-enforced — นี่คือกลไกกัน over-test).
- concrete data + observable expected, no placeholder.
- `sc_id`/`ac_id` resolve; `alt_index` ครบ 0..N-1 ไม่ซ้ำ.
- ห้ามแต่งพฤติกรรมที่ scenario ไม่ได้ระบุ — ถ้า scenario ขาด ให้ย้อนไปแก้ scenario ไม่ใช่แต่งใน EC.

## Gate
`checks/test_case_coverage.py qa/<epic>` — ต่อ SC: ≥1 success EC + **เป๊ะ N** alternative EC (N=len(alternative[])); ref resolve; steps/test_data/expected ไม่ว่าง; alt_index ครบ.
