# Posts Analytics — delivery.md เทียบกับ spec.md (2026-10-08)

- **แหล่ง:** `solution/posts-analytics` @ `4fe1362` (PR #358) · snapshot ใน `products/admin-console/posts-analytics/solution/`
- **วิธีอ่าน:** spec.md คือ oracle ของ QA · delivery.md คือบันทึกสิ่งที่ build จริง รวมหัวข้อ *"Questions logged (defaults taken by the lead, for the user's review)"* ซึ่งเป็นการตัดสินใจระหว่าง build ที่ยังไม่มีใครรีวิว
- **ขอบเขต:** สิ่งที่ dev บอกว่าแก้แล้วหลัง 2026-10-02 (dashboard#262, commit 9eb5d71) ถือว่าแก้แล้ว แต่ต้องยืนยันตอนทดสอบ · build ยังไม่ final

## 🔴 1. build ต่างจาก rule — ถ้าทดสอบวันนี้จะเป็น defect

| # | rule ใน spec | build (delivery.md) | ผลต่อ release นี้ (Key insights + sheet) | ต้องการ |
|---|---|---|---|---|
| D1 | **R8 / S-R8-1:** "The network sent no view events **in the range** → Reach, Impressions, ER: N/A, not 0" | SL-00 L26: "the network **never** sent impressions → N/A; **zero in range → 0**, as `/v1/content` does" | กระทบ sheet (Reach / Impressions / ER) และค่า engagement ที่ insight ใช้ · ช่วงที่ไม่มี view แต่ network เคยส่งจะได้ 0 แทน N/A | เลือกว่า spec หรือ build ถูก · ถ้า build ถูกต้องแก้ R8 และ S-R8-1 |
| D2 | **R8:** "A metric shows N/A, never 0, when its data cannot exist" · Locked เมื่อไม่ได้ซื้อ module | SL-02 L102: "the chart offers all 7 metrics even when comments or reactions are locked; **locked metrics plot their zeros**" | อยู่นอก release (กราฟ) แต่ขัดกับ rule ตรง ๆ | กราฟของ metric ที่ถูกล็อกต้องแสดง N/A หรือ Locked ไม่ใช่ 0 |
| D3 | **R5 / S-R5-4:** post ที่ soft-delete ยังนับ "And it is listed in Content Performance" · **R14:** "keyword search on title and text" | SL-05 L206: "search runs `matchingOnlyParentPost` with no deleted flag, so **a deleted post is not found by keyword**" | นอก release | ยอมรับเป็นข้อจำกัดแล้วเขียนลง spec หรือแก้ build |
| D4 | **R13 / S-R13-1:** export "every post with activity in the range" · Content performance "all rows" | SL-07 L265–266: ตัดไฟล์ที่ **100,000 rows ต่อตาราง** · CORS ไม่ expose `X-Export-Truncated` / `Content-Disposition` ทำให้ **console ไม่รู้ว่าถูกตัด** และไม่แสดง toast | export ของ Key insights อยู่ใน popover เดียวกัน | เพิ่ม cap ลงใน R13 · ฝั่ง dashboard ต้องเพิ่ม `Access-Control-Expose-Headers` |
| D5 | **R6** (แก้ 2026-10-06): Comments นับเฉพาะ comment ระดับบนสุด | SL-00 L27: "Comments include replies" | กระทบค่า engagement ของทั้ง 3 insight | dev แก้แล้วใน dashboard#262 (merged) · **ยืนยันตอนทดสอบ และต้องรู้ว่า backfill รันแล้วหรือยัง** |

## 🟠 2. build ตัดสินเองในจุดที่ spec ไม่ได้เขียน — ต้องเขียนลง spec ไม่งั้นไม่มี oracle

| # | เรื่อง | build ทำอะไร | ใน release นี้? | ตรงกับคำถาม |
|---|---|---|---|---|
| E1 | Top content เมื่อ post อยู่บน user feed | SL-06 L239: "This post generated the most engagement **in a user feed**." (no Figma copy, TBC with Design) | ✓ | C1 |
| E2 | การปัดเศษของ % บนการ์ด | SL-06 L241: "shares and deltas read up to **one decimal** ('12.5%', '20%')" | ✓ | C3 |
| E3 | post ที่ถูกลบ หรือที่ core ไม่ส่งข้อมูลกลับมาแล้ว | SL-03 L133: แถวยังคงอันดับไว้ แสดง "**Post content is not available.**" (copy ใหม่ ไม่มีใน Figma) · destination เป็น "—" · L142: sheet แสดง Deleted tile ของ PostContent | ✓ (sheet, Top content) | C4 |
| E4 | ข้อความของ export error และ truncation | "The export failed. Try again." · "The file was cut at 100,000 rows per table." (TBC with Design) | ✓ | — |
| E5 | analyst ที่มีแค่ VIEW_DASHBOARD และ core ปฏิเสธ posts/list | SL-03 L141: แถวไม่มีชื่อ post | ไม่เกี่ยวแล้ว: B5 ตัดสินว่า analyst ไม่เห็น Posts | — |
| E6 | ค้นหาด้วย keyword | SL-05 L205: ส่ง hit แรก **100 อันเท่านั้น** · post หลังจากนั้นค้นไม่เจอ | — | ใหม่ |
| E7 | จำนวนแถวต่อหน้าของ All posts | SL-05 L209: 10 / 20 / 50 (R14 เขียน "10 per page") | — | ใหม่ |
| E8 | Clear all | SL-01 L66: ล้าง destination และ roles แต่ไม่ล้างวันที่ | ✓ (filter bar) | ใหม่ |
| E9 | สถานะที่ไม่เก็บใน URL | metric ที่เลือก, หน้าของตาราง, keyword กลับเป็นค่าเริ่มต้นเมื่อ reload | ✓ (บางส่วน) | ใหม่ |
| E10 | comment ที่รอ approve | SL-00 L27: "exclude pending" (`comments_visible_v`) | ✓ (engagement) | ใหม่ · ควรเขียนลง R6 |
| E11 | backfill | SL-00 L28: "Backfill loads every post regardless of age" · §5 เขียน "A one-off backfill loads from 2025-01-01" | ✓ (ตัวเลขรวม) | ใหม่ · build ตรงกับ R1 มากกว่า §5 |
| E12 | Key insights บน Content performance | SL-06 L243: ไม่แสดง | — | ตรงกับ R12 (เป็นของ Overview) |

## 🟡 3. เอกสารไม่ตรงกับของจริง (ไม่กระทบพฤติกรรม)
- §5: watermark ใช้ `serving.etl_watermarks` ไม่ใช่ `sp-intel.events.sync_watermark` · `role_bucket` และ `communities` ส่งแบบคั่นด้วยจุลภาค ไม่ได้ส่งซ้ำหลายครั้ง · ชื่อไฟล์ `content_creator_dims` และ `content_posts_reconcile.sql` เปลี่ยนแล้ว (SL-00 L24, L29; SL-01 L63)
- KPI ส่งกลับมาในชื่อ `metrics` ไม่ใช่ `kpis` (SL-02 L96)

## ⚠️ 4. ผลกระทบนอก feature และเรื่องที่ไม่ใช่ functional
| เรื่อง | ที่มา | ผล |
|---|---|---|
| **มีการเปลี่ยน DS ที่กระทบทั้งแอป**: header สูง 56 → 64, toggle และ breadcrumb ขยับ, สี tooltip, padding ของ Badge และ Chip, Drawer shadow, × ของ DateRangePicker, ข้อความใน Combobox | delivery L292, L327, L376, L382–385 | **ต้องทำ regression หน้าอื่น** เช่น Posts Content, Comments & Replies, Usage, Create post · Playwright ที่ใช้ตำแหน่งหรือภาพอาจพัง |
| **ตัดแท็บ Settings ออกจากหน้า Posts** (Posts spec ST2 ถูกแก้) | L294, L384, L388 | case ของ post-content ใน test-factory ไม่ได้ assert แท็บนี้ (เช็กแล้ว) แต่ `solution.json` ของ post-content จะขึ้น `SOLUTION_STALE` เมื่อ spec บน `next` เปลี่ยน → ต้อง re-import |
| **ต้นทุนและ performance**: route 365 วัน ราว 6.4–7.2 GB · lifetime ของ post เก่า 6.8 GB · การแก้ cost ถูกพักไว้ ("complete all slices first") | SL-00 L32–33 | ช่วงยาวหรือ post เก่ามีโอกาสได้ **504 (60 วินาที)** ต้องมี case ด้าน performance และ timeout |
| ต้องเพิ่ม hostname ของ prod console-next ใน CORS | SL-00 L30 | เป็นเงื่อนไขก่อน deploy · ถ้าไม่มี ทุก widget จะ error |
| **การตัดสินใจ 84 ข้อ** ใต้หัวข้อ "defaults taken by the lead, for the user's review" · ข้าม plan และ demo stop ("stops waived") | delivery L4, ทุก slice | เป็นการตัดสินใจที่ยังไม่มีใครรีวิว · จุดที่กระทบ rule ดึงออกมาไว้ในข้อ 1–2 แล้ว |

## ✓ 5. ตรงกันแล้ว
B5 (analyst — แก้ใน commit 9eb5d71) · B6 (เริ่มที่ community แรก ตรงกับ build) · R3 destination มีแค่ group · R11 sheet มี picker ของตัวเอง · R16 × บน chip · threshold ตรงกับ spec · Avg ER ใช้สูตร Σ ER ÷ n · การ sort ขอข้อมูลใหม่ทุกครั้ง

## สรุปสำหรับ release นี้
- **ต้องปิดก่อน QA confirm:** D1 (R8) · D5 (ยืนยัน #262 และ backfill) · E1, E2, E3 ต้องเขียนลง spec (ตรงกับ C1, C3, C4)
- **ไม่ block release แต่ต้องตามต่อ:** D2, D3, D4, E6–E11, regression ของ DS ทั้งแอป, performance

## การตัดสินของ QA (pidshapar, 2026-10-12)
- **D1 → ทำตาม R8:** ช่วงที่ไม่มี view event ต้องแสดง N/A · build ตอนนี้แสดง 0 (dashboard `withViews` ดูว่า "เคยส่ง" ไม่ใช่ "มีในช่วง") → ถ้าทดสอบเจอ = defect · case ใช้ R8 / S-R8-1 เป็น oracle · ยังไม่ได้แจ้ง dev
- **E3 → ยอมรับตาม build:** "Post content is not available." · destination "—" · sheet แสดง Deleted tile · ใช้เป็น expected
- **D5 (อธิบายใหม่):** การตัด reply ทำตอน query (`parent_id IS NULL`) ไม่ต้อง backfill · แต่ #262 เพิ่ม `published_at` และ **สร้างตาราง `posts_with_deleted` ใหม่ (DeleteBeforeReplace)** → ต้องรัน full backfill ใหม่หลัง deploy ไม่งั้นตารางว่างหรือขาด `published_at` → ต้องยืนยันว่ารันแล้วบน staging (และต้องรันบน prod ก่อน go-live)
- **DS ทั้งแอป:** regression ด้วยการรัน automated suite ของหน้าที่ใช้ component ร่วม (Posts content, C&R, Reactions, Usage, Create post)
- **D3 (2026-10-14):** ค้นหา keyword ไม่เจอ post ที่ soft-delete → ถือเป็น defect ตาม R5/R14 · ไม่ถามล่วงหน้า · เปิด bug ตอนทดสอบจริง (scenario CP-05)
- **N11 search 100 hits:** ถามใน #442 แล้ว · ถ้า R14 ไม่ถูกแก้ให้ยอมรับข้อจำกัด → ผลค้นหาที่ไม่ครบเป็น defect เช่นกัน
