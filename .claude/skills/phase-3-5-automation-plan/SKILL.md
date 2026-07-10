---
name: phase-3-5-automation-plan
description: 'ใช้เมื่อมี executable test cases (phase-3-4) แล้ว ต้องการตัดสินว่า EC ไหน automate ได้/ไม่ได้ แล้วทำเป็น AT plan — ต่อ EC ได้ 1 disposition: at_status "wait for automated" (→ status Automate, มี target spec) หรือ "cannot automated" (→ status Manual, มี blocker+reason). ใช้ phase-3-1 6 criteria ตัดสิน; livestream/live = cannot automate เสมอ. Trigger: มี *-test-cases.json แล้ว, ต้องแบ่ง automate vs manual, วางแผน automation suite, prioritize สำหรับ CI. Output: qa/<epic>/PDT-XXXX-ucN-automation-plan.json (qa-automation-plan-v1) + rollup AUTOMATION-PLAN.md. ไม่มี id ใหม่ — reuse ec_id (bijection กับ test-cases).'
---

# Phase 3.5 — Automation Plan (from Executable Cases)

ตัดสินทุก **EC** ว่า **automate ได้ (Automate)** หรือ **ต้อง manual (Manual)** พร้อมเหตุผล + (ถ้า automate) target spec ที่จะไปเขียนจริง — ได้ออกมาเป็น **AT plan** ที่ทีมใช้วางแผน automation suite

## Artifacts
- **Consumes:** executable cases (`*-test-cases.json` — EC ที่มี `ec_id`, `test_layer`, `name`, `steps`, `expected_result`) + context (platform / feature stability / external deps)
- **Produces:** `qa/<epic>/PDT-XXXX-ucN-automation-plan.json` (schema `qa-automation-plan-v1`) + rollup `qa/<epic>/AUTOMATION-PLAN.md`
- **Reuses:** `phase-3-1-automation-judgment` (6 criteria) เป็นเกณฑ์ตัดสิน

## Status model (คำศัพท์)
ต่อ EC มี 2 field คู่กัน — ต้อง consistent เสมอ (gate บังคับ):

| at_status | → status | ความหมาย |
|---|---|---|
| `cannot automated` | **Manual** | automate ไม่ได้ (ติด blocker) — คนรันเอง |
| `wait for automated` | **Automate** | automate ได้ แต่ยังไม่ได้เขียน code (คือ AT plan / backlog) |
| `automated` | **Automate** | เขียน spec แล้ว (ใช้ตอน phase ถัดไปเมื่อมี code) |

## เกณฑ์ตัดสิน (จาก phase-3-1 — ตรวจตามลำดับ)
Manual (`cannot automated`) ถ้าติด **blocker** ข้อใดข้อหนึ่ง — ใช้ blocker code ต่อไปนี้ (gate ตรวจ enum):

| blocker | phase-3-1 | เมื่อไหร่ |
|---|---|---|
| `live-broadcast` | criteria 5 | ต้องมี **active live stream จริง** (RTMP broadcast / live-edge / real-time) — เปิด/join live แบบ deterministic ไม่ได้ → flaky/blocked. **livestream ทุกข้อเข้าข้อนี้ = Manual เสมอ** |
| `wallclock-duration` | criteria 5 | ต้องรอเวลาจริงหลายนาที (long pause / long-run) — ช้า/flaky เกินคุ้ม |
| `observe-only` | criteria 1/6 | ไม่มี oracle ให้ assert — observe/record เท่านั้น (assumption ยังไม่ปิด หรือ "do NOT assert") |
| `web-platform-timing` | criteria 5 | reconnect/buffer timing บน web ไม่ deterministic บน shared env |

ไม่ติด blocker เลย → `Automate` (`wait for automated`) + ต้องมี **target** spec

> **กฎ livestream (จาก user):** อะไรที่เป็น live stream → `cannot automated` → Manual เสมอ. เหตุผลตรงกับ CANNOT-AUTOMATE.md ของ repo web เอง: *"requires a live livestream… no way to start/join deterministically → Manual/blocked"*. recorded video / recorded-LS (VOD) ที่ seek ได้ = automate ได้ตามปกติ

## Schema `qa-automation-plan-v1` (per entry)
```json
{
  "ec_id": "EC-UC1a-001",           // reuse — ไม่มี id ใหม่ (bijection กับ test-cases)
  "sc_id": "SC-UC1a-01", "ac_id": "AC-01",
  "path": "success", "priority": "P1", "test_layer": "e2e",
  "at_status": "wait for automated", // cannot automated | wait for automated | automated
  "status": "Automate",              // Manual | Automate  (ต้อง consistent กับ at_status)
  "blocker": null,                    // Manual: 1 ใน 4 code ด้านบน · Automate: null
  "criteria": null,                   // phase-3-1 criteria ที่ติด (Manual) · null (Automate)
  "reason": "…เหตุผลเป็นประโยค…",
  "tool": "WebdriverIO + Appium (iOS + Android)",  // Manual = "—"
  "target": {                          // Automate เท่านั้น (Manual = null)
    "repo": "social-plus-mobile-native-sampleapp-webdriverio",
    "spec": "tests/tap-to-pause/uc1a-recorded-reveal-controls.spec.ts",
    "tag": "@EC-UC1a-001"             // ต้อง == "@"+ec_id (spec-keying / bijection)
  }
}
```

## Workflow
1. Read `*-test-cases.json` ต่อ unit + ยืนยัน context (platform, stability, deps). ถ้าขาด → default + ระบุ assumption (phase-3-1).
2. ต่อ EC ตรวจ 6 criteria → ตัดสิน Automate/Manual; Manual ใส่ blocker+reason, Automate ใส่ target (tag = `@`+ec_id).
3. Emit plan JSON ต่อ unit (1 entry ต่อ EC — **ห้ามตก** แม้แต่ตัวเดียว = Dropout Rule).
4. Emit rollup `AUTOMATION-PLAN.md`: summary, spec map (Automate), manual list by blocker.
5. Gate: `python3 checks/automation_plan_coverage.py qa/<epic>`

## Quality bar
- **bijection:** plan ⋈ test-cases 1:1 — ทุก EC มี disposition, ไม่มี phantom, ไม่มีตก (gate: MISSING_EC / PHANTOM_EC).
- **consistency:** at_status ↔ status ตรงกันเสมอ (gate: INVARIANT).
- **livestream = Manual:** `blocker=live-broadcast` ⟹ Manual (gate: LIVE_RULE).
- **spec-keying:** Automate target.tag == `@`+ec_id (gate: TAG_KEY) — เพื่อ trace EC ↔ automated test ตอนเขียน code จริง.
- Manual ทุกข้อมี blocker (1 ใน 4) + reason; Automate ทุกข้อมี target ครบ repo/spec/tag.
- **ห้าม over-mark automate:** ถ้าไม่แน่ใจว่า simulator/harness ทำได้ → Manual + ระบุ (อย่าเดาว่า automate ได้).

## Gate
`checks/automation_plan_coverage.py qa/<epic>` — pair test-cases ↔ automation-plan by filename stem; bijection, enum, INVARIANT, MANUAL_FIELDS, AUTOMATE_TARGET, TAG_KEY, LIVE_RULE.
