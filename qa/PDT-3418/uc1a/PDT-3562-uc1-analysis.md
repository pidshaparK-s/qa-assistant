# Story Analysis — PDT-3562 (UC1): Tap to Reveal Controls

_Source: Jira AC (synced 2026-07-08 14:27) + PRD (`products/PDT-3418/prd/Video & live streaming.html`) + Figma (`current-01/02`, `VR-mobile-00/01/02`, `LS-mobile-01/02/03/04/05`, `LS-desktop-01`) — per-story lens_
_Skills: phase 1.1 → 1.2 → 1.3 → 1.4 · PM's AC = source of truth, QA enriches (ไม่เขียนทับ)_
_Clarifications cross-referenced to `qa/PDT-3418/clarifications.json` (ledger ids) + `qa/PDT-3418/platform-behavior-notes.md`_

> **Sync note (2026-07-08):** Re-run phase 1.3 + 1.4 หลัง Jira sync (2026-07-08 14:27) + clarification review. **สิ่งที่เปลี่ยน:**
> - **AC-02 / AC-03** — `given` now scoped **"while playing"**.
> - **AC-03** — auto-dismiss = **1 second (final, CONF-06)**; 1s idle timer **resets/holds on every control interaction** (volume/scrubber) — confirmed web+iOS+Android (**GAP-03**).
> - **AC-04** — **expanded**: playback pauses; play icon **persists** (paused ≠ auto-dismiss — only while PLAYING does the icon auto-dismiss after 1s, PM comment 68362, **GAP-02**); seek (back/forward 10s) controls บน **video / recorded LS เท่านั้น**, **'Live' = none** (**CONF-08**); tap **outside** play button dismisses overlay แต่ media **ยัง paused**.
> - **AC-05** — narrowed to **VIDEO only** (resume from exact paused position). Live-stream pause/resume → **UC2** (resume-to-current-live-moment, CONF-07).
> - Resolved: **GAP-04** ('Live' LS = separate player component → test 2 paths per platform), **AMB-03** (double-tap descoped, central button only).
> - **Platform variance (critical):** FIRST tap on a playing player differs by form factor — **Mobile** (iOS/Android/web-on-mobile) = tap reveals controls, playback continues (AC-01) · **Desktop** (Web UIKit) = **1-Step Pause** (tap pauses directly, tap-to-reveal not applied).
> - Non-blocking residuals only: **FU-2** (hit-target size, AMB-06/low), **FU-5** (our JSON diverges from Jira on seek-on-live — PM to align Jira).

---

## 0. AC Manifest  [GATE 1]

| AC | Group | Scenario |
|---|---|---|
| AC-01 | Tap behaviour | Tap playing player → controls overlay appears, playback continues |
| AC-02 | Tap behaviour | Tap outside pause button while overlay visible (while playing) → overlay dismisses, playback continues |
| AC-03 | Tap behaviour | No action after overlay appears (while playing) → overlay auto-dismisses after 1s |
| AC-04 | Pause/play button | Tap pause while playing → pauses; play icon + seek indicators persist; tap-outside dismisses overlay but stays paused |
| AC-05 | Pause behaviour (video) | Tap play while a video is paused → resumes from exact position, icon changes |
| AC-06 | Platform & surface | Behaviour identical across all in-scope surfaces |

**Total: 6 ACs — ทั้ง 6 จะถูกวิเคราะห์ ไม่มีข้อไหนหลุด (Dropout Rule)**

**Scope / platforms:** iOS · Android · React Native · Flutter · WebUIKit. **Desktop = UI-only (button size), no behaviour change** (platforms.not_supported, PM Ghita 2026-07-06).
**⚠️ Per-platform expected (test-design constraint):** every tap/pause interaction AC MUST split expected by form factor — **Mobile {iOS, Android, web-on-mobile} = reveal-controls** vs **Desktop {Web UIKit} = 1-Step Pause**. And 'Live' LS uses a **separate player component** → test video/recorded LS and 'Live' LS as **two paths** per platform (GAP-04). See `platform-behavior-notes.md` PV-1.

---

## 1. Requirement Interrogation (phase 1.1)

### 1.1 WHO — Relationship Map

