# Group: List & Content — Day 0 intake (QA)

Date: 2026-10-05 · Mode: **no-frame (PRD + Figma) · shadow** (real Day 0)
Inputs:
- PRD: Notion "Group-Content" export, `goldfish/Group-Content 3e65f8b237fc803dbe2dc363591cfe1a.html` (Status: Pitch Ready · Pitch Decision: Committed · by Ghita El Marzouki)
- Figma `M6cjjCbL4R4OUSSCabpFI8`, page `⤷ Group list 🟢` (1567:216866) — Group list 1703:311105 · Categories 1707:176731 · Create category 1731:336644 · Delete category 1761:126990 · Group header + Activities 1731:337649 / 1761:47213 · toasts 1837:154695, 1837:154583. Sibling pages seen, not read: `⤷ Manage members` 1711:336522 · `⤷ Create & Edit groups` 1598:47242
- Console today: legacy `src/pages/communities/*` at `main@e25c3466` · console-next placeholder route `/components/groups` (`src/config/sitePermissions.ts:30`, `src/lib/entitlement.ts:89` `module: 'community', built: false`)
- Core: `social-plus-core@62e15bbb8` (2026-08-27) — `src/services/v3/community.service.js`, `src/modules/social/community-category/index.ts`

Frame draft (QA-written, for PM/Architect to fill): https://claude.ai/code/artifact/6b3207a0-0268-4722-b1de-a1fd849122ee — its Open questions table is now the live list; this file keeps the analysis.
Verdict: **NO FRAME — 3 frame gaps** (rank · events · appetite) · **NOT READY — 4 questions before 03**

## 1 QA frame card

| # | Need | Value | Source | QA uses it for |
|---|---|---|---|---|
| 1 | Capabilities, ranked | C1 An admin views active and deleted groups · C2 An admin searches groups by name and filters them by one category · C3 An admin copies a group's link & ID · C4 An admin deletes a group from the list · C5 An admin views, creates and deletes categories · C6 An admin views a group's content by status tab, keyword, creator and timeframe · C7 An admin opens a content item in its own management surface. **Rank: none** | PRD stories 1, 3, 4 · Figma 1703:311105, 1707:176731, 1731:337649 · C4 placement `UNKNOWN` (PRD "TBC with designer", not drawn on the list) | traceability; test depth |
| 2 | Actors → system roles | Console admin with `VIEW_COMMUNITY_MANAGEMENT` (list, activities) and `VIEW_COMMUNITY_CATEGORY_MANAGEMENT` (categories). The manage grant needed for delete / create category is not named | console `sitePermissions.ts:30` + legacy `/communities` routes · manage grant `derived` | which roles to test with |
| 3 | Platform coverage | console only. SDK / UIKit behaviour unchanged ("configuration layer on top of current capability") | PRD A1 · `derived` | configurations |
| 4 | Boundaries (out) | Permission setup · discovery / recommendations · Comment & Reaction entries · Edit category · membership-only groups · Stories, Clips (Q4) — **and, derived:** Manage members, Create & Edit group and the Analytics tab are their own Figma pages, so their own Solutions | PRD Out of Scope · Figma page split · `derived` | out-of-scope up front |
| 5 | Constraints | entitlement module `community` (not entitled → upgrade-required) · core: name ≤ 1000, description ≤ 5000, ≤ 10 categories per group, keyword ≤ 100, **one** `categoryId` per query, sort `lastCreated/firstCreated/displayName`, cursor paging ≤ 100 with **no total**, category name unique among non-deleted, category delete is soft, **no restore for a deleted group** | console `entitlement.ts:89` · core `community.service.js:298-345, 466-500` · `community-category/index.ts:80-90` | negative cases |
| 6 | Measurement / events | `UNKNOWN` | — | instrumentation cases |
| 7 | Names | customer: "Group" · internal: `community` (core, entitlement, route `/components/groups`) · visibility labels **conflict inside the PRD** (see §6) | Figma · core · PRD | exact copy in expected |
| 8 | Complexity · appetite | `UNKNOWN` (PRD says only "Committed") | PRD header | QA time, depth |

