# Layer 3 Test Design — UC2: Live Stream Pause State

## Automation context

Per DEC-10 (overview): UC2 = Live pause/resume on {UIKit iOS, Android, RN, Flutter, WebUIKit; desktop = 1-Step Pause, BR-09} · stability MIXED (web-Live overlay + tap-to-reveal are NET-NEW / not yet validated) · external deps = Social+ SDK (room.status / stream-type / chat subscription) + live-broadcast infra + device network layer → live tests need a real broadcast + network manipulation (flaky) → most TCs are **Automate (with mock)** (mock the SDK room.status / stream-type / chat subscription / network layer); resume-to-live always asserts **≈ live within tolerance, never exact** (CONF-07 / BR-13); genuinely flaky live scenarios (real-broadcast tolerance feel, simultaneous host-end race) stay **Manual**.

---

## BR → Test Conditions

### BR-01 [permission] — ±10s seek/skip controls exist only on video/recorded, never on active Live → Decision Table

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC2-01a | BR-01 | AC-01 | flow-UC2-F02 | SDK stream = Live → assert the Live player exposes **only pause/play**; **±10s skip buttons are ABSENT** | Decision Table | P1 | All platforms; canonical term "±10s skip" (= PM "back/forward seeking") |
| TC-UC2-01b | BR-01 | AC-01 (contrast) | — | SDK stream = recorded/VOD → assert **±10s skip buttons ARE present** (confirms the Live-vs-recorded gating dimension) | Decision Table | P3 | Contrast row; primary coverage is UC3 (recorded uses the video component) |

### BR-02 [permission] — Pause/resume of an active Live stream is not available on mobile web → Decision Table

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC2-02a | BR-02 | AC-05 | flow-UC2-F08 | web-**mobile** viewport + Live → assert **NO pause control offered** (no pause affordance in the player chrome) | Decision Table | P1 | Standing boundary (platform table 68264), not a bug — EXCLUDE web-mobile from the pause/resume suite |
| TC-UC2-02b | BR-02 | AC-05 (contrast) | flow-UC2-F08 | web-**desktop** + Live → assert **pause control IS present** (1-step pause, BR-09) | Decision Table | P2 | Contrast; positive pause path is AC-01/flow-UC2-F02 |
| TC-UC2-02c | BR-02 | AC-05 (contrast) | flow-UC2-F08 | **iOS / Android** app + Live → assert **pause control IS present** (2-step reveal-then-pause, BR-09) | Decision Table | P2 | Contrast; positive pause path is AC-01/flow-UC2-F02 |

### BR-07 [computation] — The pause indicator IS the central ▶ overlay itself, not a separate badge/banner → EP (presence classes; no numeric range → the E of BVA+EP)

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC2-03a | BR-07 | AC-01 | flow-UC2-F02 | On pause → assert the **central play (▶) button overlay is shown AS the pause indicator** (LS-mobile-04) | EP | P1 | web-Live overlay is NET-NEW — automate on web once built; iOS/Android now |
| TC-UC2-03b | BR-07 | AC-01 | flow-UC2-F02 | On pause → assert there is **NO separate badge/banner element** (the ▶ overlay is the only pause-state indicator) | EP | P1 | web-Live overlay is NET-NEW — automate on web once built; iOS/Android now |

### BR-09 [computation] — First-tap interaction model is platform-dependent (mobile reveal / desktop 1-step) → EP (form-factor classes)

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC2-04a | BR-09 | AC-01 | flow-UC2-F02 | **Mobile {iOS, Android}**: first tap on a playing Live → **reveals controls, playback CONTINUES (no pause)**; tap the central button → **pauses** (2-step) | EP | P1 | PV-1 mobile path; web-mobile excluded (BR-02); web-live tap-to-reveal is net-new (UC1b) |
| TC-UC2-04b | BR-09 | AC-01 | flow-UC2-F02 | **web-desktop**: a **single tap pauses directly** (1-step) | EP | P1 | PV-1 desktop path |

