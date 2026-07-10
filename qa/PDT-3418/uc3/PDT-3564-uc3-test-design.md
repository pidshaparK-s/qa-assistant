# Layer 3 Test Design — UC3: 10-Second Skip Back/Forward for Video Playback

## Automation context

Per ledger DEC-10 — video / recorded playback is the *stable* side of the epic (local media, known-length fixtures) so most TCs are `Automate` (Playwright web / Detox mobile); stream-type gating needs an SDK mock; the web rapid-tap path is a *dev delta* (debounce→accumulate) so its TCs are `Automate (when stable)`; the web-buffer skip is PENDING FU-3.

---

## BR → Test Conditions

Boundary-heavy unit — BVA is used thoroughly around `0:00` and the final frame. All boundary TCs assume a **known-length video fixture** (e.g. a 2:00 clip).

### BR-01 [permission] — Seek/±10s exists only on video/recorded, never on active Live → Decision Table

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC3-01a | BR-01 | AC-06 | flow-UC3-F08 | stream = **Live** → −10s / +10s buttons NOT rendered in the overlay | Decision Table | P1 | in-app only |
| TC-UC3-01b | BR-01 | AC-06 | flow-UC3-F08 | stream = **recorded LS** → ±10s buttons ARE rendered (contrast case) | Decision Table | P1 | recorded uses video player |
| TC-UC3-01c | BR-01 | AC-06 | flow-UC3-F08 | stream = **video** → ±10s buttons rendered | Decision Table | P2 | — |

### BR-04 [constraint] — Each skip moves playback by exactly 10 seconds → BVA / EP

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC3-02a | BR-04 | AC-01 | flow-UC3-F01 | playing at 1:00, skip-back → position exactly **0:50** (−10s), continues playing | BVA | P1 | — |
| TC-UC3-02b | BR-04 | AC-02 | flow-UC3-F02 | playing at 1:00, skip-fwd → position exactly **1:10** (+10s), continues playing | BVA | P1 | — |
| TC-UC3-02c | BR-04 | AC-01, AC-02 | flow-UC3-F01 | skip delta is exactly 10s, not 9/11 (0:30 → 0:20 / 0:40) | EP | P2 | — |

### BR-05 [constraint] — Skip clamps at content boundaries; never <0:00 or past final frame; never loops, even mid-burst → BVA

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC3-03a | BR-05 | AC-03 | flow-UC3-F03 | at 0:05, skip-back → clamps to **0:00**, never a negative position | BVA | P1 | — |
| TC-UC3-03b | BR-05 | AC-03 | flow-UC3-F03 | at 0:00 exactly, skip-back → stays 0:00 (idempotent at floor) | BVA | P2 | — |
| TC-UC3-03c | BR-05 | AC-03 | flow-UC3-F03 | at 0:10 exactly, skip-back → 0:00 (on-boundary) | BVA | P2 | — |
| TC-UC3-03d | BR-05 | AC-04 | flow-UC3-F04 | 2:00 clip at 1:55, skip-fwd → clamps to final frame **2:00**, no loop to 0:00 | BVA | P1 | — |
| TC-UC3-03e | BR-05 | AC-04 | flow-UC3-F04 | at exactly final-frame−10s, skip-fwd → final frame (on-boundary) | BVA | P2 | — |
| TC-UC3-03f | BR-05 | AC-08 | flow-UC3-F07 | rapid skip-back ×3 from 0:15 → 0:05 then clamps **0:00** mid-burst, never negative | BVA (mid-burst) | P1 | web: needs accumulate fix; mobile now |
| TC-UC3-03g | BR-05 | AC-08 | flow-UC3-F07 | rapid skip-fwd ×N near end → stops at final frame mid-burst, no loop | BVA (mid-burst) | P2 | web: needs accumulate fix; mobile now |

### BR-08 [computation] — Rapid taps accumulate (each +10s); icon always shows per-tap ±10, never the total → BVA + EP

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC3-04a | BR-08 | AC-07 | flow-UC3-F06 | playing 1:00, +10 ×3 fast → net **1:30** (accumulate, NOT 1:10) | BVA | P1 | **web debounce→accumulate regression guard**; mobile already accumulates |
| TC-UC3-04b | BR-08 | AC-07 | flow-UC3-F06 | icon shows "+10" on every tap, never "+30" (per-tap value, not total) | EP | P1 | — |
| TC-UC3-04c | BR-08 | AC-07 | flow-UC3-F06 | −10 ×3 fast → net −30s; icon shows "−10" each tap | EP | P2 | web: when accumulate fix lands |

