# PDT-3418 — Open Items & Conflicts

## จาก PRD (Source Normalization)

| # | Issue | Source | ต้องได้คำตอบจาก | สถานะ |
|---|---|---|---|---|
| OI-01 | Auto-dismiss timeout ขัดแย้งกัน — PRD บอก "~1 second" แต่ comment บอก "assume 3s" | [PRD-UC1] | Engineering | ⏳ Open |
| OI-02 | "Return to live" CTA — อยู่ใน scope ticket นี้ หรือเป็น follow-on ticket? | [PRD-UC2] | PM | ⏳ Open |

---

## จาก Jira AC

| # | Issue | Source | ต้องได้คำตอบจาก | สถานะ |
|---|---|---|---|---|
| OI-UC2-01 | "Return to live" CTA scope ไม่ชัด — ถ้า in-scope ต้องมี AC เพิ่มสำหรับ CTA behavior | [AC-02, PDT-3563] | PM | ⏳ Open |

---

## จาก Figma

| # | Issue | Screen | ต้องได้คำตอบจาก | สถานะ |
|---|---|---|---|---|
| OI-FIGMA-01 | Behind-live indicator ไม่ปรากฏใน design — UC2 AC-01 ระบุว่าต้องมี visual indicator แต่ `LS-mobile-04-paused.png` แสดงแค่ play button (▶) โดยไม่มี badge หรือ banner บอกว่า "behind live" | LS-mobile-04-paused.png | PM / Design | ⏳ Open |
| OI-FIGMA-02 | LS-mobile-02, 03, 05 มีหน้าตาเหมือนกันทุกประการ — ไม่ชัดว่า "tab-media-control" vs "resume-to-live-edge" ต่างกันตรงไหน อาจมี annotation ใน Figma ที่ export ออกมาไม่เห็น | LS-mobile-02/03/05 | Design | ⏳ Open |
| OI-FIGMA-03 | "Return to live" CTA ไม่ปรากฏใน design เลยทุก screen — สนับสนุน OI-02 + OI-UC2-01 ว่า CTA นี้ไม่ได้อยู่ใน scope ปัจจุบัน แต่ยังต้องการ PM confirm เป็นทางการ | LS-mobile-all | PM | ⏳ Open |
| OI-FIGMA-04 | Desktop screen เป็น "existing behavior" เท่านั้น — ไม่มี "new behavior" design สำหรับ desktop ไม่ชัดว่า desktop in scope หรือ mobile-only | LS-desktop-01 | PM | ⏳ Open |

---

## Figma — Confirmed (ไม่ใช่ open item)

| ✅ | สิ่งที่ยืนยันได้จาก design | Screen |
|---|---|---|
| ✅ | Skip buttons แสดงตัวเลข "10" ชัดเจน — ยืนยัน 10-second value (UC3 AC-01/02) | VR-mobile-02-controls-appear.png |
| ✅ | Live stream ไม่มี skip buttons — ยืนยัน UC3 AC-06 | LS-mobile-02/03 |
| ✅ | Controls overlay VR ประกอบด้วย: X, Volume, 3-dot, skip-back-10, pause/play, skip-forward-10, scrubber | VR-mobile-02-controls-appear.png |
| ✅ | Video playing by default = ไม่มี controls overlay — user ต้อง tap ก่อนถึงจะเห็น | VR-mobile-01-default-playing.png |
| ✅ | Live stream controls = pause button เท่านั้น ไม่มี scrubber, ไม่มี skip | LS-mobile-02/03 |
| ✅ | OI-FIGMA-03 support — ไม่มี "Return to Live" CTA ใน design ทุก screen | LS-mobile-all |

---

_Last updated: 2026-06-30_
