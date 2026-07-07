# Clarifications for PM & Design — PDT-3418: Video & Live Streaming (Tap-to-Reveal Controls)

_รวบรวมจาก phase 1.1–1.4 analysis ของ PDT-3562 (UC1) / PDT-3563 (UC2) / PDT-3564 (UC3)_
_ground truth: Jira AC (**synced 2026-07-06 17:07** — UC2 rewritten) + PRD + Figma (11 screens) + platform table (Prisa, comment 68264)_
_Updated: 2026-07-06 · per-story analysis: `qa/PDT-3418/PDT-356{2,3,4}-*-analysis.md`_

---

## 🔄 Changelog — update 2026-07-06 (Jira 17:02–17:07)

PM (Ghita) **เขียน AC ของ UC2 ใหม่** + เพิ่ม Platforms section ทุก story → **เคลียร์ 7 clarifications** (ส่วนใหญ่เป็น High):

| เดิม | ผลลัพธ์ |
|---|---|
| CONF-01 resume target | ✅ **RESOLVED** — resume ไป current live moment (Figma "resume-to-live-edge" ถูกแล้ว) |
| CONF-02 rolling buffer | ✅ **MOOT** — resume ไป live ไม่ใช่ pause position แล้ว |
| CONF-03 LIVE badge | ✅ **RESOLVED** — out of scope (separate enhancement) |
| CONF-04 web-desktop tap | ✅ **RESOLVED** — desktop ไม่เปลี่ยน behavior |
| CONF-05 desktop scope | ✅ **RESOLVED** — no behavior change, UI-only (button size) |
| AMB-01 return-to-live CTA | ✅ **MOOT** — resume ไป live อยู่แล้ว |
| AMB-02 chat sync | ✅ **RESOLVED** — chat วิ่ง real-time เสมอ (ใน AC + platform table) |
| GAP-01 behind-live indicator | ⤵️ **DOWNGRADED** → กลายเป็น "pause indicator" (ปุ่ม ▶ น่าจะใช่) = AMB-09 (low) |

**🆕 เกิดข้อใหม่ 2 ข้อ:** CONF-07 (resume-to-live เป็น behavior change), AMB-10 (user_story ไม่ตรง AC ใหม่)

**สถานะปัจจุบัน:** 22 เดิม → **7 เคลียร์** · **15 ยกมา** (14 คงเดิม + GAP-01 ลดระดับ) · **+2 ใหม่** = **17 ข้อที่ยังเปิด** (High: 5 · Medium: 6 · Low: 6)

---

## วิธีอ่านเอกสารนี้

3 หมวด เรียงตาม priority. ทุกข้อเขียนแบบ **observation → consequence → question** พร้อม tag: priority · ask→ใคร · story/AC · source. ข้อที่ ✅ resolved แสดงแบบย่อพร้อม resolution; ข้อที่ยังเปิดแสดงเต็ม

---

## A. Conflicts

### ✅ RESOLVED (2026-07-06)
- **CONF-01 · UC2 AC-02 · resume target** — ✅ AC-02 rewritten: resume ไป **current live moment** (ไม่ใช่ paused position). Figma `LS-mobile-05-resume-to-live-edge` ถูกต้องแล้ว
- **CONF-02 · UC2 AC-02 · rolling buffer** — ✅ **moot** — resume ไป live ไม่ใช่ pause position, ปัญหา buffer boundary หายไป
- **CONF-03 · UC2 AC-01 · LIVE badge ตอน paused** — ✅ Ghita: อัปเดต LIVE badge = separate enhancement, **out of scope** release นี้
- **CONF-04 · UC2 · web-desktop tap-to-resume** — ✅ Ghita: **no behavior changes on Desktop** (out of scope)
- **CONF-05 · UC1 AC-06 · desktop scope** — ✅ Jira: Desktop "no behaviour change; only a small UI design change (button size)"