## 2 Rule candidates (from PRD + Figma — NOT rules; the room decides)
- RC1 [product] The list has two tabs, Active and Deleted; a deleted group stays listed as a historical record — PRD §1, Figma 1703:311884/312662
- RC2 [product] A row shows group name, categories (up to N, then "+N"), type, members count and content count, and a View group action — Figma 1703:311105
- RC3 [system] Search matches group name, at most 100 characters — core `community.service.js:470`
- RC4 [system] The category filter takes one category or All categories — core `:478` (single `categoryId`)
- RC5 [product] The list pages 20 per page — Figma "20/page" (total: see Q6)
- RC6 [product] Copy group link & ID copies the shareable link and the ID, toast "Link copied." — Figma 1731:337649 header, 1837:154695
- RC7 [product] Categories list shows name, ID and created date, 10 per page — Figma 1707:176731 (PRD says avatar + name — Q8)
- RC8 [system] A category name is 1–64 characters and unique among non-deleted categories; a deleted category's name can be reused — Figma 1731:336644 "0/64", 1761:126990 · core `community-category/index.ts:80-90`
- RC9 [system] A category avatar must be an image — core `community-category/index.ts:68-75`
- RC10 [product] Deleting a category asks first and removes it from the list without deleting its groups — PRD §3, Figma 1761:126990, toast "Category has been deleted."
- RC11 [product] A group page has three tabs: Activities, Manage members, Group details — Figma 1731:337649
- RC12 [product] Activities has the Posts tabs — Published, Featured, Scheduled, Requires approval (Pending / Declined), Deleted — with keyword search, creator filter and a timeframe ("Showing all time") — Figma 1761:47213 · PRD §4
- RC13 [product] Each item's Manage action opens that content's own management surface — PRD §4, Figma section "Activities / Redirect / Post" 1871:132117
- RC14 [product] The engagement footer follows the reaction and comment entitlements ("Unlock reactions / Unlock comments") — Figma 1731:337649 · same as posts R21
- RC15 [system] A deleted group cannot be restored — core (no restore action in `community.service.js`)

## 3 States the inputs show (S-CAT walk, draft)

| Surface (Figma node) | Drawn | Not drawn — standing look applies (S-CAT §) unless noted |
| --- | --- | --- |
| Group list (1703:311105) | populated, Active / Deleted, paging | §1 skeleton · §2 busy overlay · §3 empty (no groups yet) · §4 filtered to nothing · §6/7 fetch error · §9 denied · §11 not entitled → upgrade-required · §14 group deleted while viewed |
| Categories (1707:176731) | populated, paging | §1–4, §6–9 standard · §3 "no categories yet" copy not written |
| Create category modal (1731:336644) | empty, typed, 0/64 counter | §8 error after submit (generic toast drawn 1837:154583) · **duplicate name** has no drawn error → Q in §5 |
| Delete category (1761:126990) | confirm dialog, success toast | §14 category already deleted by another admin |
| Group header + Activities (1731:337649, 1761:47213) | populated post card, five tabs + Pending/Declined, Unlock footer | everything the Posts spec already lists for the same card (posts ST1–ST99) — if Q2 says "Posts list scoped to the group", reuse them |
| Deleted group, opened | — | not drawn at all → Q4 |

## 4 Early testability flags
- TF1 **A deleted group cannot be restored** (core) → every delete case consumes a group, and the Deleted tab grows forever on shared staging. Need: a per-run group factory and a dedicated network or naming convention. Route: QA infra, raise at 02. — knowledge `TC-COMMUNITY-NO-RESTORE` (added)
- TF2 **Shared category names** — names are unique per network, so parallel runs collide. Need: unique suffix per run; reuse-after-delete is itself a case. — `TC-NETWORK-SETTING`
- TF3 **Activities needs a group seeded in every content status** (published, featured, scheduled, pending, declined, deleted). Pending needs `needApprovalOnPostCreation` on the group and a post by an end user, not the admin. Reuse the Posts fixtures if Q2 = reuse.
- TF4 **Not-entitled states** — `community` not bought → upgrade-required page; reaction/comment not bought → Unlock footer. Need networks in those states. — `TC-ENTITLEMENT-GATE`
- TF5 **Copy group link** depends on the network's deep-link pattern. Need a network with and without one. — `TC-NETWORK-SETTING`
- TF6 **Livestream items** in Activities (if Q3 keeps them) need a stream; no RTMP publisher in the harness → manual. — `TC-RTMP`
- TF7 **Totals** — Figma shows "1-20 of 1,234,123 items"; that total cannot be produced on staging and core gives none today (Q6). Paging itself is testable with 21+ groups.

