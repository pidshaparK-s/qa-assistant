# Layer 3 Test Design — UC1a: Tap to Reveal Controls — Video / Recorded Live Stream

> Source of truth: `PDT-3562-uc1a-complete-jira-story.json` (8 BRs / 11 ACs) + `PDT-3562-uc1a-user-flow.json` (F01–F11). BRs used AS-IS from L2 — not re-extracted. `flow_id` shortened `F0X` = `flow-UC1a-F0X`. TC-ID = `TC-UC1a-NN`; `a/b/c` suffix = a boundary/decision family from one BR.

## Automation context

Per **DEC-10**: video/recorded = local-media → *stable* → default **Automate** (Playwright web · Detox mobile, known-length fixtures); stream-type gating (recorded-vs-Live) needs an **SDK mock**; web overlay auto-dismiss (BR-03, 3s→1s in `VideoPlayerControls.tsx:60-70`) is a *changing* behaviour → **regression guard, automate when web fix lands**; app backgrounding (AC-11) → **Partial + real-device confirm**; Live contrasts assert **≈ live within tolerance**, never exact.

## BR → Test Conditions

### BR-01 [permission] — ±10s skip controls exist only on video / recorded LS, never on an active Live stream → Decision Table

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC1a-01a | BR-01 | AC-04 | F07 | Video, controls overlay visible after central pause → both −10s and +10s skip buttons are visible | Decision Table | P1 | video/recorded component; mobile + desktop identical |
| TC-UC1a-01b | BR-01 | AC-04 | F07 | Recorded LS (shares the video component), controls visible → −10s/+10s skip buttons visible, same as video | Decision Table | P2 | mock SDK stream-type = recorded LS |
| TC-UC1a-01c | BR-01 | AC-04 | F07 (contrast) | Active **Live** stream, controls visible → −10s/+10s skip buttons are NOT present (negative row) | Decision Table | P2 | mock SDK stream-type = Live; cross-ref UC1b/UC3 — Live overlay is a separate component |

### BR-03 [constraint] — overlay auto-dismisses after 1s of no interaction while playing; countdown restarts on every control interaction → BVA / EP

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC1a-02a | BR-03 | AC-03 | F05 | Playing + overlay visible, no interaction, advance to 900ms (< 1s) → overlay STILL visible; playing | BVA | P2 | just-below boundary |
| TC-UC1a-02b | BR-03 | AC-03 | F05 | Playing + overlay visible, no interaction, advance to 1000ms → overlay hidden (auto-dismissed); currentTime still advancing | BVA | P1 | **REGRESSION GUARD** — target = 1000ms; web currently 3000ms (`VideoPlayerControls.tsx:60-70`), iOS already 1s → mobile automate now, web automate when 3s→1s fix lands |
| TC-UC1a-02c | BR-03 | AC-08 | F06 | Overlay visible + playing, fire a control interaction (volume/scrubber) at 800ms → countdown resets, overlay still visible; 1000ms after the last interaction → overlay hidden; playing throughout | BVA | P2 | timeout constant tied to the web 3s→1s fix |
| TC-UC1a-02d | BR-03 | AC-08 | F06 | Overlay visible + playing, repeated interactions each < 1s apart → overlay NEVER dismisses while interacting | EP | P2 | each interaction = one reset class |

### BR-06 [constraint] — controls behaviour identical across all in-scope surfaces (surface-invariant, NOT platform-invariant) → EP

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC1a-03a | BR-06 | AC-06 | F02 | Reveal-controls result identical across {global, user, community, event-discussion feed, media gallery, fullscreen} → overlay visible + playing on each surface | EP | P1 | parameterize over the 6 surface classes; hold platform fixed |
| TC-UC1a-03b | BR-06 | AC-06 | F02/F03 | Same surface, form factor varied → mobile reveals (playing) vs desktop 1-step pause (paused) differ → surface-invariant ≠ platform-invariant | EP (contrast) | P2 | guards against collapsing the BR-09 platform split into BR-06 |

### BR-09 [computation] — first-tap model is platform-dependent: mobile reveals (no toggle); desktop (Web UIKit) = direct 1-step pause → BVA + EP

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC1a-04a | BR-09 | AC-01 | F02 | **Mobile** (iOS / Android / web-on-mobile): first tap on a playing player → overlay revealed, currentTime keeps advancing (NO pause), central button shows PAUSE icon | BVA + EP | P1 | mobile reveal class — expected differs from desktop; never reuse on Web UIKit desktop |
| TC-UC1a-04b | BR-09 | AC-01 | F03 | **Desktop** (Web UIKit): first click on a playing player → media PAUSES (currentTime stops), central button shows PLAY icon, ±10s skip visible; mobile reveal branch NOT taken | BVA + EP | P1 | desktop 1-Step Pause class (PV-1) — separate expected by form factor |