```
                     ┌───────────────────────────┐
                     │   VIDEO / LIVE-STREAM      │
                     │   PLAYER + controls overlay│
                     └─────────────┬─────────────┘
                                   │
        ┌──────────────────┬───────┴────────┬──────────────────┐
        │                  │                │                  │
 [Community member]  [Auto-dismiss    [Render path]      [Form factor]
  (primary actor)     timer/System]    video = recorded    Mobile = reveal
  tap / pause /        hide overlay     LS (same comp.)     Desktop = 1-Step
  play                 after 1s idle    ≠ 'Live' LS         Pause (no reveal)
                       (resets on       (diff. comp.)       → PV-1
                        interaction)     → GAP-04 ✅
                        → GAP-03 ✅       (test 2 paths)
```

**Actor analysis:**

| Actor | Interaction | ใน AC ไหม? |
|---|---|---|
| Community member (viewer) | tap surface, tap pause/play button | ✅ AC-01…AC-05 |
| System (auto-dismiss timer) | ซ่อน overlay หลัง 1s idle; **reset ทุก interaction** (GAP-03 ✅) | ✅ AC-03 |
| Render path — video / recorded LS | ใช้ component เดียวกัน; seek controls แสดงตอน paused | ✅ AC-01/AC-04 |
| Render path — **'Live' live stream** | ใช้ **คนละ component** → test แยก; paused overlay **ไม่มี seek** | ✅ resolved **GAP-04 / CONF-08** — test 2 paths |
| **Form factor** — Mobile vs Desktop | Mobile = tap reveals; **Desktop (Web UIKit) = 1-Step Pause** | ✅ resolved **PV-1** — split expected |
| Concurrent viewers | player state เป็น per-viewer อิสระ | ❌ ไม่มีใน AC (acceptable) |

**Silent-actor gap (RESOLVED):** Jira comments (Chayanit 68297, Prisa 68302, Fidriyanto 68318, 2026-07-07) ยืนยันว่า **'Live' live stream ใช้คนละ player component** จาก video/recorded LS บน web/iOS/Android → tap-to-reveal ที่ผ่านบน video/recorded LS **ไม่ครอบคลุม 'Live' LS อัตโนมัติ** ต้อง implement + test แยกเป็น 2 paths ต่อ platform (**GAP-04**). Cross-cutting เพิ่ม: first-tap behaviour ต่างตาม form factor — **desktop = 1-Step Pause**, tap-to-reveal ใช้เฉพาะ mobile (**PV-1**).

### 1.2 WHAT — State Machine (player + overlay) — refreshed per resolved behaviour

```
MOBILE (iOS / Android / web-on-mobile) — tap-to-reveal applies
────────────────────────────────────────────────────────────
[PLAYING · overlay HIDDEN]
      │  tap surface (AC-01)
      ▼
[PLAYING · overlay VISIBLE] ──── 1s idle, no interaction (AC-03) ────► [PLAYING · overlay HIDDEN]
      │   ▲   │                    (timer RESETS on control interaction — GAP-03 ✅)
      │   └───┘ interact (volume/scrubber) → hold/restart 1s
      │        │
      │        │ tap OUTSIDE central button (AC-02) → [PLAYING · overlay HIDDEN]
      │
      │ tap central PAUSE button (AC-04)
      ▼
[PAUSED · overlay VISIBLE]  ── NO auto-dismiss while paused (GAP-02 ✅); play icon + seek* persist
      │        │                (*seek = video/recorded only; 'Live' = none — CONF-08)
      │        │ tap OUTSIDE play button (AC-04) ──► [PAUSED · overlay HIDDEN]  (media STAYS paused)
      │        │                                              │ tap surface → re-reveal (stays paused)
      │        ▼
      │  tap central PLAY button (AC-05, VIDEO) ──► [PLAYING · overlay VISIBLE]  (resume EXACT position)
      ▼
   (live resume → owned by UC2: current live moment, not paused position — CONF-07)

DESKTOP (Web UIKit) — tap-to-reveal NOT applied
────────────────────────────────────────────────
[PLAYING] ── tap/click surface = 1-Step Pause (PV-1) ──► [PAUSED]   (no reveal step; button-size UI only)
```

**Transitions — สถานะล่าสุด:**