### 🔴 CONF-07 · OI-UC2-07 · Resume-to-live คือ behavior change จาก current (NEW)
- **Priority:** Medium–High · **Ask:** Engineering / PM · **Story:** UC2 (PDT-3563) AC-02 · **Source:** AC-02 (rewritten) ↔ platform table (Prisa, 68264)
- **Observation:** AC-02 ใหม่ต้องการ resume ไป current live moment. แต่ตาราง platform ของ Prisa ยืนยันว่า **current behavior ทุก platform = resume-from-paused-position** (iOS ✅, Android ✅, web-desktop ✅)
- **Consequence:** AC-02 จึงเป็นการ **เปลี่ยน behavior ที่มีอยู่** ไม่ใช่การ spec ของเดิม — dev ต้อง implement ใหม่ทุก platform และ QA ต้องเทส behavior ใหม่ (ไม่ใช่ current). ถ้าเข้าใจผิดว่าเป็น "ของเดิม" จะไม่มีใคร implement
- **Question:** ยืนยันว่า resume-to-live-moment เป็น behavior ใหม่ที่ต้องการบนทุก platform (แทน resume-from-pause เดิม) ใช่ไหม? มี platform exception หรือ migration concern ไหม?

### 🟡 CONF-06 · UC1-Q1 · Auto-dismiss timeout: 1s (Jira) vs "assume 3s" (PRD)
- **Priority:** Low · **Ask:** Engineering / PM · **Story:** UC1 (PDT-3562) AC-03 · **Source:** Jira ↔ PRD
- **Observation:** Jira AC-03 = "1 second" (resolved) แต่ PRD ยังมี comment "*(assume 3s)*" ค้าง
- **Consequence:** doc ไม่ sync — ยึด PRD จะเข้าใจ 3s
- **Question:** ยืนยัน 1s final และ update PRD ให้ตรง?

---

## B. Unclear / Gaps

### 🔴 GAP-02 · UC1-Q2 · Controls overlay ค้างหรือหายหลังกด pause?
- **Priority:** High · **Ask:** Engineering · **Story:** UC1 AC-04 · **Source:** Jira AC (ไม่ระบุ)
- **Observation:** AC-04 บอก pause + icon เปลี่ยน แต่ไม่ระบุว่า overlay ยังอยู่หรือ auto-dismiss
- **Consequence:** ถ้าหายทันที → user ต้อง tap ใหม่เพื่อกด play → extra step; dev implement ต่างกันได้
- **Question:** เมื่อ pause, overlay ยังแสดงอยู่ไหม? timer (1s) ยังทำงานต่อ หรือหยุด?

### 🔴 GAP-03 · UC1-Q3 · Auto-dismiss timer reset เมื่อ interact?
- **Priority:** High · **Ask:** Engineering · **Story:** UC1 AC-03 · **Source:** Jira AC (ไม่ระบุ)
- **Observation:** AC-03 = auto-dismiss หลัง "no action 1s"; ไม่ระบุว่า interact (กด volume) reset timer ไหม
- **Consequence:** ถ้าไม่ reset → overlay หายกลางที่ user ใช้อยู่
- **Question:** timer (1s) reset เมื่อ user interact กับ overlay ไหม?

### 🔴 GAP-04 · UC1-Q6 · 'Live' live stream ใช้คนละ component — coverage แยก?
- **Priority:** High · **Ask:** Engineering / Design · **Story:** UC1 AC-01/AC-06 · **Source:** Jira comment (Chayanit, 2026-07-03)
- **Observation:** web — video + recorded LS ใช้ component เดียวกัน แต่ **'Live' LS คนละ component**. _(UC3 precondition ใหม่ยืนยัน recorded LS อยู่ใน video-family)_
- **Consequence:** tap-to-reveal ที่ผ่านบน video/recorded LS ไม่ครอบ Live LS อัตโนมัติ → core fix อาจไม่ผลบน Live
- **Question:** ยืนยัน tap-to-reveal ต้องใช้ได้เหมือนกันทั้ง video/recorded LS/'Live' LS? ถ้าใช่ Live ต้อง implement + test แยก

