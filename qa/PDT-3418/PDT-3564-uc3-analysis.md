# Story Analysis — PDT-3564 (UC3): 10-Second Skip Back/Forward  ·  **Nice-to-Have**

_Source: Jira AC (synced 2026-07-06 17:03) + PRD ("Nice to have… can be descoped") + Figma (`VR-mobile-02` confirms skip "10"; `LS-mobile-02/03` confirm live has no skip) — per-story lens_
_Skills: phase 1.1 → 1.2 → 1.3 → 1.4 · PM's AC = source of truth, QA enriches_
_Label: `nice-to-have` · descopable if it impacts delivery timeline_
_Clarification IDs cross-referenced to `PDT-3418-clarifications-for-pm-design.md`_

> **Sync note (2026-07-06 17:03):** Precondition เปลี่ยน "video post" → **"video post หรือ recorded livestream (ไม่รวม live stream)"** → ยืนยันว่า recorded LS ได้ skip buttons (สอดคล้อง OI-UC1-02: recorded LS = video component); Live ยังไม่ได้. เพิ่ม Platforms section. AC ทั้ง 6 ข้อไม่เปลี่ยน

---

## 0. AC Manifest  [GATE 1]

| AC | Group | Scenario |
|---|---|---|
| AC-01 | Skip controls | Tap skip back (−10s) → jumps back 10s, continues |
| AC-02 | Skip controls | Tap skip forward (+10s) → jumps forward 10s, continues |
| AC-03 | Boundary behaviour | Skip back at <10s from start → jumps to 0:00, no negative |
| AC-04 | Boundary behaviour | Skip forward at <10s from end → jumps to final frame, end state |
| AC-05 | Skip + pause state | Skip while paused → position updates, stays paused |
| AC-06 | Live streams | Live stream + controls visible → skip buttons not shown |

**Total: 6 ACs — ทั้ง 6 จะถูกวิเคราะห์ ไม่มีข้อไหนหลุด (Dropout Rule)**
**Applies to:** video post **+ recorded livestream** (NOT live) · **Platforms:** iOS · Android · RN · Flutter · WebUIKit _(Desktop UI-only)_

---

## 1. Requirement Interrogation (phase 1.1)

### 1.1 WHO — Relationship Map

```
                  ┌──────────────────────────────┐
                  │   VIDEO / RECORDED-LS PLAYER  │
                  │   controls: −10s · ⏸ · +10s   │
                  └───────────────┬──────────────┘
                                  │
        ┌──────────────┬──────────┴───────┬────────────────────┐
        │              │                  │                    │
   [Viewer]      [Playback      [Video boundary]      ['Live' stream —
    tap −10s /    position]      0:00 (start) /         EXCLUDED]
    +10s          current pos    final frame (end)      skip buttons
                                                         ไม่แสดง (AC-06)
                                                         (OS media control
                                                         ≠ in-app → UC3-Q4)
```

**Actor analysis:**

| Actor / object | Interaction | ใน AC ไหม? |
|---|---|---|
| Viewer (video / recorded LS) | tap skip −10s / +10s | ✅ AC-01, AC-02 |
| Playback position | update ±10s, clamp ที่ boundary | ✅ AC-03, AC-04 |
| Pause state | skip ไม่ auto-resume | ✅ AC-05 |
| 'Live' stream | skip buttons ไม่แสดง (in-app) | ✅ AC-06 |
| **OS native media control** | Android scrub live ได้ผ่าน native control | ❌ ไม่แยกจาก AC-06 — **UC3-Q4** |

**Scope clarified (2026-07-06):** precondition ตอนนี้ = "video post **or recorded livestream** (No live stream)" → **recorded LS อยู่ใน scope skip** (สอดคล้อง OI-UC1-02: recorded LS ใช้ video component). 'Live' stream ยังถูกกันออก (AC-06).

### 1.2 WHAT — State Machine (playback position)

```
                 tap −10s (AC-01)              tap +10s (AC-02)
[pos = P] ────────────────────────► [pos = P−10]   [pos = P] ────► [pos = P+10]
   │ P < 10s (AC-03)                                   │ P > (end−10s) (AC-04)
   ▼                                                   ▼
[pos = 0:00]  (ไม่ติดลบ)                       [pos = final frame → END state]

paused + skip (AC-05): pos updates, state ยังคง PAUSED (ไม่ auto-resume)
'Live' stream (AC-06): ปุ่ม −10s/+10s ไม่ render (in-app)
```

**Boundary questions:**

| Question | สถานะ | Clarification |
|---|---|---|
| pos = **พอดี 10s** จาก start/end → clamp หรือ skip ปกติ | ⚠️ AC คลุม "<10s"/"within 10s" | UC3-Q5 (Low) |
| Rapid repeated skip taps → accumulate/debounce | ❓ ไม่ระบุ | **UC3-Q2** (Med) |
| Skip ขณะ buffering → queue/seek-rebuffer | ❓ ไม่ระบุ | UC3-Q3 (Low) |

