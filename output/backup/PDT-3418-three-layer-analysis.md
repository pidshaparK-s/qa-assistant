# Three-Layer Analysis — PDT-3418: Video & Live Streaming (Tap to Reveal Controls)

_Source: PRD (Notion export) + Jira stories PDT-3562/3563/3564 + Figma design (11 screens)_
_Generated: 2026-06-30 | phase-1.1 + phase-1.2_

---

## PHASE 1.1 — Requirement Interrogation

### WHO — Relationship Map

```
                    ┌─────────────────────────┐
                    │     VIDEO / LS PLAYER    │
                    │   (controls overlay)     │
                    └───────────┬─────────────┘
                                │
          ┌─────────────────────┼──────────────────────┐
          │                     │                      │
   [Community Member]    [System / Timer]      [Room State Machine]
   (primary actor)       auto-dismiss           live → ended/recorded
   taps player           timeout (1s)
          │                                             │
          │                                    [Live Stream Host]
          │                                    (silent actor)
   [Other Viewers]                             broadcaster — not affected
   concurrent watchers                         by viewer pause individually
   each independent session
```

**Actor analysis:**

| Actor | Interaction | ใน AC ไหม? |
|---|---|---|
| Community member (viewer) | taps, pauses, resumes | ✅ |
| System (auto-dismiss timer) | triggers overlay hide after timeout | ✅ (AC-03) |
| Room state machine (live → ended) | ends stream while viewer paused | ✅ (UC2 AC-03) |
| Live stream host | not directly affected by viewer behavior | ❌ ไม่มีใน AC (silent — acceptable) |
| Concurrent viewers | each has independent player state | ❌ ไม่มีใน AC |

**Concurrent actor gap:**
UC2 ไม่มี AC ครอบ scenario ที่ viewer หลายคน pause พร้อมกัน — acceptable เพราะ player state เป็น per-viewer
แต่ควร explicit confirm ว่า viewer A pause ไม่มีผลต่อ viewer B

---

### WHAT — State Machine

#### Object 1: Video Player (VOD)

```
[PLAYING / CONTROLS_HIDDEN]
        │
        │ tap anywhere
        ▼
[PLAYING / CONTROLS_VISIBLE]  ──── auto-dismiss (1s) ────► [PLAYING / CONTROLS_HIDDEN]
        │         │
        │ tap     │ tap pause button
        │ outside │
        │ pause ──┘
        │ button
        ▼
[PLAYING / CONTROLS_HIDDEN]           [PAUSED / CONTROLS_VISIBLE]
                                              │         │
                                    tap play  │         │ tap outside
                                    button    │         │ pause button
                                              ▼         ▼
                                      [PLAYING / ...]  [PAUSED / CONTROLS_HIDDEN] ?
                                                              │
                                                         tap anywhere
                                                              ▼
                                                    [PAUSED / CONTROLS_VISIBLE]
```

**Invalid / missing transitions:**

| Transition | สถานะ | หมายเหตุ |
|---|---|---|
| PAUSED → END_STATE | ❓ ไม่มีใน AC | UC2 cover สำหรับ live stream เท่านั้น — VOD end while paused ไม่ได้ระบุ |
| PLAYING/CONTROLS_VISIBLE → (ถ้าแตะ pause แล้ว controls หายหรือไม่?) | ❓ ไม่ชัด | AC-04 บอก "playback pauses, icon changes" แต่ไม่บอกว่า overlay ยังอยู่หรือ auto-dismiss |
| Timer reset on interaction | ❓ ไม่ชัด | ถ้า user กด volume ขณะ overlay ขึ้น timer reset ไหม? |

#### Object 2: Live Stream Player (UC2)

```
[WATCHING_LIVE / AT_LIVE_EDGE]
        │
        │ tap pause button
        ▼
[PAUSED / BEHIND_LIVE / INDICATOR_SHOWN] ──── stream ends ────► [ENDED/RECORDED_STATE]
        │
        │ tap play button
        ▼
[PLAYING / FROM_PAUSE_POSITION / BEHIND_LIVE]
        │
        │ ??? return to live?
        ▼
[WATCHING_LIVE / AT_LIVE_EDGE]  ← OI-UC2-01: CTA "Return to Live" in scope ไหม?
```

