# Posts — Analytics · QA pre-Solution draft (v2)

> **สถานะ:** ยังไม่มี `docs/solution/<feature>/` ใน console-next → feature อยู่ก่อน Goldfish 02 (Solutioning)
> เอกสารนี้คือ **ข้อเสนอของ QA สำหรับห้อง Solution** ไม่ใช่ spec — ID ของ F / ST / R / QA-R ในนี้เป็น **draft numbering**
> เมื่อห้องเขียน spec.md จริง ให้ map ใหม่ตาม R ของห้อง แล้วค่อยเขียน QA-R ใน test-factory (`pnpm solution:import` → `cases:scaffold`)
> Clarification id (PA-CL-nn) ต่อท้ายเสมอ ไม่ renumber · ข้อที่ตอบแล้วคงไว้พร้อมสถานะ
>
> Feature key ที่เสนอ: `admin-console/post-analytics` (แยกจาก `post-content`)
> v1 2026-10-01 (จาก dev brief + Figma) · **v2 2026-10-01 — เทียบกับ Notion "Posts — Analytics" ตัวจริง** · ผู้เขียน: QA (pidshapar) + Claude

## 0. แหล่งข้อมูล

| ป้าย | แหล่ง | อ่านเมื่อ | หมายเหตุ |
|---|---|---|---|
| **N** | Notion `products/admin-console/posts-analytics/Posts — Analytics 2475f8b2….html` (Status: Pitch Ready · Committed · PM Lindley) | 2026-10-01 | **source of truth** ของ product |
| **ML** | 03 Metric Library — Google Sheet `1CK5nBFQ…` | 2026-10-01 | อ่านได้ตรงแค่ 2 แถว (Total Posts Published, Total Users Reached) — ตรงกับ brief ทุกคำ · แถวที่เหลืออ้างผ่าน brief glossary + Figma tooltip |
| **B** | Dev brief artifact `L2PsEPTQUrVoS915uajqvS` (as of 2026-09-29) | 2026-10-01 | data / API / BigQuery · ข้อเสนอ default ของ 24 decision |
| **F** | Figma Componentization `⤷ Analytics` 1012:32193 · Generic `⤷ Analytics` 1378:32648 | 2026-10-01 | node id อ้างในทุกข้อ |
| **C&O** | Notion "Posts — Content & Operations" | 2026-10-01 | บริบท: entitlement, destination, post as brand, scheduled/pending/declined |
| **CN** | console-next `next`: `src/config/adminPermissions.ts`, `sitePermissions.ts:27`, `docs/solution/posts/spec.md` ST2 | 2026-10-01 | ไม่มี permission ของ analytics |

### สิ่งที่ v2 เปลี่ยนจาก v1
- **Persona คือ marketer / ทีม analytics** ไม่ใช่ทีม operations และ Notion ตัดสินแล้วว่า **Analytics แยกจาก Operations และไม่ทำ operational workflow ซ้ำ** → R1 ใหม่ และทำให้คำถามเรื่อง permission (PA-CL-20) หนักขึ้น
- **Notion ขัดกันเองเรื่องฐานของ insight**: Appendix A กับตัวอย่างใช้ engagement แต่ Product Decision บอกว่า 3 type นี้เน้น passive signal (reach/impression) และเลื่อน insight ที่อิง engagement ไปปี 2027 → Figma (ใช้ reach) อาจถูก ส่วน brief (สรุปว่าใช้ engagement) อาจผิด → **PA-CL-26 (high)**
- **"Posts published" กับ "Posts created" ใช้ปนกัน** (KPI ใช้ published · กราฟกับตาราง CP ใช้ created · cohort ใช้ creation date) → scheduled / pending / declined post นับเมื่อไหร่ → **PA-CL-28 (high)**
- **N/A เพราะ engagement ไม่ได้เปิดใช้** เป็น requirement ของ Notion แต่ brief ทำได้แค่ N/A เมื่อไม่มีข้อมูลเลย → PM ต้องยอมรับว่าตัด scope → **PA-CL-29 (high)**
- ตอบแล้ว 2 ข้อ (CL-08 soft-deleted · CL-18 search) และตอบบางส่วน 6 ข้อ · เพิ่มใหม่ 12 ข้อ (CL-26…37)

---

## 1. Requirement analysis (BA + QA)

### 1.1 Who / What / Why

| | |
|---|---|
| **Who** | **Marketer / ทีม analytics** (N A2: ลูกค้า enterprise อย่าง True, Airbnb, Ulta แยกทีม operations กับทีม analysis) · ลูกค้าเล็กอาจเป็นคนเดียวกันแต่ job ต่างกัน · Console admin ที่ถูกจำกัด community (ข้อมูลถูก narrow เงียบ ๆ — B §04) · ทางอ้อม: CS |
| **What** | ใน Analytics มี 2 หน้า: **Overview** = channel performance (Key insights ≤3, Key metrics 7 ตัว + เทียบช่วงก่อน, Performance over time, Top performing posts, Export) และ **Content performance** = content performance (By post type, By destination, All posts, Top creators, export ทีละ widget + export ทั้งหน้า) |
| **Why** | ลูกค้า (Ulta, David Lloyd, XM) มองไม่เห็นว่า content บน social.plus ทำผลงานยังไง · post ถูกกระจายไปหลาย destination ตาม componentization · ตั้งใจให้เป็นทางนำไปสู่ Audience Intelligence (PLG: Show the value → Identify the audience → Take action) |

### 1.2 Three-layer check

| Layer | สิ่งที่มี | ช่องว่าง |
|---|---|---|
| Business goal | ตอบ feedback ของลูกค้า + PLG ไป Audience Intelligence (paid module) | **ไม่มี success metric ของ analytics** · GTM summary ยังว่าง · ไม่รู้ว่าเป็น Core หรือ paid → ตัดสินเรื่อง entitlement ไม่ได้ (PA-CL-21) |
| User need | 2 คำถาม: "post ในฐานะ channel ทำผลงานยังไง" และ "post ไหน / อะไรเป็นตัวขับ" | Explore Further ถูกตัด และ insight ไม่มี navigation → ทางจาก insight ไปหาหลักฐาน (A.5 Insight → Evidence → Investigation) ต้องให้ผู้ใช้หาเอง |
| System behaviour | Metric Library + brief ละเอียด | state ของ UI (N/A, locked, partial, last refreshed, insight empty) ยังวาดไม่ครบ · Notion กำหนด N/A ตาม engagement availability ในอดีต แต่ data ยังไม่มี signal นี้ |

