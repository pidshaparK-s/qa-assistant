# Business Rules — PDT-3418: Video & Live Streaming

_phase-2.3 Business Rule Extraction — ดึงจาก output/PDT-3418-acceptance-criteria.md_
_Generated: 2026-06-30_

---

## สรุปก่อนเข้า catalog

จาก **38 AC** ใน 3 stories → สกัดได้ **13 Business Rules**

| ประเภท BR | จำนวน | หมายเหตุ |
|---|---|---|
| **Permission / Authorization** | **0** | feature นี้เป็น viewer-only — ไม่มี role/permission matrix → **ไม่ต้อง test permission boundary** |
| **Constraint / Limit** | 5 | timeout, cross-surface, skip applicability + magnitude + clamping |
| **Computation / Display** | **0** | ไม่มี count/format display logic → **ไม่ต้อง test display-format** |
| **State / Lifecycle** | 8 | core invariant ของ feature นี้อยู่ที่ state ทั้งหมด |

**ข้อสังเกตสำคัญ:** BR ของ feature นี้ **กระจุกที่ State (8/13)** — บอกชัดว่า test effort หลักคือ **state transition testing** ไม่ใช่ permission หรือ computation นี่คือ signature ของ "gesture/playback redesign" feature

---

## ส่วนที่ 1 · BR Catalog (จัดตามประเภท)

### Permission / Authorization

```
(ไม่มี)
```
**ทำไม:** ทุก community member ที่ดู content ได้ ก็ใช้ feature นี้ได้เหมือนกันหมด
ไม่มี behavior ที่ขึ้นกับ role → ไม่มี permission rule

---

### Constraint / Limit

```
BR-C1 [Constraint]
Rule: The controls overlay auto-dismisses after exactly 1 second of inactivity
      while the media is playing.
Scope: video + live stream, all surfaces
Source: A-H3
Refine: [PENDING A-02] ยังไม่ระบุว่า timer reset เมื่อ user interact กับ overlay หรือไม่

BR-C2 [Constraint · scope]
Rule: The control gesture model must behave identically across every in-scope surface
      (global / user / community / event discussion feed, media gallery, fullscreen).
      Behaviour must not vary by surface.
Scope: all surfaces
Source: A-H6

BR-C3 [Constraint · applicability]
Rule: Skip controls (−10s / +10s) are shown only on video posts;
      they are never shown on live streams (seeking is not applicable to a live edge).
Scope: video vs live distinction
Source: C-D1, C-D2

BR-C4 [Constraint]
Rule: A skip operation moves playback exactly 10 seconds from the current position.
Scope: video only
Source: C-H1, C-H2

BR-C5 [Constraint · boundary]
Rule: Skip operations are clamped to the media bounds —
      skip back never yields a negative position (clamps to 0:00);
      skip forward never overshoots (clamps to the final frame and enters the end state,
      never loops or errors).
Scope: video only
Source: C-V1, C-V2
```

---

### Computation / Display Format

```
(ไม่มี)
```
**ทำไม:** ไม่มี count, badge, หรือ numeric format ใน feature นี้
(ต่างจาก feed/moderation features ที่มี reaction count, pending count)

---

### State / Lifecycle

```
BR-S1 [State] ★ core invariant
Rule: Playback state (playing ⇄ paused) changes ONLY via the central pause/play button.
      A tap anywhere else on the player surface toggles the controls overlay
      and never alters playback state.
Scope: video + live stream, all surfaces
Source: A-H1, A-H2, A-H4, A-H5, A-V1   ← 5 AC รวมเป็น BR เดียว

BR-S2 [State · default]
Rule: A playing player shows no controls overlay by default;
      the overlay appears only in response to a surface tap.
Scope: video + live stream
Source: A-D1

BR-S3 [State]
Rule: While the media is paused, the controls overlay does not auto-dismiss —
      it persists until a surface tap dismisses it.
Scope: video + live stream
Source: A-H4, A-EG2
Status: [PENDING A-03] ยังต้อง confirm กับ Engineering

BR-S4 [State]
Rule: Resuming playback always continues from the exact position at which it was paused.
Scope: video + live stream (live adds BR-S6)
Source: A-H5

BR-S5 [State]
Rule: When a live stream is paused, the viewer becomes "behind the live edge"
      and a behind-live indicator is shown immediately — without an additional tap —
      and remains visible while the viewer is behind live.
Scope: live stream only
Source: B-H1
Status: [PENDING uc2-G1] visual form ของ indicator ยังไม่ define (ไม่มีใน Figma)

BR-S6 [State] (extends BR-S4)
Rule: Resuming a paused live stream continues from the paused position — not the live edge —
      and the viewer remains behind live until they explicitly catch up.
Scope: live stream only
Source: B-H2

BR-S7 [State · lifecycle]
Rule: When a live stream's Room transitions to ended or recorded while the viewer is paused,
      the player moves to the corresponding ended/recorded state —
      it must never remain on a frozen frame.
Scope: live stream only
Source: B-H3, B-EG1, B-EG2

BR-S8 [State]
Rule: A skip operation updates the playback position without changing the playback state —
      skipping while paused keeps the media paused (no auto-resume).
Scope: video only
Source: C-V3
```

