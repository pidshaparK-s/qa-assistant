# Story Analysis — PDT-3564 (UC3): 10-Second Skip Back/Forward  ·  **Nice-to-Have (IN SCOPE this release)**

_Source: Jira AC (**re-synced 2026-07-08**) + resolved clarifications (`qa/PDT-3418/clarifications.json`) + PRD ("Nice to have… can be descoped") + Figma (`VR-mobile-02` skip "10"; `LS-mobile-02/03` live has no skip) + `qa/PDT-3418/platform-behavior-notes.md` — per-story lens_
_Skills: phase 1.3 → 1.4 (re-run บน current ACs) · PM's AC = source of truth, QA enriches_
_Depends on UC1 (controls overlay must exist first)_
_Clarification IDs: ledger ids (`clarifications.json`) + story-local `OI-UC3-xx`_

> **⚠️ Sync note (2026-07-08) — re-run หลัง AC re-sync + clarifications ปิดครบ:**
> analysis เดิม (2026-07-06, 6 ACs) **STALE** → re-run phase 1.3 + 1.4 บน current ACs (ตอนนี้ **8 ACs**)
> - **+2 ACs ใหม่** (group **"Rapid repeated taps (MVP)"**): **AC-07** = rapid taps **accumulate** (แต่ละ tap +±10s; icon ยังโชว์ ±10 เท่านั้น), **AC-08** = rapid taps ใกล้ start/end ยังเคารพ boundary rules mid-burst (**GAP-07** ✅)
> - **AC-03** — boundary skip-back ชน 0:00 ตอนนี้ **คงสถานะเดิม** (playing→เล่นต่อจาก 0:00, paused→คง paused) **ไม่ force pause** (**AMB-11** ✅) → สอดคล้อง AC-01/AC-05
> - **AC-04** — skip-forward ชน final frame → **end state (paused)** เพราะถึงจุดจบจริง (ไม่มีอะไรเล่นต่อ) → asymmetry vs AC-03 เป็นเจตนา
> - **AMB-04** ✅ — UC3 **IN SCOPE** release นี้ (คง flag nice-to-have; descope ได้ถ้า timeline หลุด)
> - **AMB-05** ✅ — AC-06 = in-app buttons เท่านั้น; Android native media-control scrub บน live = **bug** (FU-4)
> - **AMB-08** ✅ — exact-10s → boundary (0:00 / final frame), ไม่ off-by-one
> - **GAP-08** — mobile = seek-and-rebuffer (ชัด); web skip ขณะ buffering ยังต้อง confirm → **FU-3** (low, non-blocking)
> - ⚠️ **FU-5** — story JSON เราตั้งใจ **diverge จาก Jira** เรื่อง AC-03 preserve-state (Jira ยังเขียน "paused state") → PM ต้อง align Jira

---

## 0. AC Manifest  [GATE 1]

| AC | Group | Scenario |
|---|---|---|
| AC-01 | Skip controls | Tap skip back (−10s) → jumps back 10s, continues |
| AC-02 | Skip controls | Tap skip forward (+10s) → jumps forward 10s, continues |
| AC-03 | Boundary behaviour | Skip back at <10s from start → jumps to 0:00, **preserves prior state** |
| AC-04 | Boundary behaviour | Skip forward at <10s from end → jumps to final frame, **end state (paused)** |
| AC-05 | Skip + pause state | Skip while paused → position updates, stays paused |
| AC-06 | Live streams | Live + controls visible → skip buttons not shown (in-app only) |
| AC-07 | Rapid repeated taps (MVP) | Rapid taps **accumulate** ±10s each; icon still shows ±10 |
| AC-08 | Rapid repeated taps (MVP) | Rapid taps near start/end obey boundary rules **mid-burst** |

