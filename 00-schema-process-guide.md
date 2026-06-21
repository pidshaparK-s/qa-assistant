# Schema Process Guide
## Complete Jira Story + User Flow JSON — เมื่อไหร่ใช้อะไร และต้องการ input อะไร

---

## ทำไมต้องมีสอง schema

| | Complete Jira Story | User Flow JSON |
|---|---|---|
| **ใช้สื่อสารกับ** | คน (PM, dev, QA, stakeholder) | AI + coding tools (Claude Code, Copilot, Playwright) |
| **รูปแบบภาษา** | Human-readable prose + structure | Machine-readable actor-based steps |
| **จุดประสงค์** | ทำให้ทุกคนเข้าใจตรงกัน | ทำให้ AI generate code/test ได้ถูกต้อง |
| **สร้างเมื่อ** | หลัง clarification ครบ ก่อน sprint | หลัง Complete Jira Story พร้อมแล้ว |
| **input ที่ต้องการ** | PM's AC + clarification answers + BR | Complete Jira Story ที่สมบูรณ์แล้ว |

---

## Process — ขั้นตอนตามลำดับ

```
PHASE 1 — ได้รับ requirement จาก PM
──────────────────────────────────────────
Input:  PRD (Notion/Confluence)
        PM's draft Jira story (User Story + happy path AC)
Output: รายการ gap และ clarification questions

Tools:  Phase 1.1 Requirement Interrogation
        Phase 1.2 Three-Layer Analysis
        Phase 1.3 Happy Path AC Enrichment

ห้ามไปต่อถ้า: PM's AC ยังตีความได้มากกว่าหนึ่งแบบ


PHASE 2 — Clarification
──────────────────────────────────────────
Input:  Clarification questions จาก Phase 1
        คำตอบจาก PM (ใน refinement meeting หรือ async)
Output: Confirmed decisions สำหรับทุก gap

ห้ามไปต่อถ้า: ยังมี [PENDING] ที่ยังไม่ได้คำตอบ


PHASE 3 — สร้าง Business Rules
──────────────────────────────────────────
Input:  PM's AC ที่ confirmed + Phase 2.3 BR Extraction skill
Output: BR list พร้อม br_id, type, statement

ห้ามไปต่อถ้า: ยังมี AC ที่ logic ไม่ชัดพอจะแยก BR ได้


PHASE 4 — สร้าง Complete Jira Story  ← Schema 1
──────────────────────────────────────────
Input:  PM's User Story
        Confirmed AC (PM's happy path + QA-enriched edge/error)
        BR list จาก Phase 3
        Preconditions จาก story
Output: Complete Jira Story (human-readable)
        พร้อม story_id, uc_id, br_id, ac_id ครบ

ใช้สำหรับ: อัปเดต Jira card, รีวิวกับทีม, sign-off ก่อน sprint


PHASE 5 — สร้าง User Flow JSON  ← Schema 2
──────────────────────────────────────────
Input:  Complete Jira Story จาก Phase 4 (ต้องสมบูรณ์ก่อน)
Output: User Flow JSON แยกต่อ flow
        พร้อม flow_id, ac_id[], br_ids[], steps[], entry_from

ใช้สำหรับ: ส่งให้ Claude Code / Copilot generate test
           Dev ใช้เป็น spec ในการ implement
           QA ใช้ bootstrap automation test


PHASE 6 — Generate Test Cases (จาก Flow JSON)
──────────────────────────────────────────
Input:  User Flow JSON จาก Phase 5
Output: Unit test skeleton
        Scenario test cases
        E2E test cases (Playwright/Cypress)

Tools:  Claude Code + CLAUDE.md ที่มี skills ครบ
```

---

## Input Requirements — ก่อนสร้าง Schema 1 (Complete Jira Story)