### BR-10 [state] — Play/pause changes only via explicit user action or a terminal room state; no implicit op (incl. network stall) toggles it → State Transition (+ concurrent)

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC2-05a | BR-10 | AC-08 | flow-UC2-F07 | paused → network **drops** (implicit event) → assert player **stays paused** (invalid transition: no implicit toggle) | State Transition | P1 | Concurrent/timing — drop lands while paused |
| TC-UC2-05b | BR-10 | AC-08 | flow-UC2-F07 | paused → network **recovers** (implicit event) → assert player **stays paused, NO auto-resume** (resumes only on explicit user play) | State Transition | P2 | — |

### BR-11 [state] — Paused overlay persists and dismisses only on a tap outside the play button; the stream stays paused → State Transition

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC2-06a | BR-11 | AC-01 | flow-UC2-F02 | paused, overlay visible → **tap OUTSIDE the play button** → assert overlay **dismisses**, player **stays paused**, playback position **unchanged (no seek)** | State Transition | P1 | web-Live overlay net-new; a Live stream exposes no seek (BR-01) |
| TC-UC2-06b | BR-11 | AC-01, AC-02 | flow-UC2-F02, flow-UC2-F03 | paused, overlay visible → **tap ON the play button** → assert player **resumes** (valid transition — distinct from tap-outside dismiss) | State Transition | P2 | resume-target assertion is BR-13/TC-UC2-08a |

### BR-12 [state] — A terminal room state (ended/recorded) always takes priority over paused; resolves to ended regardless of recording readiness (no 'processing' state) → State Transition (+ concurrent)

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC2-07a | BR-12 | AC-03 | flow-UC2-F06 | player = paused → flip SDK room.status **live→ended** → assert player **leaves paused and shows the ended state** (terminal wins) | State Transition | P1 | — |
| TC-UC2-07b | BR-12 | AC-03 | flow-UC2-F06 | player = paused → room → **recorded** (recording ready) → assert player shows the **recorded/VOD state** | State Transition | P2 | recorded then behaves like video (has ±10s skip) |
| TC-UC2-07c | BR-12 | AC-03 | flow-UC2-F06 | **CONCURRENT race**: pause action and room-end fire **simultaneously** → assert **ended wins** over paused | State Transition (concurrent) | P2 | Hard to stage a true race on a real broadcast → Manual |
| TC-UC2-07d | BR-12 | AC-03 | flow-UC2-F06 | room = ended, recording **NOT ready** → assert **'Livestream ended'** is shown, with **NO intermediate 'processing' state** | State Transition | P1 | — |

### BR-13 [state] — Resume target: Live → current live edge within normal buffering tolerance (a few seconds behind is expected) → State Transition (+ BVA on pause-duration boundary)

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC2-08a | BR-13 | AC-02 | flow-UC2-F03 | paused → resume → assert seek target = **current live edge** (playback position ≠ paused offset; advances to live), ▶ overlay dismisses; iOS `seekToLiveEdge()`+`play()` fires; lands **≈ live within tolerance, NOT exact-live** | State Transition | P1 | BEHAVIOUR CHANGE vs today's resume-from-paused-position — run every platform |
| TC-UC2-08b | BR-13 | AC-02 | flow-UC2-F03 | **short pause (~15s)** → resume → assert playback lands **≈ live within tolerance** (a few seconds behind expected), not the paused position | State Transition / BVA (duration) | P2 | Tolerance-band feel on a REAL broadcast → Manual, per-platform |
| TC-UC2-08c | BR-13 | AC-06 | flow-UC2-F04 | **long pause (minutes)** → resume → assert snap to live edge **regardless of jump size**, brief buffering acceptable, still **≈ live within tolerance**, never the paused position | State Transition / BVA (duration) | P2 | Long real pause on a real broadcast → Manual |
| TC-UC2-08d | BR-13 | AC-08 | flow-UC2-F07 | after network **drop→recover while paused**, user resume → assert snap to **live edge** ≈ live within tolerance (per AC-02) | State Transition | P2 | Ties reconnect (BR-10) back to resume-to-live |

