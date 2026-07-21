# BUG-G (internal ref) — bug-ticket draft

**Title (paste into Jira):**
`[Core API / Notification Tray] New user with zero community memberships does not receive a public-community event-created notification (missing Neo4j User node — reactive sync, never created at signup)`

- **Type:** Bug · **Component:** Core API — Notification Tray (Neo4j read query / user-graph sync) · **Priority:** High (suggest)
- **Epic:** PDT-3421 (Notification Tray) · relates to AC-04 (public community → notify entire network, incl. non-members)
- **Found by:** QA — reproduced on staging + confirmed in source (2026-07-21)
- **Affects:** ALL clients (Web / iOS / Android) — backend read-path defect, not client-specific
- **⚠️ Coupled with BUG-F** (`qa/PDT-3421/bugs/BUG-F-new-user-network-backlog.md`) — same underlying mechanism, see "Relation to BUG-F" below. **Read that section before starting a fix — fixing one without the other makes things worse, not better.**

---

## Environment
- Backend: `social-plus-core` @ `release-4.132.0`
- Files: `src/modules/notification-tray/repositories/notification-tray-item.neo4j.ts` (`getAllFromUserId`), `src/modules/social/user-graph/repositories/user-graph.neo4j.ts`, `src/modules/notification-tray/handler/user-event.handler.ts`
- Any network with at least one public community

## Summary
A brand-new user who has **not joined any community** does not receive the Notification Tray item for an event created afterward in a **public** community — even though AC-04 says a public-community event should notify **all active, non-banned users in the network**, membership not required.

## Steps to reproduce
1. Create a brand-new user who has **not joined any community**.
2. Open/check that user's Notification Tray (it is empty — correct at this point).
3. As a different user, create a new event in a **public** community.
4. Re-check the new user's Notification Tray shortly after (within roughly 30 seconds of step 2/3).

## Expected result
- The new user receives the event-created tray item for the public-community event, per AC-04 (public → entire network, including non-members and users in zero communities).

## Actual result
- The new user's Notification Tray is still empty — the event-created item does not appear.

## Root cause (from source — confirmed; earlier cache-staleness theory ruled out)
- ~~Earlier hypothesis: stale 30s Redis tray-list cache (no invalidation hook on new item).~~ **Ruled out by QA**: waited 30+ seconds after the event was created before re-checking — the item still did not appear, which rules out a caching explanation (the cache would have expired by then).
- **Confirmed root cause:** `getAllFromUserId` (`notification-tray-item.neo4j.ts:340`) starts with
  `MATCH (user:User {id: $userId})` **before** entering the `CALL (user, thirtyDaysAgo) { … 3 UNION arms … }` subquery. If this initial `MATCH` finds no row, the `CALL` subquery runs zero times — so **all three arms return empty**, including the network-wide arm, even though that arm's own `WHERE` clause doesn't structurally require any relationship to the `user` node.
- The user's `User` node in Neo4j is created **reactively**, not at signup: `user-graph.neo4j.ts` `createOrUpdateUsers()` does `MERGE (user:User {id: id}) ON CREATE SET user.networkId = $networkId`, invoked only by specific actions — e.g. joining a community (`community-graph.service.ts:183` → `v5.user-graph._syncUsers`), following someone, or a profile-reset event. **A user who has done none of these has no `User` node at all.**
- This exact failure mode is already known/acknowledged in the codebase: `notification-tray/handler/user-event.handler.ts:123-125` has an explicit comment on a *different* event type — *"Ensure the user node exists in Neo4j before creating the notification. Newly created users may not have a node yet, which would cause the MATCH ... to silently fail."* — and proactively calls `_syncUsers` first, specifically to avoid this. No such guard exists on the **tray-read path** for a user who queries their own tray before ever taking a graph-relevant action.

## Suggested fix (pick one, or combine — see the fix-order warning below)
- **Option A (broad):** sync every user's `User` node into Neo4j eagerly — e.g. at account/network signup or first login — instead of waiting for a reactive trigger.
- **Option B (narrower, lower blast radius):** restructure the tray-read query so the network-wide arm does not depend on the initial `MATCH (user:User {id:$userId})` succeeding — e.g. run it as an `OPTIONAL MATCH`, or move the network arm outside the `CALL(user, …)` subquery so it can match purely on `$userId`/`$networkId` parameters without requiring a bound `user` node.

## ⚠️ Relation to BUG-F — fix order matters
This is the flip side of the exact same mechanism as **BUG-F** (`new-user-network-backlog.md`): BUG-F's "flood" starts the moment a user's `User` node gets created (e.g., by joining any community), because the network arm has no lower time-bound once it's reachable.
**If Option A above ships without also shipping BUG-F's network-arm time-bound fix, every brand-new signup will immediately see the full 30-day backlog of public-community notifications — a regression, not a fix, and worse than today's bug (it would no longer require even joining a community to trigger).** Ship both together, or Option B first as a safer interim fix (it does not create new users flood risk, since it only unblocks the specific network arm read, not a general node-creation change) — then decide on Option A + BUG-F's time-bound as a pair.

## Relation to BUG-F — summary
| | BUG-F | BUG-G (this ticket) |
|---|---|---|
| Trigger | New user **joins a community** (no new event created) | New user **joins nothing**; someone else creates a new public event |
| Symptom | Tray is unexpectedly **full** (old backlog) | Tray is unexpectedly **empty** (missing a new item) |
| Shared root cause | The user's `User` node did not exist until they joined → unblocked all arms, including the un-bounded network arm | The user's `User` node still does not exist → the initial `MATCH` fails → all arms return empty, including the network arm they're otherwise eligible for |
| File | `notification-tray-item.neo4j.ts` (read query) + `user-graph.neo4j.ts` / `community-graph.service.ts` (lazy sync) | same files |

Not contradictory — two symptoms (too much vs. too little) of one shared mechanism (lazy `User` node creation) crossed with one additional independent gap (network arm's missing time-bound, BUG-F).

## Scope / impact
- Any brand-new / zero-community user, on any network with public communities; all platforms (backend-level defect).
- Undermines AC-04's "network-wide" guarantee for exactly the audience it's meant to reach (users outside the community) when they are freshly created — directly hurts the epic's RSVP/reach goal for exactly the segment push/tray is meant to win back.

## Related
- AC-04 (public community → notify entire network, non-members included)
- BUG-F (`new-user-network-backlog.md`) — see comparison table above
- Manual test cases: consider adding a dedicated regression case (e.g. `[ New user, no community ] Verify a public-community event notification still reaches a user with zero community memberships`) to `qa/PDT-3421/_epic/PDT-3421-manual-spec.json`.