### 1.3 ข้อสังเกตหลัก (เรียงตามความสำคัญ)

1. **Notion ขัดกันเองเรื่องฐานของ insight** (engagement vs passive) — ทั้ง copy, ตรรกะ และ case ของ insight ขึ้นอยู่กับข้อนี้ (PA-CL-26)
2. **N/A จะเป็นภาพปกติ** — 133/202 network ไม่ส่ง view event (B §12) · staging ของ QA อาจไม่มี view event เลย (§6)
3. **ข้อมูลรีเฟรชวันละครั้ง (D-1) แต่ Figma มี preset "Today"** (PA-CL-01) · Notion สั่งให้แสดง "last refreshed" แต่ยังไม่มีแบบ
4. **Notion กำหนด N/A เมื่อ engagement ไม่ได้เปิด และให้ยึดสิ่งที่เกิดขึ้นจริงในอดีต** — MVP ของ brief ทำไม่ได้ (PA-CL-29)
5. **วันที่เดียวกันแต่ความหมายต่างกันระหว่างสองหน้า** (activity window vs creation cohort) → ตัวเลข comments สองหน้าไม่เท่ากันโดยถูกต้อง · ควรมีป้ายบอก
6. **Destination จริงยังไม่มีข้อมูล** — Notion ต้องการ "post ที่มีหลาย destination นับถ้าตรงสักอัน" แต่ proxy `target_type` มีค่าเดียวต่อ post (PA-CL-14)
7. **ER คนละสูตรกับ dashboard** (~15.8% vs ~2.5%) → ต้อง brief CS

---

## 2. Draft flows (F)

- **F1 Marketer เปิด Analytics** — Posts → Analytics → Overview พร้อม date range เริ่มต้น *(ไม่มีที่ไหนระบุค่าเริ่มต้น — PA-CL-02)* — R2, R18
  - Alt 1a ไม่มีสิทธิ์ → R36 · Alt 1b ไม่ entitled → R37 · Alt 1c network ไม่มี view event → R16
- **F2 กำหนด scope ของ Overview** — date range (activity period), destination, creator role (เลือกได้หลายอัน) → ทุก widget ใน Overview รวม insight เปลี่ยนตาม — R2, R4, R5, R7, R26
  - Alt 2a scope ว่าง → "No results found" (F 1513:112191) · Alt 2b Clear all
- **F3 เปลี่ยน metric ของกราฟ** — 1 ใน 7 metric (default Posts created) → interval ปรับตาม range — R20
- **F4 ดู Top performing posts** — Top X ตาม activity ใน range → เปลี่ยน sort (6 metric) → เลือก post → Post Detail (selected period / lifetime) — R21, R22
- **F5 อ่าน Key insights** — 0–3 การ์ด หรือ empty state · ไม่มี navigation — R23–R29
- **F6 Export Overview** — 2 dataset ตาม filter ปัจจุบัน — R30
- **F7 Content performance** — creation-date cohort + destination + role + post type → By post type (sort, export, view all posts), By destination (top X, view all, sort, export), All posts (search, sort, export, detail), Top creators (4 sort, export) · export ทั้งหน้า — R3, R6, R31–R35

## 3. Draft rules (R)

ป้าย: **N** Notion · **ML** Metric Library · **B** brief · **F** Figma node · **C&O** · **CN** console-next · **GAP** ยังไม่ตัดสิน → §5

### ขอบเขตและ filter
- **R1** [product] Analytics is for understanding performance; it offers no operational action (edit, delete, feature, approve, flag). It may link to operations where useful. *(N A2, Product Decision "Separate Analytics from Operations")*
- **R2** [product] On Overview the date range is the activity period: every widget counts activity inside it, from posts of any age. *(N Overview §1, §4)*
- **R3** [product] On Content performance the date range is the post creation date and defines the cohort; each post's metrics are lifetime, from creation until T. *(N CP §1)* — **GAP**: T = latest data day (D-1)? "creation" vs "published" for scheduled and pending posts (PA-CL-28, PA-CL-34)
- **R4** [product] Destination filter includes posts associated with the selected destination; a post with several destinations is included when any of them matches. *(N Overview §1)* MVP proxy: `target_type` community / user feed. *(B)* — **GAP** (PA-CL-14)
- **R5** [product] Creator role filter takes one or more of Admin, Moderator, User and keeps posts whose creator has that role. *(N)* Buckets come from built-in network roles; custom and community roles count as User; the role is frozen when the row loads. *(B §07, decided 2026-09-29)* — **GAP**: brand-profile posts (PA-CL-13)
- **R6** [product] Content performance also filters by post type: text, image, video, audio, file, mixed. *(N CP §1)* One type per parent post: poll / live stream win over attachments; one media kind → that type; several → mixed. *(B §06)* — **GAP**: poll, live stream, clip, custom (PA-CL-10)
- **R7** [product] Every widget on a page reflects that page's filters. *(N)*

