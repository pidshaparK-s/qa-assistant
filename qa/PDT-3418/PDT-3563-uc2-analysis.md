# Story Analysis — PDT-3563 (UC2): Live Stream Pause State

_Source: Jira AC (**re-synced 2026-07-08 14:31**) + resolved clarifications (`qa/PDT-3418/clarifications.json`) + platform table (Prisa, 68264) + `qa/PDT-3418/platform-behavior-notes.md` + PRD + Figma (`LS-mobile-01…05`, `LS-desktop-01`) — per-story lens_
_Skills: phase 1.3 → 1.4 (re-run บน current ACs) · PM's AC = source of truth, QA enriches_
_Depends on UC1 (pause/play must exist first)_
_Clarification IDs: ledger ids (`clarifications.json`) + story-local `OI-UC2-xx`_

> **⚠️ Sync note (2026-07-08) — re-run หลัง AC re-sync + clarifications ปิดครบ:**
> Story ถูก re-sync จาก Jira (updated 14:31) และแก้ตาม resolved clarifications แล้ว → analysis เดิม (2026-07-06) **STALE** จึง **re-run phase 1.3 + 1.4 ใหม่ทั้งหมด** บน current ACs
> - **user_story:** ตัด "behind the live edge" ออก → _"pause and resume ... always rejoin at what is happening live"_ (**AMB-10** ✅ — PM แก้ Jira 68319; story/AC ตรงกันแล้ว)
> - **AC-01:** pause indicator = **ปุ่ม play (▶) กลางจอ** (verified Figma `LS-mobile-04`, ไม่มี badge แยก — **AMB-09** ✅) · chat วิ่ง live ต่อระหว่าง pause (✅) · เพิ่ม **tap-outside → dismiss overlay** (ปุ่ม pause/play เท่านั้น — Live **ไม่มี seek controls** — **CONF-08** ✅) stream ยัง paused · LIVE badge คงเดิม (out of scope)
> - **AC-02:** resume → **current live moment** (ไม่ใช่ paused position) — **CONF-07** ✅ ยืนยันเป็น behaviour ใหม่ทุก platform · **test tolerance:** ลง live ช้ากว่าจริงไม่กี่วิ (buffering) = expected, ห้าม assert exact-live
> - **AC-03:** stream จบตอน paused → ended/recorded state · **ended/recorded ชนะ paused เสมอ แม้เกิดพร้อมกัน** (**GAP-05** ✅) · recording ยังไม่พร้อม → แสดง "Livestream ended", ไม่มี state 'processing' กลาง, ไม่มี frozen frame (**GAP-06** ✅)
> - **Figma:** `LS-mobile-02/03/05` = playing state เหมือนกันหมด (❚❚ + LIVE badge); เฉพาะ `LS-mobile-04` = paused (▶) — ต่างกันที่ **action/semantics ไม่ใช่ pixel** (**AMB-07** ✅)

---

## 0. AC Manifest  [GATE 1]

| AC | Group | Scenario |
|---|---|---|
| AC-01 | Pause indicator | Pause live → ปุ่ม ▶ กลางจอ (pause indicator); chat วิ่ง live ต่อ; tap-outside dismiss overlay (no seek) แต่ยัง paused |
| AC-02 | Pause indicator | Resume → **current live moment** (ไม่ใช่ paused position); chat ไม่สะดุด |
| AC-03 | Stream ends while paused | Stream จบตอน paused → ended/recorded state (**ชนะ paused เสมอ**), no frozen frame |

**Total: 3 ACs — ทั้ง 3 จะถูกวิเคราะห์ ไม่มีข้อไหนหลุด (Dropout Rule)**
**Platforms:** UIKit iOS · Android · React Native · Flutter · WebUIKit · _(Desktop = UI-only, no behaviour change)_
**⚠️ Platform scope:** **mobile web pause Live stream ไม่ได้** (platform table 68264) → ตัด web-mobile ออกจาก pause/resume test scope

---

## 1. Requirement Interrogation (phase 1.1)

### 1.1 WHO — Relationship Map

```
                    ┌──────────────────────────────┐
                    │   LIVE STREAM PLAYER          │
                    │   + pause indicator (▶)       │
                    └───────────────┬──────────────┘
                                    │
      ┌──────────────┬──────────────┼───────────────┬─────────────────┐
      │              │              │               │                 │
[Viewer]      [Room state    [Live edge]      [Live chat]       [Host /
 pause /       machine]       resume target    real-time sub     broadcaster]
 resume        live→ended/    = CURRENT LIVE    keeps running     (silent)
               recorded       MOMENT ✅CONF-07  during pause
               (external)                       (AC-01/02)
```

