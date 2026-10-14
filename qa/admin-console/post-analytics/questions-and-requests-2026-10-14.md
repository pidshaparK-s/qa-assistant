# Posts Analytics — คำถามที่เหลือและคำขอ test data (ร่าง 2026-10-14)

สถานะ: ร่างให้ pidshapar อ่านก่อน ยังไม่ได้ส่ง · ฐาน: spec.md บน main 4909b21 · dashboard main · console #413 · test-factory #50 (merged) · console #425 (open)

## A. คำถามเก่าที่ยังค้าง

ปิดแล้ว: B1–B7 · M1–M5 · I1–I4 · E1 (user feed) · E2 (rounding) · E3 (deleted post) · edited post (ตกลงแล้ว รอเขียนลง spec) · R15 data-as-of (ตัดสินว่าไม่แสดง) · I5 (Figma final ชนะ Notion)

ยังค้าง ไม่กระทบ release (ถามรอบหลัง):
| เดิม | เรื่อง | ส่วนที่กระทบ |
|---|---|---|
| M6 | ช่วงวันที่ยาวเกิน 365 วัน หรือเริ่มก่อน 2025-01-01 · API ตอบ 400 | filter, ทุก widget |
| Q12 | สัปดาห์แรกและสุดท้ายที่ไม่เต็มบนกราฟ | chart |
| Q13 | Reach ของแถว creator, destination, type | Content performance |
| — | Avg ER เมื่อบาง post เป็น N/A · เรียงตาม ER แล้ว post ที่ reach น้อยชนะ | Top creators, tables |
| E6 | ค้นหาได้แค่ 100 ผลแรก | All posts |
| E7 | ขนาดหน้า 10/20/50 แต่ R14 และ ST61 เขียน 10 | All posts |
| E9 | metric ที่เลือก หน้าของตาราง keyword ไม่อยู่ใน URL | ทุกตาราง |
| E11 | backfill โหลด post ทุกอายุ แต่ §5 เขียน "from 2025-01-01" | ตัวเลขรวม |

## B. คำถามใหม่ (release)

### Q1 · Momentum: "at least 10 posts" นับ post แบบไหน
R12: "Momentum needs at least 10 posts and a change of 10% or more." · Content mix ใช้คำเดียวกัน
build: Momentum นับ post ที่ได้ engagement ในช่วงนี้ (`insights.go` `cur.Posts` = distinct post ใน event ของช่วงนี้) · Content mix นับ post ที่ publish ในช่วง (`cohort_posts`)
ผล: boundary case 9/10 post ต้องรู้ว่าสร้าง post แบบไหน · ถ้า spec หมายถึง post ที่ publish ในช่วง build จะผิด

> **R12 · Momentum post threshold.** R12 says Momentum needs "at least 10 posts", and Content mix uses the same words. The dashboard counts them differently: Momentum counts posts that received engagement in the current period, and Content mix counts posts published in the period. Which does Momentum mean? (a) posts with engagement in the period, as built, or (b) posts published in the period. Please write the answer into R12.

### Q2 · R12 "repeats another card" และลำดับการ์ด
R12: "An insight is dropped when the filters already decide it, the data is too thin, or it repeats another card."
build: ไม่มีการตัดการ์ดซ้ำ · ลำดับคงที่ Momentum → Top content → Content mix · spec ไม่ได้เขียนลำดับ
ผล: ไม่มี oracle ว่า "ซ้ำ" คืออะไร · ลำดับการ์ดเป็นสิ่งที่ tester เห็น แต่ไม่มี rule

> **R12 · duplicate cards and card order.** R12 drops an insight that "repeats another card", but the spec doesn't say what counts as a repeat, and the dashboard drops nothing for it. Should we (a) remove that phrase, or (b) define the rule? The cards always show in the order Momentum, Top content, Content mix. Can R12 state that order?

### Q3 · ER เกิน 100% และ reach = 0
R6: ER = engaged users ÷ reach × 100 · build ใช้ `SAFE_DIVIDE` → reach 0 ได้ค่าว่าง
ผล: post ที่มี comment แต่ไม่มี view event (เช่น platform ที่ไม่ส่ง view) ได้ ER ว่างหรือเกิน 100% · sheet แสดง ER

