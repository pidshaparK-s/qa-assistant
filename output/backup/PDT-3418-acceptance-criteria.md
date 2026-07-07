# Acceptance Criteria — PDT-3418: Video & Live Streaming (Tap-to-Reveal Controls)

_Re-decomposed by method (phase-2.1) → enriched happy path (phase-1.3) → 4 scenario types (phase-2.2) → edge & error (phase-1.4)_
_Source: PRD + PDT-3562/3563/3564 + Figma (11 screens) + three-layer-analysis.md_
_Generated: 2026-06-30_

---

## ส่วนที่ 0 · Re-decomposition (phase-2.1 INVEST)

### ทำไมไม่ใช้ UC1/UC2/UC3 ของ PM ตรงๆ

PM แบ่ง story โดย "หัวข้อ" ไม่ใช่ "mechanism" ทำให้ state ปนกัน:

| ปัญหา | รายละเอียด |
|---|---|
| `PAUSED` state ถูกอธิบาย 2 ที่ | pause/resume ทั่วไป → UC1 AC-04/05 · behind-live → UC2 AC-01/02 → อ่านที่เดียวไม่เห็นพฤติกรรม paused ครบ |
| UC1 ครอบเกินชื่อ | ชื่อบอก "tap to reveal" แต่บรรจุ pause/play button + auto-dismiss + cross-surface ทั้งหมด |
| video vs live ปนใน UC1 | AC เขียน "video or live stream" ทุกข้อ แต่ live มี behavior เพิ่มที่ถูกตัดไป UC2 → ขอบเขตไม่ชัด |

### Decomposition ที่ถูกต้อง — แตกตาม implementation mechanism

```
         ┌─────────────────────────────────────────────┐
         │  STORY A · Core control gesture model        │  ← trunk (shared)
         │  tap→reveal · pause button · auto-dismiss     │     video + live เหมือนกัน
         │  · resume position · cross-surface            │
         └──────────────────┬──────────────────────────┘
                            │ extends PAUSED state
              ┌─────────────┴──────────────┐
              ▼                             ▼
   ┌────────────────────────┐   ┌──────────────────────────┐
   │ STORY B · Live paused   │   │ STORY C · 10s skip        │
   │ context (live only)     │   │ (VOD only, nice-to-have)  │
   │ behind-live · resume    │   │ skip ±10s · boundary ·    │
   │ semantics · stream-end  │   │ skip-while-paused         │
   └────────────────────────┘   └──────────────────────────┘
        depends on A                  independent · descopable
```

### INVEST check

| Story | I | N | V | E | S | T | หมายเหตุ |
|---|---|---|---|---|---|---|---|
| **A** Core control model | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ยืนได้เอง = fix bug หลักที่ลูกค้ารายงาน (XM, Ulta) |
| **B** Live paused context | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | **depends on A** (pause ต้องมีก่อน) → sequence หลัง A |
| **C** 10s skip | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | independent · PRD ระบุ descopable ได้ |

**หมายเหตุ INVEST:**
- Story A รวม tap-reveal + pause/play เป็นก้อนเดียวเพราะ **แยกไม่ได้** — ถ้า tap ไม่ pause แล้ว แต่ไม่มีปุ่ม pause ผู้ใช้จะ pause ไม่ได้เลย (Independent test ของ phase-2.1)
- Story B ไม่ผ่าน Independent โดยตั้งใจ — flag ว่าต้องทำหลัง A ไม่ใช่ blocker
- AC-06 (cross-surface) ของ PM = cross-cutting AC ของ Story A ไม่ใช่ scenario แยก

---

## STORY A · Core Control Gesture Model

```
As a community member watching a video or live stream,
I want tapping the player to reveal controls instead of pausing — with pause/play on a dedicated button —
so that I don't interrupt playback by accident during normal viewing.
```

**Applies to:** video posts + live streams · ทุก surface (global / user / community / event discussion feed / media gallery / fullscreen)
**Object:** player + controls overlay
**State machine:** `PLAYING·hidden` ⇄ `PLAYING·visible` ⇄ `PAUSED·visible` ⇄ `PAUSED·hidden`

### A — Default state

```
[A-D1 · Default — playing shows no controls]
Given a video or live stream is playing inline on any in-scope surface
When the player is rendered and the user has not interacted
Then no controls overlay is shown
  AND the media fills the player surface uninterrupted
```

### A — Happy path