### Metrics
- **R8** [product] Posts published counts posts whose published timestamp is in the period, including posts soft-deleted later, so history never changes retroactively. A post with N attachments counts as 1. *(ML verbatim, B §06)* — **GAP**: Notion also says "Posts created" (PA-CL-28)
- **R9** [product] Reach counts unique users who viewed at least one post in the period, whatever the post's creation date, soft-deleted posts included. A range's reach is distinct over the range, never a sum of buckets. *(ML verbatim, B)*
- **R10** [product] Impressions count post views in the period; repeat views by the same person count. *(F tooltip 1247:5710)* [system] A duplicate `impression_id` counts once; story / ad / product views are excluded. *(B §12)*
- **R11** [product] Comments count comments made on posts in the period, whatever the post's creation date. *(F 1415:147287)* — **GAP** replies (PA-CL-05)
- **R12** [product] Reactions count reactions made on posts in the period; a reaction on a child post rolls up to its parent. *(F 1415:147293, B §06)* — **GAP** reactions on comments (PA-CL-05)
- **R13** [product] Engaged users count unique users with ≥1 reaction or comment on a post in the period, once across all posts. *(ML via B, F 1415:147305)*
- **R14** [product] Engagement rate = engaged users ÷ people reached on posts where comments or reactions are enabled × 100. *(ML via B, F 1415:147311)* — **GAP** precision, >100% (PA-CL-06)
- **R15** [product] Where applicable, each KPI compares with the previous equivalent period: +x% / −x% / no change "vs. <range>"; with no baseline it reads "N/A · No baseline to compare". *(N §3, F 1412:81524)* — **GAP** ER delta unit (PA-CL-07)
- **R16** [product] A metric with insufficient data shows an unavailable state, not a misleading value. Comments, reactions, engaged users and ER show unavailable — not 0 — when engagement was not available for the posts in scope at the time of activity; 0 only when engagement was available and nothing happened. Historical existence wins over current configuration. *(N §3, Product Decision "historical data existence")* MVP: unavailable only when the network has no data. *(B)* — **GAP** (PA-CL-29)
- **R17** [product] When the network is not entitled to reactions or comments, that card is Locked: "Unlock reactions to boost engagement · View reactions". *(F 1412:81524 — not in Notion)* — **GAP** (PA-CL-09)

### เวลาและความสดของข้อมูล
- **R18** [product] Data is available from the beginning of 2025 and refreshed daily; the page states when the data was last refreshed; an unavailable period reads unavailable, not zero. *(N Product Decision "available historical data")* [system] Days are UTC; data is D-1. *(B)* — **GAP** "Today" (PA-CL-01) · not drawn
- **R19** [system] A range is at most 365 days and starts no earlier than 2025-01-01. *(B §09)* — **GAP** default, presets, limits (PA-CL-02, 03, 04)

### Performance over time
- **R20** [product] One chart shows one selected metric — Posts created (default), Reach, Impressions, Comments, Reactions, Engaged users, ER — per time interval, by the activity timestamp, with the interval adapting to the range. *(N §4)* Interval: ≤30 days → day; 31–90 → week; >90 → month. *(F sticky 1331:73532)* — **GAP** week start, partial bucket (B proposals)

### Top performing posts
- **R21** [product] Top performing posts lists the top X posts by activity in the range, whatever their publish date; sort by reach, impressions, comments, reactions, engaged users or ER; the numbers are in-period, not lifetime; all filters apply. *(N §5)* Default sort Engaged users, X = 10. *(F 1452:105407)* — **GAP** X (PA-CL-35), ties (PA-CL-11), deleted / pre-2025 rows (PA-CL-12)
- **R22** [product] Selecting a post opens Post Detail with selected-period and lifetime performance. *(N §5, F 1394:129120)*

### Key insights
- **R23** [product] Overview shows up to 3 insights from the fixed types Growth/Decline, Top content and Content mix; fewer when fewer are eligible; an empty state when none; never a generic filler. Card position is not tied to a type. *(N §2, A.1, A.7, Product Decision)*
- **R24** [product] An insight is not shown when the filters already determine it, data is insufficient, the metric cannot be calculated reliably, it duplicates another, its dimension is collapsed by a filter, or it might discourage the customer. *(N A.2)* Thresholds ≥10 posts, |Δ| ≥10%, gap ≥10 pts. *(B proposal)* — **GAP** (PA-CL-16)
- **R25** [product] Selected insights cover distinct dimensions (content, distribution, engagement, momentum). *(N A.3)*
- **R26** [product] Insight wording reflects the filter scope, e.g. "…among Admin-created posts". *(N A.4)*
- **R27** [product] Insight wording names the metric or dimension, avoids "best" / "top-performing" and evaluative words, uses specific values, and does not imply causation. *(N A.6)*
- **R28** [product] Insight cards have no navigation. *(N Product Decision "Remove navigation")* — **GAP** story §2 and examples still show links (PA-CL-27)
- **R29** [product] The metric behind each insight type — **GAP** (PA-CL-26)

### Export
- **R30** [product] Overview export respects date, destination and creator role and holds 2 datasets: (1) performance over time for all 7 metrics whatever the chart shows; (2) one row per qualifying post — every post with activity in scope, not only the top X — with in-period metrics and the same attributes as Top performing posts. *(N §6)* Period-based export and the 1P Data API are both in scope; period-based first if capacity is short. *(N Scope Decisions)* — **GAP** Figma "x of 4 widgets", "All available data" (PA-CL-19)
- **R31** [product] On Content performance each widget exports its own rows with the current filters (All posts also with the keyword search), and the page offers an export of all its data. *(N Scope, CP §2–§5)* — **GAP** (PA-CL-32)

### Content performance widgets
- **R32** [product] Performance by post type is a table with posts created, reach, impressions, comments, reactions, engaged users and ER, sortable by any column, exportable, with a way to view the posts behind each type. *(N CP §2)* — **GAP** view-all-posts behaviour (PA-CL-33)
- **R33** [product] Destination performance is a table with one row per destination in scope and the same columns, sortable, top X by default with View all destinations; when one destination is filtered it shows as a single row; lifetime metrics. *(N CP §3)* Ranked by engaged users, 10 per page. *(F 1457:241015)*
- **R34** [product] All posts lists the cohort with thumbnail, title & content, post type, creator & role, destination, creation date and the 6 performance metrics, lifetime; sortable by the metrics; keyword search on title / content; selecting a post opens Post Detail with its full content. Comparison is out of MVP. *(N CP §4, Scope Decisions)* 10 per page. *(F 1452:112240)*
- **R35** [product] Top creators ranks creators of the cohort by Most posts (default), Most comments, Most reactions or Average ER per post (Σ post ER ÷ qualifying posts) and shows name, userId, avatar, role, posts, reach, impressions, reactions, comments and average ER, lifetime. *(N CP §5, ML via B)* Top 10. *(F)* — **GAP** typo (PA-CL-31), aggregate reach (PA-CL-30), N/A posts (PA-CL-17)

