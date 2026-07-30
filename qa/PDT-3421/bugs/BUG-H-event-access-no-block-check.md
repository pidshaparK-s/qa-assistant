# BUG-H (internal ref) — bug-ticket draft

**Title (paste into Jira):**
`[Core API] Event access check has no block-relationship enforcement — blocked users can still open/RSVP to events`

- **Type:** Bug · **Component:** Core API — Event access control · **Priority:** High (suggest)
- **Epic:** PDT-3421 (Notification Tray) · relates to TR-CL-29 / DEC-08 (blocking extended to events, scope confirmed 2026-07-21)
- **Found by:** QA — reproduced on staging while running the `[ Block after notify ]` manual case + confirmed in source (2026-07-22)
- **Affects:** ALL clients (Web / iOS / Android) — backend access-check gap, not client-specific
- **Note:** DEC-08 already logged this as "not yet built" (Jack to implement) — this ticket gives a concrete, evidence-backed starting point rather than a new surprise.

---

## Environment
- Backend: `social-plus-core` @ `release-4.132.0`
- File: `src/modules/event/index.ts`, `checkEventAccess()` (~line 1134)

## Summary
Blocking between two users has no effect on event access at all. A blocked user can still open an event (and RSVP) that a blocker created, exactly as if no block relationship existed.

## Steps to reproduce
1. User A and User B are not blocked. User A creates an event in a community that both are members of; User B receives the event-created tray notification.
2. User A blocks User B (or User B blocks User A).
3. As the blocked user, tap the tray notification for that event (received before the block existed).

## Expected result
- The blocked user lands on a no-access state — blocking should prevent them from opening or interacting with the event, consistent with how blocking works for other content types (per DEC-08).

## Actual result
- The blocked user opens the event normally, with full access (including RSVP) — exactly as if no block existed.

## Root cause (from source)
`checkEventAccess()` (`event/index.ts` ~line 1134) only checks two things:
1. Whether the requester is the event creator → access granted.
2. Community privacy: public community → **everyone** can see (`return true` unconditionally); private community → members only, via `validateCommunityMembership`.

There is **no block-relationship check anywhere** in this function, or in the broader `event` module — confirmed via a repo-wide search for `isBlocked` / `blockedUserIds` / `BlockRepository` / `checkBlock` scoped to `src/modules/event`, which returned zero matches. For a **public** community event specifically, the function returns `true` for literally any user, so a blocked user has exactly the same access as anyone else.

## Suggested fix
Add a block-relationship check (bidirectional, consistent with how blocking already works for other content types per DEC-08) into `checkEventAccess()` — if a block exists between the requester and the event's creator, return `false` (no access), regardless of community privacy. This should run before or alongside the existing creator/privacy checks.

## Scope / impact
- Any blocked pair where one side created a community event the other can otherwise see — all platforms, both public and private communities (public communities are actually the more exposed case, since access is currently unconditional there).
- Directly contradicts the block-scope decision already agreed (DEC-08) — this is the concrete gap that decision anticipated.

## Related
- TR-CL-29 (Scenario A) / DEC-08 — the scope decision this bug fulfills
- Manual test case: `[ Block after notify ]` (Tray · Audience & privacy) — the case that caught this
