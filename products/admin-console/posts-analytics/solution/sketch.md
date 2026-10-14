# Posts Analytics — structure sketch

Status: 03 agreed 2026-10-01
Figma: ⤷ Analytics under Posts (1012:32193); shared states in Generic ⤷ Analytics (1378:32648)
Frame: https://app.notion.com/p/social-plus/Posts-Analytics-2475f8b237fc821f82468103bdb6655d — metric definitions in its 03 Metric Library. On conflict, Figma follows the frame (user, 2026-09-29).
Disposable. After the direction & scope check only §7 matters.

## 1 Capabilities in scope
- C1 An admin scopes the Overview by activity date range, destination and creator role — frame (Overview 1)
- C2 An admin reads up to 3 key insights: Growth / Decline, Top Content, Content Mix — frame (Overview 2, Appendix A); user, 2026-09-28
- C3 An admin reads 7 key metrics, each compared with the previous equal period — frame (Overview 3)
- C4 An admin reads one selected metric over time — frame (Overview 4)
- C5 An admin reads the top performing posts of the period and opens a post's selected-period and lifetime performance — frame (Overview 5)
- C6 An admin exports the Overview: the time series and every qualifying post — frame (Overview 6)
- C7 An admin scopes Content Performance by creation date, destination, creator role and post type — frame (Content Performance 1)
- C8 An admin reads performance by post type — frame (Content Performance 2)
- C9 An admin reads performance by destination — frame (Content Performance 3)
- C10 An admin searches, reads and exports all posts of the cohort with lifetime metrics — frame (Content Performance 4)
- C11 An admin reads the top creators — frame (Content Performance 5)
- Out by the frame: Explore further, post comparison, all posts by one creator.

## 2 Approach
The Analytics tab already on the Posts page (disabled today) opens with two sub-tabs, Overview and Content Performance. Every number comes from the dashboard's Go API over BigQuery, called by the console with the admin token it already holds; new fields are additive and row-changing modes sit behind query params, so the dashboard's own Content page is unaffected. Metrics follow the 03 Metric Library, which differs from the dashboard's engagement rate and post count. Destination reuses the Posts page model: a group destination is a community and is real, every other kind stays behind the existing mock seam. The backend work lives in `social-plus-dashboard`, so the feature depends on that team.

## 3 Main flows (step level)
- F1 Admin reviews the period: Posts → Analytics → Overview → set date, destination, creator role → read insights, metrics, chart, top posts → open a post → exit
- F2 Admin investigates content: Content Performance → set creation date, destination, creator role, post type → read the three tables → search all posts → open a post → exit
- F3 Admin exports: Export → pick what to export → file saved → exit

## 4 Behaviour that affects scope
- Draft R1 [product] The Overview counts activity inside the period from posts of any age. Content Performance counts posts published in the period and shows their lifetime metrics — frame. Changes which backend queries are needed.
- Draft R2 [product] Engagement rate is engaged users ÷ reach × 100, over posts where engagement was available — Metric Library. The console's number differs from the dashboard's.
- Draft R3 [system] Only a group destination is real (a community). Other kinds stay mocked. User-feed and content posts count in totals and appear in no destination row — Posts R3; user, 2026-10-01.
- Draft R4 [product] Creator role is admin, moderator or user, from the creator's built-in network roles. Custom and community roles count as user — user, 2026-09-29.
- Draft R5 [product] Posts published counts parent posts: a post with 5 images is 1 image post — Metric Library; user, 2026-09-28.
- Draft R6 [system] 133 of 202 networks that posted in the last 30 days send no view events, so reach, impressions and engagement rate show N/A for them — BigQuery, 2026-09-28.
- Draft R7 [system] Nothing records whether engagement was enabled when activity happened. N/A shows when there is no data; Locked shows when the network is not entitled today — Figma 1412:81524.

