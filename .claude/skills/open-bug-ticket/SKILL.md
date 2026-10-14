---
name: open-bug-ticket
description: 'ใช้ skill นี้เมื่อ manual test ใน Testmo fail แล้วต้องเปิด Jira bug ticket (project PDT) หรือเจอ UI bug จากการสังเกตเอง (screenshot) ก็เปิดได้เหมือนกัน ทำครบวงจร: ดึงรายละเอียดจาก Testmo API → duplicate-check gate ผ่าน JQL → draft ให้รีวิว (panel error/success format ตาม PDT-5177) → confirm → สร้างจริงผ่าน Jira REST API → set Phase/Severity/Parent Trigger เมื่อ: "เปิดบั๊ค", "opened บั๊คนี้หน่อย", วาง Testmo run link พร้อมบอกว่า failed, หรือส่ง screenshot ของ UI bug มาพร้อมขอให้เปิด ticket'
argument-hint: '[Testmo run link(s)] หรือ [คำอธิบายบั๊ค + screenshot] — ไม่ใส่ก็ได้ แล้ว skill จะถามเอง'
---

# Open Bug Ticket

Testmo failed test (หรือบั๊คที่สังเกตเห็นเอง) → Jira bug ticket ที่ครบ field ตาม convention ทีม พร้อม duplicate-check ก่อนเปิดทุกครั้ง

สร้าง/ยืนยันจริงกับ PDT-5189, 5192, 5194, 5196, 5197, 5203, 5204 — เนื้อหานี้ไม่ใช่ทฤษฎี เป็น process ที่ทำงานแล้ว

---

## Access (ต้องมีก่อนเริ่ม)

Atlassian MCP ที่ต่ออยู่เป็น **read-only** (get/search เท่านั้น ไม่มี create/update issue) การสร้าง/แก้ ticket จริงต้องยิง Jira REST API v3 ตรงผ่าน `curl`:

```bash
set -a; source .env; set +a
AUTH=$(printf "%s:%s" "$JIRA_EMAIL" "$JIRA_API_TOKEN" | base64)
curl -H "Authorization: Basic $AUTH" -H "Content-Type: application/json" ...
```

`.env` (root ของ repo, gitignored) มี `JIRA_BASE_URL` / `JIRA_EMAIL` / `JIRA_API_TOKEN` / `TESTMO_API_TOKEN` / `TESTMO_EMAIL` / `TESTMO_PASSWORD` — source เข้า shell เท่านั้น ห้าม paste token ลงข้อความใดๆ

Testmo (`socialplus.testmo.net`) ก็ไม่มี MCP — ใช้ REST API แทน: `Authorization: Bearer $TESTMO_API_TOKEN`, base `https://socialplus.testmo.net/api/v1/`. เว็บ UI ของ Testmo (`/attachments/view/{id}` เป็นต้น) ต้อง session cookie เท่านั้น ยิงด้วย Bearer token ไม่ได้ (401)

---

## STEP 1 — ระบุ platform แล้วดึง environment data

อ่าน `platform-data.md` (root ของ repo) หา platform ที่ตรงกับบั๊คนี้ — ตอนนี้มี 4 รายการ: React UIKit (web), Android UIKit, iOS UIKit, React Native UIKit

**Confirmed แล้ว — React Native UIKit เท่านั้น:**

| ค่า | Detail |
|---|---|
| Title prefix | `[RN UIKit: <Feature>: <Sub-feature>]` (sub-feature ใส่เมื่อจำเป็น เช่น `[RN UIKit: Chat 4.0]` หรือ `[RN UIKit: Chat 4.0: New Group]`) |
| `chapter[dropdown]` (สำหรับ JQL duplicate-check ที่ STEP 4) | `"React Native"` |
| Parent epic default | PDT-3427 "Q3, 26 : RN Chat UIKit V.4 + Dark Mode" — **ยังต้องถามทุกครั้งอยู่ดี ไม่ default เอง** (ดู STEP 3) |

