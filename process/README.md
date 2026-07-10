# Process Layer — BA+QA Pipeline

เอกสารชุดนี้คือ **process definition** — สูตรที่บอกว่า "ทำอะไร ลำดับไหน ผ่าน gate อะไร".
Process **เรียกใช้ (call)** skill ที่ `.claude/skills/` — skill เป็นแค่ **capability atomic** (technique + template)
ที่ไม่รู้เรื่องลำดับหรือ gate.

> 👉 **จะลงมือรัน?** เปิด **[`RUNBOOK.md`](RUNBOOK.md)** — มี flowchart + cheat sheet "ครั้งนี้พิมพ์/รันอะไร"
> เอกสารนี้ (README) = architecture/นิยาม; RUNBOOK = operator guide

> **หลักการแยกชั้น:** Process = orchestration + shared artifacts + gates · Skill = pure function (input artifact → output artifact)
> เหตุที่ต้องแยก: skill ตัวเดียวถูกเรียกซ้ำในหลาย process (ดู reuse map ข้างล่าง) — ถ้ายุบ skill จะพัง reuse

---

## 3 Layers

| Layer | Process doc | Skills ที่เรียก | Output |
|---|---|---|---|
| **L1 · BA Requirement Analysis** | `layer-1-ba-requirement-analysis.md` (full) | phase-1-1 … 1-4 | enriched AC + Clarification Register + readiness |
| **L2 · QA Story Authoring** | `layer-2-qa-story-authoring.md` (draft) | phase-2-1 … 2-6 | Schema 1 (`01-complete-jira-story.json`) → Schema 2 (`02-user-flow.json`) |
| **L3 · Test Design** | `layer-3-test-design.md` (draft) | phase-3-1, 3-2 | test conditions/cases + automation judgment |

Entry points (trigger phrases) ยังอยู่ที่ `.claude/skills/run-analysis/` ซึ่งตอนนี้เป็น **thin dispatcher** ชี้มาที่ doc เหล่านี้.

---

## Concepts — Enrich vs Author · AC vs BR  (คำอธิบายเวลาทีมถาม)

**Enrich (L1 · phase-1-3) ≠ Author (L2 · phase-2-2)** — คนละจุดประสงค์ ไม่ใช่ทำซ้ำ:
- **Enrich** = เติม AC ของ PM ให้ test ได้ + หา gap/edge → output เป็น *analysis doc* (จุดประสงค์: **เข้าใจ**ของที่ได้มา)
- **Author** = ประกอบ AC ชุดสุดท้ายให้ครบ **4 scenario type** (default / happy / alternative / error) + จัดรูปเป็น story สุดท้าย → output เข้า *Schema 1* (จุดประสงค์: **ผลิต**สัญญาที่ทีม commit)
- สั้น ๆ: **L1 = "เข้าใจของยุ่ง ๆ ที่ได้มา" · L2 = "ประกอบเป็นของสะอาดที่ commit ได้"** (ข้อมูลซ้อนกันได้ แต่คนละรูป/คนละเป้า)

**AC ≠ BR** — คนละบทบาท เอาไปใช้ต่างกัน:

| | **AC** (Acceptance Criteria) | **BR** (Business Rule) |
|---|---|---|
| คือ | **สถานการณ์**ที่ test ได้ — "ถ้า X → Y" | **กฎที่จริงเสมอ**ข้ามทุกสถานการณ์ |
| ผูกกับ | 1 scenario | ทั้งระบบ (หลาย AC อ้าง BR เดียว) |
| **QA** ใช้ | → แปลงเป็น **test case** · วัด coverage | → **ขอบเขต regression**: BR เปลี่ยน = รู้ทันทีว่าต้อง re-test story ไหน |
| **Dev** ใช้ | checklist "เคสนี้เสร็จยัง" | **implement ครั้งเดียว** ทุก AC ที่อ้างถูกหมด |

**ตัวอย่างจริง (CONF-08):** AC 2 ข้อเคยขัดกันเงียบ ๆ ("pause แล้ว seek โชว์" vs "Live ไม่มี seek") จนดึงออกมาเป็น **BR เดียว** (BR-01: seek เฉพาะ video/recorded) → source of truth เดียว ขัดกันซ้ำไม่ได้อีก

**Analogy บอกทีมได้เลย:** BR = **ฟังก์ชันกลางเขียนครั้งเดียว** · AC = **จุดที่เรียกใช้** — ไม่มี BR เท่ากับ copy logic ไปวางทุกที่แล้วเพี้ยนกันเอง
ใน Schema 1 ทุก AC มี `ac_id` + `br_ids[]` → traceability: test fail → AC → BR → รู้ว่ากระทบ story อื่นไหน