### Must have (ขาดไม่ได้)
- [ ] User Story ในรูปแบบ As a/I want/So that ที่ผ่าน INVEST
- [ ] Preconditions ของ story ครบ
- [ ] PM's happy path AC ทุกข้อ confirmed (ไม่มี ambiguity)
- [ ] คำตอบ clarification ทุกข้อที่ BA+QA ถามไป
- [ ] BR ที่ extract ได้จาก AC พร้อม br_id

### Should have (ควรมีก่อน sprint เริ่ม)
- [ ] QA-enriched AC — error state ทุกข้อ
- [ ] QA-enriched AC — edge case ที่ priority high ทุกข้อ
- [ ] BR cross-reference — ตรวจแล้วว่า BR ใน story นี้ไม่ซ้ำหรือขัดแย้งกับ story อื่น

### สัญญาณว่ายังไม่พร้อม
- มี AC ข้อไหนที่ Then บอกแค่ "is processed" หรือ "is done" โดยไม่ระบุ state
- มี AC ที่ยังมี [PENDING] หรือ [TBD] ค้างอยู่
- ยังไม่รู้ว่า error state ควรเป็นยังไง (ข้อมูลหาย? state rollback? retry ได้ไหม?)

---

## Input Requirements — ก่อนสร้าง Schema 2 (User Flow JSON)

### Must have (ขาดไม่ได้)
- [ ] Complete Jira Story จาก Phase 4 ที่สมบูรณ์ครบ
- [ ] ac_id และ br_id ทุกอันกำหนดแล้ว
- [ ] ทุก AC รู้ว่า type คือ default_state / happy_path / error_state / edge_case
- [ ] flow dependency รู้ชัดว่า flow ไหน entry_from อะไร

### Should have
- [ ] actor list ชัดเจน — admin, app, api, network, system (อย่าปน)
- [ ] state_changes ระบุชัดว่า object ไหนเปลี่ยน from → to

### สัญญาณว่ายังไม่พร้อม
- ยังไม่รู้ว่า step ไหน actor คือ "app" หรือ "api" (ต้องถาม dev ก่อน)
- มี AC ที่ยังไม่รู้ว่า concurrent flow เชื่อมกันยังไง
- entry_from ยังไม่ชัด — ยังไม่รู้ว่า flow นี้เริ่มจาก state ไหน

---

## ความสัมพันธ์ระหว่าง IDs

```
epic_id   PDT-2636
  └── story_id  PDT-2880
        ├── uc_id     UC-08
        ├── br_ids    BR-01, BR-02, BR-04, BR-10
        ├── ac_ids    AC-1 ... AC-14
        └── flow_ids
              ├── flow-UC08-view-pending          (AC-1,2,3,4,5 + BR-01,02)
              ├── flow-UC08-approve-success       (AC-7,8       + BR-10)
              ├── flow-UC08-approve-network-error (AC-11)
              ├── flow-UC08-concurrent-conflict   (AC-13        + BR-04)
              └── flow-UC08-empty-state           (AC-6,12)
```

**Traceability chain:**
Test case → flow_id → ac_id → story_id → uc_id
ถ้า bug เจอใน test → รู้ทันทีว่ากระทบ AC ไหน → story ไหน → BR ไหน

---

## เมื่อ PM ยังไม่ได้ clarify

ห้ามสร้าง User Flow JSON จาก AC ที่ยังไม่ชัด
ถ้า flow มาจาก AC ที่ ambiguous → test case ที่ generate ออกมาจะ test สิ่งที่ BA assume ไม่ใช่สิ่งที่ PM ต้องการ

**วิธีจัดการ:**
```
Option A — Hold flow นั้น:
  สร้าง Complete Jira Story ก่อน แต่ leave flow นั้นเป็น placeholder
  รอ clarification แล้วค่อย fill in

Option B — Mark as assumption:
  สร้าง flow แต่ mark step ที่ยังไม่ชัดว่า
  "assumption": "post remains in pending state — pending PM confirmation"
  ให้ dev และ QA รู้ว่าส่วนนี้ยังไม่ confirmed
```
