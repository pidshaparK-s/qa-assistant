# Story Analysis — PDT-3563 (UC2): Live Stream Pause State

_Source: Jira AC (**rewritten 2026-07-06 17:07 by PM Ghita**, comment 68271) + platform table (Prisa, 68264) + PRD + Figma (`LS-mobile-01…05`, `LS-desktop-01`) — per-story lens_
_Skills: phase 1.1 → 1.2 → 1.3 → 1.4 · PM's AC = source of truth, QA enriches_
_Depends on UC1 (pause/play must exist first)_
_Clarification IDs cross-referenced to `PDT-3418-clarifications-for-pm-design.md`_

> **⚠️ Sync note (2026-07-06 17:07) — AC เขียนใหม่ เปลี่ยนแนวคิด:**
> - Group เปลี่ยน "Behind-live indicator" → **"Pause indicator"** — ตัดแนวคิด "behind the live edge" ออก
> - **AC-01:** เพิ่ม "chat ยังวิ่ง real-time ระหว่าง pause"
> - **AC-02:** 🔄 กลับด้าน — resume ไป **current live moment** (ไม่ใช่ paused position) + chat ไม่สะดุด
> - เคลียร์ 5 clarifications เดิม (resume target, LIVE badge, chat, web-desktop, return-to-live) → เหลือ **2 open ใหม่** (OI-UC2-07 behaviour change, OI-UC2-08 indicator visual)
> - **`user_story` ใน Jira ยังเขียน "behind the live edge" ค้างอยู่** — ไม่ตรงกับ AC ใหม่ (ควรบอก PM แก้ → OI-UC2-09)

---

## 0. AC Manifest  [GATE 1]

| AC | Group | Scenario |
|---|---|---|
| AC-01 | Pause indicator | Pause live stream → pause indicator appears; chat keeps running live |
| AC-02 | Pause indicator | Resume → stream from **current live moment** (not paused position); chat uninterrupted |
| AC-03 | Stream ends while paused | Stream ends during pause → ended/recorded state, no frozen frame |

**Total: 3 ACs — ทั้ง 3 จะถูกวิเคราะห์ ไม่มีข้อไหนหลุด (Dropout Rule)**
**Platforms:** iOS · Android · React Native · Flutter · WebUIKit · _(Desktop = UI-only, no behaviour change)_

---

## 1. Requirement Interrogation (phase 1.1)

### 1.1 WHO — Relationship Map

```
                    ┌──────────────────────────────┐
                    │   LIVE STREAM PLAYER          │
                    │   + pause indicator           │
                    └───────────────┬──────────────┘
                                    │
      ┌──────────────┬──────────────┼───────────────┬─────────────────┐
      │              │              │               │                 │
[Viewer]      [Room state    [Live edge]      [Live chat]       [Host /
 pause /       machine]       resume target    real-time sub     broadcaster]
 resume        live→ended/    = CURRENT LIVE    keeps running     (silent)
               recorded       MOMENT (new)      during pause
               (external)                       (AC-01/02)
```

**Actor / dependency analysis:**

| Actor / dependency | Interaction | ใน AC ไหม? |
|---|---|---|
| Viewer | pause / resume live | ✅ AC-01, AC-02 |
| Room state machine | live → ended/recorded ระหว่าง pause | ✅ AC-03 |
| **Live chat (real-time sub)** | วิ่งต่อระหว่าง pause, ไม่สะดุดตอน resume | ✅ **AC-01, AC-02 (ใหม่)** |
| Live edge (resume target) | resume snap ไป current live moment | ✅ AC-02 (ใหม่) |
| Host / broadcaster | ไม่ได้รับผลจาก viewer pause | ✅ silent (acceptable) |

**การเปลี่ยนแปลงเชิงแนวคิด:** เดิม viewer pause → "อยู่หลัง live edge" → resume ที่เดิม (ต้อง catch up เอง). **ใหม่:** pause = หยุดวิดีโอเฉยๆ (chat วิ่งต่อ) → resume = **snap กลับ live ทันที** → ไม่มี state "ค้างหลัง live" ให้ต้องจัดการ. ทำให้ actor "rewind buffer" และ "return-to-live CTA" **หมดความเกี่ยวข้อง**.

### 1.2 WHAT — State Machine (live stream player)  — NEW model

```
[WATCHING_LIVE · AT_LIVE_EDGE · chat live]
      │  tap pause (ผ่าน UC1 AC-04)
      ▼
[PAUSED · pause indicator shown · chat STILL running live]
      │        │ Room ends/recorded (AC-03) ──────────────► [ENDED / RECORDED]  ✅
      │        │ recording ยังไม่พร้อม ─────────────────────► [PROCESSING ???]  ❓ GAP-06
      │
      │  tap play / resume (AC-02)
      ▼
[PLAYING · AT CURRENT LIVE MOMENT · indicator dismissed · chat continuous]
      ▲
      └─ 🆕 resume SNAP ไป live moment (ไม่ใช่ paused position)
         ← current behaviour ทุก platform = resume-from-pause → นี่คือ behaviour CHANGE (OI-UC2-07)
```