### BR-10 [state] — Play/pause changes only via explicit user pause/play; skip is position-only → State Transition

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC3-05a | BR-10 | AC-01, AC-02 | flow-UC3-F01 | playing + skip → still **playing** (position changed, state unchanged) | State Transition | P1 | — |
| TC-UC3-05b | BR-10 | AC-05 | flow-UC3-F05 | paused + skip → position updates, stays **paused**, NO auto-resume | State Transition | P1 | — |
| TC-UC3-05c | BR-10 | AC-03 | flow-UC3-F03 | **PLAYING** at 0:05, skip-back → clamps 0:00 AND continues playing from 0:00 | State Transition | P1 | AMB-11 pair (with 05d) |
| TC-UC3-05d | BR-10 | AC-03 | flow-UC3-F03 | **PAUSED** at 0:05, skip-back → clamps 0:00 AND stays paused (NOT forced play, NOT forced pause) | State Transition | P1 | AMB-11 pair (with 05c) |
| TC-UC3-05e | BR-10 | AC-05 | flow-UC3-F05 | concurrent: skip fired during a play/pause toggle → skip never toggles play state | State Transition (concurrent) | P2 | best as unit test w/ fake timers |

### BR-12 [state] — Reaching the final frame enters the end state (paused), a terminal condition → State Transition

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC3-06a | BR-12 | AC-04 | flow-UC3-F04 | playing near end, skip-fwd past end → end state = **paused at final frame** | State Transition | P1 | — |
| TC-UC3-06b | BR-12 | AC-04, AC-05 | flow-UC3-F04 | from end state (paused at final frame), skip-back → leaves end state, position moves back, stays paused (BR-10) | State Transition | P2 | — |
| TC-UC3-06c | BR-12 | AC-04 | flow-UC3-F04 | end state does not loop to 0:00 and throws no error | State Transition | P2 | — |

### BR-15 [state] — The viewer is never left on a frozen frame with no feedback → State Transition

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC3-07a | BR-15 | AC-10 | flow-UC3-F10 | **mobile** buffering at position, tap skip → seeks + rebuffers at target, explicit loading, no stuck spinner / no crash | State Transition | P1 | code-resolved (Prisa 68329) |
| TC-UC3-07b | BR-15 | AC-11 | flow-UC3-F11 | **web** buffering, tap ±10s skip → **OBSERVE/record only, do NOT assert the seek result** (PENDING FU-3) | State Transition | P2 | blocked on FU-3 |
| TC-UC3-07c | BR-15 | AC-11 | flow-UC3-F11 | **web** buffering → 'Reconnecting' UI shown + manual scrub available (a gesture distinct from ±10s); no silent frozen frame | State Transition | P2 | known part only |

### AC-direct (ACs with no BR)

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC3-08a | — | AC-09 | flow-UC3-F09 | video loaded, UC1a overlay NOT yet revealed → no skip buttons visible | State Transition | P1 | pre-overlay baseline |
| TC-UC3-08b | — | AC-09 | flow-UC3-F09 | reveal overlay (UC1a) → skip buttons appear (transition guard) | State Transition | P2 | depends on UC1a |

---

## Automation Judgment

Sorted Automate → Automate (with mock) → Automate (when stable) → Manual; then by TC-ID.

