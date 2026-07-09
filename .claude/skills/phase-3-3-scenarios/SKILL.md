---
name: phase-3-3-scenarios
description: 'ใช้เมื่อมี Schema 1 (AC + BR) และ L3 test conditions แล้ว ต้องการประกอบเป็น functional scenarios ที่ครบ success + alternative แบบไม่หลุด — 1 scenario ต่อ acceptance criterion (แตกต่อ precondition-state ถ้า AC มีหลาย valid outcome), ไม่มี unit test, alternative enumerate ตาม black-box technique (BVA/EP/Decision-Table/State-Transition/Presence), และแต่ละ business rule ถูก exercise เต็มที่ครั้งเดียว (owns_br) — scenario อื่นที่พึ่ง BR นั้นแค่ cite ไม่ re-test (กัน over-test/ซ้ำซ้อน). Trigger: มี Schema 1 + test-design แล้ว, อยากได้ scenarios ที่พร้อมแตกเป็น test case / automation. Output: qa/<epic>/PDT-XXXX-ucN-scenarios.json (qa-scenarios-v1).'
---

# Phase 3.3 — Functional Scenarios (success + technique-driven alternatives)

ประกอบ **test conditions (L3)** เป็น **scenarios ระดับพฤติกรรม** ที่มี 1 `success` + `alternative[]` ครบทุกโหมด — พร้อมแตกเป็น test case / automation ต่อ **โดยไม่แตะ unit test**

## Artifacts
- **Consumes:** Schema 1 (`*-complete-jira-story.json` — AC + BR + br_ids) · L3 test conditions (`*-test-design.md` — TC rows + technique) · automation verdicts (`phase-3-1`)
- **Produces:** `qa/<epic>/PDT-XXXX-ucN-scenarios.json` (schema `qa-scenarios-v1`)

## What a scenario IS / IS NOT
- **IS** — one AC realized as an executable-ready behaviour: a single **`success`** outcome + an **`alternative[]`** array (one entry per distinct failure / edge mode).
- **IS NOT** — a unit test (isolated boundary rows stay as L3 conditions, never emitted here); NOT a cross-unit journey (that is `phase-3-4`).

## The two locked rules (do not violate)

**① Split per precondition-state.** If an AC has **>1 valid outcome** depending on entry state (e.g. skip-back-to-0:00 *preserves* playing → continues, OR paused → stays paused — both correct), emit **one scenario per state**, each with its own single `success`. Set `precondition_state`. A single-outcome AC → `precondition_state: null`.

**② One owning scenario per business rule.** A BR consolidated across many ACs is **fully exercised in exactly one** scenario (`owns_br`). Every other scenario that depends on it lists it in `cites_br` and does **NOT** re-assert it. → this is the anti-redundancy guarantee.
- **Exception (legitimate multi-owner):** when a rule's assertion genuinely *differs by context* (e.g. BR-05 "clamp" at the start-boundary vs the end-boundary vs mid-burst), each context is its own owner — the differing assertion is what makes it non-redundant, not a duplicate. The gate flags multi-owner as advisory so a human confirms it's context-distinct, not copy-paste.

## Alternative enumeration — by technique (run to completion, never sample)

Each scenario's `technique` comes from the governing BR / L3 condition. Enumerate `alternative[]` by:

| technique | how many `alternative[]` entries |
|---|---|
| **BVA** | 1 per distinct boundary failure mode — below-min AND above-max (2 if both bounds; 1 if single bound) |
| **EP** | 1 when all invalid partitions share one observable outcome; else 1 per class with a distinct outcome/message |
| **MultiCondition** (Decision Table) | 1 per failing rule with a *distinct root cause* (collapse rules with identical outcome + no-effect condition) |
| **StateTransition** | 1 per distinct invalid transition / rejected event |
| **Presence** | 1 (the element/state is absent or wrong) |
| **Pairwise** | ≥1 Invalid combination (4+ independent factors) |

`success` covers the happy path for **this** precondition-state; `alternative[]` covers what the technique says can go wrong. A pure `default_state` baseline AC may have `alternative: []`.

## test_layer routing (from `phase-3-1`, first match wins)
`manual` = genuinely un-automatable (real 3rd-party chooser / OS dialog / un-mockable env) · `api` = pure request/response, no UI · `e2e` = everything else (default; Playwright/Detox + mocked network/SDK). Mockable backend state → `e2e`, not `manual`. Carry the phase-3-1 nuance in `automation_note`: `"with-mock: <what>"` / `"when-stable: <why>"` / `"blocked: FU-N"`.

## Schema `qa-scenarios-v1` (per scenario)
```json
{
  "sc_id": "SC-<unit>-NN",
  "title": "short behaviour label",
  "ac_id": "AC-03",
  "precondition_state": "playing",         // null if the AC has a single valid outcome
  "technique": "BVA",                       // BVA|EP|MultiCondition|StateTransition|Presence|Pairwise
  "priority": "P1",                         // P1..P4
  "test_layer": "e2e",                      // e2e|api|manual
  "automation_note": "when-stable: web-Live net-new",   // optional
  "owns_br": ["BR-05"],                     // BRs THIS scenario authoritatively exercises
  "cites_br": ["BR-10"],                    // BRs relied on but NOT re-asserted here
  "tc_ids": ["TC-UC3-03a", "TC-UC3-03c"],   // L3 conditions consumed (traceability)
  "preconditions": ["...concrete state before the test..."],
  "steps": ["Navigate ...", "Assert: ... is ..."],       // shared path; [field] refs data
  "expected": {
    "success": "single observable outcome string",
    "alternative": ["one observable string per failure mode"]
  },
  "platform_expected": [                     // optional — when PV-1 platform variance applies
    { "platforms": ["WebUIKit-desktop"], "note": "1-Step Pause (BR-09)" }
  ],
  "pending": null                            // or {"fu":"FU-3","note":"do not assert until closed"}
}
```

## Workflow
1. **Group** L3 conditions by `ac_id` (they already carry it).
2. **Per AC** → split per precondition-state (rule ①) → per state pick the `success` (happy condition) and enumerate `alternative[]` by the technique table.
3. **Assign** `owns_br` / `cites_br` (rule ②): the scenario whose behaviour most directly tests a BR owns it; every BR in Schema 1 must be `owns_br` in ≥1 scenario.
4. **Route** `test_layer` from the phase-3-1 verdict; carry `automation_note`, `platform_expected`, `pending`.
5. **Emit** JSON → run the gate:
   `python3 checks/scenario_coverage.py qa/<epic>`

## Quality bar
- `success` = one observable string; `alternative[]` = array, one observable string per failure mode (never "should work").
- Concrete data / concrete assertions — no placeholder.
- Traceability closes: `ac_id` + `tc_ids` + `owns_br/cites_br` all resolve to Schema 1 / test-design.
- Completeness (gate): every AC → ≥1 scenario; every BR → `owns_br` in ≥1 scenario.
- Don't invent behaviour the AC/BR/condition doesn't state — a missing outcome is an upstream gap, raise it.