**Transitions / questions:**

| Transition / question | สถานะ | Clarification |
|---|---|---|
| resume → current live moment (ไม่ใช่ pause position) | ⚠️ เปลี่ยนจาก current behaviour ทุก platform | **OI-UC2-07** (Med-High) |
| pause indicator visual = ปุ่ม ▶ กลางจอ หรือ element แยก | ❓ ไม่ชัด (Figma LS-mobile-04 = ▶) | **OI-UC2-08** (Low) |
| pause races stream-end → state ไหนชนะ | ❓ ไม่ระบุ | **GAP-05** (High edge) |
| stream จบตอน paused + recording ยังไม่พร้อม | ❓ ไม่ระบุ | **GAP-06** (Med edge) |
| ~~resume from pause position + rolling buffer~~ | ✅ **moot** (resume ไป live แล้ว) | ~~OI-UC2-03~~ |
| ~~return to live edge (CTA)~~ | ✅ **moot** (resume ไป live อยู่แล้ว) | ~~OI-UC2-01~~ |

### 1.3 WHY — Pain & Consequence

**Pain (ใหม่):** viewer อยาก pause live ชั่วคราว **โดยไม่พลาด chat** (chat วิ่งต่อ) และเมื่อ resume อยาก**กลับมาที่ live ปัจจุบันทันที** ไม่ใช่ดู footage เก่าค้าง.

**Consequence (ถ้า implement ผิด):**

| Wrong implementation | ผลกระทบ |
|---|---|
| resume จาก pause position (แบบเดิม) | viewer ดู footage เก่าค้าง ไม่รู้ว่าตกหลัง live → ขัด intent ใหม่ |
| chat หยุดตอน pause | viewer พลาดบทสนทนา → ขัด AC-01 |
| chat replay/ข้ามข้อความตอน resume | chat เพี้ยน → ขัด AC-02 |
| ไม่มี pause indicator | viewer ไม่รู้ว่า paused |
| stream จบตอน paused แล้วค้าง frozen | viewer ไม่รู้ว่าจบ (AC-03 กันไว้ — resolved) |

### 1.4 Gap check

1. **Actor:** live chat + live-edge resume target — เข้า AC แล้ว ✅; behaviour change ยัง open (OI-UC2-07).
2. **State transition:** pause-races-end (GAP-05), recording-not-ready (GAP-06), pause indicator visual (OI-UC2-08).
3. **Why → decision:** resume-to-live เป็น decision ที่ PM ตัดแล้ว ✅ แต่เป็น behaviour change ที่ dev/QA ต้อง aware (OI-UC2-07).

---

## 2. Three-Layer Analysis (phase 1.2)

```
Business Goal   viewer pause live ได้โดยไม่เสีย live context (chat) และกลับเข้า live ได้ทันทีบน resume
                → ลด friction/bounce บน live stream (engagement surface หลักของ growth accounts)
      ↑
User Need       "pause แล้ว chat ไม่หาย" + "resume แล้วกลับมา live ปัจจุบัน ไม่ใช่ footage เก่า"
      ↑
System Behavior AC-01 (pause indicator + chat live), AC-02 (resume→live moment + chat ต่อเนื่อง), AC-03 (stream-end)
```

**Behavior → Need → Goal:**

| System Behavior (AC) | → User Need | → Goal | Trace |
|---|---|---|---|
| AC-01 pause indicator + chat live | รู้ว่า paused, ไม่พลาด chat | ลด friction ✅ | ⚠️ indicator visual (OI-UC2-08) |
| AC-02 resume→live + chat ต่อ | กลับ live ทันที | ✅ | ⚠️ behaviour change (OI-UC2-07) |
| AC-03 stream-end → ended state | ไม่ถูกทิ้ง frozen frame | ✅ | ✅ resolved (OI-UC2-04) |

**5 Gap types:**

| Gap type | สิ่งที่พบ | Clarification |
|---|---|---|
| **Behaviour change (impl)** | resume→live ≠ current (ทุก platform resume-from-pause วันนี้) | **OI-UC2-07** |
| Assumed context | pause indicator visual = ปุ่ม ▶? | OI-UC2-08 |
| Edge (timing) | pause races stream-end | GAP-05 |
| Edge (data) | recording ยังไม่พร้อม | GAP-06 |
| **Doc inconsistency** | `user_story` ยังเขียน "behind the live edge" ไม่ตรง AC ใหม่ | **OI-UC2-09** |

