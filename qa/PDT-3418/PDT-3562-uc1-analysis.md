# Story Analysis — PDT-3562 (UC1): Tap to Reveal Controls

_Source: Jira AC (synced 2026-07-06 17:02) + PRD (`products/PDT-3418/prd/Video & live streaming.html`) + Figma (`current-01/02`, `VR-mobile-00/01/02`, `LS-mobile-01/02/03`, `LS-desktop-01`) — per-story lens_
_Skills: phase 1.1 → 1.2 → 1.3 → 1.4 · PM's AC = source of truth, QA enriches (ไม่เขียนทับ)_
_Clarification IDs cross-referenced to `PDT-3418-clarifications-for-pm-design.md`_

> **Sync note (2026-07-06):** Jira เพิ่ม **Platforms section** — supported = iOS/Android/RN/Flutter/WebUIKit; **Desktop ไม่เปลี่ยน behavior แค่ปรับ UI เล็กน้อย (ขนาดปุ่ม)** → เคลียร์ desktop-scope (เดิม UC1-Q5/CONF-05). AC ทั้ง 6 ข้อไม่เปลี่ยน

---

## 0. AC Manifest  [GATE 1]

| AC | Group | Scenario |
|---|---|---|
| AC-01 | Tap behaviour | Tap playing player → controls overlay appears, playback continues |
| AC-02 | Tap behaviour | Tap outside pause button while overlay visible → overlay dismisses, playback continues |
| AC-03 | Tap behaviour | No action after overlay appears → auto-dismiss after 1s |
| AC-04 | Pause/play button | Tap pause button while playing → pauses, icon changes |
| AC-05 | Pause/play button | Tap play button while paused → resumes from exact position, icon changes |
| AC-06 | Platform & surface | Behaviour identical across all in-scope surfaces |

**Total: 6 ACs — ทั้ง 6 จะถูกวิเคราะห์ ไม่มีข้อไหนหลุด (Dropout Rule)**
**Platforms:** iOS · Android · React Native · Flutter · WebUIKit · _(Desktop = UI-only change, no behaviour change)_

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
 [Community member]  [Auto-dismiss    [Render path]      [Concurrent
  (primary actor)     timer/System]    video = recorded    viewers]
  tap / pause /        hide overlay     LS (same comp.)     each = own
  play                 after 1s         ≠ Live LS (diff.)   player state
                                        → OI-UC1-02         (silent)
```

**Actor analysis:**

| Actor | Interaction | ใน AC ไหม? |
|---|---|---|
| Community member (viewer) | tap surface, tap pause/play button | ✅ AC-01…AC-05 |
| System (auto-dismiss timer) | ซ่อน overlay หลัง 1s | ✅ AC-03 |
| Render path — video / recorded LS | ใช้ component เดียวกัน (web) | ⚠️ implied (OI-UC1-02) |
| Render path — **'Live' live stream** | ใช้ **คนละ component** (web) | ❌ ไม่แยกใน AC — **UC1-Q6** |
| Concurrent viewers | player state เป็น per-viewer อิสระ | ❌ ไม่มีใน AC (acceptable) |

**Silent-actor gap:** Jira comment (Chayanit, 2026-07-03) — บน web "video" กับ "recorded live stream" ใช้ video component เดียวกัน แต่ **'Live' live stream ใช้คนละ component**. AC-01 เขียนรวม "a video or live stream" ทุกข้อ → tap-to-reveal ที่ผ่านบน video/recorded LS **ไม่ครอบคลุม Live LS อัตโนมัติ** (**UC1-Q6**). _(หมายเหตุ: UC3 อัปเดต precondition ให้ recorded LS เข้าข่าย video-family แล้ว — สนับสนุน insight นี้)_

### 1.2 WHAT — State Machine (player + overlay)

```
[PLAYING · overlay HIDDEN]
      │  tap surface (AC-01)
      ▼
[PLAYING · overlay VISIBLE] ──── 1s no action (AC-03) ────► [PLAYING · overlay HIDDEN]
      │        │
      │        │ tap OUTSIDE pause button (AC-02)
      │        └────────────────────────────────► [PLAYING · overlay HIDDEN]
      │
      │ tap central pause button (AC-04)
      ▼