### BR-10 [state] — play/pause state changes only via an explicit user pause/play action or a terminal room state; no implicit operation toggles it → State Transition

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC1a-05a | BR-10 | AC-01 | F02 | Playing + tap-to-reveal (mobile) → state stays `playing` (reveal is not an implicit pause) | State Transition | P1 | no-op transition; mobile |
| TC-UC1a-05b | BR-10 | AC-02 | F04 | Playing + overlay visible + tap outside the button → overlay hidden but state stays `playing` (dismiss is not an implicit pause) | State Transition | P1 | uses coarse outside coords (exact boundary = TC-UC1a-06d/FU-2) |
| TC-UC1a-05c | BR-10 | AC-04 | F07 | Playing + explicit central pause tap → transition `playing → paused` (the only valid user trigger) | State Transition | P1 | mobile = 2-step (reveal then pause); desktop reaches paused in 1-step (F03) |
| TC-UC1a-05d | BR-10 | AC-09 | F09 | **CONCURRENT** — pause tap fires at ~999ms as the 1s auto-dismiss timer is about to fire → explicit pause wins: state `paused`, play icon persists, NOT undone by the expiring timer | State Transition (concurrent) | P2 | fake-timers race; e2e timing flaky → unit/component only |
| TC-UC1a-05e | BR-10 | AC-11 | F11 | App backgrounded while playing (iOS) → OS pauses the media (terminal OS action, not an implicit app toggle) and does NOT auto-resume on foreground | State Transition | P2 | iOS OS-default (`Debouncer.swift:17-21`, `PlayerControlsVisibility.swift:16`); confirm on real device; web has no `visibilitychange` handler |

### BR-11 [state] — while playing the overlay auto-dismisses; while paused it persists and dismisses only on a tap outside the play button, and the media stays paused → State Transition

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC1a-06a | BR-11 | AC-04 | F07 | Overlay visible + **paused**, advance > 1000ms with no interaction → overlay PERSISTS (no auto-dismiss); media stays paused | State Transition | P1 | paused branch = no idle timer |
| TC-UC1a-06b | BR-11 | AC-04 | F07 | Overlay visible + paused + tap outside the play button → overlay hidden AND media STILL paused (does not resume) | State Transition | P1 | tap-outside never resumes |
| TC-UC1a-06c | BR-11 | AC-02, AC-09 | F04/F05/F09 | Dismiss-rule contrast: **playing** overlay dismisses via the 1s timer OR tap-outside; **paused** overlay dismisses ONLY via tap-outside, never by the timer | State Transition | P2 | ties the AC-09 race outcome to the paused-persists rule |
| TC-UC1a-06d | BR-11 | AC-02 | F04 | **COARSE** hit-target boundary: tap clearly OUTSIDE the central button bounds → dismiss path (overlay hidden, playing); tap clearly INSIDE → pause path. Exact px boundary is NOT asserted | State Transition / boundary | P2 | **FU-2 PENDING** (Design) — 'same size, refer from figma' is not a spec → precise just-inside/just-outside boundary blocked; keep coarse |

### BR-13 [state] — resume target by media type: video/recorded resumes from the exact paused position; Live resumes at the current live edge → State Transition

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC1a-07a | BR-13 | AC-05 | F08 | Video paused at t=42s + tap central play → resumes from currentTime == 42s (not 0, not live edge); icon play → pause | State Transition | P1 | known-length local fixture |
| TC-UC1a-07b | BR-13 | AC-05 | F08 | Recorded LS (shares the video component) paused at t=42s + tap play → resumes from exact 42s, same as video | State Transition | P2 | **ASSUME-recorded-resume PENDING** (Engineering) — hold the assertion until confirmed |
| TC-UC1a-07c | BR-13 | AC-05 | F08 (contrast) | Live stream + tap resume → resumes at the current live edge (≈ live within tolerance), NOT the exact paused position | State Transition | P3 | contrast/negative; cross-ref UC2 (CONF-07 resume-to-live tolerance) — out of UC1a's video component |

### BR-15 [state] — the viewer is never left on a frozen frame with no feedback; any interruption surfaces an explicit state → State Transition

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC1a-08a | BR-15 | AC-10 | F10 | Media buffering (not yet playing) + tap → overlay visible AND central button reflects the REAL state (loading/paused), NOT a false 'playing' pause-icon; no crash, no frozen overlay | State Transition | P2 | force buffering via network throttle / route delay or state mock |
| TC-UC1a-08b | BR-15 | AC-10 | F10 | Buffering → playing transition → central button icon UPDATES to the playing state once playback starts (explicit state, no stale icon) | State Transition | P2 | release throttle → assert icon update |
| TC-UC1a-08c | BR-15 | AC-10 | F10 | Mid-playback stall (was playing, network stalls) → an explicit loading/stall state surfaces; never a silent frozen frame | State Transition | P3 | [AI-INFERRED] extends AC-10's initial-buffer case to a mid-play stall per BR-15 'any interruption'; inject stall via network manipulation — flake risk |

