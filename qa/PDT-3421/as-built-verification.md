# As-Built Verification — PDT-3421 UC1 event-created tray item (FINAL)

- **Date:** 2026-07-16 · **Method:** source review across 5 repos — UIKit Web/iOS/Android + backend `social-plus-core` + console (peripheral) · file:line evidence
- **Branches:** Web `develop` · iOS `feat/create_event_noti_tray` · Android `fr/feat/pdt-3724-event-tray-notification` · backend `release-4.132.0`
- ⚠️ Confidence: high (source). **Recommend a live-build spot-check** for BUG-D (Android light-theme chip) + a concrete-data check for livestream chip.

## ✅ CORRECTED HEADLINE — enriched item present on ALL 3 platforms
Earlier interim claim "enriched = Web-only, mobile generic" was a **FALSE NEGATIVE**: the first iOS+Android agents missed the `event_created` code path (HEAD unchanged between runs → agent miss, not a branch/stale issue). Re-verification confirms **Web, iOS, AND Android all render** chip + start date + start time + **community** avatar.
- Web `NotificationItem.tsx:161-167` · iOS `NotificationTrayItemView.swift:79-127` · Android `AmityNotificationTrayItemView.kt:84-131`

## Client matrix (all 3 enriched)
| Q | Web | iOS | Android | verdict |
|---|---|---|---|---|
| enriched (chip+date+time+community avatar) | ✅ | ✅ | ✅ | **all 3** |
| chip labels | In-person/Virtual | In-person/Virtual | In-person/Virtual | ✅ consistent |
| unknown/null type | chip hidden | chip hidden (empty-title guard) | **→ "Virtual"** (else default) | Android diverges (latent trap; moot — enum=2 at create) |
| separator "·" | none (2 spans) | none (HStack 4pt) | none (1 string, space) | ✅ **no dot** (PRD copy wrong) → TR-CL-18 |
| **timezone** | device-local | device-local | device-default | ✅ viewer-local = CORRECT (TR-CL-05 reversed 07-21 → DEC-06); ~~BUG-B1~~ retracted |
| avatar | community ✓ | community ✓ | community ✓ | ✅ TR-CL-11 |
| **chip dark/light** | hardcoded black@50%+white (readable both) | hardcoded black@50%+white (readable both) | **theme-token bg + white text → white-on-white in LIGHT = BUG-D** | ⚠️ diverge + Android regression → TR-CL-21 |
| timestamp (relative) | ✅ | ✅ | ✅ | ✅ TR-CL-19 |
| tap→nav | Event Detail | Event Detail | Event Detail | ✅ TR-CL-01/FU-1 |
| deleted/forbidden on open | generic "unavailable" | generic "unavailable" | **"This community is private"** (deleted too → BUG-C) | conflated all; Android wrong msg for deleted |
| unseen | primary tint ✓ | primary tint ✓ | primary tint ✓ | ✅ AC-01 |

## Backend (social-plus-core release-4.132.0) — Eng bucket RESOLVED from design doc + code
- **Audience (AC-04/05):** public→network-wide (incl non-members) / private→members — IN release (PR #5453). `event-event.handler.ts:47-50`, `neo4j.ts:351-376`
- **Exclusions:** creator (actor filter), global-ban (can't auth, ADR-0003), community-ban (read-time Mongo filter), left/removed (edge gone) — all confirmed
- **Dedup (TR-CL-14):** UNION → 1 item · **Ban-after (17):** hide-at-read · **Join-after (23):** private=no retroactive · **User-block (24):** recipient↔creator bidirectional · **Edit (12):** live re-fetch · **Badge (06):** client-computed occurredAt>seenAt · **Created (09/10):** no draft/recurring, permission-gated roles · **Backfill (13):** scope forward-only, copy read-time
- **Timezone (05) — REVERSED 07-21 (DEC-06):** BOTH tray and push show start time in the VIEWER's device-local tz (existing UIKit behavior). Verified on Android + iOS. Client device-local is CORRECT → ~~BUG-B1~~ + ~~BUG-B2~~ both retracted; no push-tz decision outstanding.
- **Privacy (FU-4/16):** `getById` → **403** for non-member of private (`event/index.ts:271-290`, `checkEventAccess:1134-1164`) → PM's nav guard EXISTS; audience = snapshot (no recompute)

## 🐛 Bugs to file (spot-check first)
| Bug | Sev | Where | อาการ |
|---|---|---|---|
| ~~**BUG-B1**~~ | — | client tray | **RETRACTED 07-21** — device-local คือพฤติกรรมที่ตั้งใจ (TR-CL-05 reversed → viewer-local, DEC-06) |
| **BUG-D** | high | Android UIKit | chip = theme-token bg@50% + hardcoded white text → **light theme มองไม่เห็น** (`AmityEventTypeChip.kt:40-44`) |
| **BUG-C** | medium | Android UIKit | deleted event → "This community is private" (ITEM_NOT_FOUND conflation, `AmityEventDetailViewModel.kt:135-144`) |
| ~~**BUG-B2**~~ | — | backend push (PDT-3420) | **RETRACTED 07-21** — push โชว์ device-local ถูกต้อง (verified Android+iOS); UTC inference ไม่ reproduce |
| minor | low | backend | `getTraySeen` ไม่ apply ban filter → banned user badge/list ไม่ตรง; tray title ไม่ access-gated (leak ถ้า scoping เพี้ยน) |

## Open decisions
- **TR-CL-21 (Design):** chip appearance ที่ถูกต้อง light+dark ทุก platform (แก้ BUG-D ด้วย) · **TR-CL-15 (Design, minor):** truncation ชื่อยาว (client wrap, ไม่ ellipsize)
- ~~**TR-CL-05 open-Q** (fallback)~~ MOOT (tray=viewer-local). NEW: **push display tz** (BUG-B2) ต้องตัดสิน
- **FU-3 (PM):** update Jira user story persona → network-wide (TR-CL-07/DEC-03)
