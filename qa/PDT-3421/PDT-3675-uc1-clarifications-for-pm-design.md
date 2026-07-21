# Clarifications for PM · Design · Eng — PDT-3421: Notification Tray (event-creation item) — FINAL

_UC1 (canonical PDT-3675) · 4 platform stories identical AC (DEC-01)_
_Ground truth: Jira AC (synced 07-14) · PRD (07-14) · Figma 7 screens · social.plus docs · **as-built source review 5 repos (07-16)** · PM answers (07-16)_
_Updated: 2026-07-16 · analysis `PDT-3675-uc1-analysis.md` · verify `as-built-verification.md` · bugs `FOLLOWUPS.md`_

---

## 🎯 Scoreboard: 25 ข้อ → **resolved 23 · ac-change 1 · open 1**

เหลือให้ทีมตัดสินจริงๆ:

| ต้องการ | ใคร | คือ |
|---|---|---|
| **TR-CL-21** | 🎨 Design | chip appearance light+dark ทุก platform (ครอบ **BUG-D**: Android chip ขาวบนขาวใน light theme) |
| **TR-CL-15** (minor) | 🎨 Design | truncation ชื่อยาว (wrap ไม่ ellipsize) |
| **FU-3 / TR-CL-07** | 🧑‍💼 PM | update Jira user story persona → network-wide (behavior ยืนยันแล้ว เหลือแก้ข้อความ) |
| ~~push display tz~~ | — | ✅ RESOLVED 07-21 — tray & push = viewer-local (device), verified Android+iOS; BUG-B1 + BUG-B2 retracted; ไม่มี tz decision ค้าง |
| **file bugs** | 🔧 Dev | ~~BUG-B1~~ ~~BUG-B2~~ (retracted 07-21) · BUG-C Android deleted · BUG-D Android chip · BUG-F new-user network backlog (ดู FOLLOWUPS.md) |

---

## 🔴 ยังเปิด / ต้องตัดสิน

### 🟡 TR-CL-21 · AC-02 / AC-03 · dark/light-theme chip
- **Ask:** Design · **Source:** STEP2 phase-1-4 Environment — chip bg=rgba(0,0,0,0.5); Jira PDT-3724 comment (Android dev ถาม Design เรื่อง dark theme)
- **Observation:** chip background เป็นดำโปร่ง 50% ตัวอักษรขาว — ใน dark theme (พื้นหลังเข้ม) contrast/ความอ่านออกอาจไม่พอ; Android dev ถาม Design ไว้ใน PDT-3724 แต่ยังไม่มีคำตอบ
- **Question:** chip มี design token/สีแยกสำหรับ dark theme ไหม? behavior ต้องตรงกันทุก platform (iOS/Android/Web) หรือปล่อยต่างได้?
- **Verified:** per-platform DIVERGE: Web+iOS = hardcoded black@50% bg + white text (อ่านออกทั้ง light/dark แต่ไม่ theme-aware); Android = เปลี่ยน bg เป็น theme token AmityTheme.colors.background@50% แต่ text ยัง hardcode white → default/light theme = white-on-white มองไม่เห็น = BUG-D (regression, AmityEventTypeChip.kt:40-44, unused amityColorBlack import ยืนยัน refactor ไม่ครบ). Design ต้องชี้ขาด chip appearance ที่ถูกต้อง (light+dark) ทุก platform.

### 🔴 TR-CL-07 [AC-CHANGE] · AC-01 vs AC-04 · persona ↔ AC-04 (network/non-member)
- **Ask:** PM · **Source:** AC-01: 'Given a user is an active, non-banned member of a community... the user receives a NotificationTrayItem' | AC-04: 'PUBLIC community → all active, non-banned users in the network receive the notification'
- **Observation:** AC-01 กรอบผู้รับเป็น 'member of a community' แต่ AC-04 บอกว่า public → ทั้ง network (รวม non-member) ไม่ชัดว่า non-member network user ที่ได้ tray item จะเห็น content แบบเดียวกับ member (primary line ขึ้นชื่อ community ที่เขาไม่ได้เป็นสมาชิก)
- **Question:** สำหรับ public community: non-member network user ได้รับ tray item เดียวกัน (content เดียวกัน) กับ member ใช่ไหม? AC-01 เป็น base content ที่ใช้กับทั้ง member และ network user หรือเฉพาะ member?

---

## ✅ Resolved record (23)