**✅ Resolved by this update:** resume target (was CONF-01), LIVE badge (CONF-03 → out of scope), chat sync (AMB-02 → chat live), web-desktop tap (CONF-04 → no desktop change), return-to-live CTA (AMB-01 → moot), rolling buffer (CONF-02 → superseded).

---

## 3. Happy-Path AC Enrichment (phase 1.3)  — loop ทุก AC

### 🔍 [1/3] AC-01 — Pause live → pause indicator + chat keeps running

**Interpretation:** Then มี 3 ส่วน: (1) visual indicator ว่า "paused" (ตัด "behind live edge" ออกแล้ว), (2) visible โดยไม่ต้อง tap เพิ่ม, (3) **chat วิ่ง real-time ต่อ**. ยังไม่ระบุว่า indicator หน้าตายังไง (OI-UC2-08).

```
[Happy — AC-01: pause indicator appears; chat stays live]
Given the user is watching a live stream at the live edge (Room status = live)
When the user pauses via the central pause button (per UC1 AC-04)
Then a visual indicator communicates the stream is paused
  AND the indicator is visible without requiring an additional tap
  AND the chat continues to receive and display new messages in real time — it is NOT paused
Note: [PENDING P-UC2-Q8] pause indicator visual = central play (▶) overlay (LS-mobile-04) หรือ element แยก?
Note: ✅ chat-live = current behaviour ทุก platform (Prisa table) → low implementation risk
```

### 🔍 [2/3] AC-02 — Resume → current live moment; chat uninterrupted

**Interpretation:** Then มี 3 ส่วน: (1) **stream เริ่มจาก current live moment (ไม่ใช่ paused position)**, (2) pause indicator dismisses, (3) chat ต่อเนื่อง (ไม่ข้าม/ไม่ replay). ข้อ (1) เป็น **behaviour change** จาก current (OI-UC2-07).

```
[Happy — AC-02: resume snaps to current live moment]
Given the user has paused a live stream
When the user resumes (stream restarts)
Then playback starts from the CURRENT LIVE MOMENT — NOT from the previous paused position
  AND the pause indicator dismisses
  AND the chat remains uninterrupted — no messages are missed or replayed
Note: [PENDING P-UC2-Q7] นี่คือ behaviour CHANGE — current behaviour ทุก platform (iOS/Android/web-desktop)
      = resume-from-paused-position (Prisa table 68264). dev ต้อง implement ใหม่ทุก platform; QA เทส behaviour ใหม่
```

### 🔍 [3/3] AC-03 — Stream ends while paused → ended/recorded state

```
[Happy — AC-03: stream ends during pause → ended state]
Given the user has paused a live stream
When the Room transitions to ended or recorded during the pause
Then the player moves to an appropriate ended or recorded state
  AND the viewer is NOT left on a frozen frame with no feedback
Note: ✅ RESOLVED — current behaviour Android (Fidriyanto) + iOS (Prisa) + platform table ยืนยันตรงกัน
```

---

## 4. Edge & Error AC (phase 1.4)  — 4 models + priority

### ส่วนที่ 1 — Edge cases found

| ID | Model | Edge case | Priority |
|---|---|---|---|
| E-01 | Timing | Host จบ stream **พอดีจังหวะ** viewer กด pause → ended หรือ paused ชนะ? (GAP-05) | **High** |
| E-02 | Data integrity | Stream จบขณะ paused แต่ recording ยังไม่พร้อม → placeholder/"processing"? (GAP-06) | **High** |
| E-03 | Environment | Network หลุดขณะ paused → resume ยังไป live moment ได้ไหม? state ชัดเจน? | **High** |
| E-04 | Timing | pause นาน (นาที) แล้ว resume → snap ไป live ห่างมาก → transition/loading ชัดเจน? | Medium |
| E-05 | Timing | chat ตอน paused วิ่งไปไกล → resume video snap live → chat กับ video re-sync พอดีไหม? | Medium |
| E-06 | Boundary | pause แล้ว resume ทันที (ยังใกล้ live) → snap ระยะสั้น ไม่กระตุก | Low |
| E-07 | Data integrity | Android: fast-forward/rewind (native) ทำให้ chat desync (Fidriyanto) — แต่ pause อย่างเดียว chat ยัง sync | Medium |

### ส่วนที่ 2 — Priority
- **High:** E-01, E-02, E-03 · **Medium:** E-04, E-05, E-07 · **Low:** E-06

### ส่วนที่ 3 — AC ใหม่ (High ก่อน)