### 🔴 GAP-05 · UC2 · Pause ชนจังหวะ stream จบ — state ไหนชนะ?
- **Priority:** High · **Ask:** PM / Engineering · **Story:** UC2 AC-01/AC-03 · **Source:** phase 1.4 Timing
- **Observation:** ไม่มี AC ครอบ scenario กด pause พอดีจังหวะ host จบ stream (race)
- **Consequence:** player อาจอยู่ state ไม่สอดคล้อง (paused ผสม ended)
- **Question:** ถ้า pause กับ stream-end เกิดพร้อมกัน state ไหนชนะ — ended/recorded หรือ paused?

### 🟠 GAP-06 · UC2 · Recording ยังไม่พร้อมตอน stream จบขณะ paused
- **Priority:** Medium · **Ask:** Engineering · **Story:** UC2 AC-03 · **Source:** phase 1.4 Data-integrity
- **Observation:** AC-03 = ended/recorded state แต่ไม่ครอบกรณี recording ยัง process ไม่เสร็จ
- **Consequence:** viewer อาจเห็น frozen frame/error ระหว่างรอ
- **Question:** ถ้า stream จบขณะ paused แต่ recording ยังไม่พร้อม แสดง "processing" state ไหม?

### 🟠 GAP-07 · UC3-Q2 · Rapid repeated skip — accumulate หรือ debounce?
- **Priority:** Medium · **Ask:** Engineering · **Story:** UC3 AC-01/AC-02 · **Source:** phase 1.4 Timing
- **Observation:** ไม่ระบุพฤติกรรมเมื่อ user กด skip รัวๆ
- **Consequence:** position สุดท้ายเดาไม่ได้ (−30s หรือ −10s?)
- **Question:** rapid skip → accumulate หรือ debounce เป็น single −10s?

### 🟡 GAP-08 · UC3-Q3 · Skip ขณะ buffering
- **Priority:** Low · **Ask:** Engineering · **Story:** UC3 AC-01/AC-02 · **Source:** phase 1.4 Environment
- **Observation:** ไม่ระบุพฤติกรรมเมื่อ skip ขณะ buffer
- **Consequence:** อาจ stuck-loading / position ไม่ตรง
- **Question:** skip ขณะ buffering → queue หรือ seek-and-rebuffer?

---

## C. Ambiguous

### ✅ RESOLVED (2026-07-06)
- **AMB-01 · UC2 · return-to-live CTA** — ✅ **moot** — resume ไป live อยู่แล้ว ไม่มี state "behind live" ให้ต้องกลับ
- **AMB-02 · UC2 · chat sync ระหว่าง pause** — ✅ AC-01/02 ระบุ chat วิ่ง real-time + platform table ยืนยันทุก platform

### 🟠 AMB-03 · UC1-Q4 · Double-tap gesture descope แล้วใช่ไหม?
- **Priority:** Medium · **Ask:** PM / Design · **Story:** UC1 · **Source:** PRD (A1)
- **Observation:** PRD = pause ผูกกับ "central button **or double-tap** — Design to recommend" แต่ AC ใช้แค่ central button
- **Consequence:** ถ้า double-tap ยังต้องรองรับ → test เพิ่มมาก + ต้อง disambiguate กับ single-tap
- **Question:** double-tap descope แล้ว (central button วิธีเดียว) ใช่ไหม?

### 🟠 AMB-04 · UC3-Q1 · Nice-to-have (UC3) อยู่ใน release นี้ หรือ descope?
- **Priority:** Medium · **Ask:** PM · **Story:** UC3 · **Source:** PRD + PDT-3564 note
- **Observation:** UC3 = "Nice to have… can be descoped if it impacts delivery timeline"
- **Consequence:** กระทบ sprint planning + QA effort
- **Question:** UC3 อยู่ใน release นี้ หรือ descope?