| Transition / question | สถานะ | Clarification |
|---|---|---|
| PLAYING→PAUSED: overlay ค้าง หรือ auto-dismiss? | ✅ **RESOLVED** — paused: play icon **persists**, no auto-dismiss; dismiss เฉพาะ tap-outside | **GAP-02** |
| Auto-dismiss timer (1s) reset เมื่อ user interact? | ✅ **RESOLVED** — reset/holds ทุก control interaction | **GAP-03** |
| 'Live' LS (คนละ component) tap-to-reveal เหมือน video? | ✅ **RESOLVED** — test 2 paths; paused 'Live' ไม่มี seek | **GAP-04 / CONF-08** |
| First tap = reveal หรือ pause? | ✅ **RESOLVED** — mobile reveal / desktop 1-step pause | **PV-1** |
| Tap ที่ขอบ hit-target ของปุ่ม = button/surface? | ⚠️ followup (low, non-blocking) | **AMB-06 / FU-2** |

### 1.3 WHY — Pain & Consequence

**Pain:** PRD A1 — tap ที่ใดก็ได้ = pause ขัด convention (YouTube/TikTok/FB) → viewer pause โดยไม่ตั้งใจ; live stream ยิ่งแย่ (ตกหลัง live edge). Context: มือถือ tap พลาดง่าย. _(desktop ไม่มีปัญหานี้ → คง 1-step pause เดิม)_

**Consequence (ถ้า implement ผิด):**

| Wrong implementation | ผลกระทบ |
|---|---|
| Timeout สั้น/นานเกิน หรือไม่ reset ตอน interact | overlay หายกลางที่ user ใช้ scrubber/volume อยู่ (GAP-03) |
| overlay dismiss ทุก tap (รวมปุ่ม) / auto-dismiss ตอน paused | user กด pause แต่ play icon หาย → ต้อง tap ซ้ำเพื่อ resume (GAP-02) |
| 'Live' LS ไม่เทสแยก (คนละ component) | core fix ผ่านบน video แต่ 'Live' ยัง tap-to-pause (GAP-04) |
| แสดง seek บน 'Live' paused overlay | ขัด UC3 AC-06 — LIVE ไม่มี seek (CONF-08) |
| เขียน expected เดียว cross-platform | desktop 1-step pause fail กับ mobile expected (PV-1) |

### 1.4 Gap check (phase 1.1 Step 4)

1. **Actor:** 'Live' LS render path → ✅ resolved (GAP-04, test 2 paths). Form-factor actor → ✅ resolved (PV-1, split expected).
2. **State transitions:** controls-after-pause → ✅ resolved (GAP-02); timer-reset → ✅ resolved (GAP-03).
3. **Why → decision:** pause mechanism = **central button only** — double-tap gesture **descoped** ✅ (AMB-03).
4. **เหลือ:** hit-target size ยังไม่มี concrete spec → **FU-2** (low, non-blocking).

---

## 2. Three-Layer Analysis (phase 1.2)

```
Business Goal   ลด accidental disruption ใน viewing session → รักษา engagement (PRD: XM, Ulta รายงาน)
      ↑
User Need       viewer tap player ได้โดยไม่กลัว pause โดยไม่ตั้งใจ + เข้าถึง controls ได้ตามต้องการ
      ↑
System Behavior AC-01…AC-06 (tap→reveal บน mobile, pause บนปุ่มเดียว, auto-dismiss+reset, resume ตรงตำแหน่ง video, ทุก surface)
```

**Behavior → Need → Goal (traceable):**

| System Behavior (AC) | → User Need | → Goal |
|---|---|---|
| AC-01 tap → controls, playback ต่อ (mobile) | tap ได้โดยไม่กลัว | ลด accidental pause ✅ |
| AC-02 tap นอกปุ่ม (playing) → dismiss | เคลียร์ controls | ✅ |
| AC-03 auto-dismiss 1s + reset ตอน interact | controls ไม่บังนาน แต่ไม่หายกลางใช้งาน | ✅ (GAP-03) |
| AC-04 pause เฉพาะปุ่มกลาง; play icon persist | pause แบบตั้งใจ + resume ได้ทันที | ลด accidental pause ✅ (GAP-02) |
| AC-05 resume ตรงตำแหน่ง (video) | resume แม่นยำ | ✅ (live → UC2) |
| AC-06 cross-surface | behavior คาดเดาได้ต่อ surface | ✅ |

**5 Gap types — สถานะล่าสุด:**