```
[Edge — Timing, High] E-01 · pause races stream-end
Given the user is watching a live stream at the live edge
When the user taps pause AND the Room transitions to ended at the same instant
Then the resolution is deterministic — player lands in EITHER ended/recorded OR paused, never a mix
  AND [state หลัง action] [PENDING P-UC2-Q9→GAP-05] which state wins is defined (ask PM/Eng)

[Edge — Data integrity, High] E-02 · recording not ready on end-while-paused
Given the user has paused a live stream
When the Room ends but the recording is not yet available
Then the player shows a defined intermediate state (e.g. "processing")
  AND [state หลัง action] NOT a frozen frame and NOT an error [PENDING GAP-06]

[Error — Environment, High] E-03 · network drops while paused
Given the user has paused a live stream
When the network connection drops and later recovers, then the user resumes
Then playback rejoins the CURRENT live moment (per AC-02) once reconnected
  AND [state หลัง error] viewer is NOT left on a frozen frame; a clear reconnect/retry state is shown

[Edge — Timing, Medium] E-05 · chat/video re-sync on resume
Given the user paused for a while (chat kept running live)
When the user resumes (video snaps to current live moment)
Then chat and video are aligned at the live moment — no replayed or skipped chat
  AND [state หลัง action] the transition is smooth (brief buffering acceptable)
```

---

## 5. Completion Gate  [GATE 2]

| AC | 1.3 | 1.4 | Clarifications | สถานะ |
|---|---|---|---|---|
| AC-01 | ✓ | ✓ (E-05, E-07) | OI-UC2-08 (low) | 🟡 indicator visual confirm |
| AC-02 | ✓ | ✓ (E-03, E-04, E-05) | **OI-UC2-07** (behaviour change) | 🟡 impl change |
| AC-03 | ✓ | ✓ (E-01, E-02) | GAP-05, GAP-06 (edges) | ✅ core resolved |

**ครอบคลุม: 3/3 ACs — ไม่มี AC หลุด ✅** (story-level: OI-UC2-09 user_story ไม่ตรง AC)

---

## 6. Story findings + Readiness verdict

**Clarifications ที่ raise/คงเหลือจาก UC2 (→ consolidated file):**

| ID | Category | Priority | Ask | Summary | สถานะ |
|---|---|---|---|---|---|
| ~~OI-UC2-01~~ return-to-live | — | — | — | resume ไป live แล้ว | ✅ moot |
| ~~OI-UC2-02~~ LIVE badge | — | — | — | separate enhancement | ✅ out of scope |
| ~~OI-UC2-03~~ rolling buffer | — | — | — | superseded | ✅ moot |
| OI-UC2-04 stream-end | — | — | — | current behaviour ยืนยัน | ✅ resolved |
| ~~OI-UC2-05~~ chat sync | — | — | — | chat live in AC | ✅ resolved |
| ~~OI-UC2-06~~ web-desktop | — | — | — | no desktop change | ✅ resolved |
| **OI-UC2-07** | Conflict (impl) | **Med-High** | Eng/PM | resume→live เป็น behaviour change จาก current ทุก platform | 🔴 open |
| OI-UC2-08 | Unclear | Low | Design | pause indicator visual = ปุ่ม ▶? | 🟡 open |
| OI-UC2-09 | Ambiguous | Low | PM | user_story ยังเขียน "behind live edge" ไม่ตรง AC | 🟡 open |
| GAP-05 | Unclear (edge) | High | PM/Eng | pause races stream-end | 🟠 open |
| GAP-06 | Unclear (edge) | Medium | Eng | recording ยังไม่พร้อม | 🟠 open |

**พร้อมส่ง dev หรือยัง?** — 🟡 **ดีขึ้นมากจากเดิม (🔴 → 🟡).**
- ✅ **แนวคิดหลักตัดสินแล้ว** — resume ไป live, chat วิ่งต่อ, LIVE badge + desktop out of scope, ไม่มี behind-live indicator ที่ต้อง design ใหม่
- ⚠️ **OI-UC2-07 คือ blocker หลักที่เหลือ** — resume-to-live เป็นการเปลี่ยน behaviour จาก current ทุก platform → dev ต้อง implement ใหม่ + QA เทส behaviour ใหม่ (ต้อง confirm scope/exception)
- 🟠 **เหลือ edge:** pause races stream-end (GAP-05), recording not ready (GAP-06)
- 🎨 **OI-UC2-08 (low):** confirm pause indicator = ปุ่ม ▶ overlay (น่าจะใช่) → ไม่ใช่ blocker ใหญ่แล้ว
- 📝 **OI-UC2-09:** บอก PM แก้ `user_story` (ยังเขียน "behind live edge")

**Blocking มากสุด:** OI-UC2-07 (behaviour change confirmation) + GAP-05 (pause-races-end) — เป็น Eng/PM decision, ไม่ใช่ design blocker เหมือนก่อน