### สิทธิ์และอื่น ๆ
- **R36** [product] Access — **GAP** (PA-CL-20). Today `/components/posts` needs `VIEW_POST_AND_COMMENT_MANAGEMENT` *(CN sitePermissions.ts:27)*; a community-scoped admin is narrowed to their communities *(B §04)*
- **R37** [product] Entitlement — **GAP** (PA-CL-21)
- **R38** [system] Activity on posts published before 2025 counts in KPIs but those posts have no row in per-post tables. *(B §12)* — **GAP** label (PA-CL-12)
- **R39** [system] Responses are cached 1 hour per region, network, path and query. *(B §09)*

## 4. Draft states (ST) — S-CAT walk

### Surface: Analytics → Overview (F 1247:5639)
- ST1 [domain] Overview selected; Content performance beside it
- ST2 [system] loading, first paint — per-widget skeleton (F 1412:81524, 1531:162204) [S-CAT §1]
- ST3 [system] loading, refresh after a filter change — **not drawn** [S-CAT §2]
- ST4 [system] empty, nothing yet — network has no posts — **not drawn** [S-CAT §3]
- ST5 [system] empty, filtered to nothing — "No results found / Try adjusting…" (F 1513:112191) [S-CAT §4]
- ST6 [domain] metric unavailable — "N/A" on card; chart "No data available / Data activity is unavailable for the selected scope." (F 1412:76731)
- ST7 [domain] engagement not available for posts in scope (R16) — **not drawn; differs from ST6?**
- ST8 [domain] metric Locked — reactions / comments not entitled (F 1412:81524)
- ST9 [domain] no baseline — "No baseline to compare"
- ST10 [domain] Key insights empty — required by N A.7 — **not drawn**
- ST11 [domain] 1 or 2 insight cards — F pills "show 1 card / show 3 cards" (1567:234960) — 2-card layout not drawn
- ST12 [domain] partial bucket marker — **not drawn**
- ST13 [domain] gap before the network's first view event — **not drawn**
- ST14 [domain] "last refreshed" / UTC label — required by N — **not drawn**
- ST15 [system] error, network unreachable — Generic content fallback [S-CAT §6]
- ST16 [system] error, API error (400 / 403 / 503 / 504 after 60 s) — per widget or whole page? **not drawn** [S-CAT §7]
- ST17 [system] error after export — error toast [S-CAT §8]
- ST18 [system] denied, no role permission — see R36 [S-CAT §9]
- ST19 [system] permission revoked mid-session — 403 state [S-CAT §10]
- ST20 [system] not entitled — see R37 [S-CAT §11]
- ST21 [n/a] feature switched off via API — no switch for analytics known [S-CAT §12]
- ST22 [n/a] quota reached — no quota on reads [S-CAT §13]
- ST23 [domain] a post in Top posts deleted after load → Post Detail? [S-CAT §14]
- ST24 [system] slot reservation saturated → 504 — **not drawn** [S-CAT §15]
- ST25 [n/a] offline — console is online-only [S-CAT §16]
- ST26 [system] no console account — access-required [S-CAT §17]

### Surface: Analytics → Content performance (F 1394:130286)
- ST27 [domain] cohort empty — no post created in range — **not drawn**
- ST28 [system] partial, page n of m — "1-10 of 10 items", 10/page [S-CAT §5]
- ST29 [domain] All posts search returns nothing
- ST30 [domain] one destination filtered → By destination shows a single row (R33)
- ST31 [domain] one post type filtered → By post type shows a single row (N "Why lists instead of a chart")
- (ST2–ST26 apply the same way)

### Surface: Post Detail (F 1247:5671 SheetOverlay, 1394:129120)
- ST32 [domain] Selected period · ST33 [domain] Lifetime · Since published · ST34 [system] loading on toggle · ST35 [domain] post deleted since · ST36 [domain] post published before 2025 (F sample "Created 12 Jun 2024") — lifetime incomplete

### Surface: Export (F 1548:177712)
- ST37 [domain] option chosen, 0 widgets selected · ST38 [system] export in progress · ST39 [system] export failed [S-CAT §8] · ST40 [domain] large export (no row cap)

---

## 5. Clarifications

Format: observation → consequence → question · sev high = blocks a case's expected result · status: open / partly answered / answered

### High — ถามก่อน

| ID | Rule | Observation → consequence | Question (to the room) | Owner | Status |
|---|---|---|---|---|---|
| PA-CL-26 | R29 | Appendix A and the story examples define Top content, Content mix and Growth on **engagement**; the Product Decision says the 3 types favour **passive consumption / exposure** signals, and Scope Decisions defer engagement-based insights to 2027; Figma uses reach; the brief resolved to engagement → copy, logic and cases all hang on this | For each of Growth/Decline, Top content and Content mix: which metric — engagement, reach or impressions? | PM | new |
| PA-CL-28 | R3, R8, R20 | KPI says "Posts published" (published timestamp, ML); chart default and CP tables say "Posts created"; CP cohort uses "post creation date" → a scheduled post created 30 Aug and published 2 Sep, a pending post approved days later, a declined post never published | One timestamp for all three — created or published? Are pending, declined and not-yet-published scheduled posts counted anywhere? | PM | new |
| PA-CL-29 | R16 | Notion: unavailable (not 0) when engagement was not enabled, judged historically; MVP can only say unavailable when the network has no data at all → a destination with comments off shows 0, which Notion forbids | Accept the MVP gap (and say so in GTM), or block until core records engagement availability? | PM + Eng | new |
| PA-CL-01 | R18 | Data refreshes daily (D-1) but Figma offers "Today" → Today is always empty | Drop "Today", or show it with a "data lands tomorrow" state? | PM + Design | open |
| PA-CL-02 | R19 | Default range and preset end are undefined; Figma shows "31 Aug – 30 Sep 2026" = 31 days ending today → crosses the 30-day day/week boundary | Default range? Does "Last 30 days" end today or yesterday, inclusive? | PM | open |
| PA-CL-05 | R11, R12 | Replies and reactions on comments are unspecified; the dashboard count includes reactions on comments | Do Comments include replies? Do Reactions exclude reactions on comments? | PM | open |
| PA-CL-09 | R17, R16 | Figma has a Locked card (Notion silent); only reactions bought, comments not | What do Engaged users and ER show — partial value, unavailable, or Locked? | PM + Design | open |
| PA-CL-14 | R4 | Notion: a post with several destinations matches if any does; the proxy `target_type` has one value per post (community 71 %, user 27 %, content 2 %); Figma draws real placements | Accept community / user feed for MVP? Label for `content`? Single or multi select? | PM + Design | open |
| PA-CL-19 | R30 | Notion: Overview export = 2 datasets; Figma: pick widgets "x of 4" and an "All available data (1P Data API, ignores filters)" option | Is widget picking in? Is the 1P option in MVP? One file or two? | PM + Design | partly answered (datasets, scope by N) |

