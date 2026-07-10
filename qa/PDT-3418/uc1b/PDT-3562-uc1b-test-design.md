# Layer 3 Test Design — UC1b: Tap to Reveal Controls — 'Live' Live Stream

> Source of truth: `PDT-3562-uc1b-complete-jira-story.json` (7 BRs / 10 ACs) + `PDT-3562-uc1b-user-flow.json` (F01–F11). BRs used AS-IS from L2 — not re-extracted. UC1b = the **'Live' player component**; **web-Live has NO reveal-controls overlay today (NET-NEW — bare `<video>`+Plyr pause/play, `LivestreamPlayer.tsx:115-123`)**. `flow_id` shortened `F0X` = `flow-UC1b-F0X`. TC-ID = `TC-UC1b-NN`; `a/b/c` suffix = a boundary/decision family from one BR.

## Automation context

Per **DEC-10**: platforms iOS / Android / RN / Flutter / WebUIKit (desktop = 1-Step Pause, BR-09); stability **MIXED — the web-Live reveal overlay + 1s auto-dismiss are NET-NEW / not-yet-validated**, so reveal/overlay/auto-dismiss TCs → **Automate (when stable)** ("web-Live net-new — first-time verify"), while stream-type gating (seek-absent on Live, `room_status=live`) needs an **SDK mock** → **Automate (with mock)** (a real Live broadcast + network manipulation is flaky); app backgrounding (AC-10) → **Partial + real-device confirm**; Live resume-to-live is **owned by UC2** — never asserted here.

## BR → Test Conditions

### BR-01 [permission] — seek/skip (±10s) controls exist only on a video / recorded LS, never on an active Live stream → Decision Table

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC1b-01a | BR-01 | AC-04 | F02 | SDK stream=Live, overlay revealed while **playing** → assert NEITHER −10s NOR +10s skip button present in the view/DOM | Decision Table | P1 | mock SDK stream=Live; web-Live overlay net-new — first-time verify |
| TC-UC1b-01b | BR-01 | AC-04 | F07 | SDK stream=Live, **paused** (overlay visible, play icon) → −10s/+10s skip buttons ABSENT — the explicit AC-04 negative | Decision Table | P1 | mock SDK stream=Live; iOS/Android Live overlay exists, web-Live net-new |
| TC-UC1b-01c | BR-01 | AC-04 | F07 (contrast) | Contrast: mock SDK stream=recorded/video → −10s/+10s skip buttons PRESENT → proves the gate is stream-type driven | Decision Table | P2 | recorded/video path = UC1a/UC3 (stable); positive row confirms BR-01 |

### BR-03 [constraint] — overlay auto-dismisses after 1s of no interaction while playing; countdown restarts on every control interaction → BVA / EP

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC1b-02a | BR-03 | AC-03 | F05 | Playing + overlay visible, no interaction, advance to 999ms (< 1s) → overlay STILL visible; playback continues | BVA | P1 | just-below 1s boundary; web-Live net-new |
| TC-UC1b-02b | BR-03 | AC-03 | F05 | Playing + overlay visible, no interaction, advance to 1000ms → overlay auto-dismisses; playback continues | BVA | P1 | at 1s boundary; **REGRESSION GUARD** — web must be 1000ms (currently 3000ms `VideoPlayerControls.tsx:60-70`), iOS already 1s; web-Live net-new |
| TC-UC1b-02c | BR-03 | AC-07 | F06 | Control interaction at 800ms → 1s countdown restarts, overlay still visible at 1000ms; overlay auto-dismisses 1000ms after the LAST interaction | EP | P2 | timer-reset class; web-Live net-new |

### BR-06 [constraint] — controls behaviour identical across all in-scope surfaces (surface-invariant, NOT platform-invariant) → EP

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC1b-03a | BR-06 | AC-05 | F08 | Surface=inline feed → reveal / tap-outside dismiss / 1s auto-dismiss / pause all behave per F02·F04·F05·F07 | EP | P2 | parameterize over surface, hold platform fixed; web-Live net-new |
| TC-UC1b-03b | BR-06 | AC-05 | F08 | Surface=fullscreen/gallery → outcomes IDENTICAL to inline (same reveal/dismiss/pause results) | EP | P2 | surface-invariant ≠ platform-invariant — desktop still differs (BR-09/F03) |