```
[A-H1 · Tap playing player → reveal controls, NOT pause]   ★ core fix
Given a video or live stream is playing
  AND the controls overlay is hidden
When the user taps anywhere on the player surface
Then the controls overlay appears
  AND playback continues uninterrupted — the media does NOT pause
  AND the central control shows the pause icon (media is playing)

[A-H2 · Tap outside pause button while visible → dismiss overlay]
Given the controls overlay is visible
  AND the media is playing
When the user taps the player surface outside the central pause/play button
Then the overlay dismisses
  AND playback continues uninterrupted

[A-H3 · No action → auto-dismiss after 1s]
Given the controls overlay is visible
  AND the media is playing
When the user takes no further action for 1 second
Then the overlay auto-dismisses
  AND playback continues
  (timeout = 1 second — confirmed in Jira 2026-06-30, ref uc1-C1 RESOLVED)

[A-H4 · Tap central pause button → pause]
Given a video or live stream is playing
  AND the controls overlay is visible
When the user taps the central pause/play button
Then playback pauses at the current position
  AND the button icon switches from pause to play
  AND [PENDING A-03] the controls overlay remains visible (does not auto-dismiss while paused)

[A-H5 · Tap central play button → resume from exact position]
Given a video or live stream is paused
  AND the controls overlay is visible (or re-summoned by a tap)
When the user taps the central play/pause button
Then playback resumes from the exact position at which it was paused
  AND the button icon switches from play to pause

[A-H6 · Cross-surface consistency]   (= PM's UC1 AC-06, scoped as cross-cutting AC)
Given any in-scope surface (global / user / community / event discussion feed, media gallery, fullscreen)
When the user performs any of A-H1 … A-H5
Then the behaviour is identical regardless of surface
```

### A — Alternative / validation

```
[A-V1 · Re-summon controls while paused]
Given the media is paused
  AND the controls overlay has auto-dismissed (or been dismissed)
When the user taps anywhere on the player surface
Then the controls overlay re-appears — playback does NOT resume on this tap
  AND the central button still shows the play icon (media stays paused)

[A-V2 · Tap exactly on pause-button hit-target boundary]
Given the controls overlay is visible
When the user taps at the edge of the central button's tap target
Then the tap is resolved deterministically as either "button" or "surface" — never ambiguous
  AND [PENDING] the button hit-target size is defined (ask Design / Eng)
```

### A — Error state

```
[A-E1 · Tap during buffering / stall]
Given the media is buffering or stalled (not yet playing)
When the user taps the player surface
Then the controls overlay still appears
  AND the central button reflects the actual state (loading / paused) — not a false "playing" state
  AND no crash or frozen overlay occurs

[A-E2 · App backgrounded then resumed]
Given the media was playing with controls hidden
When the app is sent to background and later resumed
Then [PENDING] the player resumes in a defined state (playing or paused — confirm with Eng)
  AND the controls overlay state is consistent with playback state
```

### A — Edge cases (phase-1.4 · 4 models)

| ID | Model | Edge | Priority |
|---|---|---|---|
| A-EG1 | Timing | Auto-dismiss timer **reset** เมื่อ user interact กับ overlay (เช่นกด volume)? [PENDING A-02] | **High** |
| A-EG2 | Timing | กด pause พอดีตอน auto-dismiss timer กำลังจะ fire → overlay ค้างเพราะ paused หรือหาย? | High |
| A-EG3 | Timing | Rapid double-tap บนปุ่ม pause → toggle pause→play หรือ debounce? + double-tap gesture ถูก descope จริง? [PENDING A-04] | Medium |
| A-EG4 | Environment | หมุนจอ / เข้า fullscreen ขณะ controls visible → overlay persist ไหม? | Medium |
| A-EG5 | Boundary | Tap ขอบ hit-target ของปุ่ม (ดู A-V2) | Medium |

```
[A-EG1 · Edge — timer reset on interaction]   ★ High
Given the controls overlay is visible AND media is playing
  AND the user interacts with a control element (e.g. volume) before 1s elapses
When the interaction completes
Then [PENDING A-02] the auto-dismiss timer behaviour is defined —
     either it resets to a full 1s, or it continues from where it was
     (must be explicit; otherwise controls may vanish mid-use)

[A-EG2 · Edge — pause races auto-dismiss]   ★ High
Given the controls overlay is visible AND the 1s auto-dismiss is about to fire
When the user taps the central pause button at that instant
Then playback pauses
  AND the overlay does NOT auto-dismiss — it remains visible because the media is now paused
  (depends on A-03 resolution)
```

---

## STORY B · Live Stream Paused-State Context

```
As a community member watching a live stream,
I want to see that I'm paused and behind the live edge — and to resume from where I paused —
so that I understand my viewing context and can choose to catch up.
```