**Total: 8 ACs — ทั้ง 8 จะถูกวิเคราะห์ ไม่มีข้อไหนหลุด (Dropout Rule)**
**Applies to:** video post **+ recorded livestream** (NOT live) · **Platforms:** iOS · Android · RN · Flutter · WebUIKit _(Desktop = UI-only, button size)_
**⚠️ Scope note (AMB-04 ✅):** UC3 **IN SCOPE** for this release (nice-to-have flag retained). **Dependency:** needs the controls overlay from **UC1** → sequence after UC1.

---

## 1. Requirement Interrogation (phase 1.1)

### 1.1 WHO — Relationship Map

```
                  ┌──────────────────────────────┐
                  │   VIDEO / RECORDED-LS PLAYER  │
                  │   controls: −10s · ⏸ · +10s   │
                  └───────────────┬──────────────┘
                                  │
      ┌──────────────┬────────────┴───────┬──────────────────┬──────────────┐
      │              │                    │                  │              │
 [Viewer]      [Playback         [Video boundary]     [Rapid-tap      ['Live' stream —
  tap −10s /    position]         0:00 (start) /        burst]          EXCLUDED]
  +10s ·        current pos       final frame (end)     accumulate      skip buttons
  rapid burst   ±10s / clamp      · 0:00 = preserve     ±10s/tap        ไม่แสดง (AC-06)
                                    state (AMB-11 ✅)    (AC-07/08 ✅)   (native OS scrub
                                  · end  = paused                       = bug, FU-4)
```

**Actor / object analysis:**

| Actor / object | Interaction | ใน AC ไหม? |
|---|---|---|
| Viewer (video / recorded LS) | tap skip −10s / +10s | ✅ AC-01, AC-02 |
| Viewer — rapid burst | tap ซ้ำเร็ว → accumulate | ✅ **AC-07, AC-08** (GAP-07 ✅) |
| Playback position | update ±10s, clamp ที่ boundary | ✅ AC-03, AC-04 |
| Playback **state** (play/pause) | skip ไม่เปลี่ยน state; boundary 0:00 preserve, end = paused | ✅ AC-03, AC-05 (AMB-11 ✅) |
| 'Live' stream | skip buttons ไม่แสดง (in-app) | ✅ AC-06 |
| **OS native media control** | Android scrub live ได้ผ่าน native control | ✅ **resolved** — AC-06 = in-app only; native = **bug (FU-4)** |

**Silent-actor gap (RESOLVED):** precondition = "video post **or recorded livestream** (No live stream)" → recorded LS อยู่ใน scope skip (สอดคล้อง OI-UC1-02: recorded LS ใช้ video component). 'Live' stream ถูกกันออก (AC-06) — และ native OS media-control scrub บน 'Live' (Android) = **bug** ไม่ใช่ behaviour ที่ยอมรับ (AMB-05 ✅, FU-4).

### 1.2 WHAT — State Machine (playback position + state) — refreshed

```
                 tap −10s (AC-01)                       tap +10s (AC-02)
[pos=P · playing] ──────────────► [pos=P−10 · playing]  [pos=P] ──────► [pos=P+10 · playing]
      │  P < 10s from start (AC-03)                            │ P > (end−10s) (AC-04)
      ▼                                                        ▼
[pos = 0:00 · STATE PRESERVED]                          [pos = final frame · END STATE (paused)]
   • playing → continue จาก 0:00                           • ถึงจุดจบจริง → paused (ไม่มีอะไรเล่นต่อ)
   • paused  → stays paused        (AMB-11 ✅)              • ไม่ loop / ไม่ error

RAPID BURST (AC-07): tap ×N เร็ว → pos += (±10 × N)   ·  icon โชว์ ±10 เสมอ (ไม่ใช่ ±30)
   └─ ใกล้ boundary (AC-08): แต่ละ tap เคารพ AC-03/AC-04 mid-burst → ไม่ติดลบ / ไม่ loop

paused + skip (AC-05): pos updates, state ยังคง PAUSED (ไม่ auto-resume)
'Live' stream (AC-06): ปุ่ม −10s/+10s ไม่ render (in-app);  native OS scrub บน live = bug (FU-4)
```