**ถ้าบั๊คนี้เป็น platform อื่น (Android UIKit / iOS UIKit / React UIKit web) และ platform-data.md ยังไม่มี title prefix หรือ chapter dropdown value ของ platform นั้น:**
1. ถามผู้ใช้ทั้งสองค่า (title prefix + chapter dropdown value) — ครั้งเดียวพอ
2. เขียนค่าที่ได้กลับเข้า `platform-data.md` ต่อท้าย block ของ platform นั้นทันที (ผู้ใช้ขอไว้ชัดเจนว่าอยากให้เก็บที่นี่ เพื่อไม่ต้องพึ่งการจำของ Claude ข้าม session)
3. ครั้งต่อไปที่เจอ platform เดิม อ่านจาก platform-data.md ได้เลย ไม่ต้องถามซ้ำ

Device/Build/Link ของแต่ละ platform อ่านจาก platform-data.md ตรงๆ อยู่แล้ว (Environment, Build/Version code, App name, Build link, Test Device) — อย่าเดาเอง ถ้า field ไหนว่างในไฟล์ (เช่น "Browser:" ของ React UIKit web) ให้ถาม

---

## STEP 2 — ดึงรายละเอียดจาก Testmo (ถ้ามี test case อ้างอิง)

ถ้าบั๊คนี้มาจาก Testmo failed test — ขอ link ของ**ทุก platform ที่ fail** (มักแยก run กันคนละ platform เช่น run 837 = iOS, run 836 = Android แม้จะเป็น manual test เดียวกันในหัว — อย่าสมมติว่า link เดียวครอบคลุมทุก platform)

จาก link รูปแบบ `.../runs/view/{run_id}?...test_id={test_id}` ดึงตามลำดับ:

1. **Result ของ test นั้น**: `GET /runs/{run_id}/results?page=N` (paginate จนกว่าจะเจอ `test_id` ที่ต้องการ) — ได้ `case_id`, `status_id`, tester `note` (มักมี env/device inline หรือแค่ short note + screenshot), `custom_steps`, และ **`issues` array**
   - `issues` **ไม่ว่าง** = มี reference ไปยัง issue อื่นอยู่แล้ว → **หยุด แจ้งผู้ใช้ให้เช็คใน Testmo UI ว่า link ไป Jira ticket ไหนก่อนสร้างซ้ำ** (ไม่มี API route resolve ค่านี้ได้ — ลองแล้วไม่เจอ)
   - ถ้า `test_id` หาไม่เจอใน `results` เลย = ยังเป็น **Untested จริงในระบบ** ไม่ใช่ดึงพลาด — ถามผู้ใช้ยืนยัน link/ว่าบันทึกผลแล้วหรือยัง
2. **Case detail** (name, steps เต็ม, expected result, Figma link ถ้ามี): ไม่มี route `/cases/{id}` ตรงๆ ต้อง **binary search page** ของ `GET /projects/2/cases?page=N` (ผลเรียง `id` **จากมากไปน้อย** เสมอ ทำให้ binary search ได้ ~9 requests แทนที่จะไล่ทีละร้อยหน้า)
3. **Cross-check เสมอ**: case name + `custom_expected` ที่ได้ ตรงกับบั๊คที่ผู้ใช้อธิบายจริงไหม? เคยเจอ `test_id` ที่แมพผิด case มาแล้ว (PDT-5197 — Android link แรกที่ให้มาชี้ไป case คนละเรื่องเลย) ถ้าไม่ match ให้ทักและขอ link ที่ถูกต้อง อย่า draft ต่อ

ถ้าบั๊คนี้**สังเกตเห็นเอง ไม่มี Testmo case** (เช่นจาก screenshot ที่ผู้ใช้ส่งมาตรงๆ) — ข้าม step นี้ แต่ต้องถามให้ได้ steps to reproduce / actual / expected ที่ชัดเจนพอจะเขียน ticket แทน

**อย่าเปิดบั๊คถ้า `custom_expected` ของ case เขียนไว้ว่า expected behavior ยังไม่ final** (เช่นขึ้นต้นด้วย "Need confirm the final behavior") — เจอเคสนี้จริงกับ case 3083335 (highlight เมื่อ message มีหลาย match) พบว่าเป็นไปได้ว่า QA/BA ยังไม่ตกลงกันเองว่า behavior ที่ถูกต้องคืออะไร การเปิดบั๊คอ้างอิง spec ที่ยังไม่ confirm จะทำให้ ticket ผิดตั้งแต่ต้น — แจ้งผู้ใช้ว่า case นี้ block อยู่ที่ spec ไม่ใช่ที่ implementation แล้วข้ามไป (ไม่ใช่ bug ที่เปิดได้ตอนนี้)