---

## Skill-reuse map (ทำไม skill ต้อง atomic)

artifact ที่ skill หนึ่งผลิต ถูก **process ส่งต่อ** ให้ skill/step อื่น — ไม่ทำซ้ำ

| Artifact (ผลิตโดย) | ถูก reuse โดย | ที่ไหน |
|---|---|---|
| **Relationship Map** (1-1) | 1-2 (User Need ต่อ actor), 1-3 (silent actor), **2-6** (scope silent-actor gap) | L1 STEP1→STEP2, L2 STEP4 |
| **State Machine** (1-1) | 1-3 (Then ครอบ state change), 1-4 (edge timing/boundary), **2-2** (verify Then), 3-2 (State BR→transition) | L1 STEP2, L2 STEP2, L3 STEP1 |
| **Pain&Consequence "Why"** (1-1) | 1-2 (Business Goal), **2-3** (BR extraction engine), 2-4 (5 Whys) | L1 STEP1, L2 STEP3 |
| **User Need / 3-Layer** (1-2) | **2-6** (scope), 2-4 (clarification) | L2 STEP4 |
| **Enriched AC** (1-3/1-4) | 2-2 (complement), 2-3 (BR source), 2-5 (effort) | L2 |
| **Clarification Register** (all) | routing → PM/Design/Eng; gate ก่อน handoff L1→L2 | ทุก layer |

> ⚠️ **BR extraction ซ้ำ 2 ที่:** `2-3` (จาก AC, ใช้ "Why") = canonical เมื่อมี AC · `3-2` (multi-source, self-contained) = path เมื่อ AC ยังไม่ครบ. Process เป็นคนเลือกว่าใช้ตัวไหน

---

## Shared-artifact model

Process เป็นเจ้าของ artifact store; skill read/write เข้ามัน

| Artifact | ผลิตที่ | ที่เก็บ |
|---|---|---|
| **AC Manifest** | L1 STEP0 | `products/<epic>/stories/*.json` (ac_id) + snapshot `qa/<epic>/.ac-manifest.json` |
| **Relationship Map / State Machine / 3-Layer trace** | L1 STEP1 | section ใน `qa/<epic>/<story>-analysis.md` |
| **Enriched AC** | L1 STEP2 | `qa/<epic>/<story>-analysis.md` |
| **Clarification Register** | L1 ทุก step (append) | `qa/<epic>/PDT-XXXX-clarifications-for-pm-design.md` (+ optional `1_clarifications.json`) |
| **Schema 1 / Schema 2** | L2 | `output/PDT-XXXX-complete-jira-story.json` / `-user-flow.json` |

---

## Gate catalog (นิยามกลาง ใช้ซ้ำทุก layer)

| Gate | เมื่อไหร่ | เงื่อนไขผ่าน | ถ้าไม่ผ่าน |
|---|---|---|---|
| **Readiness** | ก่อนเริ่ม layer/workflow | input ครบ (ระบุ checklist ต่อ layer) | หยุด แจ้งสิ่งที่ขาด |
| **AC Manifest** | ต้นทุก workflow ที่มี AC | list ac_id + count จาก **structured JSON** (ไม่ eyeball) | ถ้าไม่มี AC → หยุด |
| **Coverage + Content** | จบ STEP specify | ทุก ac_id ถูกวิเคราะห์ **และ** fingerprint(given+when+then) ตรง snapshot | ac_id ขาด → วิเคราะห์; fingerprint เปลี่ยน → STALE, re-analyze |
| **Completion** | หลัง loop | ✓/✗ ทุก ac_id เทียบ Manifest = N/N | มี ✗ → วิเคราะห์ทันที re-check ก่อน write |
| **Freshness / Dropout** | ตลอดทาง | Manifest ตรง Jira ล่าสุด (diff) · ไม่มี AC หลุดเงียบ | added/removed/changed → re-run step ที่กระทบ |
| **Schema-1 Integrity** (L2) | จบ STEP6 emit Schema 1 | br_ids→def ครบ (no DANGLING_BR) · ทุก BR ถูก AC อ้าง (no DEAD_BR) · ไม่มี dup ac_id/br_id | exit 1 → หยุด แก้ก่อน commit |
| **Schema-1↔2 Traceability** (L2) | หลัง build Schema 2 | ทุก ac_id ถูก flow ครอบ · ไม่มี ac/br ผี (PHANTOM) · step actor ประกาศใน `actors{}` ครบ | exit 1 → หยุด แก้ก่อน commit |
| **Decision Ledger** (R2, L2) | ทุก judgment call · ก่อน autonomous run | ทุก split/priority/scope/pending ถูก log + settled (confirmed / resolved-by-code) | manual: open = advisory · autonomous: open human = HALT |
| **Scenario Coverage** (L3.5) | หลัง phase-3-3 | ทุก AC → ≥1 scenario · ทุก BR → owns_br 1 ครั้ง (test ครั้งเดียว, กัน over-test) · success + technique-driven alternative[] | exit 1 → หยุด แก้ก่อน |
| **Test-Case Coverage** (L3.5) | หลัง phase-3-4 | ต่อ scenario: ≥1 success EC + **เป๊ะ N** alternative EC (เกิน=over-test, ขาด=gap) · steps/test_data/expected ไม่ว่าง | exit 1 → หยุด แก้ก่อน |
| **Automation-Plan Coverage** (L3.6) | หลัง phase-3-5 | ทุก EC มี disposition (bijection, ไม่มีตก) · at_status↔status consistent · Manual มี blocker+reason · Automate มี target (tag=`@`+ec_id) · `live-broadcast`⟹Manual | exit 1 → หยุด แก้ก่อน |