**Missing transitions:**

| Transition | หมายเหตุ |
|---|---|
| BEHIND_LIVE → AT_LIVE_EDGE | ไม่มี AC ระบุ mechanism — เป็น OI-FIGMA-03 |
| Behind-live indicator dismiss | ถ้า user กด dismiss indicator (ถ้ามี) state เปลี่ยนยังไง? |
| Stream ends while watching live (ไม่ใช่ paused) | ไม่มีใน scope UC2 |

---

### WHY — Pain & Consequence Analysis

**Pain ที่ feature นี้แก้:**
```
ปัญหา: tap anywhere = pause — ขัดกับ convention ของ YouTube/TikTok/Facebook
Pain:  viewer pause โดยไม่ตั้งใจ → ต้องแตะเพื่อ resume → เสีย momentum
       สำหรับ live stream: pause = ตกหลัง live edge → ดูต่อไม่ได้จาก point เดิม
Context: ใช้บนมือถือขณะดู content → tap พลาดง่ายมาก
```

**Consequence ถ้า implement ผิด:**

| Wrong implementation | ผลกระทบ |
|---|---|
| Timeout 1s (สั้นเกิน) | Controls หายเร็วเกิน user ไม่ทัน interact → frustrating |
| Timeout 3s (นานเกิน) | Controls บัง content นานเกิน → ขัด immersive experience |
| Controls dismiss on any tap (ไม่ใช่แค่ outside pause button) | User พยายาม tap เพื่อ pause แล้ว controls หาย → งงและ frustrating |
| Behind-live indicator ไม่ชัด | User ไม่รู้ว่าตัวเองดูอยู่หลัง live edge → resume ไปที่ผิด |
| Desktop behavior ไม่เปลี่ยน | Inconsistency ระหว่าง platform → ทำลาย predictability |

---

## PHASE 1.2 — Three-Layer Analysis

### Layer 1: Business Goal

```
Why ladder:
"แก้ tap-to-pause บน player"
    ↓ เพื่ออะไร?
"viewer ไม่ pause โดยไม่ตั้งใจ"
    ↓ เพื่ออะไร?
"viewing session ไม่ถูกขัด — โดยเฉพาะบน live stream"
    ↓ เพื่ออะไร?
"viewer อยู่กับ content นาน engagement ไม่ drop"
    ↑ Business Goal
```

**Business Goal:** ลด accidental disruption ใน viewing session เพื่อรักษา viewer engagement
บน platform ที่ใช้ video และ live streaming เป็น engagement surface หลัก

**วัดได้จาก:** accidental pause rate, bounce rate บน live stream, viewer session length

**สำคัญ:** PRD ระบุว่า customer ที่รายงาน feedback = XM, Ulta (growth accounts)
→ fixing this เป็น trust + retention signal ไม่ใช่แค่ UX improvement

---

### Layer 2: User Needs (ทุก actor)

| Actor | User Need | มีใน AC? |
|---|---|---|
| Viewer (video) | tap player ได้โดยไม่กลัว pause โดยไม่ตั้งใจ | ✅ UC1 |
| Viewer (video) | เข้าถึง controls ได้ตามต้องการ | ✅ UC1 |
| Viewer (live stream) | รู้ว่าตัวเองอยู่ "หลัง live" เมื่อ pause | ✅ UC2 AC-01 |
| Viewer (live stream) | resume จาก position ที่ pause ได้ | ✅ UC2 AC-02 |
| Viewer (live stream) | ไม่ถูกทิ้งบน frozen frame ถ้า stream จบ | ✅ UC2 AC-03 |
| Viewer (live stream) | กลับสู่ live edge ได้ง่าย | ❌ **ไม่มี** — OI-UC2-01 |
| Viewer (video, nice-to-have) | skip forward/back โดยไม่ต้อง scrub | ✅ UC3 |
| Silent: Host | ไม่ได้รับผลกระทบจาก viewer pause | ✅ (implicit — แต่ไม่มีใน AC) |

---

### Layer 3: System Behavior → User Need Mapping