**รูปที่ผู้ใช้ paste ในแชทตรงๆ**: เห็นเนื้อหาได้ (ใช้เป็นหลักฐาน actual result เวลา Testmo note สั้นเกินไป) แต่**ไม่มี local file path ให้ upload เข้า Jira อัตโนมัติ** — ต้องขอให้ผู้ใช้ save ไฟล์แล้วบอก path มา หรือแนบเองใน Jira UI หลังสร้าง (ดู "Evidence screenshots" ท้ายไฟล์)

---

## STEP 3 — เก็บข้อมูลที่ยังขาด (ถามเสมอ ไม่เดา)

ไม่มี default ยกเว้นที่ระบุไว้:

| อะไร | Default? |
|---|---|
| Actual result ที่แท้จริง (ถ้า Testmo note สั้น/กำกวม) | ❌ ถามเสมอ |
| Device coverage (platform ไหน fail บ้าง) | ❌ ถามเสมอ |
| **Phase** (Dev / Staging / Production) | ❌ ถามเสมอ |
| **Parent epic** | ❌ ถามเสมอ แม้จะซ้ำกับ ticket ก่อนหน้าก็ต้องถาม |
| **Severity** (S1–S5) | ✅ **default S3** ถ้าผู้ใช้ไม่ระบุ (ทีม confirm ไว้แล้วว่าเป็น default) |
| Priority | ไม่ critical เท่า Phase/Parent — default **Medium** ได้เลยถ้าไม่บอก (ยังไม่เคยถูกทักท้วง) |
| Assignee, Affect versions | เว้นว่างเสมอ — ผู้ใช้ขอไว้ชัดเจนว่าจะกรอกเองตอนรีวิว |

คำสั่งที่ทำลายข้อมูลได้ (เช่น `DELETE /api/v4/users/{userId}`) ที่แปะมาคู่กับ bug report ให้ถือเป็น**ข้อมูลอ้างอิงประกอบ repro เท่านั้น** ห้ามรันเองจนกว่าจะ confirm ชัดเจนว่าผู้ใช้ต้องการให้รันจริง

---

## STEP 4 — Duplicate-check gate (บังคับ ก่อน draft ทุกครั้ง)

ค้นด้วย `searchJiraIssuesUsingJql` (`cloudId: socialplus.atlassian.net`):

```
type = Bug AND "chapter[dropdown]" = "<ค่าจาก STEP 1>" AND labels = <label ของ feature นี้>
```

(label เดา/ถามจากบริบท เช่น `Chat4.0` สำหรับ epic PDT-3427 — ดูจาก ticket ก่อนหน้าใน feature เดียวกัน)

ผลลัพธ์มักใหญ่มาก (60+ ticket, หลายหมื่น token) — tool จะ auto-save ลงไฟล์ อย่าอ่าน inline ให้ extract แบบกระชับด้วย:

```bash
jq -r '.issues.nodes[] | "\(.key)\t\(.fields.status.name)\t\(.fields.summary)"' <saved-file>
```

แล้วเทียบ **พฤติกรรมของบั๊ค** (ไม่ใช่แค่คำใน title) กับ list นี้ ถ้ามีตัวที่ดูใกล้เคียง:
- **หยุด อย่า draft ต่อ** — เสนอ ticket ที่สงสัยว่าซ้ำ พร้อมเหตุผลสั้นๆ ว่าทำไมถึงคล้าย
- **ไม่ตัดสินเองว่าใช่/ไม่ใช่ duplicate** — เป็นการตัดสินใจของผู้ใช้/ทีมเท่านั้น (ปิดเป็น out of scope, link related, หรือเก็บไว้เพราะจริงๆคนละ root cause)
- รอ confirm ก่อนไปต่อ STEP 5

