# BUG-C (internal ref) — bug-ticket draft

**Title (paste into Jira):**
`[Android UIKit] Deleted event shows "This community is private" instead of "This event is no longer available"`

- **Type:** Bug · **Component:** Android UIKit — Event Detail · **Priority:** Medium
- **Epic:** PDT-3421 (Notification Tray) · related PDT-3420 (Push), story PDT-3677 AC-02
- **Found by:** QA — source review + reproduced on build (2026-07-21)

---

## Environment
- Platform: **Android** (UIKit)
- Repo / branch: `Amity-Social-Cloud-UIKit-Android` @ `fr/feat/pdt-3724-event-tray-notification` (HEAD `9c5013ca2`)
- Device / OS / App build: _<fill in — e.g. Pixel 7, Android 14, app vX.Y.Z>_

## Summary
Opening a **deleted** event from the event-creation notification (the tray item — or a push, which reuses the same navigation) shows the error state **"This community is private"** on Android. A deleted event is not a privacy/permission problem, so the message is misleading.

## Steps to reproduce
1. In a community, create an event → the event-creation tray item is delivered to members.
2. Delete that event (`isDeleted = true`) **before** opening the notification.
3. On Android, open the Notification Tray and **tap the event-created item**.
   - Same result via a **push** tap (push reuses the tray's navigation).

## Expected result
- A graceful **"This event is no longer available"** state (per PDT-3677 UC2 AC-02) — no error, no blank screen.

## Actual result
- The screen shows **"This community is private"** — implying an access/permission issue rather than a deleted event.

## Root cause (from source)
- `event/detail/AmityEventDetailViewModel.kt` → `getEvent()` (~lines 123–149): the `.catch` block maps `FORBIDDEN_ERROR`, `PERMISSION_DENIED`, **and `ITEM_NOT_FOUND`** all to `EventDetailState.PrivateAccess` (lines 137–144).
- A deleted event returns `ITEM_NOT_FOUND` (404), which is conflated with the access-denied cases → it falls into the "private community" fallback. An in-code comment (~lines 135–136) already acknowledges that `ITEM_NOT_FOUND` also covers a genuinely deleted event.

## Suggested fix
- In the `.catch`, split `ITEM_NOT_FOUND` (deleted / does not exist) out from `FORBIDDEN_ERROR` / `PERMISSION_DENIED` (no access). Map `ITEM_NOT_FOUND` to a dedicated "event no longer available" state with the correct copy.

## Scope / impact
- The single shared entry `AmityEventDetailPageActivity.newIntent(eventId)` is reached from the **notification tray tap AND the push tap** → **both** surfaces show the wrong message.
- Correctness / clarity bug (not a crash). Risk: users read "private" and think it is a permission problem; may drive support questions.

## Related
- PDT-3677 AC-02 (deleted → "This event is no longer available")
- Cross-platform (separate, less severe): **iOS** conflates deleted vs forbidden into a generic "unavailable" (does not say "private"); **Web** shows a generic "content unavailable" + a brief flash of the error before load (internal BUG-E). Only Android shows the misleading "private" text.
- Manual test cases: `[ Deleted event ]` (Tray · Navigation) + `[ Push deleted ]` (Push · Navigation) in `qa/PDT-3421/_epic/PDT-3421-manual-spec.json`.