**Applies to:** live streams only (Room status = `live`)
**Depends on:** Story A (pause must exist) — **extends the `PAUSED` state for live streams**
**Object:** live stream player · live-edge tracking · Room state

### B — Default state

```
[B-D1 · Watching at live edge → no behind-live indicator]
Given the user is watching a live stream at the live edge (Room status = live)
When the user has not paused
Then no behind-live indicator is shown
  AND playback tracks the live edge
```

### B — Happy path

```
[B-H1 · Pause live → behind-live indicator appears immediately]
Given the user is watching a live stream at the live edge
When the user taps the central pause button (per A-H4)
Then playback pauses
  AND a behind-live indicator appears immediately — without requiring an additional tap
  AND [PENDING uc2-G1] the indicator's visual form is defined
      (badge / banner / text — NOT present in current Figma; ask PM/Design)

[B-H2 · Resume from paused live → resume from pause position]
Given the user has paused a live stream (now behind live edge)
When the user taps play (per A-H5)
Then playback resumes from the position at which it was paused — NOT from the live edge
  AND the viewer remains behind the live edge until they catch up or return to live

[B-H3 · Stream ends while paused → ended/recorded state]
Given the user has paused a live stream
When the Room transitions to ended or recorded during the pause
Then the player moves to an appropriate ended or recorded state
  AND the viewer is NOT left on a frozen frame with no feedback
```

### B — Alternative / validation

```
[B-V1 · Return to live edge]   [PENDING uc2-A1]
Given the user is paused / behind the live edge on a live stream
When the user chooses to return to the live edge
Then [PENDING] a "Return to Live" affordance behaviour is defined —
     OR it is explicitly confirmed out of scope for PDT-3418 (follow-on ticket)
     (no CTA exists in current Figma; ask PM — ref uc2-A1)
```

### B — Error state

```
[B-E1 · Network drops while paused on live]
Given the user has paused a live stream (behind live edge)
When the network connection drops and later recovers
Then [PENDING] resume behaviour is defined — resume from pause position if still buffered,
     or surface a clear state if the buffered segment expired (ask Eng)
  AND the viewer is not left on a frozen frame without feedback

[B-E2 · Stream ends while paused AND offline]
Given the user has paused a live stream AND the device is offline
When the Room transitions to ended/recorded
Then [PENDING] the player shows a defined offline-ended state on reconnect
     (not a frozen live frame)
```

### B — Edge cases (phase-1.4)

| ID | Model | Edge | Priority |
|---|---|---|---|
| B-EG1 | Timing | Host จบ stream **พอดีจังหวะ** ที่ viewer กด pause (race) → ended state หรือ paused+indicator ชนะ? | **High** |
| B-EG2 | Data integrity | Live จบขณะ paused แต่ recording ยังไม่พร้อม → placeholder / "processing" state? | High |
| B-EG3 | Boundary | Pause ตอนที่ buffer เกือบ = live edge (ตามหลังแค่เสี้ยววินาที) → indicator ยังโชว์ไหม? | Medium |

```
[B-EG1 · Edge — pause races stream end]   ★ High
Given the user is watching a live stream at the live edge
When the user taps pause AND the Room transitions to ended at the same instant
Then the resolution is deterministic — the player lands in EITHER the ended/recorded state
     OR the paused+behind-live state, never an inconsistent mix
  AND [PENDING] which state wins is defined (ask PM/Eng)

[B-EG2 · Edge — recording not yet ready on end-while-paused]   ★ High
Given the user has paused a live stream
When the Room ends but the recording is not yet available
Then the player shows a defined intermediate state (e.g. "processing" / "recording will be available")
  AND does NOT show a frozen frame or an error
```

---

## STORY C · 10-Second Skip (Nice-to-Have, VOD only)

```
As a community member watching a video,
I want to skip backward or forward 10 seconds,
so that I can quickly rewatch or jump ahead without scrubbing.
```

**Applies to:** video posts only (NOT live streams)
**Label:** nice-to-have · descopable if it impacts timeline (per PRD + PDT-3564)
**Confirmed in Figma:** skip buttons show "10" · absent on live (VR-mobile-02 / LS-mobile-02)

### C — Default state

```
[C-D1 · Controls visible on video → skip buttons present]
Given a video (not a live stream) is playing
  AND the controls overlay is visible
When the overlay is rendered
Then a skip-back (−10s) and skip-forward (+10s) button are shown alongside the central button

[C-D2 · Live stream → skip buttons NOT shown]   (= PM UC3 AC-06)
Given a live stream is playing
  AND the controls overlay is visible
When the overlay is rendered
Then the skip back and skip forward buttons are NOT shown — seeking is not applicable on a live stream
```