### BR-09 [computation] — first-tap model is platform-dependent: mobile reveals (no toggle); desktop (Web UIKit) = direct 1-step pause → BVA + EP

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC1b-04a | BR-09 | AC-01 | F02 | **Mobile** (iOS / Android / web-mobile): first tap on a playing Live player → overlay reveals, playback CONTINUES (`video.paused===false`), central icon = PAUSE | EP | P1 | mobile reveal class; web-mobile-Live net-new — first-time verify; never reuse desktop expected |
| TC-UC1b-04b | BR-09 | AC-01 | F03 | **Desktop** (Web UIKit): first click on a playing Live player → direct 1-step pause (`video.paused===true`), PLAY icon; mobile reveal branch NOT taken | EP | P1 | desktop 1-Step Pause (PV-1); mock SDK stream=Live; separate expected per form factor |

### BR-10 [state] — play/pause state changes only via an explicit user pause/play action or a terminal room state; no implicit operation toggles it → State Transition

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC1b-05a | BR-10 | AC-01 | F02 | S(playing) + tap-to-reveal (mobile) → state stays `playing` (reveal is NOT an implicit pause) | State Transition | P1 | no-op transition; web-mobile-Live net-new |
| TC-UC1b-05b | BR-10 | AC-04 | F07 | S(playing) + explicit central pause tap → transition `playing → paused` (the only valid user trigger) | State Transition | P1 | iOS/Android 2-step; **web-mobile CANNOT pause Live** (platform table 68264); desktop reaches paused 1-step (04b) |
| TC-UC1b-05c | BR-10 | AC-02 | F04 | S(playing) + overlay visible + tap outside the button → overlay hidden but state stays `playing` (dismiss is NOT an implicit pause) | State Transition | P1 | web-Live net-new; boundary = rendered 64×64 (FU-2 resolved) |
| TC-UC1b-05d | BR-10 | AC-03 | F05 | S(playing) + 1s auto-dismiss timer fires → overlay hidden but state stays `playing` (implicit dismiss does not toggle play/pause) | State Transition | P2 | web-Live net-new |
| TC-UC1b-05e | BR-10 | AC-10 | F11 | Overlay/timer active → background app > 1s → foreground → no IMPLICIT play/pause toggle beyond the OS default; well-defined state, NO stale mid-countdown overlay | State Transition | P2 | OS-default (iOS 1s timer wall-clock, no bg handler; web no `visibilitychange`); Live foreground snap-to-live = UC2 (do NOT assert); real-device confirm |

### BR-11 [state] — while playing the overlay auto-dismisses; while paused it persists and dismisses only on a tap outside the play button, and the media stays paused → State Transition (+ concurrent)

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC1b-06a | BR-11 | AC-04 | F07 | S(paused) + overlay visible, advance > 1000ms with no interaction → overlay PERSISTS (no auto-dismiss); media stays paused | State Transition | P1 | paused branch = no idle timer; contrast with playing auto-dismiss (02b); web-Live net-new |
| TC-UC1b-06b | BR-11 | AC-04 | F07 | S(paused) + tap outside the play button → overlay hidden AND media STILL paused (does NOT resume) | State Transition | P1 | tap-outside never resumes; resume-to-live = UC2 (not asserted); FU-2 resolved (64×64 target) |
| TC-UC1b-06c | BR-11 | AC-08 | F09 | **CONCURRENT** — dispatch a pause tap at t=1000ms (the exact instant the 1s auto-dismiss would fire) → explicit pause WINS: state `paused`, PLAY icon persists, overlay NOT swallowed by the expiring timer (dismisses only on a later tap-outside) | State Transition (concurrent) | P2 | fake-timer race, unit/component-deterministic; web-Live net-new |

### BR-15 [state] — the viewer is never left on a frozen frame with no feedback; any interruption surfaces an explicit state → State Transition

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC1b-07a | BR-15 | AC-09 | F10 | SDK state=buffering (not yet playing) + tap player → overlay visible AND central button reflects the REAL (buffering) state, NOT a false 'playing' pause-icon; no crash, no frozen overlay | State Transition | P1 | mock SDK=buffering / force via route stall + throttle; web-Live net-new |
| TC-UC1b-07b | BR-15 | AC-09 | F10 | Mid-play stall (was playing, network stalls) → an explicit buffering/'Reconnecting' state surfaces; never a silent frozen frame | State Transition | P2 | [AI-INFERRED] extends AC-09 initial-buffer to a mid-play stall per BR-15 'any interruption'; web gate `isLoading && isPoorConnection && isLive`, iOS scrim+spinner (code-verified); paused-reconnect is UC2 |

### AC-direct (ACs with no BR)