### 🟡 AMB-05 · UC3-Q4 · Native OS scrub บน live vs AC-06 (in-app)
- **Priority:** Low–Medium · **Ask:** PM · **Story:** UC3 AC-06 · **Source:** Jira comment (Fidriyanto/Android) + platform table
- **Observation:** AC-06 = in-app skip ไม่แสดงบน live. แต่ Android scrub live ได้ผ่าน **OS native media control** (iOS/web ❌ ตามตาราง Prisa)
- **Consequence:** ไม่ขัดกันตรงๆ (native ≠ in-app) แต่ถ้าไม่ระบุ scope อาจเข้าใจว่า seek live ถูก block หมด
- **Question:** ยืนยัน AC-06 ครอบเฉพาะ in-app buttons? native scrub บน live (Android) ยอมรับได้?

### 🟡 AMB-06 · UC1-Q7 · ขนาด hit-target ปุ่ม pause กลาง
- **Priority:** Low · **Ask:** Design · **Story:** UC1 AC-02 · **Source:** phase 1.4 Boundary
- **Observation:** AC-02 แยก "tap outside button" (dismiss) จาก tap ปุ่ม — ไม่นิยาม hit-target
- **Consequence:** tap ใกล้ขอบ resolve เป็น button/surface ไม่แน่นอน → pause vs dismiss ก้ำกึ่ง
- **Question:** hit-target ปุ่มกลางขนาดเท่าไร?

### 🟡 AMB-07 · UC2-Q8 · Figma `LS-mobile-02/03/05` เหมือนกัน
- **Priority:** Low · **Ask:** Design · **Story:** UC2 / UC1 · **Source:** Figma
- **Observation:** 3 screen หน้าตาเหมือนกันใน PNG export
- **Consequence:** อาจมี annotation/interaction ที่ export หาย → QA เข้าใจ flow ผิด
- **Question:** 3 screen ต่างกัน state อย่างไร? ขอ Figma link/annotated frames

### 🟡 AMB-08 · UC3-Q5 · Boundary "<10s" vs "=10s พอดี"
- **Priority:** Low · **Ask:** Engineering · **Story:** UC3 AC-03/AC-04 · **Source:** phase 1.4 Boundary
- **Observation:** AC คลุม "less than 10s"/"within 10s" — ไม่ระบุค่าพอดี 10s
- **Consequence:** off-by-one ที่ boundary
- **Question:** position = พอดี 10s → clamp (0:00/final) หรือ skip ปกติ?

### 🟡 AMB-09 · OI-UC2-08 · Pause indicator visual = ปุ่ม ▶ overlay? (NEW, ← GAP-01 downgraded)
- **Priority:** Low · **Ask:** Design · **Story:** UC2 AC-01 · **Source:** AC-01 (rewritten) ↔ Figma `LS-mobile-04`
- **Observation:** AC-01 ใหม่ = "visual indicator communicating the stream is paused" (ตัด "behind live edge"). Figma `LS-mobile-04` = ปุ่ม ▶ กลางจอ
- **Consequence:** ไม่ชัดว่า pause indicator คือปุ่ม ▶ overlay หรือ element แยกที่ต้อง design (แต่ความเสี่ยงต่ำกว่าเดิมมาก เพราะ ▶ สื่อ "paused" ได้)
- **Question:** ยืนยัน pause indicator = central play-button overlay (LS-mobile-04) หรือต้อง design แยก?

### 🟡 AMB-10 · OI-UC2-09 · `user_story` ยังเขียน "behind the live edge" ไม่ตรง AC ใหม่ (NEW)
- **Priority:** Low · **Ask:** PM · **Story:** UC2 · **Source:** Jira user_story ↔ AC (rewritten)
- **Observation:** AC ใหม่ตัดแนวคิด "behind live edge" ออก (pause เฉยๆ + resume ไป live) แต่ `user_story` ใน Jira ยังเขียน "know when I'm paused **and behind the live edge**"
- **Consequence:** doc ไม่สอดคล้อง — คนอ่าน user_story จะเข้าใจ intent ผิดจาก AC
- **Question:** อัปเดต `user_story` ของ UC2 ให้ตรงกับ AC ใหม่ (pause + resume-to-live, ตัด "behind live edge")?

---

## D. Recommendations & additions