> **R6/R8 · engagement rate edge cases.** In the post performance sheet, a post can have comments or reactions but no views, for example from a client that doesn't send view events. Then reach is 0, and the dashboard returns no engagement rate. (1) Does the card read N/A? (2) If reach is low, ER can go over 100%. Is that shown as it is, or capped? Please add both to R8.

### Q4 · Delta เมื่อค่าของช่วงก่อน = 0
R7: "When the previous period has no data … 'No baseline to compare'"
build: `DeltaPct` คืนค่าว่างเมื่อ metric ของช่วงก่อนเป็น 0 → การ์ดแสดง No baseline แม้ network มีข้อมูล (เช่น Comments 0 → 5)
ผล: "no data" ใน R7 หมายถึงทั้ง network หรือราย metric

> **R7 · zero in the previous period.** When one metric was 0 in the previous period (Comments 0 → 5), the card reads "No baseline to compare", because a change from 0 has no percentage. R7 says this happens when the previous period "has no data". Is a 0 for that metric what R7 means? If so, please write "or the metric was 0" into R7.

### Q5 · Backfill (D5)
#262 สร้าง `posts_with_deleted` ใหม่ (`published_at`, DeleteBeforeReplace) · ต้องรัน full backfill ใหม่ · release PR #422 ยัง open

> **Backfill after dashboard#262.** #262 recreated `posts_with_deleted` to add `published_at`, so the table needs `posts_with_deleted_full_backfill.sql` again. Has it run on staging? Is it in the go-live checklist for prod before #422 ships? Until it runs, every number on the page is short, so QA will wait for it before testing.

## C. แจ้ง (ไม่ใช่คำถาม)

> **D1 · R8 "no view events in the range" → N/A.** QA tests against R8 as written: Reach, Impressions and Engagement rate read N/A when the network sent no view events in the selected range, and 0 only when views exist and nothing happened. The build checks whether the network has *ever* sent a view event (`withViews`, `has_view_events`), so a range with no views shows 0. QA will log this as a defect when testing. If the team wants the build's behaviour instead, please change R8 and S-R8-1.

## D. คำขอเพื่อเตรียมทดสอบ

### D-1 ถึง dev ของ Posts Analytics (kazekunz)

> **Test data for Posts Analytics (staging).** To write and run the QA cases we need:
> 1. **A staging network that sends view events**, with its network id and region (`X-SP-Region`). Reach, Impressions and Engagement rate depend on it.
> 2. **The destination list on that network**: the communities and user feeds we can post into, for the `{destination}` cases (community name and user feed).
> 3. **How to make a view on staging**: which client and screen sends a post view event (UIKit web or mobile?), and whether a test can send one through an API.
> 4. **The backfill status** (Q5 above).
> 5. **A network with comments or reactions locked**, or confirmation that the console's entitlement stub is the way to test Locked cards. We won't change a shared network's modules without asking.

### D-2 ถึงเจ้าของ seed (FonAlexies · test-factory #50 merged · console #425)

> **Seed actions Posts Analytics needs.** Posts Analytics will use `ec.seed` and the #425 runner. These actions are not in the seed yet:
> 1. **view**: a user views a post (Reach, Impressions, ER, Top posts by Reach, R8 N/A).
> 2. **post content types**: `kind` takes post and poll only. We need image, video, file and audio, and a post with two types (Content mix, by content type).
> 3. **review flow**: a post created in an approval-required community, then approved or declined; and an edit that sends it back to review (R6).
> 4. **hard delete**: `delete` calls `DELETE /api/v4/posts/{id}`, which is a soft delete. We need a hard delete too (R5).
> 5. **brand user**: a user with `is_brand` (R4).
> 6. **ledger probe**: #425 needs an `OVERVIEW_PATHS` entry for posts-analytics (`/v1/post-analytics/overview/kpis`).
> If some of these can't be seeded (views most likely), we'll use standing data on a fixed network and mark those cases as reading standing data.