[PAUSED · overlay ???]  ◄── UC1-Q2: overlay ยังอยู่ หรือ auto-dismiss? ไม่ระบุ
      │        ▲
      │        │ tap surface re-summon (AC-05: "re-summoned by a tap")
      ▼        │
[PAUSED · overlay HIDDEN] ─── tap play button (AC-05) ──► [PLAYING · overlay VISIBLE]
```

**Missing transitions (ยังไม่ตอบ):**

| Transition / question | สถานะ | Clarification |
|---|---|---|
| PLAYING→PAUSED: overlay ค้าง หรือ auto-dismiss? | ❓ ไม่ระบุ | **UC1-Q2** (High) |
| Auto-dismiss timer (1s) reset เมื่อ user interact? | ❓ ไม่ระบุ | **UC1-Q3** (High) |
| Tap ที่ขอบ hit-target ของปุ่ม = button/surface? | ❓ ไม่ระบุ | **UC1-Q7** (Low) |

### 1.3 WHY — Pain & Consequence

**Pain:** PRD A1 — tap ที่ใดก็ได้ = pause ขัด convention (YouTube/TikTok/FB) → viewer pause โดยไม่ตั้งใจ; live stream ยิ่งแย่ (ตกหลัง live edge). Context: มือถือ tap พลาดง่าย.

**Consequence (ถ้า implement ผิด):**

| Wrong implementation | ผลกระทบ |
|---|---|
| Timeout สั้น/นานเกิน | overlay หายเร็ว / บัง content นาน |
| overlay dismiss ทุก tap (รวมปุ่ม) | user กด pause แต่ overlay หาย → งง |
| Live LS ไม่เทสแยก (คนละ component) | core fix ผ่านบน video แต่ Live ยัง tap-to-pause |

### 1.4 Gap check (phase 1.1 Step 4)

1. **Actor ที่ยังไม่ถาม:** 'Live' LS render path (UC1-Q6). ✅
2. **State transition ยังไม่ cover:** controls-after-pause (UC1-Q2), timer-reset (UC1-Q3). ✅
3. **Why → decision:** pause mechanism = "central button **or double-tap** — Design to recommend" (PRD) ยังไม่ตัด (UC1-Q4).

---

## 2. Three-Layer Analysis (phase 1.2)

```
Business Goal   ลด accidental disruption ใน viewing session → รักษา engagement (PRD: XM, Ulta รายงาน)
      ↑
User Need       viewer tap player ได้โดยไม่กลัว pause โดยไม่ตั้งใจ + เข้าถึง controls ได้ตามต้องการ
      ↑
System Behavior AC-01…AC-06 (tap→reveal, pause บนปุ่มเดียว, auto-dismiss, resume ตรงตำแหน่ง, ทุก surface)
```

**Behavior → Need → Goal (traceable):**

| System Behavior (AC) | → User Need | → Goal |
|---|---|---|
| AC-01 tap → controls, playback ต่อ | tap ได้โดยไม่กลัว | ลด accidental pause ✅ |
| AC-02 tap นอกปุ่ม → dismiss | เคลียร์ controls | ✅ |
| AC-03 auto-dismiss 1s | controls ไม่บังนาน | ✅ |
| AC-04 pause เฉพาะปุ่มกลาง | pause แบบตั้งใจ | ลด accidental pause ✅ |
| AC-05 resume ตรงตำแหน่ง | resume แม่นยำ | ✅ |
| AC-06 cross-surface | behavior คาดเดาได้ | ✅ |

**5 Gap types:**

| Gap type | สิ่งที่พบ | Clarification |
|---|---|---|
| Assumed context | timer reset เมื่อ interact | UC1-Q3 |
| Assumed context | overlay state หลัง pause | UC1-Q2 |
| Orphaned/undecided | double-tap gesture (PRD "Design to recommend") | UC1-Q4 |
| Silent user need | Live LS component ต่าง → coverage | UC1-Q6 |
| ~~Ambiguous scope~~ | ~~desktop scope~~ → **✅ RESOLVED** (Jira 2026-07-06: no behaviour change, UI-only) | ~~UC1-Q5~~ |

---

## 3. Happy-Path AC Enrichment (phase 1.3)  — loop ทุก AC

### 🔍 [1/6] AC-01 — Tap playing player → reveal controls

**Interpretation:** Given ไม่ระบุ overlay state ก่อน tap (ต้อง hidden) / render path; Then ไม่ระบุ icon ปุ่มกลาง.

```
[Happy — AC-01: tap reveals controls, does NOT pause]
Given a video or live stream is playing on any in-scope surface
  AND the controls overlay is currently hidden
