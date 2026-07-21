# PDT-3420 Push Notification (event creation) — Analysis

- **Epic:** PDT-3420 "Q3,26 : Push Notification" · Platform: Core API (server) + mobile clients · Status: In Progress
- **UCs:** UC1 = PDT-3676 Console config toggle (3 AC, Deployed to Staging) · UC2 = PDT-3677 Member receives + navigates (5 AC, Deployed to Staging)
- **Sources:** Jira PDT-3420/3676/3677 (fetched 2026-07-16, incl. Tanat dev note + jack comments) · backend as-built (social-plus-core release-4.132.0, from tray verification) · tray analysis `PDT-3675-uc1-analysis.md`
- **Verification target (user):** console-web (toggle) + push tap-logic on Web/iOS/Android UIKit (3 agents in flight)
- **Relationship to tray (PDT-3421):** SAME event trigger. Push is an **additional, opt-in** surface (network toggle). Push **reuses the tray's navigation** (jack: "we don't handle push on our side, it reuse navigation from noti tray"). Content pattern is identical to tray. → the two are one coherent test family.

---

## STEP 1 — Understand

### Relationship Map
| Actor | Role in push |
|---|---|
| Network Admin | Configures the network-level toggle (UC1) |
| Event creator (role w/ CreateEvent) | Triggers event creation → push fires (if toggle ON) |
| Community member (active, non-banned) | Push **recipient** (audience = members of that community) |
| Backend (core API) | Computes audience, renders OS text, fires push, suppresses Room go-live dup |
| OS / device | Delivers or suppresses (OS-level opt-out); renders the notification |
| Client UIKit / sample app | Handles the **tap** → routes to event detail/RSVP (reuses tray nav) |

