# Automation Plan (AT plan) — PDT-3418 · Video & live streaming

**Date:** 2026-07-09  ·  **Source:** phase-3-5-automation-plan  ·  **Gate:** `checks/automation_plan_coverage.py` (green)  
**Target repo (automatable):** `social-plus-mobile-native-sampleapp-webdriverio` — WebdriverIO + Appium (iOS + Android)

> **ปลายทางไม่ใช่ web.** web UIKit ไม่มี live-stream/video player (repo web mark ‘not implemented/supported on web’) — recorded-video controls automate บน mobile harness เท่านั้น. ทุก EC (109) ถูก disposition แล้ว ไม่มีตก (Dropout Rule): **Automate** = queued ใน AT backlog (`wait for automated`) · **Manual** = ต้องมีคนรัน (`cannot automated`).

## Summary

| unit | total | Automate | Manual |
|---|--:|--:|--:|
| UC1a (PDT-3562) | 31 | 28 | 3 |
| UC1b (PDT-3562) | 26 | 1 | 25 |
| UC2 (PDT-3563) | 25 | 0 | 25 |
| UC3 (PDT-3564) | 27 | 24 | 3 |
| **all** | **109** | **53** | **56** |

## ✅ Automate — 53 EC → AT backlog (mobile harness)

แต่ละ EC map ไป target spec (ยังไม่เขียน — `wait for automated`); tag = `@`+ec_id เพื่อ trace ตอนเขียน code จริง.

| planned spec | EC | ids |
|---|--:|---|
| `tests/tap-to-pause/uc1a-recorded-reveal-controls.spec.ts` | 28 | EC-UC1a-001, EC-UC1a-002, EC-UC1a-003, EC-UC1a-004, EC-UC1a-005, EC-UC1a-006, EC-UC1a-007, EC-UC1a-008, EC-UC1a-009, EC-UC1a-010, EC-UC1a-012, EC-UC1a-013, EC-UC1a-014, EC-UC1a-017, EC-UC1a-018, EC-UC1a-019, EC-UC1a-020, EC-UC1a-021, EC-UC1a-022, EC-UC1a-023, EC-UC1a-024, EC-UC1a-025, EC-UC1a-026, EC-UC1a-027, EC-UC1a-028, EC-UC1a-029, EC-UC1a-030, EC-UC1a-031 |
| `tests/tap-to-pause/uc1b-recorded-contrast.spec.ts` | 1 | EC-UC1b-010 |
| `tests/tap-to-pause/uc3-recorded-skip.spec.ts` | 24 | EC-UC3-001, EC-UC3-002, EC-UC3-003, EC-UC3-004, EC-UC3-005, EC-UC3-006, EC-UC3-007, EC-UC3-008, EC-UC3-009, EC-UC3-010, EC-UC3-011, EC-UC3-012, EC-UC3-013, EC-UC3-015, EC-UC3-016, EC-UC3-017, EC-UC3-018, EC-UC3-019, EC-UC3-020, EC-UC3-021, EC-UC3-022, EC-UC3-023, EC-UC3-024, EC-UC3-025 |

## 🚫 Manual — 56 EC (cannot automate)

| blocker | count | ทำไม | phase-3-1 |
|---|--:|---|---|
| `live-broadcast` | 49 | ต้องมี active RTMP live broadcast + live-edge/real-time — เปิด/join live แบบ deterministic ไม่ได้ | criteria 5 |
| `observe-only` | 3 | ไม่มี oracle ให้ assert — observe เท่านั้น (assumption/‘do NOT assert’) | criteria 1/6 |
| `wallclock-duration` | 3 | ต้องรอเวลาจริงหลายนาที (long pause) — ช้า/flaky เกินคุ้ม | criteria 5 |
| `web-platform-timing` | 1 | reconnect/buffer timing บน web ไม่ deterministic บน shared env | criteria 5 |

### Manual list (full — traceability)

**UC1a** — 3 manual

| ec_id | blocker | name |
|---|---|---|
| EC-UC1a-011 | live-broadcast | [Video player] Verify an active Live stream shows no +/-10s seek controls (contrast) |
| EC-UC1a-015 | live-broadcast | [Video player] Verify resume on a Live stream jumps to the live edge (not the paused position) |
| EC-UC1a-016 | observe-only | [Video player] Observe recorded-LS resume position (ASSUME-recorded-resume — do NOT assert) |