When the user taps anywhere on the player surface
Then the controls overlay appears
  AND playback continues uninterrupted — the media does NOT pause
  AND the central button shows the PAUSE icon (reflecting playing state)
Note: [P-UC1-Q6] verify แยกบน 'Live' live stream (คนละ component)
```

### 🔍 [2/6] AC-02 — Tap outside pause button → dismiss overlay

```
[Happy — AC-02: tap outside button dismisses overlay]
Given the controls overlay is visible AND the media is playing
When the user taps the player surface OUTSIDE the central pause/play button's tap target
Then the overlay dismisses
  AND playback continues uninterrupted
Note: [P-UC1-Q7] hit-target ของปุ่มกลางต้องนิยาม
```

### 🔍 [3/6] AC-03 — No action → auto-dismiss after 1s

```
[Happy — AC-03: overlay auto-dismisses after 1s idle]
Given the controls overlay is visible AND the media is playing
When the user takes no further action for 1 second
Then the overlay auto-dismisses
  AND playback continues
Note: [P-UC1-Q1] timeout = 1s (Jira RESOLVED); PRD ยังเขียน "assume 3s" — sync ให้ตรง
Note: [P-UC1-Q3] timer reset เมื่อ interact ก่อนครบ 1s?
```

### 🔍 [4/6] AC-04 — Tap pause button while playing → pause

```
[Happy — AC-04: central button pauses playback]
Given a video or live stream is playing AND the controls overlay is visible
When the user taps the central pause/play button
Then playback pauses at the current position
  AND the button icon switches from pause → play
  AND [PENDING P-UC1-Q2] overlay remains visible while paused (ไม่ auto-dismiss ระหว่าง paused)
```

### 🔍 [5/6] AC-05 — Tap play button while paused → resume from exact position

```
[Happy — AC-05a: resume from exact paused position]
Given a video or live stream is paused AND the controls overlay is visible
When the user taps the central play button
Then playback resumes from the EXACT position at which it was paused
  AND the button icon switches from play → pause

[Happy — AC-05b: re-summon controls while paused does NOT resume]
Given the media is paused AND the overlay has dismissed
When the user taps anywhere on the player surface
Then the overlay re-appears AND playback stays paused (button still shows play) — tap does NOT resume
```
> ⚠️ **Cross-story note:** AC-05 (video/VOD) resume = จากตำแหน่งที่ pause. แต่ **UC2 AC-02 (live stream) เปลี่ยนเป็น resume ไป current live moment** (ไม่ใช่ pause position) — behavior ต่างกันระหว่าง VOD กับ Live โดยตั้งใจ

### 🔍 [6/6] AC-06 — Behaviour identical across all in-scope surfaces

**Interpretation:** surfaces = global/user/community/event-discussion feed + media gallery + fullscreen (PRD). Desktop = **ไม่เปลี่ยน behavior** (UI-only) → เคลียร์แล้ว.

```
[Happy — AC-06: cross-surface consistency]
Given any in-scope surface (global / user / community / event-discussion feed, media gallery, fullscreen)
When the user performs any of AC-01…AC-05
Then the behaviour is identical regardless of surface
Note: ✅ Desktop = no behaviour change, UI-only (Jira 2026-07-06) — เดิม UC1-Q5 RESOLVED
Note: [P-UC1-Q6] web mobile vs web desktop + 'Live' component ยังต้อง verify
```

---

## 4. Edge & Error AC (phase 1.4)  — 4 models + priority

### ส่วนที่ 1 — Edge cases found

| ID | Model | Edge case | Priority |
|---|---|---|---|
| E-01 | Timing | Timer reset เมื่อ interact ก่อนครบ 1s (UC1-Q3) | **High** |
| E-02 | Timing | กด pause พอดีจังหวะ auto-dismiss fire → overlay ค้าง/หาย? | **High** |
| E-03 | Timing | Rapid double-tap ปุ่ม pause → toggle/debounce? + double-tap gesture descope? (UC1-Q4) | Medium |
| E-04 | Environment | หมุนจอ / เข้า-ออก fullscreen ขณะ overlay visible → persist? | Medium |
| E-05 | Environment | Tap ระหว่าง buffering/stall → overlay สะท้อน state จริง | Medium |
| E-06 | Environment | App backgrounded แล้ว resume → player อยู่ state ที่นิยาม | Medium |
| E-07 | Boundary | Tap ขอบ hit-target ปุ่มกลาง (UC1-Q7) → deterministic | Medium |
| E-08 | Data integrity | 'Live' LS (คนละ component) → tap-to-reveal เหมือน video? (UC1-Q6) | **High** |

### ส่วนที่ 2 — Priority
- **High:** E-01, E-02, E-08 · **Medium:** E-03–E-07

### ส่วนที่ 3 — AC ใหม่ (High ก่อน)

```
[Edge — Timing, High] E-01 · timer reset on interaction
Given the overlay is visible AND media is playing
  AND the user interacts with a control (e.g. volume) before 1s elapses
