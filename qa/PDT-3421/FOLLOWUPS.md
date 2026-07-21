# Follow-ups & Bugs — PDT-3421 (Notification Tray) — FINAL

จาก clarification-review + as-built verify ครบ 5 repo (2026-07-16). record เต็ม: `qa/PDT-3421/as-built-verification.md`

## Follow-ups
| FU | Owner | สถานะ |
|---|---|---|
| **FU-1** (TR-CL-03) | QA | ✅ **CLOSED** — tap→nav = Event Detail Page ทุก platform; deleted → graceful (Android = BUG-C) |
| **FU-2** (TR-CL-05) | — | 🔄 REVERSED 2026-07-21 → tray = viewer-local tz (existing UIKit behavior); **BUG-B1 RETRACTED** (DEC-06) |
| **FU-3** (TR-CL-07) | **PM** | ⏳ OPEN — update Jira user story persona → network-wide (รวม non-member). ผูก DEC-03. network-wide behavior ยืนยันแล้วใน backend (PR #5453) — เหลือแค่แก้ข้อความ story |
| **FU-4** (TR-CL-16) | Eng | ✅ **CLOSED** — privacy guard มีจริง: `getById` คืน 403 ให้ non-member ของ private community (`event/index.ts:271-290`). audience = snapshot. *(caveat: tray title ไม่ access-gated — minor leak ถ้า scoping เพี้ยน)* |

## Bugs (spot-check บน live build ก่อน file)
| Bug | Sev | Platform | อาการ | Evidence |
|---|---|---|---|---|
| ~~**BUG-B1**~~ | — | client | **RETRACTED 2026-07-21** — device-local คือพฤติกรรมที่ถูกต้อง (PM reverse TR-CL-05 → viewer-local tz, DEC-06). ไม่ใช่บั๊ค | — |
| **BUG-D** | high | Android | event-type chip = theme-token bg@50% + hardcoded white text → **light theme = ขาวบนขาว มองไม่เห็น** (regression) | `AmityEventTypeChip.kt:40-44` (unused `amityColorBlack` = refactor ไม่ครบ) |
| **BUG-C** | medium | Android | deleted event → "This community is private" (ITEM_NOT_FOUND conflation) | `AmityEventDetailViewModel.kt:135-144` (flagged ในโค้ด, Plan 29 Q#4) |
| ~~**BUG-B2**~~ | — | backend push (PDT-3420) | **RETRACTED 2026-07-21** — QA verified on Android + iOS: push โชว์ device-local (viewer-local) ถูกต้อง; source-based UTC inference ไม่ reproduce. push tz = viewer-local (consistent กับ tray) | — |
| minor-1 | low | backend | `getTraySeen` ไม่ apply ban filter → banned user badge/list ไม่ตรง | `index.ts:239-242` |
| minor-2 | low | backend | tray enrichment `_getByPublicIds` ข้าม `checkEventAccess` → title leak ถ้า audience scoping เพี้ยน | `event.service.ts:632-648` |

## Retracted
- ~~**BUG-B1** (client timezone)~~ — device-local คือพฤติกรรมที่ตั้งใจ (TR-CL-05 reversed 2026-07-21 → viewer-local; DEC-06). ไม่ใช่บั๊ค
- ~~**BUG-B2** (push UTC)~~ — push โชว์ device-local ถูกต้อง (verified Android+iOS 07-21); source UTC inference ไม่ reproduce. ไม่ใช่บั๊ค
- ~~BUG-A (mobile ไม่ enrich)~~ — **false alarm** จาก first-pass agent miss; enriched ครบทั้ง 3 platform (ยืนยันด้วย re-verify)

## Open decisions (ไม่ใช่ bug)
- **TR-CL-21** (Design): chip appearance light+dark ที่ถูกต้องทุก platform (ครอบ BUG-D) · **TR-CL-15** (Design, minor): truncation ชื่อยาว
- ~~**TR-CL-05 open-Q** (fallback)~~ MOOT — tray = viewer-local. Push display tz ก็ = viewer-local (verified Android+iOS 07-21, BUG-B2 retracted) → **ไม่มี tz open แล้ว**