**UC1b** — 25 manual

| ec_id | blocker | name |
|---|---|---|
| EC-UC1b-001 | live-broadcast | [Live player] Verify first tap on a playing Live stream reveals controls without pausing (mobile) |
| EC-UC1b-002 | live-broadcast | [Live player] Verify first tap never pauses the Live stream (accidental-interrupt guard) |
| EC-UC1b-003 | live-broadcast | [Live player] Verify first tap actually reveals the overlay (no-op is a failure) |
| EC-UC1b-004 | live-broadcast | [Live player] Verify tap-outside the button dismisses the overlay and keeps playing |
| EC-UC1b-005 | live-broadcast | [Live player] Verify tap-outside never pauses the stream |
| EC-UC1b-006 | live-broadcast | [Live player] Verify the overlay auto-dismisses after 1s of no interaction while playing |
| EC-UC1b-007 | live-broadcast | [Live player] Verify the overlay is still visible at 999ms (lower boundary) |
| EC-UC1b-008 | live-broadcast | [Live player] Verify the overlay dismisses at 1000ms, not 3000ms (web 3s→1s regression guard) |
| EC-UC1b-009 | live-broadcast | [Live player] Verify pause on a Live stream — play icon persists, no seek, overlay persists, tap-outside stays paused |
| EC-UC1b-011 | live-broadcast | [Live player] Verify the paused overlay does NOT auto-dismiss on the 1s idle timer |
| EC-UC1b-012 | live-broadcast | [Live player] Verify tap-outside while paused never resumes the stream |
| EC-UC1b-013 | live-broadcast | [Live player] Verify reveal/dismiss/auto-dismiss/pause are identical across surfaces |
| EC-UC1b-014 | live-broadcast | [Live player] Verify a per-surface behaviour difference is a surface-invariance break |
| EC-UC1b-015 | live-broadcast | [Live player] Verify baseline — no overlay before any tap, LIVE badge + viewer count visible |
| EC-UC1b-016 | live-broadcast | [Live player] Verify no overlay is rendered before any interaction |
| EC-UC1b-017 | live-broadcast | [Live player] Verify a control interaction restarts the 1s auto-dismiss countdown |
| EC-UC1b-018 | live-broadcast | [Live player] Verify the countdown does not ignore a later interaction |
| EC-UC1b-019 | live-broadcast | [Live player] Verify a pause tap at the auto-dismiss instant — pause wins |
| EC-UC1b-020 | live-broadcast | [Live player] Verify the expiring timer does not swallow the pause |
| EC-UC1b-021 | live-broadcast | [Live player] Verify tap during buffering reveals the overlay with the real state (no false play icon) |
| EC-UC1b-022 | live-broadcast | [Live player] Verify a mid-play stall surfaces an explicit buffering/Reconnecting state [AI-INFERRED] |
| EC-UC1b-023 | live-broadcast | [Live player] Verify the central button never shows a false 'playing' icon while buffering |
| EC-UC1b-024 | live-broadcast | [Live player] Verify backgrounding during an active overlay/timer resolves to the OS-default state |
| EC-UC1b-025 | live-broadcast | [Live player] Verify no stale overlay or implicit toggle after foreground |
| EC-UC1b-026 | observe-only | [Live player] Observe Live foreground snap-to-live (UC2 behaviour — do NOT assert) |

**UC2** — 25 manual

