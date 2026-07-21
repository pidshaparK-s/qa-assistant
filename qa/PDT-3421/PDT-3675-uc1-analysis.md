# STEP 1 · Understand — UC1: Receive tray notification on event creation

- **Epic:** PDT-3421 (Q3'26 Noti Tray) · **Canonical story:** PDT-3675 (Core API) — platform surfaces: PDT-3724 Android · PDT-3725 iOS · PDT-3726 React/Web (AC identical, per DEC-01)
- **Date:** 2026-07-15 · **Skills:** phase-1-1 (Who/What/Why) + phase-1-2 (3-Layer)
- **Sources:** PRD (products/PDT-3421/prd/), Jira PDT-3675/3724/3725/3726 + comments, Figma ground truth (products/PDT-3421/design/), social.plus docs
- **AC Manifest (5):** AC-01 tray item creation & content · AC-02 In-person chip · AC-03 Virtual chip · AC-04 public → notify network · AC-05 private → members only

> Understand-level only. Per-AC enrichment (happy/edge/error) = STEP 2. Gaps found here → Clarification Register (`1_clarifications.json`).

---

## 1 · WHO — Relationship Map

Central object: **NotificationTrayItem (`event_created`)**, generated when an event is created in a community.

```
                         (excluded from audience)
   event creator/mod ──creates event──▶ [ EVENT ]
                                            │ triggers
                                            ▼
   community.isPublic? ──────────▶ [ NotificationTrayItem: event_created ]
     │                                      │ delivered to ▼
     ├─ PUBLIC  → audienceScope=network ▶ all active, non-banned NETWORK users  (incl. NON-members)
     └─ PRIVATE → audienceScope=community ▶ active, non-banned MEMBERS only
                                            │
   excluded everywhere: global-ban · community-ban · left/removed/inactive · creator
                                            │
                    ┌───────────────────────┼───────────────────────┐
              silent: global unseen        sibling: PUSH pipeline    system: noti service
              badge/count (TR-CL-06)       PDT-3420 (TR-CL-02)       (~30s cache, broadcast)
```

| Actor | Relationship | สถานะใน AC | หมายเหตุ |
|---|---|---|---|
| Event creator (moderator) | triggers create | AC-01 ("a moderator creates") | **excluded** จาก audience (regression exclusion + docs §7) → TR-CL-08 **resolved** |
| Active non-banned member | primary recipient | AC-01, AC-05 | persona หลักของ story |
| **Network non-member** | recipient (public only) | AC-04 | ⚠️ **ไม่อยู่ใน persona** ("As a community member") → TR-CL-07 (escalated high) |
| Globally-banned user | excluded | — (dev Q&A) | exclude ทั้ง global + community ban |
| Community-banned user | excluded | AC-05 | จาก AC-05 "(global & community ban)" |
| Left/removed/inactive | excluded | regression exclusion | |
| Member ∈ network set (public) | อยู่ 2 audience | — | dedup: ควรได้ 1 item → TR-CL-14 (open) |
| System / noti service | generates + broadcasts | — | ~30s cache (docs) → ไม่ real-time |
| Community (public/private) | scopes audience | AC-04/05 | privacy change หลังสร้าง → **TR-CL-16 (new)** |
| Push pipeline (PDT-3420) | sibling audience | — | tray vs push scope mismatch → TR-CL-02 |

**Concurrent actors:** (a) 2 moderators สร้าง event พร้อมกันใน community เดียว → 2 item แยก (**ไม่ group — design ยืนยัน, TR-CL-04 resolved**); (b) create แล้ว edit/delete ทันที (race) → TR-CL-12 / TR-CL-03.

**Silent actors:** network non-member (ผู้ได้รับที่ persona ลืม), global unseen badge (TR-CL-06), push recipient (TR-CL-02).

---

## 2 · WHAT — State Machine

### Object A — NotificationTrayItem (`event_created`)
```
(none) ──event created──▶ [UNSEEN] ──open tray / tap item?──▶ [SEEN]
                             │  (lastSeenAt=null)   (เมื่อไหร่ flip? → TR-CL-06)
                             ├─ daySegment aging ──▶ Recent ▶ Older
                             ├─ event edited after create ──▶ content stale? (TR-CL-12)
                             └─ event isDeleted before tap ──▶ tap → ? (TR-CL-03)
```
- created → `lastSeenAt=null` = **UNSEEN** (design: พื้นหลังฟ้าอ่อน) — AC-01 "marked as unseen" ✓
- **external transitions:** อีก moderator สร้าง event → item ใหม่ (tray forward-only, ต้อง re-fetch page แรก — docs §6); event ถูกแก้/ลบจากที่อื่น → item stale

### Object B — Event
```
create ──▶ scheduled ──▶ live ──▶ ended / cancelled ;  isDeleted=true (any time)
type ∈ { in_person → chip "In-person" (AC-02) , virtual → chip "Virtual" (AC-03) }
```
- **"created" หมายถึง state ไหน?** draft / scheduled / recurring → ยิง item เมื่อไหร่ = **TR-CL-09 (open)**
- deleted-before-tap → **TR-CL-03 (open, ไม่มี AC)**

### Object C — Audience scope (คำนวณจาก community.isPublic)
```
PUBLIC  → audienceScope = network   → all active non-banned network users  (AC-04)
PRIVATE → audienceScope = community → active non-banned members only        (AC-05)
```
- **external transition:** community privacy flip (public↔private) หลัง item ถูก broadcast → audience/visibility ของ item เดิม recompute ไหม? = **TR-CL-16 (new)**
- user โดน ban / ออกจาก community **หลัง**ได้รับ item → item หาย/ถูก revoke ไหม? = **TR-CL-17 (new)**

---

## 3 · WHY — Pain & Consequence

**Business Goal (metric):** ปิด Live Stream Activation Funnel — เพิ่ม **tap-through rate + RSVP rate** ของ event-creation tray item

**Why-Pain:** copy เดิม "You've been invited to an event" information scent ต่ำ → member ไม่มั่นใจพอจะ tap ตอนถูก interrupt → RSVP conversion ตก (live stream พึ่ง RSVP)

**Why-Consequence (ถ้า implement ผิดทิศ):**
| ผิดแบบ | business เสียอะไร | ผูกกับ |
|---|---|---|
| date/time ผิด timezone | member เข้าใจเวลา event ผิด → พลาด live (time-sensitive) | TR-CL-05 |
| tap ไปปลายทางผิด (ไม่เห็น RSVP) | friction ล้มเป้า "one-tap RSVP" | TR-CL-01/03 |
| public ไม่ถึง non-member (หรือ member-only ชนะ) | funnel เข้าไม่ถึง audience ใหม่ → growth ล้ม | TR-CL-07 |
| group notifications | event แต่ละอันถูกกลบ → tap ลด | TR-CL-04 (resolved: design ไม่ group) |

**Success metric:** tap-through rate + RSVP rate บน event-creation tray item

---

## 4 · Three-Layer Trace + Gap analysis

```
Business Goal: ↑ RSVP conversion (live-stream funnel) — วัดด้วย tap-through / RSVP rate
      ↑
User Need (ต่อ actor)
  • member       → รู้ event/เวลา/ประเภท ทันทีโดยไม่ต้องเปิด แล้ว RSVP เร็ว
  • non-member   → ค้นพบ event ของ public community ที่น่าสนใจ (public)   ⚠️ ไม่อยู่ใน story
  • creator      → (excluded — ไม่ต้องรู้ event ตัวเอง)
      ↑
System Behavior (AC)
  • AC-01 rich content + unseen + avatar   • AC-02/03 type chip   • AC-04 network broadcast   • AC-05 members only
```

**5 ประเภท gap:**
1. **Missing Business Goal** — ไม่มี (PRD ชัด วัดได้) ✓
2. **Ambiguous User Need** — persona "community member" ไม่ครอบ need "non-member discovery" ที่ AC-04 แฝง → **TR-CL-07** (member vs network)
3. **Silent User Need** — พฤติกรรม tap→RSVP **ไม่มี AC** (core value "one-tap" ไม่ถูก cover) → **TR-CL-03**; global badge/unseen count → TR-CL-06
4. **Orphaned System Behavior** — **AC-04** (network-wide) orphan เทียบ need ของ story (member) → กระจก TR-CL-07
5. **Assumed Context** — timezone (TR-CL-05) · privacy flip หลังสร้าง (**TR-CL-16**) · นิยาม "created"/draft/scheduled (TR-CL-09) · backfill format เก่า (TR-CL-13) · ~30s cache latency (docs, advisory)

---

## 5 · Clarification Register delta (STEP 1)

**Resolved by ground truth (ไม่ต้องถามทีม):**
- **TR-CL-04** (no grouping) → design annotation ">1 Events from the same AND/OR different communities" + frames โชว์ item แยก
- **TR-CL-11** (avatar vs thumbnail) → design: community avatar, ไม่มี event thumbnail แยก
- **TR-CL-08** (creator ได้ item ตัวเองไหม) → regression exclusion + docs §7: creator **excluded**

**Escalated:**
- **TR-CL-07** medium → **high** — ยืนยันเป็น as-built (dev comment) + ขัดเชิงระบบ 5 จุด + design โชว์ content เหมือนกัน member/non-member → คำถามสำคัญสุดของ feature

**New (จาก STEP 1):**
- **TR-CL-16** — community privacy flip (public↔private) หลัง item ถูก broadcast → audience recompute ไหม (state machine external transition)
- **TR-CL-17** — user โดน ban / ออกจาก community หลังได้รับ item → item ถูก revoke/hide ไหม
- **TR-CL-18** — separator "·" : PRD copy มี dot / Figma component ไม่มี (AT assertion + cross-platform)
- **TR-CL-19** — relative timestamp ("10h"/"Just now") ใน design แต่ไม่อยู่ใน content spec/AC → อยู่ใน scope ไหม

---

---

# STEP 2 · Specify — enriched AC ต่อ ac_id (happy + edge + error)

> reads State Machine + Relationship Map จาก STEP 1 (ไม่ทำซ้ำ). Platform registry cross-check: **ไม่มี divergence ของ noti tray มาก่อน** (PB-001/002/003 = live player) → dark-theme chip = candidate ใหม่ (TR-CL-21).
> **หมายเหตุ surface:** UC1 = **"รับ" item (system-generated)** ไม่ใช่ user action → ไม่มี error แบบ "กด...แล้ว network fail". Error อยู่ที่ **generation-side data anomaly** (deleted/missing/unknown) + **fetch-side** (GET /notification-tray) ซึ่งเป็น tray chrome กลาง. tap→nav แยกเป็น TR-CL-03 (ไม่มี AC).

## [1/5] AC-01 — Tray item creation & content
**Interpret gap เดิม:** Given ไม่ระบุ exclusions/creator/privacy · Then ไม่ระบุ actionType/category, unseen-count side-effect, no-group, avatar source

```
[AC-01 · Happy — item generated for eligible recipient]
Given user เป็น active, non-banned (global & community) member ของ community C
  AND user ไม่ใช่ event creator                                    [exclusion]
  AND moderator สร้าง event E ใน C                                 [precondition]
When noti service generate event_created item (≤~30s cache — docs)
Then user ได้ NotificationTrayItem (actionType=event, trayItemCategory=event_created)
  AND primary line = "{CommunityName} has event {EventName}" (ชื่อ community+event ตัวหนา)
  AND secondary line = [type chip] + start date + start time      [→AC-02/03]
  AND icon = community avatar (targetId→community)                 [design; TR-CL-11 ✓]
  AND lastSeenAt = null → UNSEEN (row ฟ้าอ่อน)
  AND item ไม่ถูก group (row แยกของตัวเอง)                          [design; TR-CL-04 ✓]
  AND [PENDING TR-CL-06] tray unseen count/badge increment
```
**Edge/Error (4 models):**
- `[Edge·Data — High]` event ถูกลบก่อน item ถูก deliver / ก่อน tap → item แสดง/หาย? tap ไปไหน? **[PENDING TR-CL-03]**
- `[Edge·Data — Med]` event ถูกแก้ (ชื่อ/เวลา) หลังสร้าง item → snapshot หรือ update? **[PENDING TR-CL-12]**
- `[Edge·Data — Med]` community ไม่มี avatar → fallback อะไร; ชื่อยาวเกิน → truncate (date maxw80/time maxw64, name word-break) **[PENDING TR-CL-15]**
- `[Edge·Timing — Low]` ~30s cache → item ไม่ real-time; tray forward-only ต้อง re-fetch page 1 ดู item ใหม่ (docs §6) — behavior กำหนดแล้ว
- `[Error·Env — Med]` GET /notification-tray fail/timeout → tray แสดง cached/empty/error (chrome กลาง); item ไม่หายฝั่ง server, retry ตอน reconnect

## [2/5]+[3/5] AC-02 (In-person) + AC-03 (Virtual) — event-type chip
**Interpret gap เดิม:** ไม่ระบุพฤติกรรมเมื่อ type ไม่ใช่ 2 ค่านี้ + ไม่ระบุ theme

```
[AC-02 · Happy] Given event E type = in_person → Then chip label "In-person" (pill caption-bold) + start date + time
[AC-03 · Happy] Given event E type = virtual   → Then chip label "Virtual" + start date + time
```
**Edge/Error:**
- `[Edge·Data — Med]` type ∉ {in_person, virtual} (null/unknown/ค่าใหม่ในอนาคต) → chip แสดงอะไร (ว่าง/default/ซ่อน)? สำคัญต่อ AT enum handling **[PENDING TR-CL-20 ใหม่]**
- `[Edge·Env — Med]` **dark theme**: chip bg = rgba(0,0,0,0.5) → contrast ใน dark? (Android dev ถาม Design แล้ว) — platform-rendering, R3 candidate **[PENDING TR-CL-21 ใหม่]**
- `[Edge·Data — Low]` AC-03 title "Virtual / livestream" แต่ chip มี 2 ค่า → livestream render เป็น "Virtual" (ไม่มี state 3)? **[PENDING TR-CL-22 ใหม่]**
- `[Edge·Data — Med]` type แก้หลังสร้าง item (in_person↔virtual) → chip update? **[PENDING TR-CL-12]**

## [4/5]+[5/5] AC-04 (public→network) + AC-05 (private→members) — audience scope
**Interpret gap เดิม:** persona conflict (AC-04) · dedup · timing ของ ban/join/privacy

```
[AC-04 · Happy] Given event E ใน PUBLIC community → Then ทุก active non-banned network user (รวม non-member, ยกเว้น creator) ได้ 1 item  [PENDING TR-CL-07 persona · TR-CL-14 dedup]
[AC-05 · Happy] Given event E ใน PRIVATE community → Then เฉพาะ active non-banned (global & community ban) member ได้ item
  ทั้งคู่ exclude: creator, global-ban, community-ban, left/removed/inactive
```
**Edge/Error:**
- `[Edge·Timing — High]` community เปลี่ยน public↔private หลัง broadcast → recompute/revoke? (public→private = privacy leak) **[PENDING TR-CL-16]**
- `[Edge·Timing — Med]` recipient โดน ban/ออกจาก community หลังได้ item → revoke/hide? **[PENDING TR-CL-17]**
- `[Edge·Timing — Med]` user join community หลัง event ถูกสร้าง → ได้ item ย้อนหลังไหม? **[PENDING TR-CL-23 ใหม่]**
- `[Edge·Data — Med]` user-block ("blocked" ใน docs §7) → A-block-B / block กระทบ delivery ยังไง (ไม่มีนิยามใน exclusions)? **[PENDING TR-CL-24 ใหม่]**
- `[Edge·Boundary — Low]` public community ที่ active non-banned network user มีแต่ creator → 0 recipient (ไม่มี item) — valid

---

## Completion gate
**ครอบคลุม: 5/5** — AC-01, AC-02, AC-03, AC-04, AC-05 enriched (happy + edge/error + PENDING refs) ครบทุก ac_id เทียบ Manifest · ไม่มี ac หลุด
เหลือ **[PENDING]** ผูกกับ clarifications ที่ต้องได้คำตอบก่อน finalize (ดู `1_clarifications.json`)