AC-06 has `br_ids: []` (QA default_state baseline) — TC derived directly from the AC.

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC1b-08 | — (AC-06) | AC-06 | F01 | SDK `room_status=live`, post first renders, no tap yet → NO controls overlay element in the view hierarchy/DOM; only the live video surface + standing LIVE badge + viewer count are visible (baseline S0) | Presence (default-state) | P1 | mock SDK `room_status=live`; assert overlay absent pre-tap; web-Live net-new |

## Automation Judgment

| TC-ID | Scenario (short) | Verdict | Criteria hit | Suggested Tool | Note |
|---|---|---|---|---|---|
| TC-UC1b-01a | Live revealed (playing) → seek buttons absent | Automate (with mock) | 5 (stream-type via SDK) | Playwright (web) · Detox (mobile) + SDK mock | mock stream=Live; web-Live overlay net-new |
| TC-UC1b-01b | Live paused → seek buttons absent (AC-04 negative) | Automate (with mock) | 5 (stream-type via SDK) | Playwright · Detox + SDK mock | mock stream=Live; explicit ±10s ABSENT assertion |
| TC-UC1b-01c | Recorded/video → seek buttons present (gate proof) | Automate (with mock) | 5 (stream-type via SDK) | Playwright · Detox + SDK mock | mock stream=recorded; contrast row |
| TC-UC1b-04b | Desktop first click = 1-step pause | Automate (with mock) | 5 (Live via SDK) | Playwright desktop viewport + SDK mock | desktop pause exists (PV-1); never reuse mobile expected |
| TC-UC1b-05b | Explicit pause → playing→paused | Automate (with mock) | 5 (Live via SDK) | Detox (iOS/Android) + SDK mock | web-mobile CANNOT pause Live; desktop = 04b |
| TC-UC1b-07a | Buffering tap → real state, no false icon | Automate (with mock) | 5 (buffering-state setup) | Playwright route stall/throttle · Detox + mock | no crash/frozen overlay; web-Live net-new |
| TC-UC1b-07b | Mid-play stall → explicit feedback | Automate (with mock) | 5 (stall injection) | Playwright network manipulation · Detox + mock | [AI-INFERRED]; flake risk → mock preferred; paused-reconnect is UC2 |
| TC-UC1b-08 | Default — no overlay before first tap | Automate (with mock) | 5 (room_status via SDK) | Playwright · Detox + SDK mock · unit render | mock `room_status=live`; assert overlay absent + LIVE badge/count present; web-Live net-new |
| TC-UC1b-02a | 999ms → overlay still visible | Automate (when stable) | 4 (web-Live overlay net-new) | Vitest/Jest fake timers · Playwright clock | web-Live net-new — first-time verify; fake timers deterministic |
| TC-UC1b-02b | 1000ms → overlay auto-dismissed | Automate (when stable) | 4 (net-new + web 3s→1s) | Vitest fake timers · Playwright clock | REGRESSION GUARD 3000ms→1000ms; web-Live net-new |
| TC-UC1b-02c | Interaction at 800ms resets countdown | Automate (when stable) | 4 (web-Live overlay net-new) | fake timers | reset is deterministic; web-Live net-new |
| TC-UC1b-03a | Surface-invariance — inline feed | Automate (when stable) | 4 (web-Live overlay net-new) | Playwright · Detox (parameterized) | loop the surface matrix |
| TC-UC1b-03b | Surface-invariance — fullscreen identical | Automate (when stable) | 4 (web-Live overlay net-new) | Playwright · Detox | surface-invariant ≠ platform-invariant |
| TC-UC1b-04a | Mobile first tap reveals, no pause | Automate (when stable) | 4 (web-mobile-Live net-new) | Detox (iOS/Android) · Playwright mobile viewport | assert playback continues + pause icon; web-Live net-new |
| TC-UC1b-05a | Reveal → stays playing | Automate (when stable) | 4 (web-Live overlay net-new) | Detox · Playwright | no-op transition |
| TC-UC1b-05c | Tap-outside (playing) → hides, stays playing | Automate (when stable) | 4 (web-Live overlay net-new) | Playwright · Detox | boundary = 64×64 (FU-2 resolved) |
| TC-UC1b-05d | Auto-dismiss → stays playing | Automate (when stable) | 4 (web-Live overlay net-new) | Vitest fake timers · Playwright | implicit dismiss = no toggle |
| TC-UC1b-06a | Paused overlay persists (>1s) | Automate (when stable) | 4 (web-Live overlay net-new) | fake timers · Playwright · Detox | paused branch — no timer |
| TC-UC1b-06b | Paused + tap-outside → stays paused | Automate (when stable) | 4 (web-Live overlay net-new) | Playwright · Detox | no resume (UC2); FU-2 resolved (64×64) |
| TC-UC1b-06c | Pause races auto-dismiss timer | Automate (when stable) | 4 (net-new) · 5 (fake-timer race) | Vitest/Jest fake timers | unit/component ONLY; e2e timing flaky; web-Live net-new |
| TC-UC1b-05e | Background/foreground (OS default) | Partial | 2 (OS backgrounding) · 4 (real-device) | Detox background/foreground + real-device confirm | web has no bg handler; Live snap-to-live = UC2 (do not assert) |