### 1.3 WHY — Pain & Consequence

**Pain:** viewer อยาก rewatch/jump ahead เร็วๆ โดยไม่ scrub (แม่นยำยากบนมือถือ). Nice-to-have.

**Consequence (ถ้าผิด):** skip ติดลบ/loop → error; skip auto-resume ทั้งที่ paused → เสีย context; rapid-tap ไม่ deterministic → position เดาไม่ได้; แสดง skip บน live → viewer คิดว่า seek live ได้.

### 1.4 Gap check

1. **Actor:** OS native scrub บน live (UC3-Q4). ✅
2. **Transition:** rapid-tap (UC3-Q2), buffering (UC3-Q3), exact-boundary (UC3-Q5). ✅
3. **Why → decision:** descope decision (UC3-Q1).

---

## 2. Three-Layer Analysis (phase 1.2)

```
Business Goal   video navigation สะดวก → viewer อยู่กับ VOD/recorded content นานขึ้น (secondary ต่อ core fix)
      ↑
User Need       viewer skip ±10s เพื่อ rewatch/jump ahead โดยไม่ scrub (video + recorded LS, ไม่ใช่ live)
      ↑
System Behavior AC-01…AC-06 (skip ±10s, clamp boundary, stay-paused, live excluded)
```

**Behavior → Need → Goal:** ทุก AC ลาก line กลับได้ ✅ (ไม่มี orphaned/conflict).

**5 Gap types:**

| Gap type | สิ่งที่พบ | Clarification |
|---|---|---|
| **Scope decision** | nice-to-have — อยู่/ไม่อยู่ release นี้ | UC3-Q1 |
| Assumed context | rapid-tap accumulate/debounce | UC3-Q2 |
| Assumed context | skip ขณะ buffering | UC3-Q3 |
| Ambiguous scope | native OS scrub บน live vs AC-06 (in-app) | UC3-Q4 |
| Boundary precision | "<10s" vs "=10s พอดี" | UC3-Q5 |

---

## 3. Happy-Path AC Enrichment (phase 1.3)  — loop ทุก AC

### 🔍 [1/6] AC-01 — Skip back −10s
```
[Happy — AC-01: skip back 10s]
Given a video or recorded livestream is playing AND the controls overlay is visible
  AND the current position is at least 10 seconds from the start
When the user taps the skip-back (−10s) button
Then playback jumps back exactly 10 seconds from the current position
  AND playback continues without interruption
```

### 🔍 [2/6] AC-02 — Skip forward +10s
```
[Happy — AC-02: skip forward 10s]
Given a video or recorded livestream is playing AND the controls overlay is visible
  AND the current position is at least 10 seconds from the end
When the user taps the skip-forward (+10s) button
Then playback jumps forward exactly 10 seconds from the current position
  AND playback continues without interruption
```

### 🔍 [3/6] AC-03 — Skip back <10s from start → 0:00
```
[Alternative/Boundary — AC-03: clamp to 0:00]
Given a video/recorded LS AND the current position is less than 10 seconds into the video
When the user taps skip back
Then playback jumps to 0:00 — it does NOT go to a negative position
Note: [P-UC3-Q5] confirm พฤติกรรมเมื่อ position = พอดี 10s (skip = 0:00)
```

### 🔍 [4/6] AC-04 — Skip forward <10s from end → final frame + end state
```
[Alternative/Boundary — AC-04: clamp to final frame]
Given a video/recorded LS AND the current position is within 10 seconds of the end
When the user taps skip forward
Then playback jumps to the final frame and enters the end state
  AND it does NOT loop or error
  AND [state หลัง action] VOD/recorded-LS end state (cross-ref: UC2 คลุม live-end; VOD-end นิยามที่นี่)
```

### 🔍 [5/6] AC-05 — Skip while paused → stays paused
```
[Alternative — AC-05: skip preserves paused state]
Given the video is paused AND the controls overlay is visible
When the user taps either skip button
Then the position updates accordingly (frame ที่ตำแหน่งใหม่แสดงผล)
  AND the video remains paused — skip does NOT auto-resume playback
```

### 🔍 [6/6] AC-06 — 'Live' stream → skip buttons not shown
```
[Default/Constraint — AC-06: no skip on live]
Given a 'Live' stream is playing AND the controls overlay is visible
When the overlay is rendered
Then the skip-back/skip-forward buttons are NOT shown — seeking not applicable on live
  AND [PENDING P-UC3-Q4] confirm scope = in-app buttons เท่านั้น (Android native media-control scrub บน live เป็นคนละเรื่อง)
Note: recorded livestream (≠ 'Live') อยู่ใน scope skip ตาม precondition ใหม่
```