| TC-ID | Scenario (short) | Verdict | Criteria hit | Suggested Tool | Note |
|---|---|---|---|---|---|
| TC-UC3-02a | back → exactly 0:50, playing | Automate | — | Playwright (web) · Detox (mobile) | assert timecode + play state |
| TC-UC3-02b | fwd → exactly 1:10, playing | Automate | — | Playwright · Detox | — |
| TC-UC3-02c | delta is exactly 10s | Automate | — | Jest/XCTest unit · Playwright | — |
| TC-UC3-03a | 0:05 back → clamp 0:00 | Automate | — | Playwright · Detox | known-length fixture |
| TC-UC3-03b | 0:00 back → stays 0:00 | Automate | — | Jest/XCTest unit | floor idempotency |
| TC-UC3-03c | 0:10 back → 0:00 | Automate | — | Playwright · Detox | on-boundary |
| TC-UC3-03d | 1:55 fwd → final frame, no loop | Automate | — | Playwright · Detox | known-length fixture |
| TC-UC3-03e | final−10 fwd → final frame | Automate | — | Playwright · Detox | on-boundary |
| TC-UC3-04b | icon shows "+10" not "+30" | Automate | — | Playwright · Detox | assert icon text |
| TC-UC3-05a | playing + skip → still playing | Automate | — | Playwright · Detox | — |
| TC-UC3-05b | paused + skip → stays paused | Automate | — | Playwright · Detox | no auto-resume |
| TC-UC3-05c | 0:05 PLAYING back → 0:00, playing | Automate | — | Playwright · Detox | AMB-11 |
| TC-UC3-05d | 0:05 PAUSED back → 0:00, paused | Automate | — | Playwright · Detox | AMB-11 |
| TC-UC3-05e | skip during toggle → no state flip | Automate | — | Jest/XCTest unit (fake timers) | race guard |
| TC-UC3-06a | past end → paused at final frame | Automate | — | Playwright · Detox | end state |
| TC-UC3-06b | back from end state → paused | Automate | — | Playwright · Detox | — |
| TC-UC3-06c | end state: no loop, no error | Automate | — | Playwright · Detox | — |
| TC-UC3-08a | pre-overlay → no skip buttons | Automate | — | Playwright · Detox | — |
| TC-UC3-08b | reveal → skip buttons appear | Automate | — | Playwright · Detox | cross-unit UC1a |
| TC-UC3-01a | Live → skip buttons absent | Automate (with mock) | criteria 5 (mock SDK stream type) | Playwright/Detox + SDK stub | — |
| TC-UC3-01b | recorded LS → skip buttons present | Automate (with mock) | criteria 5 (mock SDK stream type) | Playwright/Detox + SDK stub | contrast |
| TC-UC3-01c | video → skip buttons present | Automate (with mock) | criteria 5 (mock SDK stream type) | Playwright/Detox + SDK stub | — |
| TC-UC3-07a | mobile buffer → seek-and-rebuffer | Automate (with mock) | criteria 5 (network throttle/mock) | Detox + network-link conditioner | code-resolved |
| TC-UC3-07c | web 'Reconnecting' UI shown | Automate (with mock) | criteria 5 (network stall mock) | Playwright + route stall | known part |
| TC-UC3-03f | rapid back ×3 → clamp 0:00 mid-burst | Automate (when stable) | criteria 4 (web accumulate fix pending) | Playwright · Detox | mobile now; web after BR-08 fix |
| TC-UC3-03g | rapid fwd ×N → final frame mid-burst | Automate (when stable) | criteria 4 (web accumulate fix pending) | Playwright · Detox | mobile now; web after BR-08 fix |
| TC-UC3-04a | +10 ×3 → net 1:30 (accumulate) | Automate (when stable) | criteria 4 (web debounce→accumulate) | Playwright · Detox | regression guard for web fix; mobile now |
| TC-UC3-04c | −10 ×3 → net −30s | Automate (when stable) | criteria 4 (web debounce→accumulate) | Playwright · Detox | web after fix; mobile now |
| TC-UC3-07b | web skip during buffer → seek result | Manual (blocked on FU-3) | criteria 1 (expected result undefined — PENDING FU-3) | — | observe/record only until FU-3 closes |

---

## QA must confirm

- **FU-3 (blocker for TC-UC3-07b):** the exact ±10s-skip-during-buffer behaviour on **web** is unconfirmed (Owner: Web Engineering). Until it closes, 07b is observe-only — do NOT write an assertion. Mobile (07a) is settled.
- **Web debounce→accumulate dependency (BR-08, ledger DEC-09/GAP-07):** TC-UC3-04a/04c/03f/03g are written to the *target* accumulate behaviour and are the **regression guard** for the web fix. On web they cannot pass until the fix lands → schedule them `when stable`. Mobile can automate now. Confirm the web fix is in the sprint before wiring these to CI.
- **Automation budget / prioritisation:** if capacity is limited, start with the P1 `Automate` (plain) set — the seek-amount (02x), boundary-clamp (03a/03c/03d), state-preservation (05a–05d), and end-state (06a) TCs give the highest correctness coverage at lowest flake risk.
- **Flakiness / external deps:** mock-dependent TCs (01a–01c SDK stream type; 07a/07c network) rely on stable stubs — confirm the SDK stream-type stub + a network-throttle harness exist for the target platforms.
- **Out of scope (do NOT author a TC):** Android **OS-native** transport scrub of a Live stream (lock screen / notification / car unit) is a separate bug — **FU-4 / AMB-05**, independent of AC-06. Tracked in FOLLOWUPS, not here.
- **Cross-unit dependency:** TC-UC3-08b and every "overlay revealed" precondition depend on **UC1a** shipping first (build order UC1a → UC3).

---

## Coverage

- **BR→TC:** 7/7 BRs have ≥1 TC (BR-01, BR-04, BR-05, BR-08, BR-10, BR-12, BR-15) — none missing.
- **AC→TC:** 11/11 ACs touched (AC-01…AC-11) — none untouched.
- **Verdicts:** Automate 19 · Automate (with mock) 5 · Automate (when stable) 4 · Partial 0 · Manual 1 (blocked on FU-3) · **Total 29**.
- **Automatable in CI:** 28/29 (only TC-UC3-07b blocked, pending FU-3).
