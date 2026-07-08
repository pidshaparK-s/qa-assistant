# Layer 2 · STEP 2 — AC Authoring (phase-2-2)

_Skill: `phase-2-2-acceptance-criteria` · Input: STEP1 story shape (4 units) + PM's AC + Layer 1 enriched AC/edge-error findings_
_Method: classify existing AC into the 4 scenario types (Default / Happy / Alternative / Error), fill genuine gaps, verify against the State Machine (phase-1-1)_

> **Numbering convention:** each `uc_id` keeps its **own AC-01… sequence** (same pattern as UC1/UC2/UC3 already use independently). PM's existing `ac_id`s are **preserved as-is** — new QA-authored ACs are **appended**, never renumbered, so nothing breaks traceability back to Jira.
> **Source tag:** `PM` = content originates from PM's Jira AC (even if re-scoped by the UC1a/UC1b split) · `QA` = Given/When/Then newly authored this step (filling a Default/Alternative/Error gap Layer 1 had surfaced but not yet formalized).
> **[PENDING]** = genuinely unconfirmed — does **not** block Schema 1 emission (STEP 6), flagged for awareness, not a gate.

---

## AC Manifest (all units)

| Unit | uc_id | story_id | Default | Happy | Alternative | Error | Total | PM | QA |
|---|---|---|---|---|---|---|---|---|---|
| Tap-to-reveal (video/recorded) | UC1a | PDT-3562 | 1 | 6 | 2 | 2 | 11 | 6 | 5 |
| Tap-to-reveal (Live) | UC1b | PDT-3562 | 1 | 5 | 2 | 2 | 10 | 5 | 5 |
| Live Stream Pause State | UC2 | PDT-3563 | 2 | 2 | 3 | 1 | 8 | 3 | 5 |
| 10-Second Skip | UC3 | PDT-3564 | 2 | 3 | 5 | 1 | 11 | 8 | 3 |
| **Epic total** _(finalized at STEP 6)_ | | | **6** | **16** | **12** | **6** | **40** | **22** | **18** |

> _Counts finalized in the Schema-1 files at STEP 6 (a few ACs were reclassified during assembly — e.g. UC3 skip-while-paused → alternative, live-no-skip → default). The four `*-complete-jira-story.json` are authoritative; this table is the working tally._

Rule-of-thumb (≥3–5 AC, all 4 types present) — **every unit passes**; UC1a/UC1b/UC3 run higher than the floor because each is a genuine multi-state interaction model (reveal/dismiss/pause/resume), not padding — see per-unit tables.

---

## UC1a + UC1b — Tap-to-reveal (split per STEP1: video/recorded component vs 'Live' component)

**Shared State Machine (phase-1-1, mobile form factor):**
```
[PLAYING · overlay HIDDEN] --tap--> [PLAYING · overlay VISIBLE] --1s idle--> [PLAYING · overlay HIDDEN]
                                        |--tap-outside--> [PLAYING · overlay HIDDEN]
                                        |--tap-pause--> [PAUSED · overlay VISIBLE, no auto-dismiss]
                                                            |--tap-outside--> [PAUSED · overlay HIDDEN] (still paused)
                                                            |--tap-play--> [PLAYING · overlay VISIBLE]  (UC1a: exact position · UC1b: N/A — live resume is UC2's)
```
Desktop (Web UIKit) = 1-Step Pause, no reveal step (PV-1) — carried as a platform note on the shared ACs below, not a separate scenario type.

### Shared ACs — identical Given/When/Then, tested independently on each component (GAP-04)

| ac_id (UC1a / UC1b) | Type | Source | Scenario |
|---|---|---|---|
| AC-01 / AC-02 | Happy | PM | Tap playing player → overlay appears, playback continues |
| AC-02 / AC-03 | Happy | PM | Tap outside pause button (playing) → overlay dismisses |
| AC-03 / AC-04 | Happy | PM | No action 1s (playing) → overlay auto-dismisses |
| AC-07 / AC-05 | Default | QA | Baseline — before any tap |
| AC-08 / AC-06 | Alternative | QA | Idle timer resets on control interaction |
| AC-09 / AC-08 | Alternative | QA | Pause tap coincides with timer firing |
| AC-06 / AC-09 | Happy | PM | Cross-surface consistency |
| AC-10 / AC-10 | Error | QA | Tap during buffering/stall |
| AC-11 / AC-11 | Error | QA | App backgrounded then foregrounded — [PENDING] |