### BR-14 [state] — Live chat is independent of playback; keeps running during pause, never replayed/skipped on resume → State Transition

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC2-09a | BR-14 | AC-01, AC-04 | flow-UC2-F02, flow-UC2-F01 | during pause → inject chat messages → assert chat **keeps receiving and displaying new messages in real time** (chat is NOT paused, separate subscription) | State Transition | P1 | chat = separate SDK subscription, independent of AVPlayer/HLS.js |
| TC-UC2-09b | BR-14 | AC-07 | flow-UC2-F05 | capture chat message ids **before vs after resume** → assert **NO message replayed (re-shown)** and **NONE skipped** | State Transition | P1 | — |
| TC-UC2-09c | BR-14 | AC-07 | flow-UC2-F05 | long paused window with continuous chat → on resume assert chat **already at the live moment** and **aligns** with the video (no replay/skip) | State Transition | P2 | also exercises AC-06/flow-UC2-F04 (long pause) |

### BR-15 [state] — The viewer is never left on a frozen frame with no feedback; interruptions surface an explicit state (Reconnecting w/ auto-retry, or ended) → State Transition

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC2-10a | BR-15 | AC-08 | flow-UC2-F07 | **iOS**: device network drops while paused → assert a **'Reconnecting' scrim + spinner shows EVEN while paused** (auto-retry, **no manual button**) — not a no-feedback frozen frame | State Transition | P1 | iOS overlay tied to device network via NWPathMonitor (device-connectivity, independent of play state) |
| TC-UC2-10b | BR-15 | AC-08 | flow-UC2-F07 | **web**: network drops while paused → assert **NO 'Reconnecting' overlay** (a paused `<video>` emits no `waiting` stall); then set SDK room.status = **waitingReconnect** → assert the overlay **DOES show** | State Transition | P2 | web overlay gated `isLoading && isPoorConnection && isLive`; distinguish viewer device-network vs broadcaster-drop |
| TC-UC2-10c | BR-15 | AC-03 | flow-UC2-F06 | room ends while paused → assert an **explicit ended state surfaces** (feedback), viewer not left on a frozen frame | State Transition | P2 | pairs with BR-12/TC-UC2-07a |

### AC-direct (ACs with no BR)

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC2-11 | — (AC-04 default, br_ids: []) | AC-04 | flow-UC2-F01 | Live at live edge, viewer has **not** paused → assert **NO ▶ overlay / pause indicator present**, **LIVE badge + viewer count render as-is** (unaffected by this feature); chat is live (BR-14 baseline, see TC-UC2-09a) | Presence / EP | P1 | Baseline before any interaction |

---

## Automation Judgment

Sorted Automate → Partial → Manual, then TC-ID. (Partial: none.) Plain `Automate` is rare here because **every Live scenario needs the SDK / player / network mocked** to be deterministic in CI — the `Automate (with mock)` rows ARE automatable; only genuinely flaky real-broadcast scenarios are Manual.