| Gap type | สิ่งที่พบ | Clarification |
|---|---|---|
| ~~Assumed context~~ | ~~timer reset เมื่อ interact~~ → ✅ **RESOLVED** | **GAP-03** |
| ~~Assumed context~~ | ~~overlay state หลัง pause~~ → ✅ **RESOLVED** (persists, no auto-dismiss) | **GAP-02** |
| ~~Orphaned/undecided~~ | ~~double-tap gesture~~ → ✅ **DESCOPED** (central button only) | **AMB-03** |
| ~~Silent user need~~ | ~~'Live' LS component ต่าง~~ → ✅ **RESOLVED** (test 2 paths) | **GAP-04** |
| ~~Ambiguous scope~~ | ~~desktop scope~~ → ✅ **RESOLVED** (1-step pause, UI-only) | **PV-1** |
| Ambiguous constraint | central-button hit-target size ยังไม่ concrete | **AMB-06 / FU-2** (low) |

---

## 3. Happy-Path AC Enrichment (phase 1.3)  — loop ทุก AC

### 🔍 [1/6] AC-01 — Tap playing player → reveal controls (mobile) / 1-Step Pause (desktop)

**Interpretation:** Given ไม่ระบุ overlay state ก่อน tap (ต้อง hidden) / render path / form factor; Then ไม่ระบุ icon ปุ่มกลาง. First-tap behaviour **ต่างตาม form factor** — ต้อง split expected.

```
[Happy — AC-01 (MOBILE): tap reveals controls, does NOT pause]
Given a video or live stream is playing on any in-scope surface (iOS / Android / web-on-mobile)
  AND the controls overlay is currently hidden
When the user taps anywhere on the player surface
Then the controls overlay appears
  AND playback continues uninterrupted — the media does NOT pause
  AND the central button shows the PAUSE icon (reflecting the playing state)
Note [GAP-04]: verify แยก 2 paths — (1) video + recorded LS, (2) 'Live' LS — 'Live' ใช้คนละ player component (web/iOS/Android)

[Happy — AC-01 (DESKTOP / Web UIKit): 1-Step Pause, tap-to-reveal NOT applied]
Given a video or live stream is playing on Web UIKit (desktop)
When the user clicks/taps the player surface
Then playback PAUSES directly (1-step) — AC-01 "controls appear + playback continues" does NOT hold on desktop
Note [PV-1]: desktop = no behaviour change, UI-only (button size). อย่าเขียน expected เดียว cross-platform สำหรับ tap ACs
```

### 🔍 [2/6] AC-02 — Tap outside pause button (while playing) → dismiss overlay

**Interpretation:** given now scoped **"while playing"** — paused-state tap-outside ถูกย้ายไปครอบใน AC-04 (dismiss but stays paused).

```
[Happy — AC-02: tap outside button dismisses overlay, playback continues]
Given the controls overlay is visible AND the media is PLAYING
When the user taps the player surface OUTSIDE the central pause/play button's tap target
Then the overlay dismisses
  AND playback continues uninterrupted
Note [AMB-06 / FU-2]: central-button hit-target size ยังไม่มี concrete spec (Design "refer from Figma") — low, non-blocking; จำเป็นต่อการเทส pause-vs-dismiss edge ให้ deterministic
Note: การ tap นอกปุ่มขณะ PAUSED (dismiss overlay, media ยัง paused) → ดู AC-04
```

### 🔍 [3/6] AC-03 — No action (while playing) → auto-dismiss after 1s; timer resets on interaction

**Interpretation:** given now scoped **"while playing"**; auto-dismiss ใช้ตอน PLAYING เท่านั้น (ตอน PAUSED play icon persist — GAP-02). Timeout = 1s final; timer reset ตอน interact.

```
[Happy — AC-03a: overlay auto-dismisses after 1s idle while playing]
Given the controls overlay is visible AND the media is PLAYING
When the user takes no further action for 1 second
Then the overlay auto-dismisses
  AND playback continues
Note [CONF-06]: 1 second เป็นค่า FINAL (Jira AC-03 + PM confirm). PRD ยังมี comment "assume 3s" — เป็น doc-hygiene cleanup (FU-1)

[Happy — AC-03b: idle timer RESETS on control interaction]
Given the controls overlay is visible AND the media is PLAYING
  AND the user interacts with an overlay control (volume, scrubber) before the 1s timeout elapses
When the interaction occurs
Then the 1s idle countdown restarts — the overlay does NOT disappear while the user is interacting
  AND after the last interaction the overlay auto-dismisses 1s later; playback continues throughout
Note [GAP-03]: ยืนยันทุก platform — web (68297 "counting includes volume + scrubber, controls will not disappear while changing"), iOS (68302 "agree"), Android (68318 "reset on every interaction"). PM ควร fold rule นี้เข้า AC-03 text
```