### Medium

| ID | Rule | Observation → consequence | Question | Owner | Status |
|---|---|---|---|---|---|
| PA-CL-03 | R19 | Two preset lists: Posts page (Today, 7 d, 2 w, 3 w, 30 d — F 1432:87588) vs Generic (7, 14, 30, 90 d, "Showing all time" — F 1548:177057); with 30-day presets, week / month intervals need a custom range | Which list ships? "All time" (since 1 Jan 2025)? | PM + Design | open |
| PA-CL-04 | R19 | Custom range: future dates, end before start, >365 days, before 2025-01-01 | Disable, clamp or error for each? | Design | open |
| PA-CL-06 | R14 | Engaged users can exceed reach (engage without a recorded view) → ER >100 % | Cap at 100 %? Display precision? | PM + Eng | open |
| PA-CL-07 | R15 | ER 4.0 % → 5.0 % is +1 pt or +25 % | ER delta unit? Rounding of deltas? | PM | open |
| PA-CL-10 | R6 | Notion types: text, image, video, audio, file, mixed; data also has poll, live stream, clip, custom; Figma uses "Photo" and "Image" | Where do poll, live stream, clip, custom go? Label Image or Photo? | PM + Design | partly answered (6 types by N) |
| PA-CL-12 | R21, R38 | Deleted and pre-2025 posts can rank by activity | Show, label or exclude? What does Post Detail show for them? | PM + Design | open |
| PA-CL-13 | R5 | Figma Top creators shows "Brand user"; Notion has 3 roles; C&O lets admins post as a brand profile | Which bucket is a brand-profile post? Remove "Brand user" from Figma? | PM | partly answered (3 roles by N) |
| PA-CL-15 | R23 | Notion requires an empty state; Figma has none and no 2-card layout | Design the empty state and the 1- / 2-card layouts | Design | partly answered |
| PA-CL-16 | R24 | Notion: "exclude insights that might discourage" | Is a Decline ever shown? Thresholds ≥10 posts / ≥10 % / ≥10 pts accepted? | PM | partly answered |
| PA-CL-17 | R35 | Average ER per post when some posts have ER unavailable; deleted creator | Exclude unavailable posts from the average? How is a deleted creator shown? | PM | open |
| PA-CL-20 | R36 | No analytics permission exists; Notion targets a separate analytics team, who may hold no post-management grant; a community-scoped admin is narrowed silently | New VIEW_ANALYTICS-style grant, or reuse post VIEW? Tell a scoped admin their numbers are narrowed? | PM + Eng | open — stronger after N |
| PA-CL-21 | R37 | Notion silent on entitlement; GTM plan type empty; C&O keeps read access for previously-entitled customers | Is Analytics part of the Posts entitlement or a paid add-on? Locked look? | PM | open |
| PA-CL-22 | R16 | Network starts sending view events mid-range | Gap before the first event day? KPI partial or unavailable? | PM + Design | open |
| PA-CL-25 | R7 | Overview and CP have different filter sets and date meanings | Do destination / role persist across the two pages and in the URL? Does the date carry over despite meaning something else? | Design | open |
| PA-CL-27 | R28 | Story §2 says "provide a clear path to the relevant deeper analysis" and the examples show "View … →"; A.5 wants evidence investigable; the Product Decision removes navigation | Confirm: no link on any card, and A.5 is met by Content performance existing | PM | new |
| PA-CL-30 | R32, R33, R35 | Reach is unique users; a creator / destination / type row could be distinct users across its posts or a sum of per-post reach → rows never add up to total reach either way | Row reach = distinct users or sum? Tooltip that rows do not add up? | PM + Eng | new |
| PA-CL-32 | R31 | "Export all data on Content performance page" plus per-widget exports; format undefined | One file with 4 sheets, a zip, or 4 CSVs? Does page export include the All posts search? | PM + Design | new |
| PA-CL-35 | R21, R33 | Top X is TBD in Notion; Figma 10 posts, 10 destinations per page; brief proposes 5 destinations | X for posts and for destinations? | PM + Design | new |

### Low

| ID | Rule | Question | Owner | Status |
|---|---|---|---|---|
| PA-CL-11 | R21 | Tie-break order; fewer than X posts → show fewer rows? | PM | open |
| PA-CL-23 | R20 | Tooltip that weekly reach does not add up to total reach — accepted? | Design | open |
| PA-CL-24 | R39 | 1 h cache + D-1: a just-deleted post still ranks — acceptable? | Eng | open |
| PA-CL-31 | R35 | Notion swaps the definitions: "Most Comments — ranks by reactions", "Most Reactions — ranks by comments". Fix to the obvious meaning? | PM | new |
| PA-CL-33 | R32 | "View all posts" for a type → All posts filtered by that type, in page? | Design | new |
| PA-CL-34 | R3, R22 | Lifetime "until T" — T = latest data day? Lifetime of a pre-2025 post starts 1 Jan 2025? | PM | new |
| PA-CL-36 | R34 | Post Detail "full content": media, polls, a deleted post's content? | Design | new |
| PA-CL-37 | R1 | Does Post Detail offer a link to the post in Content (operations), or nothing? | PM + Design | new |