**Boundary / transition questions — สถานะล่าสุด:**

| Question | สถานะ | Clarification |
|---|---|---|
| Rapid repeated skip taps → accumulate หรือ debounce | ✅ **RESOLVED** — accumulate (±10s/tap); icon โชว์ ±10 | **GAP-07** (AC-07/08) |
| Skip-back ชน 0:00 → pause หรือ preserve state | ✅ **RESOLVED** — preserve prior state | **AMB-11** (AC-03) |
| pos = **พอดี 10s** จาก start/end → clamp หรือ skip ปกติ | ✅ **RESOLVED** — clamp ไป 0:00 / final frame (ตรงกับ skip ปกติพอดี) | **AMB-08** |
| Skip ขณะ buffering → queue/seek-rebuffer | ⚠️ mobile ชัด (seek-rebuffer); web ยังต้อง confirm | **GAP-08 / FU-3** (low) |
| Native OS scrub บน live vs AC-06 (in-app) | ✅ **RESOLVED** — AC-06 in-app only; native = bug | **AMB-05 / FU-4** |

### 1.3 WHY — Pain & Consequence

**Pain:** viewer อยาก rewatch/jump ahead เร็วๆ โดยไม่ scrub (แม่นยำยากบนมือถือ). Nice-to-have — **IN SCOPE release นี้** (AMB-04 ✅).

**Consequence (ถ้า implement ผิด):**

| Wrong implementation | ผลกระทบ |
|---|---|
| Rapid-tap debounce (แบบ web ปัจจุบัน) แทน accumulate | tap 3 ครั้งได้ −10s ไม่ใช่ −30s → ขัด AC-07; **web ต้องแก้จาก debounce → accumulate** (GAP-07) |
| Skip-back ชน 0:00 แล้ว force pause | playing ที่ skip-back ใกล้ต้น จู่ๆ หยุด → ขัด AC-01/AC-03 (AMB-11) |
| Skip ติดลบ / loop ที่ boundary | error / วิดีโอวน → ขัด AC-03/AC-04/AC-08 |
| Skip auto-resume ทั้งที่ paused | เสีย context ผู้ใช้ → ขัด AC-05 |
| แสดง skip บน 'Live' / ยอมรับ native scrub | viewer คิดว่า seek live ได้ → ขัด AC-06; native scrub = bug (AMB-05) |

### 1.4 Gap check (phase 1.1 Step 4)

1. **Actor:** rapid-tap burst → ✅ resolved (GAP-07, AC-07/08); native OS scrub บน live → ✅ resolved (AMB-05, bug FU-4).
2. **State transitions:** boundary-preserve-state → ✅ resolved (AMB-11); exact-10 → ✅ resolved (AMB-08); buffering → ⚠️ mobile ชัด, web = FU-3 (low).
3. **Why → decision:** descope decision → ✅ **IN SCOPE** (AMB-04).

---

## 2. Three-Layer Analysis (phase 1.2)

```
Business Goal   video navigation สะดวก → viewer อยู่กับ VOD/recorded content นานขึ้น (secondary ต่อ core fix)
      ↑
User Need       viewer skip ±10s (รวม rapid burst) เพื่อ rewatch/jump ahead โดยไม่ scrub (video + recorded LS, ไม่ใช่ live)
      ↑
System Behavior AC-01…AC-08 (skip ±10s, rapid accumulate, clamp+preserve-state boundary, stay-paused, live excluded)
```

**Behavior → Need → Goal (traceable):**