```
[Happy — tap reveals, playback continues]
Given a video/recorded LS (UC1a) OR a 'Live' stream (UC1b) is playing on a mobile surface
  AND the controls overlay is currently hidden
When the user taps anywhere on the player surface
Then the controls overlay appears
  AND playback continues uninterrupted — the media does NOT pause
  AND the central button shows the PAUSE icon
Note (desktop, PV-1): 1-Step Pause applies instead — tap pauses directly, this AC does not hold on desktop.

[Happy — tap outside dismisses]
Given the controls overlay is visible AND the media is PLAYING
When the user taps the player surface OUTSIDE the central pause/play button's tap target
Then the overlay dismisses AND playback continues uninterrupted
Note: [PENDING — FU-2] exact hit-target dimensions not yet spec'd by Design ("same size, refer from figma" is not a spec).

[Happy — auto-dismiss after 1s]
Given the controls overlay is visible AND the media is PLAYING
When the user takes no further action for 1 second
Then the overlay auto-dismisses AND playback continues

[Default — baseline before any tap]  ← NEW, fills the Type-1 gap
Given a video/recorded LS (UC1a) OR a 'Live' stream (UC1b) is actively playing on any in-scope surface
When the post first renders and no tap has occurred yet
Then no controls overlay is shown — only the media surface is visible
  AND this holds regardless of how playback started (out of scope: autoplay policy itself)

[Alternative — idle timer resets on interaction]  ← from L1 GAP-03
Given the controls overlay is visible AND the media is PLAYING
  AND the user interacts with an overlay control (volume, scrubber) before the 1s idle timeout elapses
When the interaction occurs
Then the 1s idle countdown restarts — the overlay does NOT disappear while the user is interacting
  AND after the last interaction, the overlay auto-dismisses 1s later

[Alternative — pause tap coincides with the auto-dismiss timer firing]  ← from L1 (pause-vs-timer race)
Given the controls overlay is visible AND the media is PLAYING AND the 1s idle timer is about to fire
When the user taps the central pause button at that instant
Then playback pauses AND the play icon is shown and PERSISTS — it is NOT caught by the expiring timer
  AND the overlay only dismisses on a subsequent tap-outside

[Happy — cross-surface consistency]
Given any in-scope surface (global/user/community/event-discussion feed, media gallery, fullscreen)
When the user performs any of the ACs above
Then behaviour is identical regardless of surface (surface-invariance, NOT platform-invariance — mobile vs desktop still differ per PV-1)

[Error — tap during buffering/stall]  ← NEW, from L1 E-07
Given the media is buffering (not yet playing)
When the user taps the player surface
Then the overlay appears AND the central button reflects the REAL state (loading/paused) — not a false "playing" icon
  AND no crash or frozen overlay occurs; the icon updates once playback actually starts

[Error — app backgrounded during an active overlay/timer]  ← from L1 E-08 — RESOLVED (code-grounded) 2026-07-08
Given the controls overlay is visible (playing or paused) and the app is backgrounded
When the user returns the app to the foreground
Then the player/overlay reach a well-defined state via the OS default — NOT a stale overlay stuck mid-countdown
Decision (Option 1 — adopt the OS default, grounded in current code): backgrounding is delegated to the OS/browser; QA specs the observed default rather than requiring new lifecycle code.
  • iOS: OS pauses AVPlayer on background (no background-audio mode), no auto-resume; the 1s auto-dismiss timer is wall-clock (Debouncer.swift:17-21) so a playing overlay is already dismissed on return and a paused overlay persists — NO stale mid-countdown state (the flagged risk is mitigated by design).
  • Web: delegated to the browser's native <video>/HLS.js; no app handling.
Note: the ONLY open product choice = whether to upgrade to Option 2 (explicit foreground reset: re-derive overlay from state, and for LIVE snap to live edge on resume). Low value since the wall-clock timer already avoids the stale-overlay bug. Does not block Schema 1. Refs → platform-behavior-notes.md · Code-verified notes.
```

### UC1a-only — video/recorded component

| ac_id | Type | Source | Scenario |
|---|---|---|---|
| AC-04 | Happy | PM | Tap pause → pauses; play icon + **seek controls remain visible** (video/recorded) |
| AC-05 | Happy | PM | Tap play while VIDEO paused → resumes from **exact** paused position |