**A. Conflicts**
- ✅ **TR-CL-01 deep-link destination** — Destination = existing event detail page (RSVP CTA already visible there), NOT a separate RSVP page — resolves the PRD Opportunity-Brief vs Release-Note contradiction toward the detail-page 
- ✅ **TR-CL-02 tray vs push audience** — Intentional asymmetry confirmed: tray broadcasts network-wide on public communities (passive surface → low spam risk); push does NOT. Tray↔push audience divergence is by design, not a gap.
- ✅ **TR-CL-11 community avatar vs thumbnail** — icon = community avatar เท่านั้น ไม่มี event thumbnail แยก
- ✅ **TR-CL-18 separator '·'** — ไม่มี separator '·' ทุก platform (Web=2 span+gap, iOS/Android=combined template) — PRD copy ที่มี dot ผิด
- ✅ **TR-CL-25 mobile tray enriched? (web-only?)** — RETRACTED (false alarm) — enriched item (chip+date+time+community avatar) render ครบทั้ง 3 platform. รอบแรก iOS+Android agent พลาด code path ของ event_created (HEAD ไม่เปลี่ยน = agent miss ไ

**B. Gaps**
- ✅ **TR-CL-03 tap→nav + deleted-event** — Scope = message enrichment ONLY; tap-nav + deleted-event handling stay as current shipped behavior (no new AC). Spec question closed. QA must baseline the current nav + deleted-event behavio
- ✅ **TR-CL-04 no grouping** — ไม่ group — แต่ละ event = 1 tray item แยก (รวมถึงหลาย event จาก community เดียวกัน)
- 🔄 **TR-CL-05 date/time timezone** — REVERSED 2026-07-21 (DEC-06): tray shows start time in the VIEWER's LOCAL timezone (existing UIKit behavior, matches event cards/detail), NOT the event timezone. Client device-local display is CORRECT → BUG-B1 retracted. Push verified device-local too (Android+iOS) → BUG-B2 retracted; both surfaces viewer-local, consistent.
- ✅ **TR-CL-06 unseen badge + seen** — badge = client คำนวณจาก lastTrayOccurredAt > lastTraySeenAt (ไม่มี server count); event_created ดัน occurredAt ให้ non-member ด้วย; seen set โดย markTraySeen/markItemsSeen เท่านั้น (fetch ไม
- ✅ **TR-CL-08 creator excluded** — event creator/host ไม่ได้รับ tray item ของ event ตัวเอง (excluded)
- ✅ **TR-CL-09 'event created' definition** — ไม่มี draft/recurring — ทุก event สร้างเป็น SCHEDULED (start ≥ now+15m); fire ทุกครั้งที่สร้าง event ใน community (USER origin ถูก reject)
- ✅ **TR-CL-10 which roles trigger** — permission-gated: role ที่มี CreateEvent (หรือ admin ManageEvent) trigger ได้ — ไม่ hardcode moderator, ตั้งให้ member ได้; creator ถูก exclude จากผู้รับ
- ✅ **TR-CL-12 event edited → update/snapshot** — live (ไม่ใช่ snapshot) — tray เก็บแค่ actionReferenceId, serializer re-fetch event ตอน read; edit reflect หลัง Redis cache หมด (short TTL)
- ✅ **TR-CL-13 backfill old format** — network-broadcast scope = forward-only (ไม่ backfill; item เก่า stay community-scoped) แต่ copy generate ตอน read → item เก่าได้ text ใหม่; push copy migrate ด้วย migration
- ✅ **TR-CL-14 dedup member∈network** — member∈network (public) ได้ 1 item — UNION (ไม่ใช่ UNION ALL) dedup
- ✅ **TR-CL-15 avatar fallback + truncation** — fallback มีทุก platform (Web=community glyph SVG, iOS=initials, Android=event placeholder). truncation ต่างกัน: Web/iOS wrap ไม่ตัด, Android maxLines=3+ellipsis
- ✅ **TR-CL-16 privacy flip after broadcast** — Audience is a SNAPSHOT at send time (no recompute on privacy change). public→private exposure is delegated to the navigation/permission layer — PM ASSUMES it already guards access. FU-4: QA 
- ✅ **TR-CL-17 ban/leave after receive** — banned/left หลังรับ → hide ตอน read (node ไม่ถูกลบ): banned public → Mongo ban filter; left private → edge หาย; un-ban/re-join แล้วกลับมา (ภายใน 30 วัน)
- ✅ **TR-CL-19 relative timestamp scope** — relative timestamp (occurredAt) render ทุก platform เป็น tray chrome กลาง (Just now/m/h/d/date) — ไม่ใช่ event-specific
- ✅ **TR-CL-20 unknown event type → chip** — create form บังคับ type 2 ค่า (Virtual/InPerson) → unknown ไม่เกิดจริง (moot). client fallback ต่างกัน: Web ซ่อน chip / iOS+Android ตกเป็น 'Virtual' (divergence, low risk)
- ✅ **TR-CL-23 join after event created** — private = ไม่ได้ item ย้อนหลัง (community arm filter occurredAt > member.createdAt); public = ได้อยู่แล้ว network-wide
- ✅ **TR-CL-24 user-block delivery** — user-block กด suppress: block recipient↔creator (2 ทาง either direction) → arm filter NOT actors._id IN blockedUserIds

**C. Ambiguous**
- ✅ **TR-CL-22 livestream → Virtual chip** — livestream = virtual event → chip 'Virtual' (ไม่มี state 3) ทุก platform

---

## Readiness verdict

**NEAR-READY** — ไม่มี behavioral blocker: network-wide audience + privacy guard (getById 403) + dedup + exclusions ยืนยันจาก backend; enriched item render ครบ 3 platform. เหลือ Design decision (TR-CL-21/BUG-D) + PM persona-text (FU-3) + bug fixes. ไม่มี still-ambiguous → gate เข้า L2 ได้ (หรือรอ Design/bug ก่อนตามต้องการ)