| System Behavior (AC) | → User Need | → Business Goal |
|---|---|---|
| Tap → controls appear, playback continues (UC1 AC-01) | Viewer: tap ได้โดยไม่กลัว | ลด accidental pause ✅ |
| Tap outside pause → overlay dismisses (UC1 AC-02) | Viewer: dismiss controls | ✅ |
| Auto-dismiss 1s (UC1 AC-03) | Controls auto-clear | ✅ |
| Central pause button only triggers pause (UC1 AC-04) | Intentional pause only | ลด accidental pause ✅ |
| Resume from exact position (UC1 AC-05) | Precise resume | ✅ |
| Cross-surface consistency (UC1 AC-06) | Predictable behavior | ✅ |
| Behind-live indicator on pause (UC2 AC-01) | Viewer รู้ context | ลด confusion ✅ |
| Resume from pause position, not live edge (UC2 AC-02) | Context-aware resume | ✅ |
| Stream ends during pause → ended state (UC2 AC-03) | No frozen frame | ✅ |
| Skip 10s back/forward (UC3 AC-01/02) | Quick navigation | ✅ |
| Skip boundary handling (UC3 AC-03/04) | No negative/over position | ✅ |
| Skip while paused stays paused (UC3 AC-05) | Predictable state | ✅ |
| No skip on live stream (UC3 AC-06) | Live constraint | ✅ |
| **Return to live CTA** | Viewer: กลับสู่ live edge | ✅ — **ไม่มี Behavior รองรับ** |

---

## Gaps (ลาก line ไม่ได้)

| Gap | ประเภท | Impact | ถามใคร |
|---|---|---|---|
| **Return to live CTA** ไม่มี AC — viewer อยู่หลัง live edge แล้วจะกลับมายังไง | Silent User Need | UX สำคัญสำหรับ live stream | PM |
| **Controls state หลัง pause** — overlay ยังอยู่หรือ auto-dismiss เมื่อ transition PLAYING→PAUSED | Ambiguous transition | Dev อาจ implement ต่างกัน | PM / Engineering |
| **Timer reset** — auto-dismiss timer reset เมื่อ user interact กับ controls (เช่น กด volume) ไหม | Assumed context | อาจทำ controls หายเร็วเกิน | Engineering |
| **VOD end while paused** — UC2 AC-03 cover live เท่านั้น, VOD end while paused ไม่ได้ระบุ | Missing behavior | end state behavior ไม่สอดคล้อง | PM |
| **Desktop behavior** — PRD บอก "small change on design side" แต่ scope บอก desktop ไม่ support | Conflict | desktop scope ไม่ชัด | PM |

---

## Assumptions List

| # | Assumption | ชั้น | Confirmed? | ถ้า assume ผิดจะเกิดอะไร |
|---|---|---|---|---|
| A-01 | Auto-dismiss timeout = **1 second** (Jira ระบุชัดเจน ณ วันที่ fetch) | System | ✅ Resolved (Jira 2026-06-30) | Timeout ผิด = UX ผิด / test case ผิด |
| A-02 | Controls overlay auto-dismiss timer **ไม่ reset** เมื่อ user interact กับ overlay | System | ❓ Not confirmed | ถ้า timer reset: overlay อยู่นานกว่าที่ design ต้องการ |
| A-03 | Controls overlay **ยังอยู่** เมื่อ user กด pause (PLAYING → PAUSED) | System | ❓ Not confirmed | ถ้าหาย: user ต้อง tap อีกครั้งเพื่อกด play → extra step |
| A-04 | Double-tap gesture **ถูก descope** — central button เป็นวิธีเดียวที่ trigger pause | System | ❓ ไม่ได้ระบุชัดใน AC | ถ้า double-tap ยังใช้ได้: test case เพิ่มขึ้นมาก |
| A-05 | Behind-live indicator ปรากฏ **ทันที** เมื่อ pause (ไม่มี delay) | System | ❓ Not confirmed | ถ้ามี delay: user เห็น playing state ก่อนแล้วค่อยเห็น indicator |
| A-06 | Live stream viewer **ไม่สามารถ seek/scrub** ได้เลย (ไม่ใช่แค่ไม่มี skip buttons) | System | ❓ Not confirmed | ถ้า scrub ยังได้: test coverage ไม่ครบ |
| A-07 | Controls overlay layout **เหมือนกันทุก surface** — ต่างแค่ live stream ไม่มี skip buttons | System | ✅ Implied (AC-06 + Figma) | — |
| A-08 | "Return to live" CTA **ไม่อยู่ใน scope** ticket นี้ | Scope | ❓ Not confirmed (OI-UC2-01) | ถ้า in scope: ต้องมี AC เพิ่ม + design ใหม่ |
| A-09 | Desktop behavior เปลี่ยนเฉพาะ design เล็กน้อย (**ไม่ใช่ full feature parity**) | Scope | ❓ Not confirmed (OI-FIGMA-04) | ถ้า full parity: scope ใหญ่กว่านี้มาก |
| A-10 | Viewer ที่ pause live stream แล้ว resume จะ **play จาก pause position** ไม่ใช่ live edge | System | ✅ AC-02 (UC2) | — |