```
[Happy — pause on video/recorded: seek controls remain visible]
Given a video or recorded livestream is playing AND the controls overlay is visible
When the user taps the central pause button
Then playback pauses at the current position
  AND the button icon switches pause → play and REMAINS visible
  AND the back/forward seeking (±10s skip) controls REMAIN VISIBLE (this is the video/recorded component)
  AND tapping anywhere outside the play button dismisses the overlay — the media STAYS paused

[Happy — resume from exact position (video only)]
Given a video is paused AND the play button is displayed
When the user taps the central play button
Then playback resumes from the EXACT position at which it was paused
  AND the button icon switches play → pause
Note: recorded livestream shares the video component (GAP-04) — reasonable to assume the same exact-position resume applies, though PM's AC text says "a video" specifically. Minor scope note, not a blocker.
```

### UC1b-only — 'Live' component

| ac_id | Type | Source | Scenario |
|---|---|---|---|
| AC-07 | Happy | PM | Tap pause → pauses; play icon persists; **NO seek controls shown** (Live) |
| — | — | — | **No resume AC here** — live resume is fully owned by UC2 AC-02 (current live moment). Do not author a duplicate/conflicting resume AC in UC1b. |

```
[Happy — pause on Live: NO seek controls]
Given a 'Live' stream is playing AND the controls overlay is visible
When the user taps the central pause button
Then playback pauses
  AND the button icon switches pause → play and REMAINS visible
  AND NO seek controls are shown (consistent with UC3 AC-06 — Live has no ±10s skip at all)
  AND tapping anywhere outside the play button dismisses the overlay — the stream STAYS paused
```

**Note — this split cleaned up a compound AC:** PM's original AC-04 had a single Then with an embedded if/else ("on video/recorded show seek; on Live don't"). Splitting into UC1a/UC1b turns it into two unconditional, atomic ACs — each cleanly testable without a branch inside the assertion.

---

## UC2 — Live Stream Pause State

**State Machine (phase-1-1):**
```
[LIVE · AT EDGE] --tap-pause--> [PAUSED · indicator ▶ shown, chat live] --tap-outside--> [PAUSED · overlay hidden] (still paused)
     [PAUSED] --tap-resume--> [LIVE · AT CURRENT MOMENT]  (behaviour CHANGE — CONF-07, buffering tolerance applies)
     [PAUSED] --room ends--> [ENDED/RECORDED]  (always wins over paused, even simultaneous — GAP-05)
```

| ac_id | Type | Source | Scenario |
|---|---|---|---|
| AC-01 | Happy | PM | Pause → indicator (▶) + chat stays live + tap-outside dismisses (no seek) |
| AC-02 | Happy | PM | Resume → CURRENT live moment (not paused position); chat uninterrupted |
| AC-03 | Alternative | PM | Stream ends while paused → ended/recorded wins, no frozen frame |
| AC-04 | Default | QA | Baseline — playing at live edge, before any pause |
| AC-05 | Default | QA | Platform exclusion — web-mobile has no pause control on Live at all |
| AC-06 | Alternative | QA | Long pause → resume lands further behind live, still within buffering tolerance |
| AC-07 | Alternative | QA | Chat/video re-sync on resume — no replayed or skipped messages |
| AC-08 | Error | QA | Network drops while paused — [PENDING] |

