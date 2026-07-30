# BUG-I (internal ref) — bug-ticket draft

**Title (paste into Jira):**
`[UIKit Web] Event-created tray item swaps to a different avatar after its event is deleted (should stay the community avatar)`

- **Type:** Bug · **Component:** UIKit Web — Notification Tray item rendering · **Priority:** Medium (suggest)
- **Epic:** PDT-3421 (Notification Tray) · relates to Tray AC-01 (item icon = community avatar)
- **Found by:** QA — reproduced while running the `[ Tray content ]` manual case with a deleted event (2026-07-24)
- **Affects:** web-desktop & mobile-web only (iOS / Android render the community avatar correctly after deletion)

---

## Summary
Tray AC-01 says the event-created tray item's icon is the **community avatar** (not the creator/user avatar, not the event thumbnail). This holds while the event is live, but on web-desktop and mobile-web the icon **changes to a different avatar** once the event is deleted (isDeleted = true) — the item stops showing the community avatar even though the tray item itself still exists.

## Steps to reproduce
1. As a member, open the Notification Tray and confirm a fresh event-created item shows the **community avatar** as its icon.
2. Have a moderator delete the event (isDeleted = true).
3. Refresh / re-open the Notification Tray.
4. Re-locate the same event item and inspect its icon.

## Expected result
- The item icon is **still the community avatar** — identical to before the deletion. Deleting the event must not change how the tray item's icon renders.

## Actual result
- On web-desktop and mobile-web the icon is **swapped to a different avatar** (no longer the community avatar) after the event is deleted.

## Scope / impact
- web-desktop and mobile-web only; iOS and Android are unaffected.
- Visual-only (the tap-navigation path for a deleted event is covered separately and is out of scope here), but it breaks Tray AC-01's icon guarantee for the deleted-event state.

## Related
- Tray AC-01 — the icon-source guarantee this bug violates
- Manual test case: `[ Tray content — deleted event ]` (Tray · Content & rendering) — the case that catches this
- Contrast: `[ Deleted event ]` (Tray · Navigation) — tap destination for a deleted event, a different concern