---

## Readiness Assessment

| เงื่อนไข | สถานะ |
|---|---|
| Business Goal ชัดเจน วัดได้ | ✅ |
| User Need ครอบทุก actor | ⚠️ Return to live CTA ยังขาด |
| ทุก User Need มี System Behavior รองรับ | ⚠️ Return to live ไม่มี Behavior |
| ทุก System Behavior ลาก line กลับถึง Need | ✅ |
| Gap ทุกข้อได้รับคำตอบ | ❌ 5 gaps ยังเปิดอยู่ |
| Assumptions ถูก explicit | ⚠️ A-02, A-03, A-04, A-05 ยังไม่ได้ confirm |

**ผล: ยังไม่พร้อม implement เต็มรูปแบบ**

Gap ที่ block มากที่สุด:
1. **Return to live CTA** (uc2-A1) — PM ต้องตัดสินใจก่อน
2. **Controls state หลัง pause** (A-03) — Engineering ต้องระบุ

---

## คำถามกลับหา PM / Engineering

**[PM] Q1 — Return to live CTA**
> UC2 ไม่ได้ระบุว่า viewer ที่ pause แล้วอยู่หลัง live edge จะกลับสู่ live edge ได้อย่างไร
> ถ้าไม่มี CTA viewer ต้องทำ action เองโดยไม่มี guidance
> ซึ่งอาจทำให้ viewer ออกจาก stream แทนที่จะ resume
> **Return to live CTA อยู่ใน scope PDT-3418 หรือเป็น follow-on ticket?**

**[Engineering] Q2 — Controls state หลัง pause**
> AC ไม่ได้ระบุว่า controls overlay ยังอยู่หรือหายไปเมื่อ user กด pause
> ถ้า overlay หายทันทีที่ pause → user ต้อง tap ใหม่เพื่อกด play → extra step
> **Controls overlay ยังแสดงอยู่เมื่อ playback pause ไหม? และ auto-dismiss timer ยังทำงานต่อหรือ reset?**

**[Engineering] Q3 — Auto-dismiss timer reset**
> ไม่มีการระบุว่า timer reset เมื่อ user กด volume หรือ interact กับ element ใน overlay
> ถ้า timer ไม่ reset: controls อาจหายระหว่างที่ user ยังใช้อยู่
> **Auto-dismiss timer (1s) reset เมื่อ user interact กับ controls ไหม?**

**[PM] Q4 — Desktop scope**
> PRD บอก desktop "Platform not supported" แต่ก็บอก "small change on design side for desktop"
> ไม่ชัดว่า desktop ต้องเปลี่ยน behavior เหมือน mobile หรือแค่ design ที่ hover state
> **Desktop ต้องเปลี่ยน tap behavior เหมือน mobile ไหม หรือแค่ hover state เปลี่ยน?**

**[PM] Q5 — Double-tap gesture**
> PRD mention double-tap เป็น option สำหรับ pause mechanism
> แต่ AC ไม่มี double-tap เลย — assume ว่าถูก descope และ central button เป็นวิธีเดียว
> **Double-tap gesture ถูก descope แล้วใช่ไหม? หรือยังเป็น alternative ที่ต้องรองรับ?**