### AC-direct (ACs with no BR)

AC-07 has `br_ids: []` (QA default_state baseline) — TC derived directly from the AC.

| TC-ID | BR-ID | ac_id | flow_id | Condition | Technique | Priority | Platform note |
|---|---|---|---|---|---|---|---|
| TC-UC1a-09 | — (AC-07) | AC-07 | F01 | Video/recorded playing on any in-scope surface, first render, no tap yet → NO controls overlay element in the view hierarchy / DOM; only the media surface is visible | Presence (default-state) | P1 | assert absence of the overlay element pre-tap |

## Automation Judgment

| TC-ID | Scenario (short) | Verdict | Criteria hit | Suggested Tool | Note |
|---|---|---|---|---|---|
| TC-UC1a-01a | Video → ±10s skip visible | Automate | — | Playwright (web) · Detox (mobile) | local media fixture |
| TC-UC1a-02a | 900ms → overlay still visible | Automate | — | Vitest/Jest fake timers · Playwright clock | flake risk in real-time e2e → prefer fake timers |
| TC-UC1a-02c | Interaction at 800ms resets countdown | Automate | — | fake timers | reset assertion is deterministic |
| TC-UC1a-02d | Repeated interactions never dismiss | Automate | — | fake timers | — |
| TC-UC1a-03a | Surface-invariance across 6 surfaces | Automate | — | Playwright · Detox (parameterized) | loop the surface matrix |
| TC-UC1a-03b | Surface-invariant ≠ platform-invariant | Automate | — | Playwright (desktop + mobile viewport) | run both form factors |
| TC-UC1a-04a | Mobile first tap reveals, no pause | Automate | — | Detox (iOS/Android) · Playwright mobile viewport | assert currentTime advances + pause icon |
| TC-UC1a-04b | Desktop first click = 1-step pause | Automate | — | Playwright desktop viewport (Web UIKit) | never reuse mobile expected (PV-1) |
| TC-UC1a-05a | Reveal → stays playing | Automate | — | Detox · Playwright | no-op transition |
| TC-UC1a-05b | Tap-outside (playing) → hides, stays playing | Automate | — | Playwright · Detox | coarse outside coords |
| TC-UC1a-05c | Explicit pause → playing→paused | Automate | — | Playwright · Detox | — |
| TC-UC1a-05d | Pause races auto-dismiss timer | Automate | 5 (timing setup — fake timers) | Vitest/Jest fake timers | unit/component ONLY; e2e timing flaky |
| TC-UC1a-06a | Paused overlay persists (>1s) | Automate | — | fake timers | paused branch — no timer |
| TC-UC1a-06b | Paused + tap-outside → stays paused | Automate | — | Playwright · Detox | — |
| TC-UC1a-06c | Playing-vs-paused dismiss contrast | Automate | — | Playwright · Detox + fake timers | two branches in one design |
| TC-UC1a-07a | Video resume from exact 42s | Automate | — | Playwright · Detox (known-length fixture) | assert currentTime == paused position |
| TC-UC1a-09 | Default — no overlay before first tap | Automate | — | Playwright · Detox · unit render | assert overlay element absent |
| TC-UC1a-01b | Recorded LS → ±10s skip visible | Automate (with mock) | 5 (stream-type via SDK) | Playwright · Detox + SDK mock | mock stream-type = recorded LS |
| TC-UC1a-01c | Live → ±10s skip absent | Automate (with mock) | 5 (stream-type via SDK) | Playwright · Detox + SDK mock | mock stream-type = Live; web-Live overlay net-new (UC1b) |
| TC-UC1a-07b | Recorded LS resume exact | Automate (with mock) | 5 (recorded-LS source) | Playwright · Detox + SDK mock | expected pending ASSUME-recorded-resume — hold assertion |
| TC-UC1a-07c | Live resumes at live edge (≈) | Automate (with mock) | 5 (Live env / SDK) | Playwright · Detox + SDK mock | assert ≈ live within tolerance (CONF-07); cross-ref UC2 |
| TC-UC1a-08a | Buffering tap → real state, no false icon | Automate (with mock) | 5 (buffering setup) | Playwright route delay/throttle · Detox + mock | no crash / no frozen overlay |
| TC-UC1a-08b | Buffering→playing → icon updates | Automate (with mock) | 5 (buffering setup) | Playwright throttle · Detox + mock | release throttle → assert icon |
| TC-UC1a-08c | Mid-play stall → explicit feedback | Automate (with mock) | 5 (stall injection) | Playwright network manipulation · Detox + mock | [AI-INFERRED]; flake risk — mock preferred |
| TC-UC1a-02b | 1000ms → overlay auto-dismissed | Automate (when stable) | 4 (web behaviour changing) | Vitest fake timers · Playwright clock | REGRESSION GUARD — mobile now; web when 3s→1s fix lands |
| TC-UC1a-05e | Background/foreground (iOS OS default) | Partial | 2 (OS backgrounding), 4 (real-device) | Detox background/foreground + real-device confirm | web backgrounding not automatable → manual/scenario |
| TC-UC1a-06d | Hit-target pause-vs-dismiss boundary | Partial | 5 (spec incomplete for deterministic boundary) | Playwright · Detox (coarse) | coarse inside/outside automatable; **precise px boundary blocked on FU-2** |

