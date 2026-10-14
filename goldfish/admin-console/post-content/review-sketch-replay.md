# Posts (admin-console/post-content) — Solution review (QA) · sketch

Date: 2026-10-04 · Input: social-plus-console `docs/solution/posts/sketch.md @ 2213f6c7` · Status of the artefact: 02 (pretended — see replay note)
Mode: **Replay, blind** · Core read at `social-plus-core @ 62e15bbb8` (2026-08-27, the local checkout — older than the sha, so it is what the room could have read at 02)
Not re-checked here (solution:check does it): flow with no rule · rule with no test case · n/a state with no reason · empty permission cell · unknown id

> **Replay note — contamination.** The file at 2213f6c7 is the sketch *after* 03 and Delivery: its header reads "03 agreed", and §7 carries the baseline plus five Delivery amendments (R3, R35/R36, R19, R33, R10). The commit message summarises the same decisions. This review reads only §1–§6 as the 02 input, but §7 was seen; SQF4 in particular coincides with the R3 amendment and should not be scored as a blind hit.

## Findings (direction & scope only — detail is held for Detailing)

| # | Ref | Lens | Finding | Proposed fix | Route |
| --- | --- | --- | --- | --- | --- |
| SQF1 | Draft R5 + C7 (F2) | cross-product / core dependency | The composer lets an admin turn on **Feature post and Schedule** together. Core's scheduler stores only `postData` and, at publish time, calls `createPost` and nothing else (core `src/modules/admin/post-scheduler/index.ts` create, `internal.ts` handlePostCreation). Nothing pins a scheduled post when it publishes, so "featured + scheduled" has no mechanism. The approach in §2 says destination is "the one place the approach depends on core work" — this is a second one. | Decide before 03: either (a) `Draft R5b [product] Feature post is disabled while Schedule is on; feature after it publishes`, or (b) add core work "scheduler pins at publish" to §5 options. | huddle (PM + Architect) |
| SQF2 | Draft R4, C5 | core dependency | Core never **replaces** a pin. `pinPost` refuses a full placement — announcement holds 1, default 20 (core `app.config.ts:1161–1162`); global is capped by the network's `maxGlobalPinnedPost` (1–20) and accepts only posts in **public** communities (core `src/modules/pin-content/index.ts:89–137, 389–437`). "Replace" is therefore a console unpin-then-pin across two calls, and the sketch does not say which placement "featured to destination" means. | Architect to name the placement and the replace mechanism now: `Draft R4 [system] Featuring pins at placement <announcement|default>; replacing unpins the current one first; a post in a private community cannot be featured globally`. | chat → Architect |
| SQF3 | Draft R26 | core dependency | "1-20 of 1,234,123 items" needs a total. Core's v5 post query returns `total` only for the reviewing/declined feeds or when a date range is set (core `src/modules/social/post/index.ts:1783–1805`); paging is cursor-based. The Published and Deleted tabs cannot show "of N" without core work. | Choose before 03: (a) footer reads the page range with Previous/Next only where core gives no total, or (b) add "core returns total for published/deleted" to the core-work list. | chat → Architect |
| SQF4 | §5 option D, Draft R3 | testability of a scope option | Under D every non-group destination, source and external content is a **fixture**. Any case run against them verifies the mock, not the product; R9's "mentions are group-only" negative and every non-group destination filter can only be exercised against fake data. QA cannot sign "testable" for behaviour that has no backend. *(Contaminated — see note.)* | PM to pick, knowing this: (a) fixtures, with every non-group case carried as "UI only, not product behaviour", or (b) show non-group destinations as present-but-unavailable, so nothing a tester can choose is fake. | chat → PM |
| SQF5 | Draft R27, §6 Open (rich text) | cross-product scope | The Open item asks which editor library; it does not ask where bold/italic **live** once saved. If formatting is stored, the UIKit must render it or end users see plain text — that is a cross-product scope decision, not an editor choice. | Add to §6: `PM: is UIKit rendering of rich text in this release, or do admins see formatting and end users plain text until the UIKit lands?` | chat → PM |

Route: `PR comment` (wording/fix QA can propose) · `chat → PM` ([product] decision) · `huddle` (two roles disagree) · `QA decides` (failed the 4 criteria — goes to §QA decided)