### 🔍 [4/6] AC-04 — Tap pause button while playing → pause; play icon + seek persist; tap-outside dismisses but stays paused

**Interpretation:** EXPANDED. Then เดิมมีแค่ pause + icon change; ปัจจุบันเพิ่ม play-icon persistence, seek-control conditionality (video/recorded vs 'Live'), และ tap-outside-dismiss-stays-paused.

```
[Happy — AC-04: central button pauses; play icon + seek persist; tap-outside dismisses, stays paused]
Given a video or live stream is playing AND the controls overlay is visible
When the user taps the central pause button
Then playback pauses at the current position
  AND the button icon switches from pause → play and REMAINS visible (does NOT auto-dismiss while paused)
  AND on a VIDEO or RECORDED live stream: the back/forward seeking (10s skip) controls remain visible
  AND on a 'Live' live stream: NO seek controls are shown
  AND tapping anywhere OUTSIDE the play button dismisses the overlay controls — the media STAYS paused
Note [GAP-02]: WHILE PLAYING → pause icon auto-dismisses after 1s (AC-03); WHILE PAUSED → play icon + seek persist, NO auto-dismiss, dismiss เฉพาะ tap-outside (PM comment 68362)
Note [CONF-08]: seek (back/forward 10s) บน VIDEO + RECORDED LS เท่านั้น; 'Live' paused overlay ไม่มี seek (สอดคล้อง UC3 AC-06). ⚠️ Jira AC-04 ยังมี wording เก่า → PM ต้อง align Jira (FU-5) ไม่งั้น sync รอบหน้าดึงกลับมา
Note [AMB-03]: pause = central button เท่านั้น — double-tap gesture descoped
Note [PV-1]: path เข้าสู่ paused ต่างตาม platform — mobile = reveal-then-tap (2-step); desktop = tap เดียว paused แล้ว (1-step)
```

### 🔍 [5/6] AC-05 — Tap play while VIDEO paused → resume from exact position (video only)

**Interpretation:** NARROWED to **VIDEO** only. Live-stream resume เป็นของ UC2 (current live moment). Given ปัจจุบัน = "A video is paused / The play button is displayed".

```
[Happy — AC-05: resume video from exact paused position]
Given a VIDEO is paused AND the play button is displayed
When the user taps the central play button
Then playback resumes from the EXACT position at which it was paused
  AND the button icon switches from play → pause
Note: AC-05 scoped **VIDEO** (และ recorded) เท่านั้น. Live-stream pause/resume เป็นของ **UC2 (PDT-3563)** — resume ไป **CURRENT LIVE MOMENT** ไม่ใช่ตำแหน่งที่ pause (OI-UC1-07 / ledger CONF-07). ห้าม apply resume-from-exact-position กับ 'Live' stream
```
> ⚠️ **Cross-story split (intentional):** VIDEO resume = exact paused position (UC1 AC-05) · LIVE resume = current live moment, lands ไม่กี่วินาทีหลัง live เพราะ buffering (UC2 AC-02, CONF-07 — อย่า assert exact-live).

### 🔍 [6/6] AC-06 — Behaviour identical across all in-scope surfaces

**Interpretation:** surfaces = global/user/community/event-discussion feed + media gallery (+ fullscreen ตาม PRD). AC-06 การันตี **surface-invariance** ไม่ใช่ platform-invariance.

```
[Happy — AC-06: cross-surface consistency]
Given any in-scope surface (global / user / community / event-discussion feed, media gallery, fullscreen)
When the user performs any of AC-01…AC-05
Then the behaviour is identical regardless of surface
Note: "identical across surfaces" ≠ "identical across platforms" — first-tap ยังต่างตาม form factor (mobile reveal vs desktop 1-step pause — PV-1) และ 'Live' LS ใช้คนละ component (GAP-04)
Note: Desktop = no behaviour change, UI-only button-size change (platforms.not_supported, PM Ghita 2026-07-06)
```

---

## 4. Edge & Error AC (phase 1.4)  — 4 models + priority

### ส่วนที่ 1 — Edge cases found