**Actor / dependency analysis:**

| Actor / dependency | Interaction | ใน AC ไหม? |
|---|---|---|
| Viewer | pause / resume live | ✅ AC-01, AC-02 |
| Room state machine | live → ended/recorded ระหว่าง pause | ✅ AC-03 |
| **Live chat (real-time sub)** | วิ่งต่อระหว่าง pause, ไม่สะดุดตอน resume | ✅ AC-01, AC-02 |
| Live edge (resume target) | resume snap ไป current live moment | ✅ AC-02 (**CONF-07** confirmed) |
| Host / broadcaster | ไม่ได้รับผลจาก viewer pause | ✅ silent (acceptable) |

**การเปลี่ยนแปลงเชิงแนวคิด:** เดิม viewer pause → "อยู่หลัง live edge" → resume ที่เดิม (ต้อง catch up เอง). **ใหม่:** pause = หยุดวิดีโอเฉยๆ (chat วิ่งต่อ) → resume = **snap กลับ live ทันที** → ไม่มี state "ค้างหลัง live" ให้ต้องจัดการ. ทำให้ actor "rolling rewind buffer" และ "return-to-live CTA" **หมดความเกี่ยวข้อง** (moot). user_story ตัด "behind live edge" ออกแล้ว (AMB-10 ✅) → story/AC ตรงกันสมบูรณ์.

### 1.2 WHAT — State Machine (live stream player)

```
[WATCHING_LIVE · AT_LIVE_EDGE · chat live]
      │  tap pause
      │    mobile (iOS/Android): reveal controls (UC1) → tap ปุ่ม ❚❚ กลางจอ (2-step)
      │    desktop (Web UIKit):  tap = pause ตรงๆ (1-step, no behaviour change)
      │    web-on-mobile:        pause Live ไม่ได้เลย (platform table 68264)
      ▼
[PAUSED · ปุ่ม ▶ กลางจอ = pause indicator · chat STILL running live · LIVE badge คงเดิม]
      │   tap-outside ปุ่ม → overlay control dismiss (ปุ่ม pause/play เท่านั้น — NO seek บน Live, CONF-08) · ยัง PAUSED
      │
      ├─ Room ends/recorded ระหว่าง paused (AC-03) ──────► [ENDED / RECORDED · "Livestream ended"]  ✅
      │     • ended/recorded ชนะ paused เสมอ แม้เกิดพร้อมกัน (GAP-05 ✅)
      │     • recording ยังไม่พร้อม → ยังแสดง "Livestream ended" ไม่มี 'processing', ไม่มี frozen frame (GAP-06 ✅)
      │
      │  tap play / resume (AC-02)
      ▼
[PLAYING · AT CURRENT LIVE MOMENT · indicator dismissed · chat continuous]
      └─ 🆕 resume SNAP ไป current live moment (ไม่ใช่ paused position)
         • behaviour CHANGE จาก current ทุก platform (วันนี้ = resume-from-pause) — CONF-07 ✅ ยืนยัน → dev implement ใหม่ + QA เทสใหม่
         • tolerance: ลง live ช้ากว่าจริงไม่กี่วิ (normal buffering) = expected, ห้าม assert exact-live
```

**Transitions / decisions:**

| Transition / decision | สถานะ | Clarification |
|---|---|---|
| resume → current live moment (ไม่ใช่ pause position) | ✅ confirmed new behaviour (เป็น behaviour change) | **CONF-07** (OI-UC2-07) |
| pause indicator = ปุ่ม ▶ กลางจอ (ไม่มี badge แยก) | ✅ confirmed (Figma `LS-mobile-04`) | **AMB-09** (OI-UC2-08) |
| tap-outside → dismiss overlay; Live overlay **ไม่มี seek controls** | ✅ confirmed (ปุ่ม pause/play เท่านั้น) | **CONF-08** (OI-UC2-09) |
| pause races stream-end → state ไหนชนะ | ✅ ended/recorded ชนะเสมอ | **GAP-05** (OI-UC2-10) |
| stream จบตอน paused + recording ยังไม่พร้อม | ✅ "Livestream ended" (no processing) | **GAP-06** (OI-UC2-11) |
| ~~resume from pause position + rolling buffer~~ | ✅ **moot** (resume ไป live แล้ว) | ~~OI-UC2-03~~ |
| ~~return to live edge (CTA)~~ | ✅ **moot** (resume ไป live อยู่แล้ว) | ~~OI-UC2-01~~ |