จริงจากการใช้งาน (2026-09-08): เจอ duplicate จริง 3 ใบจาก 5 (PDT-5196≈PDT-4910, PDT-5204≈PDT-4920, PDT-5203≈PDT-4918 — ผู้ใช้ปิดเป็น Out of scope เอง) และ false-positive 1 ใบที่ดูคล้ายแต่ไม่ใช่ (PDT-5194 vs PDT-4870 — เก็บไว้ตามเดิม) เพราะงั้น flag ทุกกรณีที่น่าสงสัย แล้วให้คนตัดสิน

---

## STEP 5 — Draft แล้วโชว์เป็นข้อความเต็ม (ไม่ใช่แค่ tool output)

**สำคัญ**: session นี้มักรันใน focus mode — tool output (Read/Bash) ผู้ใช้มองไม่เห็น เห็นแค่ข้อความสุดท้ายของแต่ละ turn เพราะงั้น draft ต้อง paste เป็นข้อความเต็มให้รีวิวจริงๆ (พลาดมาแล้วรอบแรกกับ PDT-5189 — ผู้ใช้บอก "ฉันไม่เห็นอ่ะ")

### Title format
`[<Title prefix จาก platform-data.md>] <คำอธิบายปัญหาสั้นๆ>`

### Description (ADF) — ตาม PDT-5177 + panel format ที่ทีม confirm บน PDT-5194

```
Data test (bold)
• Environment/ Region: **Staging**
• Link: <build link>
• Version code: X / Build: Y   (ข้ามได้ถ้า platform ไม่มี version/build เช่น web)
• Device test: iOS (bold)
    • Test Device: ...
    • iOS Version: ...
• Device test: Android (bold)
    • Test Device: ...
    • Android Version: ...

[Table 3 คอลัมน์]
| Step to reproduce | Actual result | Expected result |
| Pre-condition (ถ้ามี) + Steps to reproduce (ordered list) | panel(panelType: error) — คำอธิบาย actual + evidence screenshot ถ้ามี (อยู่ใน panel เดียวกัน) | panel(panelType: success) — คำอธิบาย expected ตาม design/case; ถ้ามี Figma ใส่เป็น paragraph แยก**ต่อท้ายนอก panel**: "**Figma:** [label](link)" |
```

Panel node เปล่าๆ: `{"type": "panel", "attrs": {"panelType": "error"}, "content": [...]}` (`"success"` สำหรับ expected) — ยิงผ่าน create API ได้ตรงๆ ไม่ต้องรอ user แก้ทีหลัง (confirm บน PDT-5196)

**Fields อื่นที่ต้องโชว์ในข้อความ draft**: Issue type: Bug, Priority, Label, Severity, Phase, Parent, Assignee (—), Affect versions (—)

### Ordered ที่ควรทำ
โชว์ draft → รอ "สร้างเลย" / feedback แก้ไข → ค่อยยิง create — ห้ามข้าม confirm แม้จะรู้สึกว่า pattern เดิมซ้ำๆ แล้วก็ตาม เพราะเป็น action ที่มองเห็นได้ทั้งทีม

---

## STEP 6 — สร้างจริง + set Details fields

```bash
POST {JIRA_BASE_URL}/rest/api/3/issue
{
  "fields": {
    "project": {"key": "PDT"},
    "issuetype": {"id": "10130"},
    "summary": "...",
    "description": { ...ADF... },
    "priority": {"name": "Medium"},
    "labels": ["Chat4.0"]
  }
}
```

`project` + `issuetype` + `summary` คือ field เดียวที่ Jira บังคับจริง (เช็คแล้วผ่าน `createmeta`) ที่เหลือ optional ในระดับ API แต่ทีมอยากให้กรอกครบเป็น process

จากนั้น `PUT /rest/api/3/issue/{key}` เพื่อ set Details fields (แยก call เพราะ custom field id ต้อง lookup):

| Field | Field ID | ค่าที่ใช้ (ตัวอย่างที่ confirm แล้ว) |
|---|---|---|
| Phase | `customfield_10794` | Dev=`11854` / **Staging=`11820`** / Production=`11821` |
| Severity | `customfield_10330` | S1=`10043` S2=`10044` **S3=`10045`(default)** S4=`10046` S5=`10047` |
| Parent | system `parent` | `{"key": "PDT-XXXX"}` |
| Affect versions | `customfield_11061` | ไม่ set |
| Assignee | system `assignee` | ไม่ set |

