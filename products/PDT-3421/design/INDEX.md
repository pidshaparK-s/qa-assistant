# PDT-3421 — Design assets (Figma ground truth)

Pulled via Figma MCP 2026-07-14. Source file: `Notification-Tray`
fileKey `ialY0mQkYwK0FHGKBIO5u7` · canvas "- Event Tray Item 🆕"

Design URLs:
- Mobile: https://www.figma.com/design/ialY0mQkYwK0FHGKBIO5u7/Notification-Tray?node-id=3759-26398
- Web:    https://www.figma.com/design/ialY0mQkYwK0FHGKBIO5u7/Notification-Tray?node-id=3759-26399

| File | Platform | Figma node | Shows |
|---|---|---|---|
| `mobile-01-overview-annotated.png` | Mobile | 3759:26400 | Section overview + design annotation pills ("Noti Item", ">1 Events from the same AND/OR different communities") + both tray frames |
| `mobile-02-tray-event-same-A.png` | Mobile | 3759:26401 | Tray screen — 2 event items from the SAME community (Ulta Beauty ×2), unseen = blue tint, Recent/Older sections |
| `mobile-03-tray-event-same-B.png` | Mobile | 3759:26415 | Tray screen — 3 event items from DIFFERENT communities, each a distinct row |
| `mobile-04-event-reminder-context.png` | Mobile | 3759:26434 | Event **Reminder** item (different noti category — context only, not this story) |
| `web-01-overview-annotated.png` | Web | 3759:27812 | Section overview + annotation pills + Same/Different tray frames |
| `web-02-tray-event-same.png` | Web | 3759:27813 | Web tray — events from same community |
| `web-03-tray-event-different.png` | Web | 3759:27831 | Web tray — events from different communities |

## Ground-truth facts (for AC enrichment / test design)
- **Primary line**: `{{CommunityName}} has event {{EventName}}` — community + event name bold, "has event" regular.
- **Secondary line**: event-type chip (`In-person` | `Virtual`) followed by `DD Mon YYYY · H:MM AM/PM` (event scheduled start).
- **Icon**: community avatar (NOT a separate event thumbnail) → resolves TR-CL-11.
- **Unseen**: light-blue row background.
- **No grouping**: design explicitly shows >1 events (same and different communities) as separate rows → resolves TR-CL-04.
- **Two timestamps**: relative occurredAt on the right ("Just now" / "2m" / "10h"); absolute event start in the secondary line (timezone still unspecified → TR-CL-05 open).
- **Not depicted**: tap destination (RSVP vs detail — TR-CL-01/03), deleted-event state, member-vs-non-member content difference for public communities (TR-CL-07). These remain open clarifications.

To re-pull: Figma MCP `get_screenshot` / `get_design_context` with the fileKey + node ids above.