| ID | Model | Edge case | สถานะ clarification | Priority |
|---|---|---|---|---|
| E-01 | Timing | Interact กับ control (volume/scrubber) ก่อนครบ 1s → timer reset, overlay ไม่หาย | ✅ RESOLVED (GAP-03) — เทสเป็น confirmed behaviour | **High** |
| E-02 | Timing | กด pause พอดีจังหวะ 1s auto-dismiss fire → pause ชนะ, play icon persist (ไม่โดน timer เก็บ) | ✅ derived from GAP-02 | **High** |
| E-03 | Data integrity | 'Live' LS (คนละ component) → tap-to-reveal เหมือน video? paused overlay ไม่มี seek? | ✅ RESOLVED (GAP-04, CONF-08) — เทส 2 paths | **High** |
| E-04 | Boundary | seek-control presence boundary: video/recorded = แสดง, 'Live' = ไม่แสดง → assert overlay contents ตาม media type | ✅ RESOLVED (CONF-08) | Medium |
| E-05 | Boundary | Tap ขอบ hit-target ปุ่มกลาง → pause vs dismiss deterministic | ⚠️ FU-2 (low, non-blocking) | Low |
| E-06 | Environment | หมุนจอ / เข้า-ออก fullscreen ขณะ overlay visible → persist? | open (test-design) | Medium |
| E-07 | Environment | Tap ระหว่าง buffering/stall → overlay สะท้อน state จริง | open (→ error case) | Medium |
| E-08 | Environment | App backgrounded แล้ว resume → player อยู่ state ที่นิยาม | open (test-design) | Medium |
| E-09 | Timing | บน 'Live': pause พอดีจังหวะ host จบ stream (race) | ↗ owned by **UC2 GAP-05** (ended wins) — cross-ref | (UC2) |

### ส่วนที่ 2 — Priority
- **High:** E-01, E-02, E-03 · **Medium:** E-04, E-06, E-07, E-08 · **Low:** E-05 (FU-2)
- **Cross-cutting test-design (ไม่ใช่ bug edge แต่ห้ามพลาด):** per-form-factor expected (mobile reveal vs desktop 1-step pause — PV-1) ต้อง carry ผ่านทุก tap/pause condition.

### ส่วนที่ 3 — AC ใหม่ (High ก่อน)

```
[Edge — Timing, High] E-01 · idle timer resets on control interaction  (GAP-03 — RESOLVED)
Given the overlay is visible AND the media is PLAYING
  AND the user interacts with a control (volume / scrubber) before the 1s idle timeout elapses
When the interaction occurs
Then the 1s idle countdown restarts — the overlay stays visible while the user interacts
  AND [state หลัง action] เมื่อ interaction หยุด, overlay auto-dismisses 1s ต่อมา; playback ต่อเนื่องตลอด

[Edge — Timing, High] E-02 · pause tap coincides with auto-dismiss fire
Given the overlay is visible AND the media is PLAYING AND the 1s idle timer is about to fire
When the user taps the central pause button at that instant
Then playback pauses AND the play icon is shown and PERSISTS (ไม่ถูก timer เก็บ)
  AND [state หลัง action] paused + play icon visible; overlay dismisses เฉพาะเมื่อ tap-outside รอบถัดไป (GAP-02)

[Edge — Data integrity, High] E-03 · 'Live' LS uses a separate player component  (GAP-04 / CONF-08 — RESOLVED)
Given a 'Live' live stream is playing (separate render component on web / iOS / Android, mobile form factor)
When the user taps the player surface
Then the overlay appears AND playback does NOT pause — identical to the video path
  AND [state หลัง action] verified อิสระบน 'Live' component — pass บน video/recorded LS ไม่ implies pass บน 'Live'
  AND เมื่อ paused, the 'Live' overlay shows NO seek controls (CONF-08)
```

```
[Error — Environment] E-07 · tap during buffering / stall
Given the media is buffering / not yet playing
When the user taps the player surface
Then the overlay appears AND the central button reflects the real state (loading / paused) — ไม่ใช่ false "playing"
  AND [state หลัง error] no frozen overlay, no crash; button updates เมื่อ playback resumes

[Error — Boundary, Low/FU-2] E-05 · tap lands on central-button hit-target edge  (AMB-06 — followup)
Given the overlay is visible
When the user taps at the boundary between the central button and the surrounding surface
Then pause-vs-dismiss resolves deterministically ตาม hit-target ที่นิยาม
  AND [state หลัง action] blocked on FU-2 — Design/Figma ต้องให้ exact hit-target dimensions (low, non-blocking)
```