## Testability flags
- TF1 Draft R6, R15, R30 (time windows: 15-min reschedule cutoff, 1-hour minimum, 30-day ceiling) — QA cannot move the server or scheduler clock; a cutoff case means scheduling ~16 min ahead and waiting. If the cutoff is console-only (the Architect question in §6), it runs on the **browser** clock and a tester can shift it locally; if core enforces it, they wait. Ask now: a configurable cutoff on staging, or accept real-time waits — generic lens *Time*.
- TF2 Draft R7, R20 (Failed scheduled post; cancel after it published) — needs the scheduler to actually fire on staging and a destination deleted before the time; the result arrives late — generic lens *Async*. Ask: does staging run the AWS scheduler, and how long after `scheduledAt` does the status flip?
- TF3 Draft R10 (100 pending scheduled posts) — filling 100 on a shared network collides with everyone else (TC-NETWORK-SETTING). Core reads `networkSetting.postScheduler.limit` per network (core `src/services/v1/post-scheduler.service.ts:81`), so a dedicated network with the limit lowered (for example 3) makes it testable — ask for that network.
- TF4 Draft R13 (no edited mark, no owner notification) and SQF5 rich text — the observable result is in the **UIKit**, a different product and build — generic lens *Cross-product*. Ask: who verifies the app side, on which build?
- TF5 C10, Draft R14, R21 (posts / brand / reaction / comment entitlements) — needs one network per entitlement state under `mode: enforce`; console-next itself is closed to networks whose entitlement is off (TC-ENTITLEMENT-GATE). Ask for named networks per state, or the stub.
- TF6 Draft R11 (deleted or reviewed by someone else mid-process) — two admins at once; console and console-next share one session on staging (TC-SHARED-SESSION) → two browser profiles, two accounts.
- TF7 Draft R2 + the per-tab kebab by role — every role × action needs a standing custom role, because roles cannot be deleted (TC-ADMIN-ROLE-PERMANENT). Ask once for the set.
- TF8 Draft R25 revoked-permission toast — revoking mid-session means editing a shared role, and the console re-checks only on full load (TC-PERMISSION-REVOKED).
- TF9 Draft R18 + C3 "AI moderation results stay visible" and "deleted by AI" — AI moderation is not provisioned on staging (TC-AI-MODERATION) → seeded data or manual.
- TF10 Draft R10 blocked word / blocked link — the blocklist is a network setting shared on staging (TC-NETWORK-SETTING); the case names the network that has it.

## Effort drivers (no numbers unless the team asks)
- Surfaces: list page with 5 tabs + 2 sub-tabs, post card, composer (create / edit published / edit scheduled), post-details sheet, upgrade page.
- Per-tab kebab × role sets (VIEW, MANAGE, EDIT, MODERATE, PIN community vs global, none) — the matrix is the largest single driver.
- Entitlement configurations: post module, brand, reaction, comment — each × enforce/shadow/off.
- Time-based rules: reschedule cutoff, 1-hour minimum, 30-day ceiling, Failed status — real-time waits unless TF1 is answered.
- Concurrency: two-admin cases (Draft R11) need two profiles.
- Cross-product: UIKit side of R13 and rich text; feature/pin visible in the app.
- Env set up by a person: dedicated scheduled-limit network, entitlement networks, blocklist, standing roles.

## QA decided (not asked)
- Draft R13 — core already supports it: the post update keeps `editedAt` when `preserveEditedAt` is sent and records history only for `isAdmin && recordHistory` (core `src/modules/social/post/index.ts:1120, 1131`). No question; QA checks the flags are named at Detailing.
- Draft R12 "10 most recent + original" — core keeps 11 records and never deletes version 1 (core `src/modules/content-history/repositories/content-history.repository.ts:46, 92`). Matches; QA writes the 11th/12th-edit boundary case.
- Draft R6 Architect question (core vs console cutoff) — already asked by the room; QA adds only TF1.

Held for Detailing (detail, not direction — raise at 04):
- C6 / F4 — core refuses approve/decline of one's **own** post (`legacy/post/index.js:1668`), and an admin's post into a community with `needApprovalOnPostCreation` lands in Pending unless the admin holds review permission (`PostValidator.ts:345`). Possible dead end for admin-authored posts.
- Draft R7/R20 — core refuses to edit a FAIL or DONE scheduled post but its delete does not check status at all; what a Failed post offers needs a rule.
- Draft R10 — core refuses only when the waiting count is `> limit`, so a network holds limit + 1.
- Draft R16/R22 — default sort per tab; Featured tab ordering across destinations.

## Summary
Findings: 5 (to room 5 · QA decides 3, + 4 held for Detailing) · Testability flags: 10 · Blocking before 03: SQF1, SQF2, SQF3 (each adds core work the approach does not list) and SQF4 (PM picks D knowing what it leaves untestable)