| TC-ID | Scenario (short) | Verdict | Criteria hit | Suggested Tool | Note |
|---|---|---|---|---|---|
| TC-UC2-01a | Live → no ±10s skip controls | Automate (with mock) | C5 (setup→mock SDK) | Playwright (web) / Detox (mobile) | mock SDK stream=Live; assert skip buttons absent, only pause/play |
| TC-UC2-01b | recorded → ±10s skip present (contrast) | Automate | — | Playwright / Detox | local recorded/VOD fixture, no live infra; primary coverage UC3 |
| TC-UC2-02a | web-mobile Live → no pause control | Automate (with mock) | C5 (setup→mock SDK) | Playwright (mobile viewport) | absence assertion is stable; only the Live render needs mocked SDK=Live |
| TC-UC2-02b | web-desktop Live → 1-step pause present | Automate (with mock) | C5 (setup→mock SDK) | Playwright | mock SDK Live; assert pause affordance present |
| TC-UC2-02c | iOS/Android Live → pause present (2-step) | Automate (with mock) | C5 (setup→mock SDK) | Detox | mock SDK Live; assert pause affordance present |
| TC-UC2-03a | ▶ overlay IS the pause indicator | Automate (with mock) | C4 (web-live net-new) · C5 (mock) | Detox / Playwright | web-Live overlay NET-NEW → automate on web once built; iOS/Android now |
| TC-UC2-03b | no separate badge/banner element | Automate (with mock) | C4 (web-live net-new) · C5 (mock) | Detox / Playwright | assert no badge/banner node besides the ▶ overlay |
| TC-UC2-04a | mobile 2-step reveal→pause | Automate (with mock) | C4 (web-live net-new) · C5 (mock) | Detox | reveal-window timing = minor flake; web-live tap-to-reveal is net-new (UC1b) |
| TC-UC2-04b | web-desktop 1-step pause | Automate (with mock) | C5 (setup→mock SDK) | Playwright | single tap toggles pause |
| TC-UC2-05a | drop while paused → stays paused | Automate (with mock) | C5 (mock network layer) | Detox / Playwright + network mock | assert no implicit toggle on stall (BR-10); real-network variant = Manual |
| TC-UC2-05b | recover while paused → no auto-resume | Automate (with mock) | C5 (mock network layer) | Detox / Playwright + network mock | assert play state unchanged through recover |
| TC-UC2-06a | tap outside → dismiss + stays paused, no seek | Automate (with mock) | C4 (web-live net-new) · C5 (mock) | Detox / Playwright | assert overlay hidden + player paused + position unchanged |
| TC-UC2-06b | tap on ▶ → resumes (not dismiss) | Automate (with mock) | C5 (setup→mock SDK) | Detox / Playwright | distinguishes resume from tap-outside dismiss |
| TC-UC2-07a | room live→ended while paused → ended wins | Automate (with mock) | C5 (mock SDK room.status) | Detox / Playwright + SDK mock | flip room.status via mock; real host-end = Manual |
| TC-UC2-07b | room→recorded while paused → recorded state | Automate (with mock) | C5 (mock SDK room.status) | Detox / Playwright + SDK mock | — |
| TC-UC2-07d | ended, recording not ready → 'Livestream ended', no 'processing' | Automate (with mock) | C5 (mock SDK room.status) | Detox / Playwright + SDK mock | assert ended text + no processing UI |
| TC-UC2-08a | resume → seek to live edge (≠ paused pos), overlay dismiss | Automate (with mock) | C5 (mock live source/player) | Detox / Playwright + player mock | assert seek target = live edge + iOS seekToLiveEdge()+play(); real tolerance feel = QA confirm |
| TC-UC2-08d | resume after drop→recover → snap to live edge | Automate (with mock) | C5 (mock network+player) | Detox / Playwright + mocks | ties reconnect to resume-to-live |
| TC-UC2-09a | chat keeps running during pause | Automate (with mock) | C5 (mock chat subscription) | Detox / Playwright + SDK chat mock | inject messages while player.paused → assert they render (not paused) |
| TC-UC2-09b | before/after resume → no replay/skip | Automate (with mock) | C5 (mock chat subscription) | Detox / Playwright + SDK chat mock | compare message ids; assert no dup, no gap |
| TC-UC2-09c | long pause → chat aligned at live on resume | Automate (with mock) | C5 (mock chat subscription) | Detox / Playwright + SDK chat mock | mock injects across a simulated long pause; real feed = QA confirm |
| TC-UC2-10a | iOS Reconnecting shows while paused | Automate (with mock) | C5 (mock NetworkMonitor) | Detox + NetworkMonitor mock | mock NWPathMonitor drop; assert scrim shows while paused; real device-network toggle = Manual (real-device-farm) alt |
| TC-UC2-10b | web: no overlay on drop; shows on waitingReconnect | Automate (with mock) | C5 (route intercept + SDK mock) | Playwright route intercept + SDK mock | assert no overlay on plain drop; overlay on room.status=waitingReconnect |
| TC-UC2-10c | room ends while paused → explicit ended feedback | Automate (with mock) | C5 (mock SDK room.status) | Detox / Playwright + SDK mock | assert explicit ended state, not frozen frame |
| TC-UC2-11 | default: no pause indicator, LIVE badge as-is | Automate (with mock) | C5 (setup→mock SDK Live) | Detox / Playwright | assert no ▶ overlay + LIVE badge/viewer count render as-is |
| TC-UC2-07c | concurrent pause+host-end → ended wins | Manual | C5 (flaky live env — hard to stage a true race) | Manual (real broadcast) | true simultaneity on a real broadcast is hard to stage; a mock-level event-ordering check is possible at unit level |
| TC-UC2-08b | short pause resume ≈ live within tolerance | Manual (real-device-farm) | C5 (flaky live env) · cross-platform behaviour-change matrix | Real-device farm + real broadcast | per-platform {iOS, Android, web-desktop} confirm of the resume behaviour CHANGE on a real live edge |
| TC-UC2-08c | long pause resume snaps to live, brief buffering | Manual | C5 (flaky live env — long real pause) | Manual (real broadcast) | assert live-edge snap + buffering + ≈ live within tolerance, never paused position |