## QA must confirm

- **Feature stability**
  - **FU-2 (Design) — RESOLVED 2026-07-09:** hit-target = **64×64px** (Figma); impl is the developer's call (may use native). **TC-UC1b-05c / 06b** now target the rendered 64×64 area (assert against rendered bounds; web-Live overlay is still net-new, so these stay "when stable"). No longer blocking.
  - **web-Live overlay is NET-NEW (DEC-10 / DEV-DELTA)** — the entire reveal-controls overlay + 1s auto-dismiss timer does not exist on web-Live today (bare `<video>`+Plyr pause/play only, `LivestreamPlayer.tsx:115-123`). All **12 `Automate (when stable)` TCs** need first-time verification once the component is built; do NOT gate CI on them until the web-Live overlay is validated. iOS/Android Live overlay already exists (1s wall-clock timer, code-verified).
  - **Web auto-dismiss 3s→1s (BR-03, DEV DELTA)** — web is currently 3000ms (`VideoPlayerControls.tsx:60-70`); spec/iOS = 1s. **TC-UC1b-02a/02b** are authored to the 1s target and will fail on web until the fix lands. Q: sprint commitment, and is the new LIVE overlay wired to the same auto-dismiss timer or its own?
  - **web-mobile cannot pause a Live stream** (platform table 68264) — **TC-UC1b-05b** (explicit pause) applies to iOS/Android only; desktop pauses via 1-step (**TC-UC1b-04b**). Confirm web-mobile pause is truly out of scope for UC1b (reveal is in scope on web-mobile; pause is not).
- **Automation-budget prioritisation** — 20 automatable TCs, but **0 run clean today** (each needs an SDK mock OR the net-new web-Live overlay). Cheapest reliable start = the 8 `Automate (with mock)` gating/state TCs (01a, 01b, 01c, 04b, 05b, 07a, 07b, 08) once the SDK stream/room-status mock harness is confirmed; defer the 12 `when stable` overlay TCs to a second pass after the web-Live build lands.
- **Flakiness risks**
  - **Live environment** — a real broadcast + network manipulation is flaky (DEC-10). Confirm the SDK stream/room-status mock is available at the test boundary so the Live TCs (01a, 01b, 04b, 05b, 07a, 07b, 08) don't require a live broadcast.
  - **Timing / fake-timer TCs** — TC-UC1b-02a/02b/02c/05d/06a/06c: keep at unit/component with fake timers; do NOT assert wall-clock timing in real-time e2e. TC-UC1b-06c (pause-vs-timer race) is e2e-untimeable → unit only.
  - **Device-lifecycle** — TC-UC1b-05e: simulator backgrounding differs from real devices → confirm on a real device first. For Live, foreground may snap toward the live edge — that behaviour is **UC2's**, not asserted here.

## Coverage

- **BR → TC:** 7/7 covered — BR-01 (01a/b/c) · BR-03 (02a/b/c) · BR-06 (03a/b) · BR-09 (04a/b) · BR-10 (05a/b/c/d/e) · BR-11 (06a/b/c) · BR-15 (07a/b). **0-TC BRs: none.**
- **AC → TC:** 10/10 touched — AC-01 (04a, 04b, 05a) · AC-02 (05c) · AC-03 (02a, 02b, 05d) · AC-04 (01a, 01b, 01c, 05b, 06a, 06b) · AC-05 (03a, 03b) · AC-06 (08) · AC-07 (02c) · AC-08 (06c) · AC-09 (07a, 07b) · AC-10 (05e). **Untouched ACs: none.**
- **Verdicts:** Automate 0 · variants 20 (8 with-mock + 12 when-stable) · Partial 1 · Manual 0 · **Total 21**.