| Object | Notes |
|---|---|
| Push toggle setting | Network-level (Admin Console → Settings → Push notifications → Event-related events) |
| Event | Trigger; carries type (in_person/virtual), scheduled start, timezone (IANA, optional) |
| Community | privacy (public/private) + members + avatar (icon) |
| Push notification | OS notification, **server-rendered** title/body; data payload for routing |
| Room | virtual event auto-creates a Room → its go-live push is **suppressed** (dedup) |
| Event detail / RSVP page | nav target on tap (= tray's target) |

### State Machine (push lifecycle)
```
[network toggle]  OFF ──────────────► no push  (tray still fires — AC-02/UC1)
                  ON
                   │  event created (SCHEDULED, start ≥ now+15m)
                   ▼
            compute audience = active, non-banned MEMBERS of that community
                   │   (NOT network-wide — differs from tray; "notify whole network" toggle was HELD)
                   ▼
            dedup vs Room go-live push  → exactly ONE push (virtual)
                   ▼
            per recipient device:  OS push enabled? ── no ──► no push (tray still fires — AC-03/UC2)
                   │ yes
                   ▼
            OS shows notification (server-rendered text; icon = community avatar)
                   │  user taps
                   ▼
            route on data.eventName == "event.created" → open event by data.eventId
                   ▼
            event exists? ── no (404 / isDeleted) ──► "This event is no longer available"
                   │ yes                                   (⚠ shared nav → Android BUG-C, iOS conflation)
                   ▼
            event detail / RSVP page (RSVP CTA visible)
```

### Pain & Consequence
Members who don't open the app miss new events entirely (tray is passive/in-app only). For time-sensitive live-stream activations (Ulta), admins need an **external** prompt to drive RSVPs **before** the stream. Without push: RSVP counts stay low; brand partners get a smaller warm audience.

### 3-Layer
- **Business goal:** grow pre-event RSVP for live-stream activations; give admins network-level control (opt-in) to avoid spam.
- **User need (admin):** one optional step to reach members outside the app at creation time. **(member):** a tap that lands directly on RSVP.
- **System behavior:** opt-in network toggle → members-audience push on event creation → single push for virtual → deep-link to RSVP → respect OS/toggle opt-out, independent of tray.

---

## STEP 2 — Specify (enriched AC · happy / edge / error)

### UC1 · PDT-3676 — Console configuration

**AC-01 · toggle visible**
- Happy: admin @ Settings → Push notifications → Event-related events → sees toggle "When someone creates a new event in the community".
- Edge: non-admin / insufficient role → settings not visible; label i18n; toggle **default state** (ON or OFF on a fresh network?) → *P-CL-1*.
- Error: settings section fails to load → toggle absent.

**AC-02 · toggle OFF → no push, tray still fires**
- Happy: OFF → create event → no push delivered; tray item still appears to members.
- Edge: flip OFF then create immediately (setting read at fire-time, not cached stale).
- Error: push still sent while OFF = regression (must-not).

**AC-03 · toggle ON → push to members + deep-link**
- Happy: ON → create event → push to all active, non-banned **members of that community**; tap deep-links to event RSVP/detail page.
- Edge: **public vs private community → BOTH members-only** (push does NOT broadcast network-wide even for public — "notify whole network" HELD → *P-CL-2*); event **creator excluded** from own push? (tray excludes creator → consistency → *P-CL-3*); large community fan-out.
- Error: deep-link opens wrong screen / broken.

### UC2 · PDT-3677 — Member receives & navigates

**AC-01 · tap → RSVP page**
- Happy: tap push → event detail/RSVP page (RSVP CTA visible). ("RSVP page" = event detail page per shared tray nav → *P-CL-6* resolved).
- Edge: app cold-start (killed) vs warm (backgrounded) vs foreground → deep-link routes in all states → *P-CL-7* (test-design).
- Error: route fails / lands on home.

**AC-02 · deleted event before tap → "no longer available"**
- Happy: event deleted (isDeleted=true) → tap → "This event is no longer available", no error/blank. (GET events/{id} → 404).
- Edge: event **edited** (not deleted) → still opens fine (live data).
- Error: ⚠ **Android BUG-C** shows "This community is private" for a *deleted* event; **iOS** conflates deleted vs forbidden — both on the **shared** nav path push also uses → verify (mobile agent).

**AC-03 · OS opt-out → no push, tray still fires**
- Happy: OS/device push disabled → no push; tray item still appears (push⊥tray).
- Edge: OS-level vs app-master vs (if any) in-app toggle interplay — all independent of tray.
- Error: tray suppressed together with push = wrong (must stay independent).

**AC-04 · virtual event → single push (Room dedup)**
- Happy: virtual event (Room auto-generated) → exactly ONE push per eligible user; Room/livestream go-live push suppressed (backend, SDD UC4).
- Edge: in-person event (no Room) → no dedup needed, single push anyway.
- Error: TWO pushes (event.created + Room go-live) = dedup fail.

**AC-05 · push content + icon**
- Happy: title "{{CommunityName}} has event {{EventName}}"; body = event-type chip (In-person/Virtual) + start date + start time; icon = community avatar.
- Edge: **timezone** — start time shows in the **VIEWER's LOCAL tz** (TR-CL-05 REVERSED 07-21 / DEC-06: existing UIKit behavior, matches event cards/detail; GMT-5 event 7:00 PM → a GMT+7 viewer sees 7:00 AM next day). Push verified device-local too (Android+iOS 07-21); missing eventType → chip "" ; long names → OS truncates.
- Verified 07-21: push renders **viewer-local (device)** correctly on Android + iOS → matches the tray. The earlier source-based UTC concern (**BUG-B2**) did NOT reproduce on device → **retracted**.

---

## Clarifications (push) — mini-register

| id | severity | question | status |
|---|---|---|---|
| **P-CL-1** | medium | Toggle **default state** on a fresh network — ON or OFF? (affects "clean env" test baseline) | ⏳ verify via console agent / PM |
| **P-CL-2** | — | Push audience = community **members only** for BOTH public & private (network-wide toggle HELD, unlike tray)? | ✅ resolved — AC-03 "members of that community" + jack held "notify whole network" |
| **P-CL-3** | low | Event **creator** excluded from own push (as with tray)? | ⏳ verify (same audience builder as tray creator-exclusion — expected excluded) |
| **P-CL-4** | low | Toggle is **network-level** (applies to all communities), not per-community? | ✅ resolved — "network admin" setting, AC-01 |
| **P-CL-5** | — | Push display timezone | ✅ resolved 07-21 — push = viewer-local (device), verified Android+iOS; consistent with tray; BUG-B2 retracted |
| **P-CL-6** | — | "RSVP page" == event detail page (has RSVP CTA)? | ✅ resolved — push reuses tray nav (TR-CL-01) |
| **P-CL-7** | low | Cold-start deep-link (app killed) routes correctly? | 🧪 test-design (cover cold/warm/foreground), not a spec blocker |

**Blocking? NO.** P-CL-1 (toggle default) + P-CL-3 (creator exclusion) resolve from the console/mobile agents or a 1-line PM confirm; neither blocks authoring — the manual case just verifies whichever the build does. All behavioral questions resolved.

---

## Cross-surface integration points (tray ⇄ push) — become manual test cases
1. Push OFF (toggle) → **tray still fires** (UC1 AC-02).
2. OS push opt-out → **tray still fires** (UC2 AC-03).
3. Same event → tray item (network-wide on public) **and** push (members only) — audience **differs by design** (TR-CL-02); a public-community non-member gets the **tray** item but **no push**.
4. Deleted event → both tray-tap and push-tap hit the same "unavailable" nav path (shared BUG-C/iOS conflation).
5. Timezone → **both tray and push = viewer-local (device)** — verified on Android + iOS (07-21); ~~BUG-B1~~ + ~~BUG-B2~~ both retracted. Consistent across surfaces, no decision outstanding.

---

## As-Built Verification (Push) — console + Web/iOS/Android UIKit + sample apps (2026-07-16)

**Branches:** console `asc-console-web` develop @9c701618 · Web UIKit develop @046cf179c · iOS `feat/create_event_noti_tray` @632dd077 · Android `fr/feat/pdt-3724-event-tray-notification` @9c5013ca2 · web/mobile sample apps = test harnesses (no runtime push source). Method: read-only source review (3 background agents).

### Console (PDT-3676) — toggle CONFIRMED, matches Jira exactly
- Toggle: `EventActivator.tsx:32-38` · `data-testid="event-activate-switch"` · field **`isPushNotifiable`**
- Label byte-for-byte: `i18n/en/index.ts:3110` **"When someone creates a new event in the community"**
- Section **"Event-related events"** (Community tab, `notifications/index.tsx:162-169`) beside `event.reminder`, `event.started`
- Persist: `POST /admin/v1/notification/setting` with `level:'network'` → **P-CL-4 ✅ network-level** (applies to all communities)
- **"Notify whole network" toggle ABSENT** (held — only PR #903 shipped `event.created`) → **P-CL-2 ✅ push = members only**
- `sc-console-playwright`: **NO existing e2e** for this toggle (the community-create push-*mode* radios are unrelated) → net-new coverage
- Default ON/OFF not in console code (backend default) → **P-CL-1 = observe on staging** (test baseline)

### Push tap→nav — NOT wired in sample apps (reuse target exists; integrator's job)
- **Web:** no push receipt at all — no service worker / FCM / PushManager (`registerDevice()` = session login, red herring). → **push N/A on web**.
- **iOS:** APNs registration wired (`AppDelegate.swift:61-65` → `registerDeviceForPushNotification`); **tap handler `didReceive` is EMPTY** (`AppDelegate.swift:84-86`) — no payload parse, no nav. Intended reuse entry = `AmityNotificationTrayPageBehavior.goToEventDetailPage` → `AmityEventDetailPage(eventId:)` (same as tray).
- **Android:** FCM registration wired (`MainActivity.kt:186-190` + `AmityFcm`); `showNotification` builds a `NotificationCompat` with **no `setContentIntent`/PendingIntent** and the **data payload is discarded** (`AmityNotificationUtil.kt:17-40`) → tap opens launcher only. Intended reuse entry = `AmityEventDetailPageActivity.newIntent(eventId)`.
- **Reading (not alarm):** per jack + Tanat dev-note, client push-tap routing is the **host-app/integrator's** responsibility (route off the documented `data` payload → open event by `eventId`). The reference sample apps simply don't wire it. Destination nav + deleted-handling = the SAME code the tray tap uses → **fully testable via the Tray**. → NEW **P-CL-8** (confirm release scope).

### Shared event-detail path carries the SAME bugs (push inherits once wired)
- iOS `AmityEventDetailPageViewModel.swift:57-81` — deleted & forbidden both → `isEventUnavailable` (conflation), entry-agnostic
- Android `AmityEventDetailViewModel.kt:123-149,137-144` — FORBIDDEN + PERMISSION_DENIED + **ITEM_NOT_FOUND → PrivateAccess**; comment `:135-136` admits deleted also hits it = **BUG-C**. Single `eventId` entry (tray/push/deep-link)
- Web `EventDetail.tsx:40` `!event||isDeleted → FailedToShow` generic "content unavailable" (conflates deleted/forbidden/404) + **flash risk** (no `isLoading` guard → FailedToShow flashes during initial fetch) = **BUG-E candidate (minor)**

### Client dedup / timezone (both mobile platforms)
- **No** client-side dedup for virtual (Room go-live vs event.created) → backend-only ✅ (AC-04 = backend behavior; observe count on device)
- Push time display: **observed device-local (viewer-local) on Android + iOS (verified 07-21) = correct**, matching the tray. (An earlier source pass suggested server-rendered text; the on-device result is device-local, so either the client re-localizes or a different path applies — correct either way; BUG-B2 retracted.) ✅

### Push testability matrix (what's executable where)
| Push AC | Web | iOS | Android | how to test |
|---|---|---|---|---|
| 3677 AC-01 tap→RSVP | N/A (no push) | ⚠ tap not wired | ⚠ tap not wired | needs push-integrated host app; shared nav covered by **Tray-Nav** cases |
| 3677 AC-02 deleted→unavailable | — | ⚠ via tray | ⚠ via tray | shared handling via **Tray-Nav**; Android = BUG-C |
| 3677 AC-03 OS opt-out→no push, tray fires | N/A | ✅ | ✅ | disable OS push → create event → observe |
| 3677 AC-04 virtual→single push | N/A | ✅ | ✅ | create virtual event → count push banners |
| 3677 AC-05 content+icon(+tz) | N/A | ✅ | ✅ | observe banner; push time = device-local (verified correct) |
| 3676 AC-01/02/03 console toggle | ✅ console (web) | — | — | Admin Console toggle → observe push + tray |

### Clarifications (push) — final
- **P-CL-1** (toggle default ON/OFF) → observe on staging, non-blocking
- **P-CL-2** (members only, no network broadcast) ✅ resolved (console)
- **P-CL-3** (creator excluded from push) → expected excluded (same backend audience builder as tray creator-exclusion); verify on staging; low
- **P-CL-4** (network-level toggle) ✅ resolved (console)
- **P-CL-8** (NEW, medium) — **client push-tap deep-linking: in scope for this release (sample/UIKit demonstrates it) or integrator-only?** Sample apps don't route the `event.created` payload. Affects whether AC-01/02 are executable end-to-end on the sample app. **NOT a blocker** for authoring — push-tap cases authored with a precondition + shared nav covered by Tray-Nav. One-line PM/Eng confirm closes it.

**Net: 0 hard blocker.** Push delivery/content/dedup/opt-out (AC-03/04/05) fully testable on iOS+Android sample app; push tap-nav + deleted (AC-01/02) tested via the shared Tray path (+ optional host-app integration check). Console toggle testable on web console.