**Coverage+Content คือหัวใจ:** นับจำนวนอย่างเดียวไม่พอ — UC2 (PDT-3563) มี 3 AC เท่าเดิมแต่ AC-01/02 ถูกเขียนใหม่ 2026-07-06;
ถ้าเช็คแค่ "3/3" จะ false-pass analysis เก่า. Gate จึงผูก `ac_id` + **content fingerprint**.

**Gate ที่บังคับด้วย script จริง (exit 0/1) — ไม่ใช่ prose:**
| Script | Layer | จับอะไร |
|---|---|---|
| `checks/ac_coverage.py qa/<epic>` | L1 | analysis .md ครอบทุก ac_id + STALE (fingerprint เปลี่ยน) |
| `checks/schema1_integrity.py qa/<epic>` | L2 | Schema 1 referential: dangling/dead br_id, dup id |
| `checks/schema_trace.py qa/<epic>` | L2 | Schema 1↔2: ac coverage, phantom ac/br, undeclared actor |
| `checks/decision_ledger.py qa/<epic> [--autonomous]` | L2 | judgment ledger well-formed; `--autonomous` → open human decision = HALT |
| `checks/br_tc_coverage.py qa/<epic>` | L3 | `*-test-design.md` ครอบทุก BR + AC ของ Schema 1 (BR→TC coverage) |
| `checks/scenario_coverage.py qa/<epic>` | L3.5 | `*-scenarios.json`: ทุก AC → ≥1 scenario · ทุก BR → owns_br 1 ครั้ง · success + alternative[] · no phantom ref |
| `checks/test_case_coverage.py qa/<epic>` | L3.5 | `*-test-cases.json`: ต่อ SC มี ≥1 success EC + **เป๊ะ N** alternative EC (N=len(alternative[])) · alt_index ครบ · ref resolve |
| `checks/automation_plan_coverage.py qa/<epic>` | L3.6 | `*-automation-plan.json`: ทุก EC มี disposition (bijection) · at_status↔status · Manual→blocker+reason · Automate→target tag=`@`+ec_id · `live-broadcast`⟹Manual |

> ทั้ง 3 เป็น stdlib-only, deterministic, no network — run มือก่อน handoff/commit. schema1_integrity + schema_trace codify script ที่จับ error จริงตอนรัน PDT-3418 (ก่อนหน้านี้เป็น ad-hoc ที่ไม่ได้ commit)

---

## Rules (Dropout protection — ใช้ทุก layer)
1. ห้าม AC หลุดโดยไม่แจ้ง (critical failure)
2. ห้าม write output ก่อน Completion gate ผ่าน
3. แสดง progress `[X/N]` ทุก AC/flow ใหม่
4. Process เป็นคน "อ่าน skill ก่อน loop" ไม่ใช่ skill สั่งกันเอง
5. เจอ AC หลุดหลัง gate → วิเคราะห์ทันที re-check
6. **(R1) write boundary:** L2 เขียนแค่ `qa/` + `output/` · `products/<epic>/stories/*.json` = READ-ONLY (แก้ได้เฉพาะ L1 STEP 0 Jira-sync แล้ว `ac_coverage.py --update`) — กันเขียนทับ PM AC; การละเมิดโผล่เป็น STALE ใน `ac_coverage.py`
7. **(R2) log judgment:** ทุก split/priority/scope/pending-resolution → `qa/<epic>/decisions.json` · autonomous run HALT ถ้ามี open human decision