### ตอบแล้วโดย Notion / Metric Library

| ID | คำตอบ | ผลต่อ build |
|---|---|---|
| PA-CL-08 | ML: Posts published และ Reach **รวม** soft-deleted post เพื่อไม่ให้ตัวเลขย้อนหลังเปลี่ยน | rule ชัดแล้ว · serving ปัจจุบันลบ post ภายใน 85 วัน (B) → ถ้าไม่เก็บ `is_deleted` จะเป็น **defect** · Eng ยืนยันว่าทำได้ |
| PA-CL-18 | N CP §4: keyword search ค้นใน title / content | ปิด |

**Figma inconsistencies (สำหรับ Design):** "Engaged user" vs "Engaged users" · "Posts published" / "Published posts" / Notion "Posts created" · หัวตาราง Top posts ใน 1247:5639 ไม่มีคอลัมน์ Reach และ ER แต่ 1378:50800 มี · tooltip ของ Top posts บอกว่า "cohort" แต่ ranking ใช้ activity (N §5) · Generic filter มี Target types / Reaction names (เป็นของ analytics อื่น ไม่เกี่ยว) · ตัวอย่าง insight "Video Posts account for more reach…" ขัดกับ A.6 (ต้องใช้ค่าเฉพาะ ไม่ใช้คำกว้าง ๆ)

## 6. Testability flags (สำหรับ Sketch PR)

1. **Test data คือต้นทุนหลัก** — ทุกตัวเลขมาจาก BigQuery แบบ D-1 · ต้องมี staging network ที่ (a) ส่ง view event จริง (b) มี post ทุก type รวม mixed / poll / live stream (c) มี creator ครบ 3 role + brand profile (d) มี post ก่อน 2025 (e) มี scheduled / pending / declined post (PA-CL-28) — และต้องรอ 1 วันหลังสร้าง data ทุกครั้ง → **ขอ Eng: fixture network + วิธี seed BigQuery staging หรือ snapshot คงที่**
2. **Oracle ของตัวเลข** — tester คำนวณ reach / engaged users ด้วยมือไม่ได้ → ต้องมี SQL oracle query ต่อ metric (brief มี SQL แล้ว) · case ด้าน metric จึงควร automate ระดับ API (`/v1/content/*`) เทียบ SQL
3. **Network ที่ไม่มี view event** — ต้องมีอีก network หนึ่ง (เป็นกรณีที่พบบ่อยที่สุด)
4. **Engagement availability ในอดีต (R16)** — ต้องมี destination ที่ปิด comments ไว้ช่วงหนึ่งแล้วเปิด · ถ้า MVP ไม่ทำ case นี้ต้องอยู่ใน `out_of_scope[]`
5. **Entitlement** — ต้องสลับ reactions / comments / posts entitlement บน staging ได้ (ห้ามเปลี่ยน network setting จริงโดยไม่ถาม)
6. **เวลา** — partial bucket, D-1, "Today" → mock clock ใน UI test หรือเป็น manual
7. **Insight wording (R26, R27)** — ตรวจด้วย i18n template ได้ แต่การตัดสินว่า "discouraging" หรือ "implies causation" เป็นงานของคน → manual review
8. **UI ล้วน** (layout, สีกราฟ, tooltip copy) → manual

## 7. QA test cases — ร่างล่วงหน้า

ID draft `QA-R<n>-<k>` ผูก R ใน §3 · type: S = success · B = boundary · N = negative · St = state · ⛔ = รอ clarification · layer: API = เทียบ SQL oracle ที่ Go API, UI = console, Rev = human review