## QA must confirm

- **Feature stability**
  - **FU-2 (Design, PENDING)** — central pause/play button hit-target size/spec. Affects **TC-UC1a-06d** (and the coarse coords in TC-UC1a-05b). Without it there is no deterministic just-inside/just-outside pause-vs-dismiss boundary. Q: what is the exact hit-target (px / dp), or is it the visible button bounds?
  - **ASSUME-recorded-resume (Engineering, PENDING)** — recorded LS resumes from the exact paused position like video. Affects **TC-UC1a-07b**. The assertion (exact resume, not live edge) is held until Engineering confirms; if recorded LS instead snaps to live edge, TC-UC1a-07b flips toward the TC-UC1a-07c expected.
  - **Web overlay 3s→1s (BR-03, DEV DELTA)** — is the web fix (`VideoPlayerControls.tsx:60-70`, 3000ms→1000ms) committed for this sprint? **TC-UC1a-02b** is a regression guard authored to the 1s target; it fails on web until the fix lands (iOS already 1s). Q: PM/dev sprint commitment + target date.
  - **web-Live overlay is net-new** (per DEC-10) — TC-UC1a-01c's Live contrast runs against the video component here; the actual Live overlay validation belongs to UC1b. Confirm the Live component surface before extending.
- **Automation-budget prioritisation** — 17 clean `Automate` TCs are the cheapest, highest-value start (local-media, no external deps): lead with the P1s TC-UC1a-04a, TC-UC1a-04b (platform split), TC-UC1a-05a/05b/05c, TC-UC1a-06a/06b, TC-UC1a-07a, TC-UC1a-09. Defer the 7 `Automate (with mock)` (SDK-mock cost) and TC-UC1a-02b (blocked on the web fix) to a second pass.
- **Flakiness risks**
  - Timing / fake-timer TCs: **TC-UC1a-02a, -02b, -02c, -05d, -06a, -06c** — keep at unit/component with fake timers; do NOT assert wall-clock timing in real-time e2e. TC-UC1a-05d (pause-vs-timer race) is e2e-untimeable → unit only.
  - External-dep / mock TCs: **TC-UC1a-01b, -01c, -07b, -07c, -08a, -08b, -08c** depend on SDK stream-type or network manipulation — confirm the mock/stub harness is stable before counting them as reliable CI green. TC-UC1a-07c (real Live) is the flakiest (broadcast + network) → mock or treat as manual.
  - Device-lifecycle: **TC-UC1a-05e** — simulator backgrounding differs from real devices → confirm on a real device first; web has no background handler.

## Coverage

- **BR → TC:** 8/8 covered — BR-01 (01a/b/c) · BR-03 (02a/b/c/d) · BR-06 (03a/b) · BR-09 (04a/b) · BR-10 (05a/b/c/d/e) · BR-11 (06a/b/c/d) · BR-13 (07a/b/c) · BR-15 (08a/b/c). **0-TC BRs: none.**
- **AC → TC:** 11/11 touched — AC-01 (04a,04b,05a) · AC-02 (05b,06c,06d) · AC-03 (02a,02b,06c) · AC-04 (01a,01b,05c,06a,06b) · AC-05 (07a,07b,07c) · AC-06 (03a,03b) · AC-07 (09) · AC-08 (02c,02d) · AC-09 (05d,06c) · AC-10 (08a,08b,08c) · AC-11 (05e). **Untouched ACs: none.**
- **Verdicts:** Automate 17 · variants 8 (7 with-mock + 1 when-stable) · Partial 2 · Manual 0 · **Total 27**.