Payload:
```json
{"fields": {"customfield_10794": {"id": "11820"}, "customfield_10330": {"id": "10045"}, "parent": {"key": "PDT-3427"}}}
```

ปิดท้ายด้วยการส่งลิงก์ ticket ที่สร้างจริงกลับให้ผู้ใช้ (`{JIRA_BASE_URL}/browse/{key}`)

---

## Gotchas อื่นๆ

- **Evidence files — plain attachment confirmed working (PDT-5205)**: เมื่อมี local file path จริง (ผู้ใช้บอก path มา, หรือหาไฟล์เจอเองในเครื่อง) ยิง `curl -H "X-Atlassian-Token: no-check" -F "file=@<path>" POST {JIRA_BASE_URL}/rest/api/3/issue/{key}/attachments` ได้ตรงๆ — ใช้ได้กับทุกไฟล์ (ลองแล้วกับวิดีโอ .MP4 4.6MB สำเร็จ) กลายเป็น attachment ปกติที่เห็นใน Attachments panel ของ ticket ทันที
  - **Inline embed ใน panel — confirmed ว่าทำไม่ได้ด้วยวิธีนี้ (ทดสอบจริงบน PDT-5205, ไม่ใช่แค่เดา)**: เอา numeric id ที่ classic attachment endpoint คืนมา (เช่น `66733`) ไปใส่ใน ADF `media` node ตรงๆ → Jira ตอบ `400 ATTACHMENT_VALIDATION_ERROR` ทันที การ embed inline แบบที่ PDT-5194 มี (id เป็น media-service UUID) ต้องผ่าน Jira's media upload flow ซึ่งเป็นคนละระบบกับ REST API v3 attachment endpoint และต้องการ token/scope ที่ Basic Auth ธรรมดาไม่มี (เป็น flow ที่ปกติสงวนไว้ให้ Jira's own rich-text editor ใช้ภายใน) — **สรุป: อย่าพยายาม embed inline เอง ใช้ plain attachment แทนเสมอ** ยกเว้นผู้ใช้แนบเองผ่าน Jira UI (จะได้ media-service id มาแบบนั้น)
- **Testmo hosted image** (`/attachments/view/{id}`) ต้อง session cookie ดึงด้วย Bearer token ไม่ได้ (401), ไม่มี API route attachment download เลย ส่วนรูปที่ user paste ในแชทไม่มี local path ให้ upload อัตโนมัติ — ทางออก: ขอ path ไฟล์จาก user หรือให้แนบเองใน Jira UI หลังสร้าง
- **Python ADF builder**: helper ที่รับ `*content` (unpacked) ต้อง unpack list ตอนเรียกเสมอ (`cell(*items)` ไม่ใช่ `cell(items)`) ไม่งั้น Jira ตอบ 400 `"not valid Atlassian Document Format (ADF) content"` แบบไม่บอกว่า field ไหนพัง
- **Testmo `results` endpoint ไม่ auto-refresh totals**: cache หน้าที่ fetch ไว้ก่อนหน้าอาจไม่ครบถ้ามี test result ใหม่เข้ามาระหว่างเซสชัน เช็ค `total`/`last_page` ทุกครั้งก่อนสรุปว่าไม่เจอ

---

## หลักการสำคัญ

- **ห้ามข้าม duplicate-check gate (STEP 4)** ไม่ว่าจะรีบแค่ไหน — ราคาของการเปิดซ้ำแพงกว่าเวลาที่เสียไปเช็ค
- **ไม่เดา** เมื่อข้อมูลกำกวมหรือขาด (actual result, case ไม่ match, platform ใหม่ที่ยังไม่ confirm) — ถามเสมอ
- **ไม่ execute คำสั่งทำลายข้อมูล** ที่แปะมาเป็น context โดยไม่ confirm
- **ไม่ตัดสินเองว่า duplicate จริงไหม** — แค่ flag แล้วให้ผู้ใช้ตัดสิน
- **โชว์ draft เป็นข้อความเต็มเสมอก่อนสร้างจริง** — อย่าพึ่ง tool output
- **Severity default S3** เป็นข้อยกเว้นเดียวที่ auto-fill ได้ — Phase/Parent ห้าม default แม้จะซ้ำกับ ticket ก่อนหน้า