```
[Happy — AC-01, unchanged from PM/L1]
Given the user pauses a live stream
When the pause is applied
Then a visual indicator (central ▶ button, AMB-09) is shown communicating the stream is paused
  AND the chat continues to receive/display new messages in real time
  AND tapping anywhere outside the play button dismisses the overlay (pause/play button ONLY — no seek, CONF-08); the stream REMAINS paused

[Happy — AC-02, unchanged from PM/L1]
Given the user resumes from a paused live stream
When the stream restarts
Then playback starts from the CURRENT LIVE MOMENT — not the previous paused position
  AND the pause indicator dismisses
  AND the chat remains uninterrupted — no messages missed or replayed
Note: TEST TOLERANCE — lands a few seconds behind live due to normal buffering; this is EXPECTED (CONF-07), do not assert exact-live.

[Alternative — AC-03, reclassified from Happy → Alternative]
Given the user has paused a live stream
When the Room transitions to ended or recorded during the pause
Then the player moves to an appropriate ended/recorded state
  AND the ended/recorded state ALWAYS takes priority over paused, even if both occur simultaneously (GAP-05)
  AND the viewer is not left on a frozen frame; if the recording isn't ready, shows "Livestream ended" (no intermediate 'processing' state, GAP-06)
Note: reclassified as Alternative (not Happy) — it's a conditional branch triggered by an external event (host ends stream), not the primary intended flow.

[Default — baseline before any pause]  ← NEW, fills the Type-1 gap
Given a live stream (Room status = live) is playing at the live edge
When the viewer has not yet paused
Then no pause indicator is shown, chat is live, and the LIVE badge / viewer-count displays as-is (unaffected by this feature — out of scope per PM, OI-UC2-02)

[Default — platform exclusion]  ← NEW, formalizes a platform fact from platform-behavior-notes.md
Given a viewer is on mobile web watching a 'Live' stream
When the player renders
Then NO pause control is offered — this feature does not apply to web-mobile Live (platform table 68264)
Note: not a bug, not an AC-01/02 gap — a standing platform-support boundary. Exclude web-mobile from UC2 pause/resume test scope.

[Alternative — long pause → resume lands further behind, still within tolerance]  ← NEW, from L1 E-05
Given the user paused a live stream for an extended period (minutes)
When the user resumes
Then playback snaps to the current live moment (same as AC-02) — the size of the jump does not change the guarantee
  AND a brief buffering/loading state is acceptable while the jump completes

[Alternative — chat/video re-sync on resume]  ← NEW, from L1 E-06
Given the user paused for a while (chat kept running live throughout)
When the user resumes (video snaps to the current live moment)
Then chat and video are aligned at the live moment — no chat messages are replayed or skipped
  AND the transition is smooth; brief buffering is acceptable

[Error — network drops while paused]  ← from L1 E-04 — RESOLVED BY CODE 2026-07-08 (Web + iOS repos)
Given the user has paused a live stream
When the network connection drops and later recovers
Then a "Reconnecting" indicator is shown (auto-retry, no manual button) — the viewer is NOT left on a no-feedback frozen frame
  AND the stream STAYS PAUSED through the drop→recover cycle — no auto-resume
  AND on user resume, playback snaps to the current live moment / live edge (per AC-02)
Note: RESOLVED from source, no PM needed. iOS: reconnecting overlay tied to device network (NWPathMonitor) — shows even while paused; resume → seekToLiveEdge()+play() (LiveStreamPlayerView.swift:27-50; LiveStreamViewerView.swift:244-272). Web: "Reconnecting" overlay on stall/SDK-status + HLS.js auto-retry (LivestreamOverlay.tsx:57-66; useLiveStreamPlayer.ts:47-77) — generally does NOT show while paused (needs active-playback 'waiting' event). The INDICATOR differs by platform; both agree "no frozen frame, resume→live edge". Full refs → platform-behavior-notes.md · Code-verified notes.
```

---

## UC3 — 10-Second Skip Back/Forward

**State Machine (phase-1-1, position):**
```
[pos=P, playing] --skip ±10s--> [pos=P±10, playing]  (rapid taps ACCUMULATE, icon always shows ±10 — GAP-07)
   boundary pos<10 from start --skip-back--> [pos=0:00, STATE PRESERVED — playing continues / paused stays paused, AMB-11]
   boundary pos>(end-10) --skip-fwd--> [pos=final frame, END STATE (paused) — no content past the end]
   [paused] --skip--> [pos updated, stays paused]
   'Live' --> no skip buttons shown at all (AC-06)
```

| ac_id | Type | Source | Scenario |
|---|---|---|---|
| AC-01 | Happy | PM | Skip back −10s, continues |
| AC-02 | Happy | PM | Skip forward +10s, continues |
| AC-03 | Alternative | PM | Boundary skip-back → 0:00, state preserved (AMB-11) |
| AC-04 | Alternative | PM | Boundary skip-forward → final frame, end state |
| AC-05 | Happy | PM | Skip while paused → stays paused |
| AC-06 | Default | PM | Live → no skip buttons (in-app only, AMB-05) |
| AC-07 | Happy | PM | Rapid taps accumulate ±10s each |
| AC-08 | Alternative | PM | Rapid taps near boundary respect clamp mid-burst |
| AC-09 | Default | QA | Baseline — before overlay revealed (ties to UC1a), no skip buttons visible yet |
| AC-10 | Alternative | QA | Skip while buffering — mobile: seek-and-rebuffer (resolved) |
| AC-11 | Error | QA | Skip while buffering — web: exact behaviour unconfirmed — [PENDING, FU-3] |

