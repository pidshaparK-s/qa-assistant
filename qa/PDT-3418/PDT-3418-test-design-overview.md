# Layer 3 — Test Design Overview · PDT-3418

**STEP 0 input-select:** Schema 1 is canonical + gated (G1/G2/R2 green, 40 ACs / 32 BR-instances / 15 unique BRs). → normal path: **BRs come from L2 (do NOT re-extract)**; `phase-3-2` does BR→Test-Condition only. AC coverage already guaranteed by Schema 2 (G2).

**Output:** per-unit `PDT-XXXX-ucN-test-design.md` — BR→TC table + Automation Judgment table + QA-must-confirm + coverage rollup.

---

## TC-ID scheme

`TC-<unit>-<NN>` sequential per unit (e.g. `TC-UC3-01`); suffix `a/b/c` for a boundary/decision family from one BR (e.g. `TC-UC3-07a`, `-07b`). Every TC row carries: `BR-ID · ac_id(s) · flow_id(s) · condition · technique · priority · platform-note`.

**Technique by BR type** (from `phase-3-2`):
| BR type | technique |
|---|---|
| permission | Decision Table |
| constraint | BVA / EP |
| computation | BVA + EP |
| state | State Transition (+ concurrent-action TC where relevant) |

ACs with `br_ids: []` (QA default_state baselines) still get ≥1 TC derived directly from the AC.

**Priority:** P1 = happy path + hard blockers + boundary correctness · P2 = alternative/error · P3 = rare/edge.

---

## Automation context (drives every verdict — see ledger DEC-10)

| Factor | Value |
|---|---|
| **Platforms** | UIKit iOS · Android · React Native · Flutter · WebUIKit · (Desktop web = 1-Step Pause, BR-09) |
| **Stability** | **MIXED** — mobile video/recorded player = *stable* · web overlay behaviours *changing* (BR-03 3s→1s, BR-08 debounce→accumulate) · **web-Live overlay = NET-NEW / not yet validated** |
| **External deps** | Social+ SDK (stream type/room status) · live-broadcast infra · network layer. Live tests need a real broadcast + network manipulation → *complex/flaky setup*. Video/recorded = local media → *stable*. |
| **Environment** | video/recorded = *stable* · **Live = flaky** (broadcast + network-drop + host-ends race + chat/video re-sync) |

**Verdict implications (guidance for units):**
- **video/recorded interactions** (UC1a, UC3) → mostly `Automate` (Playwright web / Detox mobile); known-length fixtures for seek/boundary.
- **stream-type gating** (skip buttons hidden on Live, UC1b/UC3) → `Automate (with mock)` — mock SDK stream=Live vs recorded.
- **Live playback / pause-resume** (UC2) → resume-to-live = assert **≈ live within tolerance** not exact; network-drop / host-ends / chat-resync = `Automate (with mock)` or `Manual` (flaky live env); some `Manual (real-device-farm)`.
- **timing** (1s auto-dismiss, rapid-tap accumulate) → `Automate` but note flake risk; web debounce→accumulate TC = **regression guard for the BR-08 fix**.
- **app backgrounding** (UC1 AC-11/AC-10) → `Partial` / confirm on real device first.
- **PENDING** (UC3 AC-11 web-buffer FU-3) → TC = **observe/record, do NOT assert**; verdict `Manual (blocked on FU-3)`.

---

## L3 gate (to codify next)

**BR→TC coverage:** every br_id in a unit's Schema 1 has ≥1 Test Condition. + Completion (every ac_id touched). Rollup below is filled after the per-unit docs land.

## Per-unit index + coverage rollup

| Unit | file | BRs | BR→TC | ACs | AC→TC | TCs | Automate* | Partial | Manual |
|---|---|---|---|---|---|---|---|---|---|
| UC1a | PDT-3562-uc1a-test-design.md | 8 | 8/8 | 11 | 11/11 | 27 | 25 | 2 | 0 |
| UC1b | PDT-3562-uc1b-test-design.md | 7 | 7/7 | 10 | 10/10 | 21 | 20 | 1 | 0 |
| UC2  | PDT-3563-uc2-test-design.md  | 10 | 10/10 | 8 | 8/8 | 28 | 25 | 0 | 3 |
| UC3  | PDT-3564-uc3-test-design.md  | 7 | 7/7 | 11 | 11/11 | 29 | 28 | 0 | 1 |
| **Total** | | **32** | **32/32** | **40** | **40/40** | **105** | **98** | **3** | **4** |

BRs column = per-unit BR-instances (15 unique BRs, consolidated across units). **\*Automate** = all automate-family (plain + with-mock + when-stable). The **4 Manual** = UC2 host-end race · UC2 long-pause tolerance on real broadcast · UC2 per-platform resume on real live edge (real-device-farm) · UC3 web-skip-during-buffer (blocked on FU-3). Gate `checks/br_tc_coverage.py` → green (BR + AC coverage 100%).