## 5 Questions for the ticket chat (each passes the 4 criteria)

### Frame gaps (one note to PM, not asked one by one)
- No frame: capability **rank**, **appetite** and **events/measurement** are missing. QA will treat C1, C2, C6 as the core (they are the PRD's stories 1 and 4) unless told otherwise.

### Must answer before 03
- **Q1 → PM:** Does this Solution cover only Group list, Categories and Activities — with Manage members and Create & Edit group as separate Solutions (they are separate Figma pages)? — changes: scope, every capability boundary
- **Q2 → PM + Eng:** Is Activities the Posts list scoped to this one group — same tabs, kebab actions and rules as the Posts Solution — or a review-only view where an item's only action is Manage (redirect)? Figma shows the Posts tabs incl. Scheduled and Requires approval, and on each post a Moderations panel and a Manage action (corrected 2026-10-05 after rendering 1731:337649 — the text dump missed the panel's role); the PRD says "light moderation". — changes: whether ~40 Posts rules apply here or a handful of new ones
- **Q3 → PM:** Which content types does Activities show in this release? Figma draws posts only; the PRD lists Posts, Livestreams and Polls, and lists External content while the decision log says external content cannot belong to a group. — changes: scope, states, cases per type
- **Q4 → Design:** Is "delete group" offered on the list row at all (PRD: "TBC with designer"; Figma draws only View group on the row), or only on Group details? — changes: whether C4 exists in this Solution

### Can wait for Detailing
- **Q5 → Architect:** What does an admin see when opening a group from the Deleted tab — its Activities, read-only, or nothing (View group not drawn for deleted rows)? — changes: RC1, a whole surface's states
- **Q6 → Architect:** The list footer shows "1-20 of N items", but core's community query is cursor-based with no total and today's console shows none. Is a total coming, or does the footer drop N (as Posts R26 had to decide)? — changes: RC5
- **Q7 → PM:** What does "All contents" count — published only (PRD: "Post published count"), or every status / content type? — changes: expected value of the count column
- **Q8 → Design:** Categories table: Figma shows Name, Category ID, Created date; the PRD says Avatar + Name. Which columns? — changes: RC7
- **Q9 → PM:** Today's list also sorts by name / created date and filters flagged groups; Figma draws neither. Drop both? — changes: whether two rules exist
- **Q10 → Design:** Creating a category with a name that already exists — what does the admin see? (core refuses with "Category name already exists"; no error drawn) — changes: the error state of 1731:336644
- **Q11 → Architect:** After a category is deleted, do groups that used it stop showing it in their Category column? — changes: expected of RC10

## 6 QA decided (did not ask)
- Category edit is out (PRD out-of-scope wins over the MVP bullet "Can edit a category"; Figma draws no edit). No question.
- Search / filter / timeframe on Activities follow the Posts rules if Q2 = reuse; otherwise asked at Detailing.
- Categories shown as "up to N then +N": the N is a Figma measurement (count from node data), not a question.
- The "Analytics" tab on the Groups header is a separate feature; out.

### Noted for the sibling Solutions (Manage members · Create & Edit) — not asked here
Found in the same PRD; hand to whoever picks those up:
- Visibility labels conflict: "Public, Invite-only, Discoverable & hidden" (Scope, story 2) vs "Public, Private & Visible, Private & Hidden" (story 8, Figma list). Core has `isPublic` + `isDiscoverable`.
- Membership modes conflict: "Anyone can join, Invite only, Requires approval" vs the decision log (approval forced on for private groups, optional for public). Core has only `requiresJoinApproval` (boolean).
- "The creator is added with the **Owner** role" vs A1 "reuse existing roles, no new role system" — core has no owner role (only the last-moderator guard). Also: a console admin is not a social user, so who is the creator?
- "Removed users with the count" (Scope) vs "Removed members are not shown at all" (story 5, decision log).
- Push notification mode depends on the notification module question still open in the PRD.