_AC-01 through AC-08 carried verbatim from PM's Jira AC + Layer 1 enrichment (see `PDT-3564-uc3-analysis.md` section 3 for full text) — no changes, only type classification added above._

```
[Default — baseline before overlay revealed]  ← NEW, fills the Type-1 gap
Given a video/recorded LS is loaded and the controls overlay has not yet been revealed (per UC1a)
When the player first renders
Then no skip buttons are visible — they only appear as part of UC1a's controls overlay
Note: this ties UC3's default state to UC1a's overlay lifecycle — confirms the dependency already noted in STEP1 (build order UC1a → UC3).

[Alternative — skip while buffering, mobile]  ← NEW, from L1 GAP-08, mobile half RESOLVED
Given the video is buffering at the current position (mobile)
When the user taps a skip button
Then playback seeks and rebuffers at the target position (Prisa 68329) — no stuck loading, no crash

[Error — skip while buffering, web]  ← NEW, from L1 GAP-08, web half — [PENDING, FU-3]
Given the video is buffering at the current position (web)
When the user taps a skip button
Then [PENDING] exact behaviour of the ±10s button mid-buffer is not yet confirmed
  AND [known] the player separately shows a "Reconnecting" UI + allows manual scrub — but that is a DIFFERENT gesture from tapping ±10s skip (see glossary, `platform-behavior-notes.md`)
Note: does not block Schema 1 — tracked as FU-3, low severity (nice-to-have feature).
```

**Not an AC of this story:** Android's OS-native media control seeking a Live stream (AMB-05) is a **bug**, tracked separately as **FU-4** — it is not part of UC3's own Given/When/Then set (UC3 has no skip buttons on Live at all, per AC-06/AC-09).

---

## [PENDING] items — both RESOLVED FROM SOURCE CODE 2026-07-08 (no PM round needed)

Flagged `[PENDING]` when first authored, then resolved by reading the actual player code in `Amity-Social-Cloud-UIKit-Web` + `AmityUIKitIOS` (per the steer: "the answer is probably in the source"). Full refs in `platform-behavior-notes.md` → *Code-verified implementation notes*.

| Where | Question | Resolution |
|---|---|---|
| UC2 AC-08 | Reconnect UX on network drop while paused | "Reconnecting" indicator (auto-retry, no manual button); paused stays paused; resume → live edge. iOS shows it even while paused (device network); web only on a playback stall. Never a no-feedback frozen frame. |
| UC1 AC-11 | App-backgrounded while overlay/timer active | Delegated to OS/browser (Option 1, adopted). iOS: OS pauses, wall-clock 1s timer already elapses → no stale overlay. Only open choice = optional Option-2 polish (low value). |

### 🔎 Bonus — two implementation deltas surfaced by the code read (dev work, NOT spec gaps)
1. **Web auto-dismiss = 3s, spec (CONF-06) = 1s** (`VideoPlayerControls.tsx:60-70`). Web must change 3s→1s (iOS already 1s). The PRD's old "assume 3s" mirrored real web code, not a typo.
2. **Web LIVE path has no reveal-controls overlay at all** — only the recorded `VideoPlayer` has it; the live path is a bare Plyr (pause/play only). UC1b's tap-to-reveal + auto-dismiss looks like **net-new dev on web-live**.

These two feed STEP 5 (effort/priority) + dev handoff — flagged now so they're not discovered mid-sprint. Neither blocks STEP 3.

---

## STEP 2 exit — ready for STEP 3 (Business Rules, `phase-2-3`)

**Yes.** All 4 units pass the rule-of-thumb (≥3–5 AC, all 4 types represented). 40 ACs total (22 PM-sourced, 18 QA-authored) — final counts locked in the Schema-1 files at STEP 6. No `[PENDING]` item blocks moving forward — Business Rule extraction reuses the "Why" from `phase-1-1` and works from AC content that's already stable.