### 1.3 WHY — Pain & Consequence

**Pain:** viewer อยาก pause live ชั่วคราว **โดยไม่พลาด chat** (chat วิ่งต่อ) และเมื่อ resume อยาก **กลับมาที่ live ปัจจุบันทันที** ไม่ใช่ดู footage เก่าค้าง.

**Consequence (ถ้า implement ผิด):**

| Wrong implementation | ผลกระทบ |
|---|---|
| resume จาก pause position (แบบเดิม) | viewer ดู footage เก่าค้าง ตกหลัง live → ขัด intent ใหม่ (CONF-07) |
| chat หยุดตอน pause | viewer พลาดบทสนทนา → ขัด AC-01 |
| chat replay/ข้ามข้อความตอน resume | chat เพี้ยน → ขัด AC-02 |
| ไม่มี pause indicator / ไม่ใช่ ▶ overlay | viewer ไม่รู้ว่า paused → ขัด AC-01 (AMB-09) |
| stream จบตอน paused แล้วค้าง frozen | viewer ไม่รู้ว่าจบ → ขัด AC-03 (GAP-05/06 ✅) |
| Live overlay โผล่ seek controls | ขัด UC3 AC-06 (Live ไม่มี seek) → CONF-08 |

### 1.4 Gap check

1. **Actor:** live chat + live-edge resume target — เข้า AC แล้ว ✅; behaviour change ยืนยันแล้ว (CONF-07).
2. **State transition:** pause-races-end (GAP-05 ✅), recording-not-ready (GAP-06 ✅), pause indicator visual (AMB-09 ✅), tap-outside/no-seek (CONF-08 ✅) — ปิดครบ.
3. **Why → decision:** resume-to-live เป็น decision ที่ PM ตัดแล้ว ✅ แต่เป็น behaviour change ที่ dev implement ใหม่ + QA เทส behaviour ใหม่ (พร้อม buffering tolerance).

---

## 2. Three-Layer Analysis (phase 1.2)

```
Business Goal   viewer pause live ได้โดยไม่เสีย live context (chat) และกลับเข้า live ได้ทันทีบน resume
                → ลด friction/bounce บน live stream (engagement surface หลักของ growth accounts)
      ↑
User Need       "pause แล้ว chat ไม่หาย" + "resume แล้วกลับมา live ปัจจุบัน ไม่ใช่ footage เก่า"
      ↑
System Behavior AC-01 (pause indicator ▶ + chat live), AC-02 (resume→live moment + chat ต่อเนื่อง), AC-03 (stream-end)
```

**Behavior → Need → Goal:**

| System Behavior (AC) | → User Need | → Goal | Trace |
|---|---|---|---|
| AC-01 pause indicator (▶) + chat live | รู้ว่า paused, ไม่พลาด chat | ลด friction ✅ | ✅ AMB-09 / CONF-08 resolved |
| AC-02 resume→live + chat ต่อ | กลับ live ทันที | ✅ | ✅ CONF-07 resolved (behaviour change — เทสใหม่ + tolerance) |
| AC-03 stream-end → ended state | ไม่ถูกทิ้ง frozen frame | ✅ | ✅ GAP-05 / GAP-06 resolved |

**5 Gap types — สถานะปัจจุบัน:**

| Gap type | สิ่งที่พบ | Clarification | สถานะ |
|---|---|---|---|
| Behaviour change (impl) | resume→live ≠ current (วันนี้ทุก platform resume-from-pause) | **CONF-07** | ✅ resolved (เทส behaviour ใหม่ + buffering tolerance) |
| Assumed context | pause indicator visual = ปุ่ม ▶? | **AMB-09** | ✅ resolved (Figma `LS-mobile-04`) |
| Conflict (scope) | Live pause overlay มี seek controls ไหม | **CONF-08** | ✅ resolved (NO seek บน Live) · FU-5 Jira ยังค้าง |
| Edge (timing) | pause races stream-end | **GAP-05** | ✅ resolved (ended/recorded ชนะ) |
| Edge (data) | recording ยังไม่พร้อม | **GAP-06** | ✅ resolved ("Livestream ended", no processing) |
| Doc inconsistency | `user_story` เขียน "behind the live edge" | **AMB-10** | ✅ resolved (PM reworded) |
| Design read | `LS-mobile-02/03/05` เหมือนกันใน PNG | **AMB-07** | ✅ resolved (playing state; แยกด้วย action) |