## 5 Scope options
| Option | Retain / simplify / defer / omit | User impact | Workaround, owner |
| --- | --- | --- | --- |
| A | Retain C1–C11. Export is the period CSV only; the 1P Data API is deferred, as the frame allows | Full frame outcome | Customers needing raw data use the 1P Data API later — PM |
| B | Retain C1, C3–C11; defer C2 insights | No synthesized findings at launch | Read the KPIs and tables — PM |
| C | Retain the Overview (C1–C6); defer Content Performance (C7–C11) | No per-type, per-destination or per-creator view | The dashboard's Content page — PM |

All options: real destination kinds beyond groups wait for core and the SDK; group destinations ship.

## 6 Decisions requested
- PM: accept option A — preferred: A · **decided: A** (user, 2026-10-01)
- PM: Growth / Decline metric and Decline — **decided: follow the frame** (user, 2026-10-01): post engagement, as in its example; Decline passes the frame's eligibility rules, including "exclude insights that might discourage the customer"
- PM: soft-deleted posts — decided first to exclude them; **amended 2026-10-01: count them**, as the Metric Library says (see §7)
- Architect: the console calls the dashboard Go API directly with `Bearer adminToken` + `X-SP-Region`; the dashboard owns the endpoints — **agreed**
- Architect: compute everything with query-time joins over existing tables, no new tables or migrations — **agreed**
- Architect: new fields always-on and additive; params only where row meaning changes — **agreed** (user, 2026-10-01)
- Open: Design aligns Figma to the frame on 8 conflicts (Notion vs Figma review) and draws "data as of", the export menu and the empty insights state
- Open: the dashboard team agrees to build and review the endpoints, add the console origin to CORS and share the 100-slot reservation

## 7 Baseline — written after the direction & scope check
Agreed: option A — C1–C11, period CSV export, group destinations real and other kinds mocked · Excluded: the 1P Data API export; destination kinds other than group until core and the SDK serve them; destination rows for user-feed and content posts (they count in totals only); Mitigations: N/A and Locked states where data or entitlement is missing; Figma follows the frame on the 8 conflicts in the Notion vs Figma review · Assumptions: the dashboard team builds and reviews the endpoints, adds the console origin to CORS and shares the 100-slot reservation; Growth / Decline uses post engagement as in the frame
Deciders: Chanatip as PM, Chanatip as Architect · 2026-10-01 · Loops back to 02: 5
Amended 2026-10-01 (Chanatip as PM and Architect): soft-deleted posts count, as the Metric Library says. They are kept with `is_deleted` in a new table, `dashboard_serving_prod.posts_with_deleted`, loaded incrementally by change time from the raw change log, and read through a new route group `/v1/post-analytics/*`. This replaces "no new tables" and "params on existing routes": nothing existing in the dashboard changes. Swept through spec R5, R6, §5, §6, Open and slices.

Amended 2026-10-02 (Chanatip as PM): the Figma is final and now wins over the frame; the 8 Notion-vs-Figma conflicts are superseded. Decisions D1–D10 from the Figma inventory (https://claude.ai/artifact/8e7yLv1XsYUYHWdog9eRAg): Brand user is its own creator role from `is_brand` in `posts_with_deleted`; engagement rate availability is per network; default range Last 7 days; content type filter single-select and only on Content performance; a post with several types counts in each (no Mixed); export has two modes over 4 widgets; every sort refetches from the API, ranked descending by the selected metric (amended again 2026-10-02: no sorting in the browser); insights are Momentum, Top content and Content mix; no "data as of" line. Swept through spec F1–F3, ST, R4–R18, §5, §6, Open, handoff and slices.

Amended 2026-10-02 in Delivery (Chanatip as PM): only soft-deleted posts count. Hard-deleted posts and all their activity (views, comments, reactions) are left out of every widget and the export, as the Figma tooltip names soft deletes only and a hard delete removes the data. The nightly load removes a hard-deleted post's row from `posts_with_deleted` (it already reads the change log's `DELETE` rows, so the cost is unchanged); activity only counts through a post row, so no route needs a filter. Swept through spec R5, R6, §5, S-R5-4…S-R5-7 and slices SL-00.