| System Behavior (AC) | → User Need | → Goal | Trace |
|---|---|---|---|
| AC-01/02 skip ±10s, playback ต่อ | jump เร็วโดยไม่ scrub | video navigation ✅ | ✅ |
| AC-07 rapid accumulate (icon ±10) | กดรัวเพื่อไปไกลๆ | ✅ | ✅ GAP-07 (web ต้องแก้) |
| AC-08 rapid ใกล้ boundary เคารพ clamp | ไม่พังตอนกดรัวใกล้ขอบ | ✅ | ✅ |
| AC-03 skip-back 0:00 preserve state | ไม่สะดุด state ตอนชนต้น | ✅ | ✅ AMB-11 |
| AC-04 skip-forward final frame → paused | ถึงจบแล้วหยุด | ✅ | ✅ |
| AC-05 skip ขณะ paused → stays paused | ตั้งตำแหน่งโดยไม่เล่น | ✅ | ✅ |
| AC-06 live ไม่มี skip (in-app) | ไม่หลอกว่า seek live ได้ | ✅ | ✅ AMB-05 (native = bug) |

**5 Gap types — สถานะล่าสุด:**

| Gap type | สิ่งที่พบ | Clarification | สถานะ |
|---|---|---|---|
| ~~Scope decision~~ | ~~nice-to-have อยู่/ไม่อยู่ release~~ | **AMB-04** | ✅ IN SCOPE |
| ~~Assumed context~~ | ~~rapid-tap accumulate/debounce~~ | **GAP-07** | ✅ accumulate (AC-07/08); web ต้องแก้ |
| ~~Boundary precision~~ | ~~"<10s" vs "=10s พอดี"~~ | **AMB-08** | ✅ clamp ที่ exact-10 |
| ~~State transition~~ | ~~skip-back 0:00 pause หรือ preserve~~ | **AMB-11** | ✅ preserve prior state |
| ~~Ambiguous scope~~ | ~~native OS scrub บน live vs AC-06~~ | **AMB-05** | ✅ in-app only; native = bug (FU-4) |
| Assumed context | skip ขณะ buffering (web) | **GAP-08** | ⚠️ FU-3 (low, non-blocking) |

---

## 3. Happy-Path AC Enrichment (phase 1.3)  — loop ทุก AC

### 🔍 [1/8] AC-01 — Skip back −10s
```
[Happy — AC-01: skip back 10s]
Given a video or recorded livestream is playing AND the controls overlay is visible
  AND the current position is at least 10 seconds from the start
When the user taps the skip-back (−10s) button
Then playback jumps back exactly 10 seconds from the current position
  AND playback continues without interruption
Note: controls overlay ต้อง reveal ก่อน (dependency UC1); บน mobile = reveal-then-skip
```

### 🔍 [2/8] AC-02 — Skip forward +10s
```
[Happy — AC-02: skip forward 10s]
Given a video or recorded livestream is playing AND the controls overlay is visible
  AND the current position is at least 10 seconds from the end
When the user taps the skip-forward (+10s) button
Then playback jumps forward exactly 10 seconds from the current position
  AND playback continues without interruption
```

### 🔍 [3/8] AC-03 — Skip back <10s from start → 0:00, preserve state
**Interpretation:** boundary clamp ที่ 0:00 + **preserve prior playback state** (AMB-11) — ไม่ force pause (ต่างจากเดิมที่เขียน "paused state").
```
[Boundary — AC-03: clamp to 0:00, state preserved]
Given a video / recorded LS AND the current position is less than 10 seconds into the video
When the user taps skip back
Then playback jumps to 0:00 — it does NOT go to a negative position
  AND [state หลัง action] prior playback state is PRESERVED — playing → continues from 0:00; paused → stays paused (NOT a forced pause)
Note [AMB-11]: consistent กับ AC-01 (playing skip ต่อ) และ AC-05 (paused skip คง paused). ⚠️ Jira AC-03 ยังเขียน "paused state" → PM align Jira (FU-5)
Note [AMB-08]: pos = พอดี 10s จาก start → skip-back = 0:00 (ตรงกับ skip ปกติ)
```