---

## ส่วนที่ 2 · Consolidation & Cross-story notes

| BR | สถานะ consolidation | หมายเหตุ |
|---|---|---|
| **BR-S1** | รวมจาก 5 AC | A-H1/H2/H4/H5/V1 ทั้งหมดเป็น invariant เดียว — "เฉพาะปุ่มกลางที่เปลี่ยน playback" → implement + test ครั้งเดียว ครอบทุก scenario |
| **BR-S4 ↔ BR-S6** | extends | BR-S4 = resume rule ทั่วไป · BR-S6 = live specialization (เพิ่ม "stays behind live") → test BR-S6 ต้อง cover BR-S4 ด้วย |
| **BR-S1 ↔ BR-S8** | consistent | skip = position op ไม่ใช่ playback-state op → BR-S8 ไม่ขัด BR-S1 |
| **BR-C3** | video/live gate | คุม applicability ของ Story C ทั้งก้อน — ถ้า fail = skip โผล่บน live (ผิด) |

**ไม่มี BR ซ้ำข้าม epic** — feature นี้ standalone (gesture model) ไม่ reuse logic จาก feed/moderation

---

## ส่วนที่ 3 · AC → BR Traceability

| AC | BR ที่อ้าง |
|---|---|
| A-D1 | BR-S2 |
| A-H1 | BR-S1 |
| A-H2 | BR-S1 |
| A-H3 | BR-C1 |
| A-H4 | BR-S1, BR-S3 |
| A-H5 | BR-S1, BR-S4 |
| A-H6 | BR-C2 |
| A-V1 | BR-S1 |
| A-EG1 | BR-C1 (pending refine) |
| A-EG2 | BR-S3 |
| B-D1 | BR-S5 (inverse) |
| B-H1 | BR-S5 |
| B-H2 | BR-S4, BR-S6 |
| B-H3 | BR-S7 |
| B-EG1, B-EG2 | BR-S7 |
| C-D1, C-D2 | BR-C3 |
| C-H1, C-H2 | BR-C4 |
| C-V1, C-V2 | BR-C5 |
| C-V3 | BR-S8 |

ทุก AC หลัก map กลับ BR ได้ — ไม่มี orphaned AC

---

## ส่วนที่ 4 · Projection → Test Conditions (phase-3.2 preview)

ใช้ technique mapping ของ phase-3.2 ประเมินจำนวน test condition คร่าวๆ:

| BR | Type | Technique | ~TC |
|---|---|---|---|
| BR-S1 | State | State Transition Table | 6 (tap ในแต่ละ state × playback unchanged) |
| BR-S2 | State | State Transition | 2 |
| BR-S3 | State | State Transition | 2 (pending) |
| BR-S4 | State | State Transition | 2 |
| BR-S5 | State | State Transition | 2 (pending) |
| BR-S6 | State | State Transition | 3 |
| BR-S7 | State | State Transition + race | 4 |
| BR-S8 | State | State Transition | 2 |
| BR-C1 | Constraint | BVA (timeout boundary) | 3 + reset(pending) |
| BR-C2 | Constraint | EP per surface | 6 (1/surface) |
| BR-C3 | Constraint | Decision (video/live) | 2 |
| BR-C4 | Constraint | BVA | 2 |
| BR-C5 | Constraint | BVA (boundaries) | 5 |
| **รวมประเมิน** | | | **≈ 45 test conditions** |

**สเกลที่ได้:**
```
38 AC  →  13 BR  →  ≈45 test conditions
```

- State BRs (8 ข้อ) จะผลิต TC มากที่สุด (~23) → **state transition testing คือหัวใจ**
- BR-C2 (cross-surface) ผลิต 6 TC แต่ parametrize ได้ → จริงๆ คือ 1 test ×6 surface
- TC ที่ block อยู่: BR-S3, BR-S5, BR-C1-reset → รอ clarification ก่อน finalize

---

## Checklist phase-2.3

```
☑ แต่ละ BR เป็น statement ไม่ใช่ scenario
☑ subject แม่น (playback state ≠ overlay state; video ≠ live)
☑ scope ระบุชัดทุก BR (video / live / all surfaces)
☑ ไม่มี BR ซ้ำ (BR-S4↔S6 = extends ไม่ใช่ duplicate)
☑ ทุก AC หลัก map กลับ BR
☑ BR ที่ block flag [PENDING] พร้อม ref clarification
```