1. **UC1 core (AC-01/02/03) greenlight ได้เลย** — bug หลัก (XM/Ulta), timeout resolved (1s), desktop resolved. ไม่ต้องรอ UC2
2. **UC2 พร้อมขึ้นมาก** — ไม่ต้องรอ design pass สำหรับ behind-live indicator อีกแล้ว (ตัดแนวคิดออก). โฟกัสที่ **CONF-07** — ยืนยันกับ Eng ว่า resume-to-live เป็น behavior change ที่ต้อง implement ใหม่ทุก platform
3. **เพิ่ม AC ที่ยังขาด:** VOD/recorded-LS "end while paused" (UC2 AC-03 คลุม live-end); controls-after-pause (GAP-02) และ timer-reset (GAP-03) → ควรเป็น AC เมื่อ decide; cross-platform behavior matrix (ตาราง Prisa เป็นจุดเริ่มที่ดี)
4. **PM update `user_story` ของ UC2** (AMB-10) + บันทึก Decision Log (ยังว่าง) ทุกคำตอบ
5. **เติม PRD/Figma link ใน Jira epic** (ช่องว่าง) + ขอ Figma link จริง (AMB-07)
6. **Test-platform matrix** — ใช้ตาราง Prisa (68264) เป็นฐาน; ต้อง cover iOS/Android/web-mobile/web-desktop เพราะ current behavior ต่างกัน (โดยเฉพาะ resume ที่กำลังจะเปลี่ยน)

---

## E. Readiness verdict — ทำไม (ยัง) ไม่พร้อมส่ง developer ทั้งหมด

### สรุปต่อ story (หลัง update 2026-07-06)

| Story | เดิม | ตอนนี้ | เหตุผล | Blocking |
|---|---|---|---|---|
| **UC1 (PDT-3562)** | 🟡 Partial | 🟡 **Partial** | core พร้อม, desktop เคลียร์ | GAP-02, GAP-03, GAP-04 |
| **UC2 (PDT-3563)** | 🔴 Not ready | 🟡 **ดีขึ้นมาก** | resume/chat/badge/desktop เคลียร์ | CONF-07, GAP-05, (AMB-09) |
| **UC3 (PDT-3564)** | 🟢 Cond. ready | 🟢 **Cond. ready** | design ครบ, recorded LS ชัด | AMB-04 (descope), GAP-07 |

### เหตุผลเชิงระบบที่ยังเหลือ (ลดลงจาก 5 → 3)

1. **Behavior change ยังไม่ยืนยัน** — resume-to-live (CONF-07) เป็นการเปลี่ยน behavior ทุก platform, dev/QA ต้อง aware ก่อนเริ่ม
2. **Engineering details ยังไม่นิยาม** — overlay-after-pause (GAP-02), timer-reset (GAP-03), pause-races-end (GAP-05), Live component coverage (GAP-04)
3. **Scope decision ค้าง** — UC3 descope (AMB-04), double-tap (AMB-03)

_(หายไปจากเดิม: missing design ✅, resume conflict ✅, cross-platform not unified ✅ — เคลียร์แล้วโดย update นี้)_

### เริ่มอะไรได้เลยตอนนี้

- ✅ **UC1 core (AC-01/02/03)** — พร้อม implement
- ✅ **UC2** — เริ่มออกแบบ/วางแผน implement ได้ (แนวคิดชัดแล้ว) พอ CONF-07 ยืนยัน → เริ่ม dev
- 🎯 **ลำดับ:** UC1 core → UC1 ที่เหลือ (ตอบ GAP-02/03) → UC2 (ยืนยัน CONF-07) → UC3 (ถ้าไม่ descope)

---

_ต้นทาง: per-story `qa/PDT-3418/PDT-3562-uc1-analysis.md`, `PDT-3563-uc2-analysis.md`, `PDT-3564-uc3-analysis.md` · stored stories `products/PDT-3418/stories/*.json` (synced 2026-07-06) · prior by-mechanism `output/backup/PDT-3418-*.md`_