Amended 2026-10-02 in Delivery (interaction audit against the final Figma, 12:43Z): the content type filter offers Custom again (1382:110730 supersedes comment #113). Swept through spec R5, spec Open and handoff ST2; copy rows (table descriptions, "Post type", "Published posts", "Avg. engagement rate / post") changed in handoff only.

Amended 2026-10-02 in Delivery (Chanatip as PM, "follow figma"): the Analytics destination filter lists group destinations only — the disabled "Not available yet" kinds are not drawn in 1382:110730; the Posts and Comments & Replies filters keep them. The date chip's × shows on the default range too (1333:103619) and clearing it there is a no-op. App-wide, outside the spec: the 64px app header with a separator (1103:32783), the Posts heading→tabs gap 28 and no Settings tab (1247:5639). Swept through spec R3, R16, S-R3-3 and the handoff filters note; slices name the ids only.

Amended 2026-10-06 in Delivery (Chanatip as PM, "fix all" after the re-audit): the post performance sheet's range chip is a picker of its own — the Figma annotation "effective only in the sheet" (I1538:31773) — starting at the page's range and changing only the sheet. Swept through spec R11.

Amended 2026-10-06 after QA's review of #358 (Chanatip as PM): engagement is comments plus reactions on posts; a decline is shown; the insight thresholds are the spec defaults, fixed in code; Content mix shares are defined with a worked example; an admin holding only VIEW_DASHBOARD does not get Posts (the QA review meeting's answer, replacing the 2026-10-01 decision); a community-scoped admin's numbers cover the selected community; only published or approved posts count, each at its publish time; replies do not count; with one engagement module, Engaged users counts that action. Key insights and the post performance sheet ship in this release. Swept through spec R6, R8, R12, R17, §4, S-R6-5…7, S-R17-1…3, Open and slices SL-06.

## Evidence
- Figma: Overview page (1247:5639) — filters, Key insights, Key metrics, Performance over time, Top performing posts
- Figma: Content Performance page (1394:130286) — by post type, by destination, Top 10 creators, All posts
- Figma: Post detail (1394:129120) — Selected period / Lifetime · Since published
- Figma: Metrics card states (1412:81524) — Filled, Not available, Locked, Loading
- Figma: Chart states (1412:76749) — No data available, No results found, Loading
- Figma: sticky (1331:73532) — "up to 30 days → daily points / >30 days, up to 90 days → weekly / >90 days → monthly"
- Figma: sign note (1459:314922) — "Export options: TBC"
- Console today: src/pages/posts-content/PostsPage.tsx:154-170 — the Analytics tab exists, disabled, "coming soon"
- Console today: src/api/destinations.ts:3-46 — group destination real, other kinds in MOCK_DESTINATIONS
- Console today: src/api/auth/types.ts:101 — the session holds `adminToken`; src/api/chatActivities.ts:41 already sends it as a Bearer to another host
- Core: src/services/v1/api.service.js:1011 — `POST /api/v1/analytics/activities` ingests views; core serves no post-analytics read
- Dashboard: server/internal/feature/content/routes.go:32-39 — `/v1/content/kpis|trend|by-type|reach-trend|posts|posts/{id}/trend`
- Dashboard: server/internal/feature/content/repository.go:46-54 — engagement rate = (reactions + comments) ÷ impressions
- BigQuery `sp-intel.dashboard_serving_prod` — history from 2025-01-01; 69 of 202 active networks send view events (2026-09-28)
- Prior work: build brief https://claude.ai/artifact/L2PsEPTQUrVoS915uajqvS; Notion vs Figma review https://claude.ai/artifact/9PZ4tNyYkX4jc5WSmz1LWV
- User said: "B dont do other from figma and notion" — 2026-10-01 (no destination rows for user-feed or content posts)
- User said: "agree exclude, align with dashboard. for counting deleted posts mark as tbc" — 2026-10-01
- ETL: social-plus-bigquery conversational_analytics/sync_posts_last_90d.sql:128-135 deletes soft- and hard-deleted posts; social-plus-dashboard infra/queries/scheduled/content_posts_reconcile.sql deletes them from serving within 85 days
- BigQuery change log, US, posts created in 30 days: 9,724 of 101,793 later deleted (9.6%) — 2026-10-01