**✅ Resolved by this sync:** resume target (CONF-07), pause indicator visual (AMB-09), Live-overlay-no-seek (CONF-08), pause-races-end (GAP-05), recording-not-ready (GAP-06), user_story reword (AMB-10), Figma frames (AMB-07), LIVE badge → out of scope (OI-UC2-02), chat live during pause (OI-UC2-05), return-to-live CTA moot (OI-UC2-01), rolling buffer superseded (OI-UC2-03), stream-end confirmed (OI-UC2-04).

---

## 3. Happy-Path AC Enrichment (phase 1.3)  — loop ทุก AC

### 🔍 [1/3] AC-01 — Pause live → pause indicator (▶) + chat keeps running

**Interpretation:** Then มี 3 ส่วน: (1) visual indicator ว่า "paused" = **ปุ่ม play (▶) กลางจอ** (AMB-09 verified `LS-mobile-04`, ไม่มี badge แยก), (2) **chat วิ่ง real-time ต่อ** (ไม่ paused), (3) **tap-outside → dismiss overlay control** (ปุ่ม pause/play เท่านั้น — Live ไม่มี seek, CONF-08) แต่ stream ยัง paused. LIVE badge คงเดิม (out of scope).

```
[Happy — AC-01: pause indicator (▶) appears; chat stays live; tap-outside dismisses]
Given the user is watching a live stream at the live edge (Room status = live)
  AND (mobile) controls overlay revealed per UC1  /  (desktop) direct-tap pause available
When the user pauses via the central pause button
Then the central play (▶) button overlay is shown as the pause indicator (LS-mobile-04; NO separate badge — AMB-09)
  AND the chat continues to receive/display new messages in real time — it is NOT paused
  AND the LIVE badge / viewer-count stays AS-IS (updating it is OUT OF SCOPE — separate enhancement)
  AND tapping anywhere outside the play button dismisses the overlay control (pause/play button ONLY — a Live stream has NO seek controls — CONF-08); the stream REMAINS paused
Note: ✅ chat-live = current behaviour ทุก platform (Prisa 68264) → low implementation risk
Note: ⚠️ mobile web pause Live ไม่ได้ (platform 68264) → AC-01 pause entry ไม่ apply บน web-mobile
Note: 'Live' LS ใช้ component แยกจาก video/recorded (GAP-04) → เทส pause บน Live component โดยตรง
```

### 🔍 [2/3] AC-02 — Resume → current live moment; chat uninterrupted

**Interpretation:** Then มี 3 ส่วน: (1) **stream เริ่มจาก current live moment (ไม่ใช่ paused position)** — behaviour change ที่ยืนยันแล้ว (CONF-07), (2) pause indicator (▶) dismisses, (3) chat ต่อเนื่อง (ไม่ข้าม/ไม่ replay).

```
[Happy — AC-02: resume snaps to current live moment]
Given the user has paused a live stream (chat kept running live ระหว่าง pause)
When the user resumes (stream restarts) via the play button
Then playback starts from the CURRENT LIVE MOMENT — NOT from the previous paused position
  AND the pause indicator (▶ overlay) dismisses
  AND the chat remains uninterrupted — no messages are missed or replayed
Note: 🔄 BEHAVIOUR CHANGE — วันนี้ทุก platform (iOS/Android/web-desktop) = resume-from-paused-position (Prisa 68264).
      CONF-07 ยืนยันเป็น behaviour ใหม่ทุก platform → dev implement ใหม่, QA เทส behaviour ใหม่ (ไม่ใช่ current)
Note: ✅ TEST TOLERANCE — resume ลงใกล้ live แต่ช้ากว่าจริง "ไม่กี่วินาที" (normal live buffering) = EXPECTED.
      ห้าม assert exact-live; assert "≈ live within buffering tolerance" (iOS 68306 / Android 68316)
```

### 🔍 [3/3] AC-03 — Stream ends while paused → ended/recorded state (priority over paused)

**Interpretation:** Then มี 3 ส่วน: (1) player ไป ended/recorded state, (2) **ended/recorded ชนะ paused เสมอ แม้เกิดพร้อมกัน** (GAP-05), (3) ไม่ทิ้ง viewer บน frozen frame. recording ยังไม่พร้อม → "Livestream ended" ไม่มี processing (GAP-06).

