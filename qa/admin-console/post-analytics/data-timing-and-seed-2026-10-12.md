# Posts Analytics — ข้อมูลขึ้นเมื่อไร ต้องมีเท่าไร และ seed (2026-10-12)

แหล่ง: social-plus-dashboard main (`infra/Pulumi.{prod,non-prod}.yaml`, `infra/main.go`, `server/internal/feature/postanalytics/insights.go`, `repository.go`) · spec R8, R12, R15, R16 · test-factory PR #50 (ADR-0031) · console PR #425

## 1. ข้อมูลขึ้นเมื่อไร
- ทุก job (posts_with_deleted, content_comments, content_reactions, content_impressions) รัน **ทุกวัน 05:00 UTC = 12:00 น. ไทย** ทั้ง prod และ non-prod (staging)
- วันในระบบเป็น **วัน UTC** (07:00 น. ไทย ถึง 06:59 น. ไทยของวันถัดไป) · ช่วงวันที่ใน console จบที่ "เมื่อวาน (UTC)" เสมอ
- กิจกรรมของวัน UTC X ขึ้นหลังรอบ 05:00 UTC ของ X+1 → ช้าสุด ~29 ชม. เร็วสุด ~5 ชม. (C&R วัดได้ 4–28 ชม., CRA-CL-01)
  - ทำตอน 08:00 น. ไทย 13 ต.ค. → ขึ้นราว 12:30 น. ไทย 14 ต.ค.
  - ทำตอน 06:00 น. ไทย 14 ต.ค. (= 13 ต.ค. UTC) → ขึ้นราว 12:30 น. ไทย 14 ต.ค. เช่นกัน
- ปลอดภัย: อ่านหลัง **~13:30 น. ไทย** ของวันถัดไป (เผื่อเวลารัน job)
- ไม่มีการกด refresh ได้ · หน้าไม่บอกว่าข้อมูลถึงเมื่อไร (R15)
- `has_view_events` (ใช้ตัดสิน N/A) cache ใน server 24 ชม.

## 2. ต้องมีข้อมูลเท่าไร
| ส่วน | เงื่อนไขที่จะแสดง (code จริง) |
|---|---|
| Key metrics | แสดงเสมอ · 0 เมื่อไม่มีกิจกรรม · N/A ตาม R8 · "No baseline to compare" เมื่อช่วงก่อนหน้าไม่มีข้อมูลหรือเริ่มก่อน 2025-01-01 |
| Momentum | ช่วงก่อนหน้าอยู่ใน coverage · engagement ช่วงก่อนหน้า > 0 · **post ที่ได้ engagement ในช่วงปัจจุบัน ≥ 10 post** (ไม่ใช่ post ที่ publish) · \|เปลี่ยน\| ≥ 10% เทียบค่าดิบก่อนปัด |
| Top content | post ที่ได้ engagement ในช่วงปัจจุบัน ≥ 2 · เท่ากันใช้ post_id น้อยสุด |
| Content mix | post ที่ **publish ในช่วง** ≥ 10 · engagement ของกลุ่มนั้น > 0 · ≥ 2 type · gap ≥ 10 จุด · ไม่แสดงเมื่อกรอง type |
| Key insights ทั้งส่วน | ซ่อนเมื่อไม่มีการ์ดไหนผ่าน |
| Chart | "No data available" เมื่อ scope ว่าง |

ข้อสังเกต: เกณฑ์เทียบค่าดิบ แต่จอแสดงค่าปัด 1 ตำแหน่ง → ค่าดิบ 9.95–9.99 จะซ่อนการ์ด · ตัวอย่าง seed ที่ทำได้จริง: ก่อน 10 → หลัง 11 = 10.0% (แสดง) · ก่อน 11 → หลัง 12 = 9.1% (ซ่อน) · 9.9% พอดีต้องใช้ 1000 → 1099 ไม่คุ้ม

## 3. seed (ADR-0031 + console #425)
- seed เป็น data บน case (`ec.seed`) ใน test-factory · `pnpm seed:given` เขียน given[] จาก seed · `pnpm seed:export` ส่งไฟล์ไป `qa/seeds/<feature>.json` ใน console
- console รัน `npx playwright test --project=seed-console-next` วันละครั้ง (ยังรันเอง) · test รอบถัดไปอ่าน ledger ใน metadata ของ community · **ยังไม่มีข้อมูลก็ skip ไม่ fail**
- community ต่อ case ต่อวัน `<prefix> <ec_id> <seed date>` · วันเป็น offset ("-1", "0", "1")
- merge order: test-factory #50 ก่อน แล้วค่อย console #425 · ทั้งสองยัง open

### สิ่งที่ seed ยังทำไม่ได้แต่ Posts Analytics ต้องใช้
| ต้องการ | seed ตอนนี้ | กระทบ |
|---|---|---|
| view / impression ของ post | ไม่มี action | Reach, Impressions, ER, Top posts by Reach, D1 (N/A) |
| post type รูป / วิดีโอ / ไฟล์ / เสียง | มีแค่ `post` กับ `poll` | Content mix, filter type |
| post ที่รอ review / approve / decline | ไม่มี | R6 published-at-approval, edited post |
| แก้ post (edit → reviewing) | ไม่มี | R6 edited post |
| hard delete | `delete` เรียก `DELETE /api/v4/posts/{id}` (soft) | R5 hard delete |
| brand user (`is_brand`) | ไม่มี (มีแค่ roles) | R4 creator role |
ต้องเสนอเพิ่ม action ใน ADR-0031 / #425 หรือใช้ standing data สำหรับกลุ่มนี้
