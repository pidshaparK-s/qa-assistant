# BUG-F (internal ref) — bug-ticket draft

**Title (paste into Jira):**
`[Core API / Notification Tray] New user sees a backlog of old public-community event notifications — network audience arm not bounded by user join time`

- **Type:** Bug · **Component:** Core API — Notification Tray (Neo4j read query) · **Priority:** High (suggest)
- **Epic:** PDT-3421 (Notification Tray) · relates to AC-04 (public → network-wide) and TR-CL-23 (join-after)
- **Found by:** QA — reproduced on staging + confirmed in source (2026-07-21)
- **Affects:** ALL clients (Web / iOS / Android) — it is a backend tray-query behavior, not client-specific
- **⚠️ Coupled with BUG-G** (`qa/PDT-3421/bugs/BUG-G-new-user-missing-public-event-notification.md`) — same underlying mechanism, see "Relation to BUG-G" below. **Read that section before starting a fix — fixing one without the other makes things worse, not better.**

---

## Environment
- Backend: `social-plus-core` @ `release-4.132.0`
- File: `src/modules/notification-tray/repositories/notification-tray-item.neo4j.ts`
- Any network that uses public-community event notifications

## Summary
A brand-new user, immediately after joining the network, sees their Notification Tray **flooded with old public-community event-created items** (up to the 30-day retention window) — including events whose start time has **already passed**. A newly joined user should not receive a backlog of event notifications that were broadcast before they joined.

## Steps to reproduce
1. In a network that has public communities, create several events in public communities over the past days (each broadcasts a network-wide `event_created` tray item).
2. Create a **brand-new user** (or use one created after those events).
3. Have the new user join **any** community (e.g. a private one) and open the **Notification Tray**.

## Expected result
- The new user sees, at most, event notifications generated **after** they joined the network — consistent with the private/community arm, which already bounds items to after the member joined.
- No backlog of pre-join public events, and no notifications for events that already started/ended.

## Actual result
- The tray is **full of old public-community event notifications** from up to 30 days before the user existed. Many are for events that have already passed. (All show as unseen → also inflates the unseen badge for a first-time user.)

## Root cause (from source)
Two mechanisms combine to produce this symptom — the second is the direct cause, the first is *why it's specifically triggered by "join a community"*:

1. **Why joining is the trigger:** the querying user's Neo4j `User` node is created **reactively**, not at signup — e.g. `community-graph.service.ts:183` calls `v5.user-graph._syncUsers` (→ `user-graph.neo4j.ts` `createOrUpdateUsers`, `MERGE (user:User {id: id}) ON CREATE SET user.networkId = $networkId`, **no `createdAt` is stamped**) when a user joins a community. Before that first sync, the user has no `User` node in the graph at all — see **BUG-G**, which is the flip side of this same fact.
2. **The actual flood, once the node exists:** `notification-tray-item.neo4j.ts` builds the tray with 3 UNION arms inside `CALL (user, thirtyDaysAgo)`:
   - **Community/member arm (correct):** line ~352-354 bounds items with
     `AND noti_tray.lastOccurredAt > member.createdAt` → a member only sees items that occurred after they joined that community.
   - **Network arm (defect):** lines ~366-376 select network-scoped items with only
     `audienceScope = 'NETWORK'` + `networkId = $networkId` + `lastOccurredAt >= thirtyDaysAgo` (30-day retention).
     There is **no** bound relative to when the user's node/network-membership was created — so the instant the user's `User` node exists (per #1), they match every public-community item in the 30-day retention window.

The asymmetry between the two arms is the direct bug: the community arm is time-bounded to the join; the network arm is bounded only by the 30-day retention.

## Suggested fix
- Stamp a timestamp on the `User` node at creation: add `user.createdAt = datetime()` to the `ON CREATE SET` clause in `user-graph.neo4j.ts`'s `createOrUpdateUsers` MERGE (it does not currently set one).
- Add a symmetric guard to the network arm mirroring the community arm, e.g.:
  `AND noti_tray.lastOccurredAt > user.createdAt`
- Product to confirm the exact bound: user account-creation time vs first network-join time (i.e. `user.createdAt` on the Neo4j node, once stamped, effectively means "first synced into the graph" — confirm that's an acceptable proxy) vs "only events whose start is still in the future". QA recommendation: at minimum bound by the node-creation time; ideally also suppress already-started events.

## ⚠️ Relation to BUG-G — fix order matters
BUG-G (`new-user-missing-public-event-notification.md`) is the flip side of mechanism #1 above: a user who has done **nothing** yet (not even joined a community) has no `User` node at all, so their ENTIRE tray read returns empty — including network-wide items they're structurally eligible for.
**If engineering fixes BUG-G's root cause (e.g., syncing every user's `User` node eagerly at signup) without ALSO adding the time-bound from this ticket, the result is a regression, not a fix:** every brand-new signup would immediately see the full 30-day backlog of public-community notifications from the moment their account exists — not just after joining a community. **Ship the network-arm time-bound (this ticket) together with, or before, any fix to BUG-G's missing-node issue.**

## Scope / impact
- Every new user on any network with public communities; all platforms (backend query).
- Degrades the first-run experience and inflates the unseen badge — directly undermines the epic's relevance goal ("richer, more relevant tray → higher tap-through / RSVP").

## Related
- AC-04 (public community → notify entire network) — the network-wide broadcast itself is intended; the missing per-user time bound is not.
- TR-CL-23 (join-after): resolved as "private = no backfill; public = network-wide" — this ticket refines the public side: network-wide should still not backfill pre-join items to new users.
- Manual test cases: `[ Late join ]` (Tray · Audience & privacy) exposed this while validating the private no-backfill path; consider adding a dedicated `[ New user network backlog ]` regression case.
- Sibling: badge computation (TR-CL-06) — the backlog also inflates the new user's unseen count.