---

## 5. Completion Gate  [GATE 2]

| AC | 1.3 | 1.4 | Clarifications (resolved unless noted) |
|---|---|---|---|
| AC-01 | ✓ (mobile + desktop split) | ✓ (E-03) | GAP-04 ✅, PV-1 ✅ |
| AC-02 | ✓ (scoped playing) | ✓ (E-05) | AMB-06 → FU-2 (low) |
| AC-03 | ✓ (scoped playing) | ✓ (E-01) | CONF-06 ✅ (FU-1 doc), GAP-03 ✅ |
| AC-04 | ✓ (expanded) | ✓ (E-02, E-04) | GAP-02 ✅, CONF-08 ✅ (FU-5 Jira), AMB-03 ✅ |
| AC-05 | ✓ (video only) | ✓ | CONF-07 ✅ (live → UC2) |
| AC-06 | ✓ | ✓ (E-06) | PV-1 ✅, GAP-04 ✅ |

ครอบคลุม: 6/6 ACs
_(ไม่มี AC หลุด — Dropout Rule ✅. ทุก medium+ clarification resolved; เหลือเฉพาะ FU-2/FU-5 non-blocking)_

---

## 6. Story findings + Readiness verdict

| ID | Category | Priority | Ask | Summary | สถานะ |
|---|---|---|---|---|---|
| CONF-06 | Conflict | Low | Eng/PM | auto-dismiss 1s (Jira) vs PRD "assume 3s" | ✅ **RESOLVED** — 1s final; PRD cleanup = FU-1 |
| GAP-02 | Gap | High | Eng | overlay หลัง pause | ✅ **RESOLVED** — play icon persists, no auto-dismiss, dismiss เฉพาะ tap-outside |
| GAP-03 | Gap | High | Eng | timer reset เมื่อ interact | ✅ **RESOLVED** — 1s idle restarts ทุก interaction (web+iOS+Android) |
| GAP-04 | Gap | High | Eng/Design | 'Live' LS คนละ component | ✅ **RESOLVED** — test 2 paths per platform |
| CONF-08 | Conflict | Medium | PM/Design | seek controls บน 'Live' pause overlay | ✅ **RESOLVED** — video/recorded only; 'Live' = none. ⚠️ Jira ยังไม่ align → FU-5 |
| AMB-03 | Ambiguity | Medium | PM | double-tap gesture | ✅ **RESOLVED** — descoped, central button only |
| PV-1 | Platform variance | — | PM/QA | first-tap mobile reveal vs desktop 1-step pause | ✅ **RESOLVED** — split expected per form factor |
| AMB-06 | Ambiguity | Low | Design | pause-button hit-target size | ⚠️ **followup FU-2** — non-blocking |

**พร้อมส่ง dev หรือยัง? — ✅ READY (green).** UC1 essentially CLARIFIED — ทุก medium+ clarification resolved, ไม่มี still-ambiguous / open medium+.

- ✅ **Core fix (AC-01/02/03) พร้อม** — bug หลักที่ XM/Ulta รายงาน; timeout 1s final + timer-reset rule ชัด
- ✅ **AC-04/05 เคลียร์** — overlay-after-pause (GAP-02), seek-on-media-type (CONF-08), video-only resume + live→UC2 (CONF-07)
- ✅ **'Live' coverage + platform scope** — GAP-04 (2 paths), PV-1 (mobile/desktop split)

**Caveats to carry into test design (ไม่ block):**
1. **Per-platform expected** — split ทุก tap/pause AC: mobile {iOS/Android/web-on-mobile} = reveal-controls vs desktop {Web UIKit} = 1-Step Pause (PV-1).
2. **'Live' LS = separate component** — test video/recorded LS และ 'Live' LS เป็น 2 paths ต่อ platform (GAP-04); paused 'Live' overlay ไม่มี seek (CONF-08).
3. **FU-2 (low)** — hit-target size ยังไม่มี concrete spec จาก Design; ต้องได้ก่อนเทส pause-vs-dismiss edge ให้ deterministic (non-blocking).
4. **FU-5 (heads-up)** — story JSON ของเราตั้งใจ **diverge จาก Jira** เรื่อง seek-on-live (ถอด seek ออกจาก 'Live' overlay). PM ต้อง update Jira AC-04 text ไม่งั้น sync รอบหน้าจะดึง contradiction กลับมา.