---

## QA must confirm

- **ASSUME-buffer-tolerance (AC-02, q_id ASSUME-buffer-tolerance — PENDING, owner PM):** is "a few seconds behind live" acceptable to product as the resume target? All resume TCs (**TC-UC2-08a/08b/08c/08d**, and TC-UC2-06b) assert **≈ live within tolerance, never exact-live** — but the concrete tolerance band (how many seconds) is not fixed. This is a **QA-confirm, not a blocker** (CONF-07 already accepts "expected"; tighter is not achievable — live-streaming physics).
- **Live-env flakiness (stays Manual):** **TC-UC2-08b** (short-pause tolerance, real-device-farm across {iOS, Android, web-desktop}), **TC-UC2-08c** (long-pause tolerance/buffering on a real broadcast), and **TC-UC2-07c** (simultaneous host-end race, hard to stage) require a real broadcast — do not force these into CI. Confirm the resume behaviour CHANGE per platform on real devices.
- **Real-device needs:** **TC-UC2-10a** (iOS `NWPathMonitor` reconnecting-while-paused) — confirm the device-network overlay-while-paused on a **real device first** even though the NetworkMonitor layer is mockable; **TC-UC2-08b** needs the **real-device farm** matrix (behaviour change per platform).
- **web-Live overlay is NET-NEW / not yet validated (DEC-10):** **TC-UC2-03a/03b/04a/04b/06a** depend on the web-Live pause overlay + tap-to-reveal, which is **net-new dev on web-live** (bare `<video>`+Plyr today; UC1b work). Automate these on web **once implemented**; iOS/Android are automatable now. Related dev deltas (not QA assumptions): web auto-dismiss **3s→1s**, web debounce→accumulate — cross-ref, separate from UC2.
- **Chat continuity on a real live feed:** **TC-UC2-09a/09b/09c** use a **mocked chat subscription** for determinism — smoke-check real live-chat continuity (no replay/skip, chat runs through pause) on a **real broadcast** at least once.
- **web reconnect nuance (TC-UC2-10b):** confirm on web that a paused `<video>` emits no `waiting` (so no overlay) and that only SDK `room.status='waitingReconnect'` (broadcaster/host dropped) surfaces the overlay — keep this distinct from the viewer's own device-network drop.
- **Automation budget:** 25 TCs are automatable (1 plain + 24 with-mock). If time-boxed, start with the P1 mock-based cores: TC-UC2-01a, -02a, -03a/03b, -04a/04b, -05a, -06a, -07a/07d, -08a, -09a/09b, -10a, -11.

---

## Coverage

- **BR → TC: 10 / 10** — every BR has ≥1 TC. No 0-TC BR.
  BR-01 (01a,01b) · BR-02 (02a,02b,02c) · BR-07 (03a,03b) · BR-09 (04a,04b) · BR-10 (05a,05b) · BR-11 (06a,06b) · BR-12 (07a,07b,07c,07d) · BR-13 (08a,08b,08c,08d) · BR-14 (09a,09b,09c) · BR-15 (10a,10b,10c).
- **AC → TC: 8 / 8** — every ac_id touched. No untouched AC.
  AC-01 (01a,03a,03b,04a,04b,06a,06b,09a) · AC-02 (06b,08a,08b) · AC-03 (07a,07b,07c,07d,10c) · AC-04 (11,09a) · AC-05 (02a,02b,02c) · AC-06 (08c) · AC-07 (09b,09c) · AC-08 (05a,05b,08d,10a,10b).
- **Verdicts:** Automate **1** · variants (Automate-with-mock) **24** · Partial **0** · Manual **3** · **Total 28**.
  (Manual = TC-UC2-07c, TC-UC2-08c; Manual real-device-farm = TC-UC2-08b. Automatable in CI = 25 of 28.)