### 🔍 [4/8] AC-04 — Skip forward <10s from end → final frame + end state
**Interpretation:** clamp ที่ final frame → **end state (paused)** เพราะถึงจุดจบจริง (asymmetry vs AC-03 เป็นเจตนา — ไม่มีอะไรเล่นต่อจากท้ายคลิป).
```
[Boundary — AC-04: clamp to final frame, end state]
Given a video / recorded LS AND the current position is within 10 seconds of the end
When the user taps skip forward
Then playback jumps to the final frame and enters the end state (paused at the final frame)
  AND it does NOT loop or error
Note: end = paused เพราะถึงจุดจบ (ไม่มี content เล่นต่อ) — ต่างจาก AC-03 (0:00 ยังมี content ข้างหน้า → preserve state)
Note [AMB-08]: pos = พอดี 10s จาก end → skip-forward = final frame (ตรงกับ skip ปกติ)
```

### 🔍 [5/8] AC-05 — Skip while paused → stays paused
```
[Alternative — AC-05: skip preserves paused state]
Given the video is paused AND the controls overlay is visible
When the user taps either skip button
Then the position updates accordingly (frame ที่ตำแหน่งใหม่แสดงผล)
  AND the video remains paused — skip does NOT auto-resume playback
```

### 🔍 [6/8] AC-06 — 'Live' stream → skip buttons not shown (in-app only)
```
[Constraint — AC-06: no in-app skip on live]
Given a 'Live' stream is playing AND the controls overlay is visible
When the overlay is rendered
Then the skip-back / skip-forward buttons are NOT shown — seeking not applicable on live (in-app)
Note [AMB-05 ✅]: scope = in-app overlay buttons เท่านั้น. Android OS-native media-control scrub บน live = **bug** (ไม่ยอมรับ) → file แยก FU-4
Note: recorded livestream (≠ 'Live') อยู่ใน scope skip ตาม precondition
```

### 🔍 [7/8] AC-07 — Rapid repeated taps → accumulate (icon ±10)
**Interpretation (NEW):** rapid burst แต่ละ tap +±10s สะสม; icon โชว์ ±10 เสมอ (accumulated-total UI = future enhancement).
```
[Happy — AC-07: rapid taps accumulate]
Given a video / recorded LS AND the controls overlay is visible
When the user taps a skip button multiple times quickly (e.g. skip-forward ×3 ที่ 1:00)
Then each tap adds 10 seconds to the total (→ 1:30) — taps accumulate
  AND the skip icon does NOT show the accumulated total — it always shows +10 or -10
Note [GAP-07 ✅]: PM 68330 + iOS 68329. ⚠️ web ปัจจุบัน = debounce-to-single (Chayanit 68304) → **web ต้องแก้เป็น accumulate** เพื่อ meet AC (dev + QA note)
```

### 🔍 [8/8] AC-08 — Rapid taps near boundary → obey boundary rules mid-burst
**Interpretation (NEW):** ระหว่าง burst ที่ใกล้ start/end แต่ละ tap ยังเคารพ AC-03/AC-04 — ไม่ติดลบ / ไม่ loop.
```
[Boundary — AC-08: rapid burst respects boundaries]
Given the user taps a skip button multiple times quickly near the start or end of the video
When a tap would move playback past 0:00 or past the final frame
Then that tap follows the boundary rules (AC-03 / AC-04) — it does NOT go negative or loop, even mid-burst
  AND [state หลัง action] final position deterministic; ชน 0:00 → preserve state, ชน final frame → end state
```

---

## 4. Edge & Error AC (phase 1.4)  — 4 models + priority

### ส่วนที่ 1 — Edge/Error cases found