### C — Happy path

```
[C-H1 · Skip back −10s]
Given a video is playing AND the controls overlay is visible
  AND the current position is at least 10 seconds from the start
When the user taps the skip-back (−10s) button
Then playback jumps back exactly 10 seconds from the current position
  AND playback continues without interruption

[C-H2 · Skip forward +10s]
Given a video is playing AND the controls overlay is visible
  AND the current position is at least 10 seconds from the end
When the user taps the skip-forward (+10s) button
Then playback jumps forward exactly 10 seconds from the current position
  AND playback continues without interruption
```

### C — Alternative / boundary (phase-1.4 Boundary model)

```
[C-V1 · Skip back near start → clamp to 0:00]
Given the current position is less than 10 seconds into the video
When the user taps skip back
Then playback jumps to 0:00 — it does NOT go to a negative position

[C-V2 · Skip forward near end → final frame + end state]
Given the current position is within 10 seconds of the video end
When the user taps skip forward
Then playback jumps to the final frame and enters the end state
  AND it does NOT loop or error

[C-V3 · Skip while paused → position updates, stays paused]
Given the video is paused AND the controls overlay is visible
When the user taps either skip button
Then the position updates accordingly
  AND the video remains paused — skip does NOT auto-resume playback
```

### C — Error state

```
[C-E1 · Skip while buffering]
Given the video is buffering at the current position
When the user taps a skip button
Then [PENDING] skip behaviour is defined — queue until buffered, or seek-and-rebuffer at target
  AND no crash or stuck-loading state occurs
```

### C — Edge cases (phase-1.4)

| ID | Model | Edge | Priority |
|---|---|---|---|
| C-EG1 | Boundary | Position = exactly 10s from start → skip back = 0:00 พอดี (ไม่ใช่ค้างที่ 10s) | Medium |
| C-EG2 | Boundary | Position = exactly 10s from end → skip forward = final frame พอดี | Medium |
| C-EG3 | Timing | Rapid repeated skip taps (กดรัวๆ) → accumulate (−30s จาก 3 tap) หรือ debounce? | Medium |
| C-EG4 | Boundary | Skip back ที่ 0:00 อยู่แล้ว → ค้างที่ 0:00 ไม่ error | Low |

```
[C-EG3 · Edge — rapid repeated skip]   ★ Medium
Given a video is playing AND the controls overlay is visible
When the user taps skip-back three times in quick succession
Then [PENDING] behaviour is defined — either the jumps accumulate (−30s total)
     or they are debounced to a single −10s (ask Design/Eng)
  AND the final position is deterministic and never negative
```

---

## ส่วนที่สรุป · AC Coverage Matrix

| Story | Default | Happy | Alt/Validation | Error | Edge | รวม |
|---|---|---|---|---|---|---|
| **A** Core control | 1 | 6 | 2 | 2 | 5 | 16 |
| **B** Live paused | 1 | 3 | 1 | 2 | 3 | 10 |
| **C** 10s skip | 2 | 2 | 3 | 1 | 4 | 12 |

ทุก story ผ่าน rule-of-thumb (≥3–5 AC ครบ 4 scenario types) ✅

---

## Blocking Clarifications (ต้องตอบก่อน finalize)

| Tag | Story | คำถาม | ถามใคร | ref |
|---|---|---|---|---|
| **A-03** | A | Controls overlay ค้างอยู่ไหมเมื่อ pause? (กระทบ A-H4, A-EG2) | Engineering | three-layer Q2 |
| **A-02** | A | Auto-dismiss timer reset เมื่อ interact กับ overlay? (A-EG1) | Engineering | three-layer Q3 |
| **A-04** | A | Double-tap gesture ถูก descope? (A-EG3) | PM | three-layer Q5 |
| **uc2-G1** | B | Behind-live indicator หน้าตาเป็นอย่างไร? (ไม่มีใน Figma) | PM / Design | 1_clarifications |
| **uc2-A1** | B | "Return to Live" CTA in scope? (B-V1) | PM | 1_clarifications |
| **B-EG1** | B | Pause races stream-end → state ไหนชนะ? | PM / Eng | new |
| **uc1-G1** | A | Desktop in scope แค่ไหน? | PM | 1_clarifications |

**สถานะ:** AC draft พร้อม แต่ **ยังไม่ finalize** — มี 7 [PENDING] ที่ block อยู่
A-H1/H2/H3 (core fix) finalize ได้เลยเพราะ uc1-C1 resolved แล้ว