| ec_id | blocker | name |
|---|---|---|
| EC-UC2-001 | live-broadcast | [Live player] Verify pausing shows the ▶ overlay, keeps chat live, and tap-outside dismisses without seeking (paused at live edge) |
| EC-UC2-002 | live-broadcast | [Live player] Verify the pause overlay shows no ±10s seek controls (Live stream) |
| EC-UC2-003 | live-broadcast | [Live player] Verify tapping ON the play button resumes playback (not the tap-outside dismiss) |
| EC-UC2-004 | live-broadcast | [Live player] Verify the ▶ overlay is the only pause indicator (no separate badge/banner) |
| EC-UC2-005 | live-broadcast | [Live player] Verify resume seeks to ≈ the live edge within tolerance, dismisses the overlay, and keeps chat uninterrupted (paused live stream) |
| EC-UC2-006 | live-broadcast | [Live player] Verify resume never returns to the previous paused offset (paused live stream) |
| EC-UC2-007 | live-broadcast | [Live player] Verify the resume target is near-live within tolerance, not exact-live (CONF-07) |
| EC-UC2-008 | live-broadcast | [Live player] Verify a room ending during a pause leaves paused for the ended state with no frozen frame (terminal wins) |
| EC-UC2-009 | live-broadcast | [Live player] Verify a not-yet-ready recording shows 'Livestream ended' with no processing state (recording not ready) |
| EC-UC2-010 | live-broadcast | [Live player] Verify a room that becomes recorded shows the recorded/VOD state (room recorded) |
| EC-UC2-011 | live-broadcast | [Live player] Verify a simultaneous pause + host-end race resolves to ended (terminal wins, staged manually) |
| EC-UC2-012 | live-broadcast | [Live player] Verify the default live-edge state shows no pause indicator with LIVE badge, viewer count, and live chat intact (before any pause) |
| EC-UC2-013 | live-broadcast | [Live player] Verify mobile web offers no pause control on a Live stream (web-mobile) |
| EC-UC2-014 | live-broadcast | [Live player] Verify web-desktop presents the pause control (web-desktop, 1-step pause) |
| EC-UC2-015 | live-broadcast | [Live player] Verify iOS / Android present the pause control (2-step reveal-then-pause) |
| EC-UC2-016 | wallclock-duration | [Live player] Verify a multi-minute pause still resumes to ≈ the live moment within tolerance (long pause) |
| EC-UC2-017 | wallclock-duration | [Live player] Verify jump size does not change the resume-to-live guarantee (long pause, large jump) |
| EC-UC2-018 | wallclock-duration | [Live player] Verify a long-pause resume lands ≈ live within tolerance (further behind still within guarantee) |
| EC-UC2-019 | live-broadcast | [Live player] Verify chat and video re-align at the live moment on resume with no replay and no skip (resume after pause) |
| EC-UC2-020 | live-broadcast | [Live player] Verify before-vs-after message ids show no duplicate and no gap on resume (message id diff) |
| EC-UC2-021 | live-broadcast | [Live player] Verify after a long paused window chat is already at the live moment on resume (long pause, continuous chat) |
| EC-UC2-022 | live-broadcast | [Live player] Verify a network drop while paused shows Reconnecting, stays paused through recover, and resumes to ≈ live (network drop/recover) |
| EC-UC2-023 | live-broadcast | [Live player] Verify the stream never auto-resumes on network recover (stays paused until explicit resume) |
| EC-UC2-024 | live-broadcast | [Live player] Verify iOS shows the Reconnecting scrim even while paused (iOS NWPathMonitor) |
| EC-UC2-025 | live-broadcast | [Live player] Verify web shows no overlay on a plain paused-video drop, only on broadcaster waitingReconnect (web) |

**UC3** — 3 manual

| ec_id | blocker | name |
|---|---|---|
| EC-UC3-014 | live-broadcast | [Live player] Verify a Live stream shows no in-app skip buttons |
| EC-UC3-026 | web-platform-timing | [Video player] Verify web buffering shows Reconnecting UI and keeps manual scrub available |
| EC-UC3-027 | observe-only | [Video player] Observe the ±10s skip result mid-buffer on web (do NOT assert — FU-3) |

## Next step (เมื่อมี slot ทำ mobile automation)

1. เขียน spec จริงใน `social-plus-mobile-native-sampleapp-webdriverio` ตาม target ของ Automate EC (tag = `@`+ec_id).
2. ตอน spec เขียนเสร็จ → เปลี่ยน `at_status` ของ EC นั้นเป็น `automated`.
3. เพิ่ม bijection gate: ทุก EC `automated` ต้องมี test จริงในไฟล์ target ที่ tag ตรง (whole-token, no-stub) — เหมือน coverage gate ของ admin-on-the-go.
4. Manual EC → รวมเป็น manual test pass; live-broadcast ต้องมี broadcaster จริงตอนรัน.