| ID | Model | Edge/Error case | สถานะ | Priority |
|---|---|---|---|---|
| E-01 | Timing | Rapid repeated skip taps → accumulate (−30s/3tap), icon โชว์ ±10 | ✅ RESOLVED (GAP-07 → AC-07) | **High** |
| E-02 | Boundary | Rapid burst ใกล้ start/end → แต่ละ tap เคารพ clamp mid-burst | ✅ RESOLVED (AC-08) | **High** |
| E-03 | Boundary | pos = **พอดี 10s** จาก start/end → clamp = 0:00 / final frame | ✅ RESOLVED (AMB-08) | Medium |
| E-04 | Boundary | Skip-back ชน 0:00 ขณะ **playing** → เล่นต่อจาก 0:00 (ไม่ pause) | ✅ RESOLVED (AMB-11) | **High** |
| E-05 | Boundary | Skip-back ที่ 0:00 อยู่แล้ว / skip-forward ที่ final frame → ไม่ error/loop | ✅ derived (AC-03/04/08) | Low |
| E-06 | Environment | Skip ขณะ buffering → mobile seek-rebuffer; **web ยังต้อง confirm** | ⚠️ FU-3 (low) | Medium |
| E-07 | Data integrity | Video/recorded LS สั้นกว่า 10s → skip = start/end ทันที (clamp) | open (test-design) | Low |
| E-08 | Environment | Android native media-control scrub บน 'Live' | ✅ = **bug** (AMB-05, FU-4) — ไม่ใช่ AC | (bug) |

### ส่วนที่ 2 — Priority
- **High:** E-01, E-02, E-04 · **Medium:** E-03, E-06 · **Low:** E-05, E-07 · **Bug (แยก):** E-08 (FU-4)
- **Cross-cutting dev/QA note:** web rapid-tap ต้องเปลี่ยนจาก debounce → accumulate (GAP-07) — เป็น behaviour change เฉพาะ web ที่ต้องเทสยืนยัน.

### ส่วนที่ 3 — Edge/Error AC (High ก่อน)

```
[Edge — Timing, High] E-01 · rapid repeated skip accumulates  (GAP-07 → AC-07, RESOLVED)
Given a video / recorded LS is playing AND the controls overlay is visible
When the user taps skip-back three times in quick succession
Then playback moves −30s total (each tap accumulates ±10s)
  AND the skip icon still shows −10 (not −30)
  AND [state หลัง action] final position deterministic; web ต้องแก้จาก debounce → accumulate

[Edge — Boundary, High] E-02/E-04 · rapid burst + start boundary, state preserved  (AC-08 + AMB-11)
Given the current position is a few seconds into the video AND playback is PLAYING
When the user taps skip-back rapidly so a tap would pass 0:00
Then playback clamps to 0:00 — never negative, even mid-burst
  AND [state หลัง action] playback state PRESERVED — continues from 0:00 (playing) / stays paused (paused); no forced pause

[Edge — Boundary, Medium] E-03 · exact-10s boundary  (AMB-08, RESOLVED)
Given the current position is exactly 10 seconds from the start (or end)
When the user taps skip back (or forward)
Then playback lands exactly on 0:00 (or the final frame) — deterministic, no off-by-one

[Error — Environment, Medium/FU-3] E-06 · skip while buffering
Given the video is buffering at the current position
When the user taps a skip button
Then mobile = seek-and-rebuffer at the target position (Prisa 68329)
  AND [PENDING FU-3, web] web behaviour ของ +10/−10 mid-buffer ยังต้อง confirm (ปัจจุบันโชว์ "Reconnecting" + manual scrub)
  AND [state หลัง error] no crash, no stuck-loading; position resolves deterministically
```

---

## 5. Completion Gate  [GATE 2]