---

## 4. Edge & Error AC (phase 1.4)  — 4 models + priority

### ส่วนที่ 1 — Edge cases found

| ID | Model | Edge case | Priority |
|---|---|---|---|
| E-01 | Boundary | pos = **พอดี 10s** จาก start → skip back = 0:00 พอดี (UC3-Q5) | Medium |
| E-02 | Boundary | pos = **พอดี 10s** จาก end → skip forward = final frame พอดี | Medium |
| E-03 | Boundary | Skip back ที่ 0:00 อยู่แล้ว → ค้าง 0:00 ไม่ error | Low |
| E-04 | Boundary | Skip forward ที่ final frame → ไม่ loop/error | Low |
| E-05 | Timing | Rapid repeated skip taps → accumulate (−30s/3tap) หรือ debounce? (UC3-Q2) | **Medium** |
| E-06 | Environment | Skip ขณะ buffering → queue/seek-rebuffer (UC3-Q3) | Medium |
| E-07 | Data integrity | Video/recorded LS สั้นกว่า 10s → skip = start/end ทันที | Low |

### ส่วนที่ 2 — Priority
- **High:** — (nice-to-have, ไม่มี data-loss/security) · **Medium:** E-01, E-02, E-05, E-06 · **Low:** E-03, E-04, E-07

### ส่วนที่ 3 — AC ใหม่ (Medium ก่อน)

```
[Edge — Timing, Medium] E-05 · rapid repeated skip
Given a video/recorded LS is playing AND the controls overlay is visible
When the user taps skip-back three times in quick succession
Then [PENDING P-UC3-Q2] behaviour is defined — accumulate (−30s) OR debounce to single −10s
  AND [state หลัง action] final position is deterministic and never negative

[Edge — Boundary, Medium] E-01/E-02 · exact 10s boundary
Given the current position is exactly 10 seconds from the start (or end)
When the user taps skip back (or forward)
Then playback lands exactly on 0:00 (or the final frame) — deterministic, no off-by-one

[Error — Environment, Medium] E-06 · skip while buffering
Given the video is buffering at the current position
When the user taps a skip button
Then [PENDING P-UC3-Q3] behaviour is defined — queue until buffered OR seek-and-rebuffer at target
  AND [state หลัง error] no crash, no stuck-loading; position resolves deterministically
```

---

## 5. Completion Gate  [GATE 2]

| AC | 1.3 | 1.4 | Clarifications |
|---|---|---|---|
| AC-01 | ✓ | ✓ (E-05, E-06) | — |
| AC-02 | ✓ | ✓ (E-05, E-06) | — |
| AC-03 | ✓ | ✓ (E-01, E-03) | UC3-Q5 |
| AC-04 | ✓ | ✓ (E-02, E-04) | — |
| AC-05 | ✓ | ✓ | — |
| AC-06 | ✓ | ✓ | UC3-Q4 |

**ครอบคลุม: 6/6 ACs — ไม่มี AC หลุด ✅** (story-level: UC3-Q1 descope, UC3-Q2 rapid-tap)

---

## 6. Story findings + Readiness verdict

| ID | Category | Priority | Ask | Summary |
|---|---|---|---|---|
| UC3-Q1 | Ambiguous (scope) | Medium | PM | nice-to-have อยู่ใน release นี้ หรือ descope? |
| UC3-Q2 | Unclear | Medium | Eng | rapid repeated skip → accumulate/debounce |
| UC3-Q3 | Unclear | Low | Eng | skip ขณะ buffering |
| UC3-Q4 | Ambiguous | Low–Med | PM | native OS scrub บน live vs AC-06 (in-app) |
| UC3-Q5 | Ambiguous | Low | Eng | boundary "=10s พอดี" |

**พร้อมส่ง dev หรือยัง?** — 🟢 **Conditionally ready (พร้อมสุดใน 3 story).**
- ✅ **Design ครบ** (Figma VR-mobile-02 ยืนยันปุ่ม/layout; LS-mobile-02/03 ยืนยัน live ไม่มี skip)
- ✅ **Scope ชัดขึ้น** — recorded LS เข้าข่าย skip แล้ว (precondition ใหม่)
- ⚠️ **ติดแค่ product decision + minor edges** — descope decision (UC3-Q1) เป็น blocker ระดับ planning; rapid-tap (UC3-Q2) ควร confirm
- 📌 **Dependency:** ต้องมี controls overlay จาก UC1 ก่อน → sequence หลัง UC1

**Blocking:** UC3-Q1 (descope decision) — ถ้า descope ไม่ต้องทำ story นี้; ถ้าเก็บ → UC3-Q2 (rapid-tap) ควรเคลียร์ก่อน dev