```
[Happy — AC-03: stream ends during pause → ended state wins]
Given the user has paused a live stream
When the Room transitions to ended or recorded during the pause
Then the player moves to an appropriate ended or recorded state
  AND the ended/recorded state ALWAYS takes priority over the paused state (แม้เกิดพร้อมกัน — GAP-05)
  AND the viewer is NOT left on a frozen frame with no feedback
  AND if the recording is not yet ready, the player shows "Livestream ended" (NO intermediate 'processing' state — GAP-06)
Note: ✅ RESOLVED — ตรง current Android (Fidriyanto 68316) + iOS (Prisa 68306) behaviour; same as non-paused end case
```

---

## 4. Edge & Error AC (phase 1.4)  — 4 models + priority

### ส่วนที่ 1 — Edge/Error cases found (จัดหมวดตาม 4 models)

| ID | Model | Edge/Error case | Priority | สถานะ |
|---|---|---|---|---|
| E-01 | Timing | Host จบ stream **พอดีจังหวะ** viewer กด pause → state ไหนชนะ | **High** | ✅ resolved — ended/recorded ชนะเสมอ (GAP-05, AC-03 then[1]) |
| E-02 | Data integrity | Stream จบขณะ paused แต่ recording ยังไม่พร้อม → placeholder/processing? | **High** | ✅ resolved — แสดง "Livestream ended", no processing, no frozen (GAP-06) |
| E-03 | Environment | **mobile web: pause Live ไม่ได้เลย** → pause entry ต้องไม่ apply | **High** | ✅ known platform fact (68264) → ตัดออกจาก pause scope |
| E-04 | Environment | Network หลุดขณะ paused แล้วกลับมา → resume ยังไป live moment? state ชัด? | **High** | ⚠️ error path — เทส |
| E-05 | Timing | pause นาน (นาที) → resume snap ไป live ห่างมาก → loading/buffering ชัดเจน? | Medium | ⚠️ เทส (tie to CONF-07 tolerance) |
| E-06 | Timing | chat วิ่งไปไกลตอน paused → resume video snap live → chat/video align, ไม่ replay/skip | Medium | ⚠️ เทส |
| E-07 | Environment | app ถูก background/kill ขณะ paused → กลับมา state ชัด (resume-to-live / ended ถ้าจบไปแล้ว) | Medium | ⚠️ เทส |
| E-08 | Boundary | pause แล้ว resume ทันที (ยังใกล้ live) → snap ระยะสั้น ไม่กระตุก | Low | log ไว้ |

### ส่วนที่ 2 — Priority
- **High:** E-01 (✅ resolved), E-02 (✅ resolved), E-03 (platform, ✅), E-04 · **Medium:** E-05, E-06, E-07 · **Low:** E-08

### ส่วนที่ 3 — Edge/Error AC (High ก่อน)

```
[Edge — Timing, High] E-01 · pause races stream-end  — ✅ RESOLVED
Given the user is watching a live stream at the live edge
When the user taps pause AND the Room transitions to ended/recorded at the same instant
Then the player lands in the ended/recorded state — ended/recorded ALWAYS wins over paused (GAP-05)
  AND [state หลัง action] never a mixed paused+ended UI; shows "Livestream ended"; no frozen frame
Note: ✅ encoded in AC-03 then[1]; PM 68319 + iOS 68306 + Android 68316

[Edge — Data integrity, High] E-02 · recording not ready on end-while-paused  — ✅ RESOLVED
Given the user has paused a live stream
When the Room ends but the recording is not yet available
Then the player shows "Livestream ended" (same as the non-paused end case)
  AND [state หลัง action] NO intermediate 'processing' state, NO frozen frame (GAP-06)
Note: ✅ iOS 68306 / Android 68316 — lands on the ended state regardless of recording readiness

[Edge — Environment, High] E-03 · mobile web cannot pause a Live stream  — platform fact
Given the user is on mobile web watching a Live stream
When the user attempts to pause
Then pause is NOT available on web-mobile for a Live stream (platform table 68264)
  AND [state หลัง action] the AC-01/AC-02 pause+resume flow does NOT apply to web-mobile Live
Note: standing platform fact (not a defect) — see platform-behavior-notes.md PV-1 → exclude from pause test scope

[Error — Environment, High] E-04 · network drops while paused
Given the user has paused a live stream
When the network connection drops and later recovers, then the user resumes
Then playback rejoins the CURRENT live moment once reconnected (per AC-02)
  AND [state หลัง error] viewer is NOT left on a frozen frame; a clear reconnect/retry state is shown
  AND the user can retry resume (lands ≈ live within buffering tolerance, not exact-live — CONF-07)

[Edge — Timing, Medium] E-06 · chat/video re-sync on resume
Given the user paused for a while (chat kept running live)
When the user resumes (video snaps to the current live moment)
Then chat and video are aligned at the live moment — no replayed or skipped chat
  AND [state หลัง action] transition is smooth; brief buffering acceptable (within tolerance — CONF-07)
```