| AC | 1.3 | 1.4 | Clarifications (resolved unless noted) |
|---|---|---|---|
| AC-01 | ✓ | ✓ (E-06) | GAP-08 → FU-3 (web, low) |
| AC-02 | ✓ | ✓ (E-06) | GAP-08 → FU-3 (web, low) |
| AC-03 | ✓ (preserve state) | ✓ (E-02, E-04) | AMB-11 ✅ (FU-5 Jira), AMB-08 ✅ |
| AC-04 | ✓ (end state) | ✓ (E-03, E-05) | AMB-08 ✅ |
| AC-05 | ✓ | ✓ | — |
| AC-06 | ✓ | ✓ (E-08) | AMB-05 ✅ (native scrub = bug, FU-4) |
| AC-07 | ✓ (NEW) | ✓ (E-01) | GAP-07 ✅ (web debounce→accumulate) |
| AC-08 | ✓ (NEW) | ✓ (E-02) | GAP-07 ✅ |

ครอบคลุม: 8/8 ACs
_(ไม่มี AC หลุด — Dropout Rule ✅. ทุก medium+ clarification resolved; เหลือเฉพาะ FU-3 (web buffer, low) + FU-4 (native-scrub bug, แยก) + FU-5 (Jira align) non-blocking)_

---

## 6. Story findings + Readiness verdict

| ID | Category | Priority | Ask | Summary | สถานะ |
|---|---|---|---|---|---|
| AMB-04 | Ambiguity (scope) | Medium | PM | nice-to-have อยู่ใน release นี้? | ✅ **RESOLVED** — IN SCOPE (คง nice-to-have flag) |
| GAP-07 | Gap (timing) | Medium | Eng | rapid repeated skip → accumulate/debounce | ✅ **RESOLVED** — accumulate (AC-07/08); ⚠️ web ต้องแก้จาก debounce |
| AMB-11 | Ambiguity | Low | PM | skip-back ชน 0:00 → pause หรือ preserve | ✅ **RESOLVED** — preserve prior state (AC-03). ⚠️ Jira ยังไม่ align → FU-5 |
| AMB-08 | Ambiguity | Low | Eng | boundary "=10s พอดี" | ✅ **RESOLVED** — clamp ที่ 0:00 / final frame |
| AMB-05 | Ambiguity | Medium | PM | native OS scrub บน live vs AC-06 (in-app) | ✅ **RESOLVED** — in-app only; native = bug (FU-4) |
| GAP-08 | Gap (environment) | Low | Eng | skip ขณะ buffering | ⚠️ **followup FU-3** — mobile ชัด, web ต้อง confirm (non-blocking) |

**พร้อมส่ง dev หรือยัง? — ✅ READY (green).** UC3 CLARIFIED + **IN SCOPE** — ทุก medium+ clarification resolved, ไม่มี still-ambiguous / open medium+.

- ✅ **Scope ชัด** — IN SCOPE release นี้ (AMB-04); recorded LS เข้าข่าย skip, 'Live' กันออก
- ✅ **Rapid-tap + boundary เคลียร์** — accumulate (AC-07/08), preserve-state ที่ 0:00 (AMB-11), exact-10 (AMB-08)
- ✅ **AC-06 scope ชัด** — in-app only; native scrub = bug (แยก)

**Caveats to carry into test design (ไม่ block):**
1. **Web behaviour change** — web rapid-tap ปัจจุบัน debounce → ต้องแก้เป็น **accumulate** ให้ตรง AC-07 (GAP-07); เทสยืนยันเฉพาะ web.
2. **FU-3 (low)** — web skip-during-buffer ยังต้อง confirm 1 จุด (mobile = seek-rebuffer ชัดแล้ว).
3. **FU-4 (bug, แยก)** — file defect: Android native media-control scrub บน live stream (ไม่ยอมรับ, ref 68264).
4. **Dependency** — ต้องมี controls overlay จาก **UC1** ก่อน → sequence หลัง UC1.
5. **FU-5 (heads-up)** — story JSON เราตั้งใจ **diverge จาก Jira** เรื่อง AC-03 preserve-state (Jira ยังเขียน "paused state"). PM ต้อง align Jira ไม่งั้น sync รอบหน้าดึงกลับ.

**Blocking:** ไม่มี. ทุก caveat เป็น test-scope / dev-note / doc-alignment, ไม่ใช่ open decision.