| ID | Type | Given | When | Then | Layer |
|---|---|---|---|---|---|
| QA-R1-1 | N | a post in Top performing posts | marketer opens its Post Detail | no edit, delete, feature or approve action is offered | UI |
| QA-R2-1 | S | a post published in August with activity only in September | marketer selects September on Overview | its activity counts in every September widget and it can rank in Top posts | API |
| QA-R3-1 | S | the same August post | marketer selects September on Content performance | it is not in the cohort | API |
| QA-R3-2 | S | a post published 5 Sep with activity in October; range 1–15 Sep | marketer opens Content performance | it is included and its metrics include October activity | API |
| QA-R3-3 | ⛔ | a scheduled post created 30 Aug, published 2 Sep; range Sep | marketer opens Content performance | in or out? ⛔ CL-28 | API |
| QA-R4-1 | S | community posts and user-feed posts | marketer filters destination = User feed | every Overview widget counts only user-feed posts | API |
| QA-R4-2 | ⛔ | a post associated with destinations A and B | marketer filters B | it is included ⛔ CL-14 (proxy cannot) | API |
| QA-R5-1 | S | posts by a global-admin, a network moderator, a community moderator and a plain user | marketer selects Moderator | only the network moderator's post remains | API |
| QA-R5-2 | S | same data | marketer selects User | the plain user's and the community moderator's posts remain | API |
| QA-R5-3 | S | same data | marketer selects Admin and Moderator together | the admin's and the network moderator's posts remain | API |
| QA-R5-4 | ⛔ | an admin posts as a brand profile | marketer selects Admin | included? ⛔ CL-13 | API |
| QA-R6-1 | S | posts: text, 5 images, 1 video, image + video | marketer opens By post type | rows text 1, image 1, video 1, mixed 1 | API |
| QA-R6-2 | S | — | marketer filters post type = Video | every Content performance widget holds video posts only | UI |
| QA-R6-3 | ⛔ | a poll with images | marketer opens By post type | which type? ⛔ CL-10 | API |
| QA-R7-1 | S | filters set on Overview | marketer clicks Clear all | every widget returns to the default scope | UI |
| QA-R8-1 | S | 3 posts published in range: text, 5-image, image + file | marketer opens Overview | Posts published = 3 | API |
| QA-R8-2 | B | a post published 23:59:59 UTC on the last day, another 00:00:00 UTC the next day | marketer opens Overview | only the first counts | API |
| QA-R8-3 | S | a post published in range, soft-deleted later | marketer reopens the same range | Posts published is unchanged | API |
| QA-R9-1 | S | user A views post X 5 times and post Y once | marketer opens Overview | Reach = 1, Impressions = 6 | API |
| QA-R9-2 | B | 14-day range, two weekly buckets each with reach 10 from the same 10 users | marketer opens Overview | KPI Reach = 10, not 20 | API |
| QA-R9-3 | S | a post viewed in range, soft-deleted later | marketer reopens the range | its viewers still count in Reach | API |
| QA-R10-1 | N | a story and an ad viewed in range | marketer opens Overview | Impressions excludes them | API |
| QA-R10-2 | N | the same impression_id stored twice | marketer opens Overview | it counts once | API |
| QA-R11-1 | S | 2 comments in range on a post published before it | marketer opens Overview | Total comments = 2 | API |
| QA-R11-2 | ⛔ | 1 comment + 1 reply in range | marketer opens Overview | Total comments = ? ⛔ CL-05 | API |
| QA-R12-1 | S | a reaction on the 3rd image of a 5-image post | marketer opens Overview | Total reactions counts it once, under the parent | API |
| QA-R12-2 | ⛔ | a reaction on a comment | marketer opens Overview | excluded? ⛔ CL-05 | API |
| QA-R13-1 | S | user A reacts on 3 posts and comments on 2 | marketer opens Overview | Engaged users = 1 | API |
| QA-R14-1 | S | 40 viewers, 8 of them engage | marketer opens Overview | ER = 20.0 % | API |
| QA-R14-2 | S | 1 of the 8 adds 30 more reactions | marketer opens Overview | ER stays 20.0 % | API |
| QA-R14-3 | N | reach = 0 | marketer opens Overview | ER shows unavailable, not 0 % and not ∞ | UI |
| QA-R14-4 | ⛔ | engaged users exceed reach | marketer opens Overview | capped or shown? ⛔ CL-06 | API |
| QA-R15-1 | S | Last 7 days 57 posts, previous 7 days 52 | marketer opens Overview | card reads "+10% vs. last 7 days", increasing style | UI |
| QA-R15-2 | St | previous period has 0 posts | marketer opens Overview | "N/A · No baseline to compare" | UI |
| QA-R15-3 | B | range starts 2025-01-01 | marketer opens Overview | every delta reads "No baseline to compare" | UI |
| QA-R15-4 | S | equal values in both periods | marketer opens Overview | no-change style | UI |
| QA-R16-1 | St | network sends no view events | marketer opens Overview | Reach, Impressions, ER unavailable; Posts, Comments, Reactions, Engaged users show values | UI |
| QA-R16-2 | St | view events exist, engagement on, nobody engaged | marketer opens Overview | Comments, Reactions, Engaged users = 0; ER = 0 % | UI |
| QA-R16-3 | ⛔ | comments disabled on the only destination in scope during the range | marketer opens Overview | Total comments unavailable, not 0 ⛔ CL-29 | UI |
| QA-R16-4 | ⛔ | comments were enabled during the range and are disabled today | marketer opens that range | Total comments shows the historical count ⛔ CL-29 | API |
| QA-R16-5 | St | network has no view events | marketer selects Reach in the chart | "No data available / Data activity is unavailable for the selected scope." | UI |
| QA-R17-1 | St | network not entitled to reactions | marketer opens Overview | Total reactions is Locked with "Unlock reactions…" and View reactions | UI |
| QA-R17-2 | ⛔ | reactions bought, comments not | marketer opens Overview | Engaged users / ER = ? ⛔ CL-09 | UI |
| QA-R18-1 | S | data loaded through yesterday | marketer opens Overview | the page states it was last refreshed yesterday | UI |
| QA-R18-2 | ⛔ | — | marketer selects Today | ? ⛔ CL-01 | UI |
| QA-R19-1 | B | — | marketer picks exactly 365 days | it applies | UI |
| QA-R19-2 | N | — | marketer picks 366 days | it cannot apply ⛔ CL-04 (how) | UI |
| QA-R19-3 | N | — | marketer opens the calendar | dates before 1 Jan 2025 cannot be picked | UI |
| QA-R19-4 | S | marketer in UTC+7 | marketer picks 1–7 Sep | numbers cover 1 Sep 00:00 – 7 Sep 23:59 UTC; the picker says UTC | API + UI |
| QA-R20-1 | S | — | marketer opens Overview | the chart shows Posts created by default | UI |
| QA-R20-2 | S | — | marketer switches through the 7 metrics | the chart redraws with per-interval values, not cumulative | UI |
| QA-R20-3 | B | — | marketer picks 30 days / 31 days | days / weeks | UI |
| QA-R20-4 | B | — | marketer picks 90 days / 91 days | weeks / months | UI |
| QA-R20-5 | St | range ends mid-week | weekly chart | the last bucket is marked partial | UI |
| QA-R21-1 | S | 12 posts with activity in range | marketer opens Overview | Top performing posts lists 10, by engaged users desc ⛔ CL-35 (X) | API + UI |
| QA-R21-2 | S | — | marketer sorts by each of reach, impressions, comments, reactions, engaged users, ER | order follows that metric | UI |
| QA-R21-3 | S | a post with 100 lifetime comments, 5 in range | marketer opens Top posts | its Comments cell reads 5 | API |
| QA-R21-4 | B | 3 posts with activity in range | marketer opens Overview | 3 rows ⛔ CL-11 | UI |
| QA-R22-1 | S | — | marketer selects a Top post and toggles Lifetime | values run from publish date and read "Since published" | API + UI |
| QA-R22-2 | St | post published in 2024 | marketer opens Lifetime | the sheet signals data only from 1 Jan 2025 ⛔ CL-34 | UI |
| QA-R23-1 | S | all 3 insight types eligible | marketer opens Overview | 3 cards | UI |
| QA-R23-2 | St | no insight eligible | marketer opens Overview | Key insights shows its empty state, no filler card ⛔ CL-15 (look) | UI |
| QA-R23-3 | St | only Growth eligible | marketer opens Overview | 1 card | UI |
| QA-R24-1 | B | 9 posts in scope | marketer opens Overview | no Growth/Decline card ⛔ CL-16 (threshold) | API |
| QA-R24-2 | B | Content mix gap 9.9 pts vs 10.0 pts | marketer opens Overview | not shown / shown ⛔ CL-16 | API |
| QA-R24-3 | N | only 1 post with activity in scope | marketer opens Overview | no Top content card | API |
| QA-R24-4 | N | impressions fell 30 % vs the previous period | marketer opens Overview | no Decline card ⛔ CL-16 | API |
| QA-R24-5 | N | network has no view events | marketer opens Overview | no insight built on reach or impressions ⛔ CL-26 | API |
| QA-R25-1 | N | Top content and Content mix would both name Video | marketer opens Overview | the two cards do not repeat the same finding | Rev |
| QA-R26-1 | S | creator role = Admin | marketer opens Overview | each insight names "Admin-created posts" | UI |
| QA-R26-2 | S | destination = Community | marketer opens Overview | each insight names the destination scope | UI |
| QA-R27-1 | S | each insight template | reviewer reads all wording | names the metric, gives values, no "best" / "top-performing", no causal verb | Rev |
| QA-R28-1 | N | — | marketer clicks each insight card | nothing navigates ⛔ CL-27 | UI |
| QA-R29-1 | ⛔ | — | marketer opens Overview | each insight uses the agreed metric ⛔ CL-26 | API |
| QA-R30-1 | S | 25 posts with activity in scope, Top posts shows 10 | marketer exports Overview | dataset 2 holds 25 rows with in-period metrics and the Top posts columns | API |
| QA-R30-2 | S | chart shows Reach | marketer exports Overview | dataset 1 holds all 7 metrics per interval | API |
| QA-R30-3 | S | destination and role filters set | marketer exports Overview | both datasets are filtered the same way | API |
| QA-R30-4 | B | 5,000 qualifying posts | marketer exports Overview | 5,000 rows, no 100 cap | API |
| QA-R30-5 | ⛔ | — | marketer opens Export | which options and widget picker ⛔ CL-19 | UI |
| QA-R31-1 | S | All posts searched for "summer" | marketer exports All posts | only matching posts, current filters applied | API |
| QA-R31-2 | S | — | marketer exports By post type / By destination / Top creators | one row per type / destination / creator with the widget's columns | API |
| QA-R31-3 | ⛔ | — | marketer exports the whole Content performance page | format ⛔ CL-32 | UI |
| QA-R32-1 | S | cohort with 3 post types | marketer opens By post type | one row per type with 7 metrics | API |
| QA-R32-2 | S | — | marketer sorts By post type by each column | order follows that column | UI |
| QA-R32-3 | ⛔ | — | marketer chooses view all posts on the Video row | ⛔ CL-33 | UI |
| QA-R33-1 | S | 11 destinations | marketer opens By destination | top X rows, then View all destinations shows 11 ⛔ CL-35 | UI |
| QA-R33-2 | S | destination filter = User feed | marketer opens By destination | one row, same columns | UI |
| QA-R33-3 | S | — | marketer sorts By destination by each column | order follows that column | UI |
| QA-R34-1 | S | cohort of 25 posts | marketer opens All posts | 10/page, "1-10 of 25 items", lifetime metrics, all columns of R34 | UI |
| QA-R34-2 | S | — | marketer searches a word in a post's body | the post is listed | API + UI |
| QA-R34-3 | S | — | marketer sorts All posts by each metric | order follows it | UI |
| QA-R34-4 | St | — | marketer searches a word no post has | the table's no-results state | UI |
| QA-R35-1 | S | — | marketer opens Top creators | ranked by Most posts by default | UI |
| QA-R35-2 | S | — | marketer sorts by Most comments | ranked by comment totals ⛔ CL-31 | API |
| QA-R35-3 | S | creator with posts of ER 10 % and 30 % | marketer opens Top creators | Average ER / post = 20 % | API |
| QA-R35-4 | ⛔ | creator whose 2 posts reach the same 10 users | marketer opens Top creators | Reach = 10 or 20 ⛔ CL-30 | API |
| QA-R36-1 | ⛔ | an analyst role without post-management grants | analyst opens Analytics | ⛔ CL-20 | UI |
| QA-R36-2 | S | admin scoped to community A | admin opens Overview | numbers cover community A only ⛔ CL-20 (label?) | API |
| QA-R37-1 | ⛔ | Posts never purchased | marketer opens Analytics | ⛔ CL-21 | UI |
| QA-R38-1 | S | activity on a pre-2025 post in range | marketer compares KPI Comments with the Top posts rows | the KPI includes it; the table does not list it ⛔ CL-12 (label) | API + UI |
| QA-ST16-1 | St | /kpis returns 504 | marketer opens Overview | Key metrics shows the error fallback; other widgets still render ⛔ (per widget?) | UI |

รวม 101 ร่าง case · ⛔ 33 case รอคำตอบ · case ด้าน metric ส่วนใหญ่เป็น API เทียบ SQL oracle · 2 case เป็น human review (wording)

## 8. ถัดไป

1. ส่ง §5 High (9 ข้อ) ให้ห้อง ก่อนเรื่องอื่น — **PA-CL-26, 28, 29** มาจาก Notion ขัดกันเอง ต้องให้ PM ตัดสิน
2. ส่ง §6 testability flags เข้า Sketch PR (fixture network + SQL oracle คือ precondition ของ automation)
3. ขอ Metric Library ฉบับเต็ม (export เป็น CSV ของแท็บ 03) เพื่อยืนยัน R10–R14 ตรงจากต้นทาง
4. เมื่อห้องเขียน `docs/solution/post-analytics/spec.md` → `pnpm solution:import admin-console/post-analytics` ใน test-factory แล้ว map §7 เข้ากับ R จริง