When the interaction completes
Then [PENDING P-UC1-Q3] timer behaviour is defined (reset to 1s OR continue)
  AND [state หลัง action] overlay ไม่หายกลางที่ user ใช้อยู่

[Edge — Data integrity, High] E-08 · tap-to-reveal on 'Live' live stream
Given a 'Live' live stream is playing (different render component)
When the user taps the player surface
Then the overlay appears AND playback does NOT pause — identical to video
  AND [state หลัง action] verified on the Live component [PENDING P-UC1-Q6]
```

```
[Error — Environment] tap during buffering/stall
Given media is buffering / not yet playing
When the user taps the player surface
Then overlay appears AND central button reflects real state (loading/paused) — not false "playing"
  AND [state หลัง error] no frozen overlay, no crash; button updates when playback resumes
```

---

## 5. Completion Gate  [GATE 2]

| AC | 1.3 | 1.4 | Clarifications |
|---|---|---|---|
| AC-01 | ✓ | ✓ (E-08) | UC1-Q6 |
| AC-02 | ✓ | ✓ (E-07) | UC1-Q7 |
| AC-03 | ✓ | ✓ (E-01) | UC1-Q1, UC1-Q3 |
| AC-04 | ✓ | ✓ (E-02) | UC1-Q2 |
| AC-05 | ✓ | ✓ | — |
| AC-06 | ✓ | ✓ (E-04) | ~~UC1-Q5~~ ✅resolved |

**ครอบคลุม: 6/6 ACs — ไม่มี AC หลุด ✅**

---

## 6. Story findings + Readiness verdict

| ID | Category | Priority | Ask | Summary | สถานะ |
|---|---|---|---|---|---|
| UC1-Q1 | Conflict | Low | Eng/PM | timeout 1s (Jira) vs PRD "assume 3s" | open (doc sync) |
| UC1-Q2 | Unclear | **High** | Eng | overlay ค้าง/หายหลัง pause | open |
| UC1-Q3 | Unclear | **High** | Eng | timer reset เมื่อ interact | open |
| UC1-Q4 | Ambiguous | Medium | PM/Design | double-tap descope? | open |
| ~~UC1-Q5~~ | ~~Conflict~~ | — | — | desktop scope | ✅ **RESOLVED** (2026-07-06) |
| UC1-Q6 | Unclear | **High** | Eng/Design | 'Live' LS คนละ component | open |
| UC1-Q7 | Ambiguous | Low | Design | pause-button hit-target | open |

**พร้อมส่ง dev หรือยัง?** — **Partial (ดีขึ้นจาก desktop resolved).**
- ✅ **Core fix (AC-01/02/03) พร้อมเกือบ 100%** — bug หลักที่ XM/Ulta รายงาน; timeout resolved (1s)
- ✅ **Desktop scope เคลียร์** (2026-07-06: ไม่เปลี่ยน behavior, UI-only)
- ⚠️ **AC-04/05 ยังติด** — UC1-Q2 (overlay หลัง pause), UC1-Q3 (timer reset)
- ⚠️ **AC-06 (Live coverage)** — UC1-Q6 ('Live' LS คนละ component)

**Blocking:** UC1-Q2 (overlay-after-pause), UC1-Q6 (Live component) — เหลือเป็น Engineering questions เป็นหลัก