---

## 5. Completion Gate  [GATE 2]

| AC | 1.3 | 1.4 | Clarifications | สถานะ |
|---|---|---|---|---|
| AC-01 | ✓ | ✓ (E-03) | AMB-09, CONF-08, LIVE badge OOS, chat-live | ✅ resolved |
| AC-02 | ✓ | ✓ (E-04, E-05, E-06) | **CONF-07** (behaviour change + buffering tolerance) | ✅ resolved — เทส behaviour ใหม่ |
| AC-03 | ✓ | ✓ (E-01, E-02) | GAP-05, GAP-06 | ✅ resolved |

ครอบคลุม: 3/3 ACs

**ไม่มี AC หลุด ✅ (Dropout Rule ผ่าน)** — ทุก medium+ clarification ปิดครบ, ไม่มี `still-ambiguous` / `open`.

---

## 6. Story findings + Readiness verdict

**Clarifications (UC2) — ทั้งหมด resolved:**

| ID (ledger / story) | Category | Ask | Summary | สถานะ |
|---|---|---|---|---|
| **CONF-07** (OI-UC2-07) | Conflict / behaviour-change | Eng/PM | resume → current live moment (behaviour ใหม่ทุก platform) | ✅ resolved — เทส behaviour ใหม่ + buffering tolerance |
| **GAP-05** (OI-UC2-10) | Edge / timing | PM/Eng | pause races stream-end → ended/recorded ชนะ | ✅ resolved (AC-03 then[1]) |
| **GAP-06** (OI-UC2-11) | Edge / data | Eng | recording ยังไม่พร้อม → "Livestream ended", no processing | ✅ resolved |
| **CONF-08** (OI-UC2-09) | Conflict / scope | PM/Design | Live pause overlay **ไม่มี seek controls** | ✅ resolved — ⚠️ **FU-5**: Jira AC ยังค้าง old wording |
| **AMB-09** (OI-UC2-08) | Ambiguity | Design | pause indicator = ปุ่ม ▶ กลางจอ (Figma `LS-mobile-04`) | ✅ resolved |
| **AMB-07** | Ambiguity | Design | `LS-mobile-02/03/05` = playing state เหมือนกัน; แยกด้วย action ไม่ใช่ pixel | ✅ resolved |
| **AMB-10** | Ambiguity | PM | user_story ตัด "behind live edge" (ตรง AC แล้ว) | ✅ resolved |
| OI-UC2-02 | — | PM/Design | LIVE badge = out of scope (คงเดิม) | ✅ resolved |
| OI-UC2-05 | — | PM | chat วิ่ง live ระหว่าง pause | ✅ resolved |
| OI-UC2-01 / 03 / 04 | — | — | return-to-live moot / rolling buffer superseded / stream-end confirmed | ✅ resolved |

**พร้อมส่ง dev หรือยัง?** — 🟢 **CLARIFIED / READY** (ยกจากเดิม 🟡). ทุก medium+ ปิดครบ ไม่มี blocker เหลือ.

**Caveats (state ไว้ — ไม่ block):**
- **(i) resume-to-live เป็น behaviour CHANGE** — วันนี้ทุก platform resume-from-paused-position; dev ต้อง implement ใหม่ + QA **เทส behaviour ใหม่** ด้วย **buffering tolerance** (ลง live ช้ากว่าจริงไม่กี่วิ = expected, **ห้าม assert exact-live**). — CONF-07
- **(ii) mobile web pause Live ไม่ได้** (platform table 68264) → **ตัด web-mobile ออกจาก pause/resume test scope**; เทส pause บน iOS/Android/desktop เท่านั้น. — platform-behavior-notes.md PV-1
- **(iii) heads-up FU-5** — story JSON ของเรา **ตั้งใจ diverge** จาก Jira เรื่อง seek-on-live (Live overlay ไม่มี seek — CONF-08); **PM ต้อง align Jira AC text** ไม่งั้น next sync จะ re-introduce conflict. เป็น doc-hygiene, ไม่กระทบ test behaviour.

**Blocking:** ไม่มี. ทั้งสาม caveat เป็น test-scope / doc-alignment note, ไม่ใช่ open decision.
