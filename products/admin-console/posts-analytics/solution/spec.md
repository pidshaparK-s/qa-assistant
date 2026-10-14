# Posts Analytics — specification

Status: 06 Solution Ready 2026-10-02
Baseline: sketch.md §7, 2026-10-01
Confirmations: Design — confirmed Chanatip, 2026-10-02 · Engineering — confirmed Chanatip, 2026-10-02 · QA — pending (review comment on #358, 2026-10-06) · Architect — confirmed Chanatip, 2026-10-02

## 1 Flows
### F1 Admin reviews the period on the Overview
1. Admin opens Posts and selects the Analytics tab; the Overview sub-tab opens — R17
2. Admin sets the date range; it is the activity period — R1, R16
3. Admin sets a destination and one or more creator roles — R3, R4
4. Admin reads up to 3 key insights — R12
   Alt 4a No insight is eligible → R12, the Key insights section is hidden
   Alt 4b Admin selects "This post" on the Top content card → R11, the post performance sheet opens
5. Admin reads the 7 key metrics, each against the previous equal period — R6, R7
   Alt 5a The network sends no view events → R8, reach, impressions and engagement rate read N/A
   Alt 5b The network is not entitled to comments or reactions → R8, those cards are Locked
   Alt 5c The previous period has no data → R7, the card reads "No baseline to compare"
6. Admin picks a metric on the Performance over time chart — R9
   Alt 6a The scope has no activity → R9, the chart reads "No data available"
7. Admin reads the top performing posts and picks another metric; the list reloads, ranked by that metric — R10
8. Admin opens a post and reads its selected-period and lifetime performance — R11
Exit: the admin stays on the Overview or on the opened post.

### F2 Admin investigates content on Content performance
1. Admin selects the Content performance sub-tab; the date range, destination and creator roles carry over, and the date label reads "Filter by creation date" — R2, R18
2. Admin sets the creation date range, a destination, creator roles and one content type — R2, R3, R4, R5
   Alt 2a The filters match no post → R14, every table reads "No results found"
3. Admin reads performance by content type and ranks it by another metric — R14
4. Admin reads performance by destination, ranks it by another metric and pages through it — R14, R3
5. Admin reads the top creators and changes the ranking — R14, R4
6. Admin searches all posts by keyword, ranks by another metric and pages — R14
7. Admin opens a post and reads its selected-period and lifetime performance — R11
Exit: the admin stays on Content performance or on the opened post.

### F3 Admin exports
1. Admin selects Export in the filter bar — R13
2. Admin keeps "All available data" or picks "Selected filters and period" and the widgets to include — R13
3. Admin selects Export CSV and the file downloads — R13
   Alt 3a The export fails → R13, an error toast, the page unchanged
Exit: the admin is back on the page they exported from.

## 2 States
### Surface: Analytics tab and filter bar (Figma 1247:5639, 1394:130286; filter 1382:110730)
- ST1 [domain] Overview sub-tab: destination, creator roles, activity date, Export; the filter bar sticks to the top while the page scrolls — Figma 1247:5639, 1378:50839
- ST2 [domain] Content performance sub-tab: destination, content type, creator roles, creation date, Export — Figma 1394:130286
- ST3 [domain] filters applied: a chip row under the bar, at most 3 chips per filter with a "+N" chip for the rest, truncated labels with the full label in a tooltip, and Clear all — Figma 1456:101034, 1378:33190
- ST4 [system] loading, first paint — every widget shows its own skeleton [S-CAT §1]
- ST5 [system] loading, refresh after a filter change — each widget keeps its rows under a busy overlay [S-CAT §2]
- ST6 [n/a] empty, nothing yet — the page is read-only; each widget owns its empty state [S-CAT §3]
- ST7 [n/a] empty, filtered to nothing — owned by each widget [S-CAT §4]
- ST8 [n/a] partial — owned by the paginated tables [S-CAT §5]
- ST9 [system] error, network unreachable — each widget shows the content fallback; the filter bar stays usable [S-CAT §6]
- ST10 [system] error, API error — the same per-widget fallback [S-CAT §7]
- ST11 [n/a] error after submitting — nothing is submitted here; export failures sit under Export [S-CAT §8]
- ST12 [system] denied, no role permission — the Analytics tab is hidden; a direct URL opens the access-denied page [S-CAT §9]
- ST13 [system] denied mid-session — the dashboard API never answers 403: it checks only that the token is valid and caches the admin's network and community scope for `TOKEN_CACHE_TTL_SECONDS` (300 in `.env.example`). A revoked token gets 401 once that entry expires, and the console sends the admin to login. A removed console permission takes effect at the console's next session check, not in the API — dashboard: server/internal/shared/middleware/auth.go:50-95, sp_verifier.go [S-CAT §10]
- ST14 [n/a] not entitled — analytics is base layer in core; per-metric entitlement sits on the metric cards [S-CAT §11]
- ST15 [n/a] feature switched off via API — no switch exists for analytics [S-CAT §12]
- ST16 [n/a] quota reached — no quota applies to reads [S-CAT §13]
- ST17 [n/a] item deleted while viewed — data is daily; a deleted post leaves on the next refresh [S-CAT §14]
- ST18 [system] rate limited — only the all-posts keyword search can be throttled, because it goes through core's search API; the dashboard API has no rate limit (social-plus-dashboard server/, no 429 path). Inline notice under the search field [S-CAT §15]
- ST19 [n/a] offline — the console is online-only [S-CAT §16]
- ST20 [system] admin has no console account — access-required page [S-CAT §17]

### Surface: Key insights (Figma 1247:5639; card 1531:163544)
- ST21 [domain] 1 to 3 insight cards, each a type badge and one sentence of at most 2 lines — Figma 1871:91421
- ST22 [system] loading, first paint — three card skeletons [S-CAT §1]
- ST23 [system] loading, refresh — cards stay under a busy overlay [S-CAT §2]
- ST24 [system] empty — no eligible insight; the whole Key insights section is hidden, never filler cards — Figma 1538:30978 "All non available → Hide Key insights" [S-CAT §3]
- ST25 [n/a] empty, filtered to nothing — same as ST24; the insight set is recomputed for the scope [S-CAT §4]
- ST26 [n/a] partial — at most 3 cards, no paging [S-CAT §5]
- ST27 [system] error, network or API — the section shows the content fallback [S-CAT §6, §7]
- ST28 [n/a] §8–§17 — covered by the page surface

### Surface: Key metrics (Figma 1412:81524)
- ST29 [domain] filled — value and delta "+10% vs. last 7 days" for a preset, "+10% vs. 18 Sep – 25 Sep 2025" for a custom range — Figma 1412:81479, 1531:163476
- ST30 [domain] no baseline — value and "No baseline to compare"
- ST31 [domain] not available — "N/A" for a metric the scope has no data for
- ST32 [domain] locked — label "Unlock comments" or "Unlock reactions", "N/A", both greyed, a lock icon in place of the info icon, no delta; tooltip "Unlock <comments|reactions> to boost engagement" with a "View <comments|reactions>" link — Figma 1531:163476, 1451:95513 [S-CAT §11]
- ST33 [system] loading, first paint — card skeleton [S-CAT §1]
- ST34 [system] loading, refresh — values stay under a busy overlay [S-CAT §2]
- ST35 [n/a] empty — a card always shows a value, N/A or Locked [S-CAT §3, §4]
- ST36 [n/a] partial — 7 fixed cards [S-CAT §5]
- ST37 [system] error, network or API — the section shows the content fallback [S-CAT §6, §7]
- ST38 [n/a] §8–§17 — covered by the page surface

### Surface: Performance over time (Figma 1247:5639; states 1412:76749)
- ST39 [domain] area chart for the selected metric, in that metric's colour; title "Performance over time", subtitle "Daily totals for the selected metric, by the date the activity happened."; hover tooltip with the date, metric name and value; no legend — Figma 1247:5639, 1568:177793
- ST40 [system] loading, first paint — a spinner in the plot area — Figma 1513:112210 [S-CAT §1]
- ST41 [system] loading, refresh — the old line stays under a busy overlay [S-CAT §2]
- ST42 [system] empty — "No data available · Data activity is unavailable for the selected scope." — Figma 1412:76731 [S-CAT §3]
- ST43 [system] empty, filtered to nothing — "No results found · Try adjusting the search keywords, filters or date range to get results." — Figma 1513:112191 [S-CAT §4]
- ST44 [n/a] partial — one series, no paging [S-CAT §5]
- ST45 [system] error, network or API — the card shows the content fallback [S-CAT §6, §7]
- ST46 [n/a] §8–§17 — covered by the page surface

### Surface: Top performing posts (Figma 1452:105407; table states 1378:66318)
- ST47 [domain] 10 rows ranked by the selected metric, a metric Select (default Reach), and a "View performance" icon action pinned on the right of each row; the table scrolls sideways inside its card — Figma 1452:105407, 1833:102509
- ST48 [system] loading, first paint — table skeleton [S-CAT §1]
- ST49 [system] loading, refresh — rows stay under a busy overlay [S-CAT §2]
- ST50 [system] empty — no post had activity in the period [S-CAT §3]
- ST51 [system] empty, filtered to nothing — "No results found" [S-CAT §4]
- ST52 [n/a] partial — a fixed top 10, no paging [S-CAT §5]
- ST53 [system] error, network or API — content fallback [S-CAT §6, §7]
- ST54 [n/a] §8–§17 — covered by the page surface

### Surface: Content performance tables (Figma 1394:130286 — by content type 1432:83271, by destination 1457:241015, top creators 1452:107752, all posts 1452:112240)
- ST55 [domain] each table: title with info icon, description, metric Select that reloads the table ranked by that metric; column heads are not clickable — Figma 1394:130286
- ST56 [domain] all posts: keyword search
- ST57 [system] loading, first paint — table skeleton per table [S-CAT §1]
- ST58 [system] loading, refresh — rows stay under a busy overlay [S-CAT §2]
- ST59 [system] empty — no post was published in the period [S-CAT §3]
- ST60 [system] empty, filtered to nothing — "No results found" per table; all posts adds the search keyword to the hint [S-CAT §4]
- ST61 [system] partial — by destination pages 10 at a time with previous and next; all posts pages with first, previous, "10/page" and next; both read "1-10 of N items" — Figma 1457:241015, 1452:112240 [S-CAT §5]
- ST62 [system] error, network or API — content fallback per table [S-CAT §6, §7]
- ST63 [n/a] §8–§17 — covered by the page surface

### Surface: Post performance sheet (Figma 1837:87272; cards 1538:33610)
- ST64 [domain] Selected period — header "Performance", "Post in <destination>", creator byline and created date, the post content (existing renderer, "See more" after 3 lines, no moderation log), then 6 cards with icons: reach, impressions, comments, reactions, engaged users, engagement rate for the page's date range, with the range chip
- ST65 [domain] Lifetime — the same cards since the post was published, with "Since published"
- ST66 [system] loading, first paint — skeleton [S-CAT §1]
- ST67 [n/a] loading, refresh — the view opens once per post [S-CAT §2]
- ST68 [system] empty — a metric with no data reads N/A, as on the metric cards [S-CAT §3]
- ST69 [n/a] filtered to nothing, partial — one post, no filters, no paging [S-CAT §4, §5]
- ST70 [system] error, network or API — content fallback [S-CAT §6, §7]
- ST71 [n/a] §8–§17 — covered by the page surface

### Surface: Export (Figma 1548:177712)
- ST72 [domain] the export popover — "All available data" (default) or "Selected filters and period" with "Export all" and one checkbox per widget, "<n> of 4 selected", and Export CSV
- ST73 [system] error after submitting — error toast; the page stays as it was [S-CAT §8]
- ST74 [system] exporting — the Export button shows a busy state until the file is ready [S-CAT §2]
- ST75 [n/a] other entries — the export has no list, filter or permission of its own

## 3 Rules
- R1 [product] On the Overview, every metric, chart point and top-post rank counts activity whose timestamp falls inside the selected date range, from posts of any age. A post published before the range counts when it had activity inside it — frame, Overview 1, 4, 5; Metric Library.
- R2 [product] On Content Performance, a post is in scope when it was published inside the selected date range. Its metrics are lifetime: from publication to the latest data day — frame, Content Performance 1.
- R3 [system] A destination of kind group is a community and is real; it matches posts whose target is that community. The Analytics destination filter lists group destinations only, as the final Figma draws it (1382:110730; user, 2026-10-02); the other kinds stay mock data in the Posts and Comments & Replies filters — src/api/destinations.ts:3-46; Posts spec R3 — amended 2026-10-02, see sketch.md §7. Posts on a user feed or on other content count under "All destinations" and appear in no destination row; choosing a destination leaves them out — user, 2026-10-01. They are 27% and 2% of top-level posts — BigQuery, 2026-09-28.
- R4 [product] A post's creator role is the first match below. A brand user is Brand user whatever roles they hold; otherwise the role comes from the creator's built-in network roles, and custom or community roles count as User. The creator role filter is multi-select over the four — user, 2026-09-29 and 2026-10-02 (amended: Brand user is its own bucket); Figma comment #88, 1452:107752.

| Creator | Creator role |
| --- | --- |
| `is_brand` is true | Brand user |
| network roles include `global-admin` | Admin |
| network roles include `super-moderator`, `moderator`, `community-moderator` or `channel-moderator` | Moderator |
| anything else, or none | User |

- R5 [product] Posts published counts parent posts: a post with 5 images is 1 post. A post's types are the media kinds it holds; a post with video and images is both Video and Photo. It shows a chip for each type, and in Performance by content type it counts once in each of its types' rows, so those rows can add up to more than Posts published. A poll or a live stream keeps its own type whatever else it holds. Types read Text, Photo, Video, Audio, File, Clip, Poll, Live stream and Custom — Metric Library; core src/modules/social/post/index.ts:103-113, 246-265; user, 2026-09-28 and 2026-10-02 (amended: no Mixed type); Figma 1871:91605. The content type filter is single-select and offers Text, Photo, Video, File, Audio and Custom — Figma 1382:110730 (final, 2026-10-02; supersedes comment #113) — amended 2026-10-02, see sketch.md §7. Soft-deleted posts still count wherever they were published or active in the range, as the Metric Library and the Figma tooltip ("including posts that were later soft deleted") say; they are kept with `is_deleted` in `posts_with_deleted` (§5). Hard-deleted posts are left out entirely, with all their activity (views, comments, reactions), on every widget and in the export: the nightly load removes their rows from `posts_with_deleted`, and activity only counts through a post row, so a late hard delete takes effect on the next run — amended 2026-10-02, see sketch.md §7 — Metric Library; user, 2026-10-01 (amended from "left out").
- R6 [product] Metrics are defined by the 03 Metric Library — frame A3:

| Metric | Counts |
| --- | --- |
| Posts published | parent posts published or approved in the period, each at its actual publish time (an approved post at its approval time); pending, declined and scheduled posts do not count; soft-deleted posts included, hard-deleted posts and their activity excluded — amended 2026-10-06, see sketch.md §7 |
| Reach | unique users who viewed at least one post in the period |
| Impressions | post views in the period; repeat views count; each view event once |
| Comments | top-level comments made on posts in the period; replies and reactions on comments do not count — amended 2026-10-06, see sketch.md §7 |
| Reactions | reactions made on posts in the period |
| Engaged users | unique users with at least one reaction or comment on a post in the period |
| Engagement rate | engaged users ÷ reach × 100; N/A when the network has neither comments nor reactions (R8). "Enabled" in the Figma tooltip means the network's modules, not a per-post setting — user, 2026-10-02 |
| Average engagement rate per post | the mean of the engagement rates of the creator's posts in scope (Top creators only) |

- R7 [product] Each key metric compares with the previous period of the same length that ends the day before the range starts, shown as a signed percentage. A preset range reads "vs. last 7 days" (the preset's name); a custom range reads "vs. <previous from> – <previous to>". A rise is green #16A34A, a fall red #DC2626, no change #171717, through the DS success, destructive and foreground colours. When the previous period has no data or starts before coverage, the card reads "No baseline to compare" — frame, Overview 3; Figma 1531:163476, 1531:163455; dashboard server/internal/feature/content/filter.go:127-145; user, 2026-10-02.
- R8 [system] A metric shows N/A, never 0, when its data cannot exist for the scope. 0 shows only when the data exists and nothing happened — frame, Overview 3; Metric Library. With only one engagement module bought, Engaged users counts that action alone — amended 2026-10-06, see sketch.md §7.

| Condition | Card shows |
| --- | --- |
| The network sent no view events in the range | Reach, Impressions, Engagement rate: N/A |
| The range ends before coverage starts (2025-01-01) | every metric: N/A |
| The network is not entitled to comments (module `comment` locked) | Comments: Locked — "Unlock comments", tooltip "Unlock comments to boost engagement" + "View comments" |
| The network is not entitled to reactions (module `reaction` locked) | Reactions: Locked — "Unlock reactions", tooltip "Unlock reactions to boost engagement" + "View reactions" |
| Both modules are locked | Engaged users and Engagement rate: N/A (no eligible engagement action) |
| Data exists and nothing happened | 0 |

  Entitlement is read today, not as it was when the activity happened; nothing records the history — src/lib/entitlement.ts:53-66; dashboard handler.go:74-79.
- R9 [product] The chart shows one metric at a time from the 7 in R6; Posts published is the default. Each metric has its own colour: Posts published chart-7, Reach chart-15, Impressions chart-9, Comments chart-13, Reactions chart-11, Engaged users chart-14, Engagement rate chart-16 — Figma 1568:177793. Each point is that metric over one interval, by activity date, never cumulative. The interval follows the range length: up to 30 days daily, 31 to 90 days weekly, over 90 days monthly — frame, Overview 4; Metric Library; Figma sticky 1331:73532. As on the dashboard, a week starts on Monday (ISO), days are UTC, and the chart carries no timezone label; a CSV export names the timezone in its header rows — social-plus-dashboard server/internal/feature/content/service.go:148-151, src/shared/charts/grain.ts:36, src/lib/exportMetadata.ts:31-42; user, 2026-10-01.
- R10 [product] Top performing posts (titled "Top posts" on screen) loads 10 posts ranked by Reach over activity inside the range. The metric Select offers Reach, Impressions, Comments, Reactions, Engaged users and Engagement rate; picking one requests the list again and shows the top 10 by that metric, highest first. A filter or date change reloads with the metric still selected. Columns: #, post, content type, creator, destination, reach, impressions, comments, reactions, engaged users, engagement rate, created date, and a pinned "View performance" action. A post with no caption reads "No caption added." Metrics are for the range, not lifetime — frame, Overview 5; Figma 1452:105407, annotation "Show default metric: Reach" 1432:87017; user, 2026-10-02 (amended: sorting refetches, not in the browser).
- R11 [product] Post performance opens in a right sheet from a table row's "View performance" action or the Top content insight's "This post". It shows two views of the same metrics — reach, impressions, comments, reactions, engaged users, engagement rate: Selected period, for the page's date range, and Lifetime, since the post was published. The sheet's range chip starts at the page's range and opens its own picker; a range picked there changes only the sheet, not the page or its URL. Clearing the chip switches to Lifetime — frame, Overview 5; Figma 1837:87272, 1538:33610, connector 1837:89405, annotation "effective only in the sheet" I1538:31773 — amended 2026-10-06, see sketch.md §7.
- R12 [product] Key insights show up to 3 cards chosen from three types, only the eligible ones, never filler; with none eligible the section is hidden — frame, Overview 2 and Appendix A; user, 2026-09-28; Figma 1538:30978, 1871:91421:

| Type | Sentence | Eligible when |
| --- | --- | --- |
| Momentum | "Post engagement {increased/decreased} {delta}% compared with the previous period." | the previous period has data and the change passes the threshold |
| Top content | "This post generated the most engagement in {destination}." — "This post" opens the post performance sheet (R11) | at least 2 posts had engagement in scope |
| Content mix | "{Type} posts represents {share%} of posts but drives {share%} of engagement." | at least 2 content types in scope and the gap passes the threshold |

  Engagement means comments plus reactions on posts. An insight is dropped when the filters already decide it, the data is too thin, or it repeats another card; a decline is shown (Momentum reads "decreased"). Each sentence fits 2 lines. Thresholds: Momentum needs at least 10 posts and a change of 10% or more; Top content needs at least 2 posts with engagement; Content mix needs at least 10 posts and a gap of 10 points or more. They are fixed in the dashboard, not configurable.

  Content mix: post share of a type = posts of that type ÷ posts published in the period; engagement share = engagement on posts of that type ÷ engagement on posts published in the period. A post with several types counts in each (R5), so shares can sum past 100%. The card names the type whose engagement share most exceeds its post share, when that gap is 10 points or more. Example: 10 posts, 4 Photo and 3 Video, one of them both. Photo is 40% of posts, Video 30%. Of 100 engagement, Photo posts have 70 and Video posts 50. Photo's gap is 30 points and Video's 20, so the card reads "Photo posts represents 40% of posts but drives 70% of engagement." — amended 2026-10-06, see sketch.md §7.
- R13 [product] Export downloads CSV from a popover with two choices. "All available data" (default) exports every widget of the current sub-tab over the last 90 days ending yesterday, without filters. "Selected filters and period" exports the widgets the admin ticks ("Export all" and one per widget, all ticked by default, "<n> of 4 selected") for the filters and range in force. Widgets: on the Overview, Key insights, Key metrics, Performance over time (all 7 metrics per interval) and Top performing posts (every post with activity in the range, not only the top 10); on Content performance, the four tables, all rows — Figma 1548:177712; user, 2026-10-02.
- R14 [product] Content performance has four tables with lifetime metrics (R2). Each has a metric Select (Published posts, Reach, Impressions, Comments, Reactions, Engaged users, Engagement rate). Picking a metric requests the table again, ranked by that metric, highest first, from page 1. A filter or date change reloads with the metric still selected. Nothing is sorted in the browser:

| Table | Rows | Default | Paging |
| --- | --- | --- | --- |
| Performance by content type | one per content type (R5); engagement rate drawn as a bar | Published posts | none |
| Performance by destination | one per group destination (R3) | Published posts | 10 per page |
| Top creators | top 10 creators by the selected metric, with creator role (R4); last column average engagement rate per post | Published posts | none |
| All posts | every post in scope; keyword search on title and text | Reach | 10 per page |

  Figma 1394:130286, 1452:107752, 1452:112240; annotation "Re-rank the order once sorting or filter changed" 1432:83271; user, 2026-10-02 (amended: every sort refetches).
- R15 [system] Data is one day behind: the pipeline loads the previous UTC day at 05:00 UTC. History starts 2025-01-01. The page shows no "data as of" line; Figma draws none — frame, product decision "Use available historical data"; social-plus-dashboard infra/Pulumi.prod.yaml:45-46; BigQuery, 2026-09-28; Figma final, 2026-10-02.
- R16 [product] The date picker offers Last 7 days, Last 2 weeks, Last 3 weeks, Last 30 days and a calendar. Every range ends yesterday at the latest; the calendar disables today and later, because data is one day behind (R15). There is no "Today" and no "All time" — dropped by user, 2026-10-01. The page opens on Last 7 days ending yesterday; clearing the date chip goes back to that default — Figma 1432:87588 annotation "default: Last 7 days"; user, 2026-10-02 (amended from the last 30 days). The chip's × shows on every range, the default too, where it changes nothing — Figma 1333:103619; user, 2026-10-02 — amended 2026-10-02, see sketch.md §7.
- R17 [system] Posts, and so its Analytics tab, needs `VIEW_POST_AND_COMMENT_MANAGEMENT` (§4). An admin holding only `VIEW_DASHBOARD` does not get Posts and uses the Dashboard instead (QA review meeting 2026-10-02; user, 2026-10-06) — amended 2026-10-06, see sketch.md §7. Data is scoped to the admin's network from the token. An admin whose role assignments are scoped to communities sees only those communities' posts. The dashboard API checks no console permission; the console's gate (§4) is the only one, accepted for MVP — dashboard server/internal/shared/middleware/auth.go:50-95, sp_verifier.go; user, 2026-10-01.
- R18 [product] Switching sub-tabs keeps the date range, destination and creator roles. Content type applies only on Content performance; the final Overview frame hides it. The date picker header reads "Filter by activity date" on the Overview and "Filter by creation date" on Content performance — user, 2026-10-01 and 2026-10-02; Figma 1247:5639, 1432:87588, 1807:82476.

## 4 Permissions
Object: post analytics (both sub-tabs, post performance, export). Every action is a read; export is a read that downloads.
Gate (user, 2026-10-06, following the QA review meeting): Posts and both its tabs need `VIEW_POST_AND_COMMENT_MANAGEMENT` (src/config/sitePermissions.ts). An admin holding only `VIEW_DASHBOARD` does not get Posts and uses the Dashboard. Checked with `hasRoleAssignmentPermission` (src/lib/permissions.ts:9-16); an admin with no role assignment has full access — amended 2026-10-06, see sketch.md §7.

| Console role (core seed) | `VIEW_POST_AND_COMMENT_MANAGEMENT` | `VIEW_DASHBOARD` | view Overview | view Content Performance | open post performance | export |
| --- | --- | --- | --- | --- | --- | --- |
| No role assignment (super-admin, legacy admin) | full | full | ✓ all | ✓ all | ✓ | ✓ |
| console-admin | ✓ | ✓ | ✓ all | ✓ all | ✓ | ✓ |
| console-community-manager | ✓ | ✓ | ✓ assigned communities (R17) | ✓ assigned communities | ✓ | ✓ |
| console-moderator | ✓ | ✓ | ✓ all | ✓ all | ✓ | ✓ |
| console-brand-partner | ✓ | – | ✓ all | ✓ all | ✓ | ✓ |
| console-content-creator | ✓ | – | ✓ all | ✓ all | ✓ | ✓ |
| console-viewer | ✓ | – | ✓ all | ✓ all | ✓ | ✓ |
| console-analyst | – | ✓ | – (no Posts; uses the Dashboard) | – | – | – |

Roles and grants: core src/modules/authorization/legacy/role/admin-role-permission.js:5-190.

Denied behaviour
| Role / action | Looks like |
| --- | --- |
| neither permission / Posts in the sidebar | hidden; direct URL → access-denied page [S-CAT §9] |
| `VIEW_DASHBOARD` only / Posts | hidden; direct URL → access-denied page; the admin uses the Dashboard [S-CAT §9] |
| `VIEW_POST_AND_COMMENT_MANAGEMENT` only / Analytics tab | shown |
| community-scoped admin / "All destinations" | not offered; the destination filter starts on the first assigned community, and numbers cover the community selected (src/components/comments-and-replies/DestinationFilter.tsx, useDestinationScope) |

Tier gating: none for the page — analytics is base layer in core (module-catalog `analytics`). Comments and reactions cards: module `comment` / `reaction` not entitled → Locked card with tooltip (R8).
The dashboard API enforces none of this; only the network and community scope (R17).

## 5 API surface
Two hosts. **Dashboard API** (`social-plus-dashboard` Go service, `VITE_DASHBOARD_API_BASE_URL`): `Authorization: Bearer <adminToken>`, `X-SP-Region`; every route takes `start_date`, `end_date`, `communities`, `roles`, `tags`, `role_bucket` (`admin|moderator|brand|user`, repeatable), `post_type`; it is not in `governance/api/routes.json`, so each call carries `api-exempt: dashboard API`. Rows prefixed `dashboard` are that host; `solution:check` and `api:check` validate only the core rows. **Core**: the console's existing `client`.
Isolation rule (Architect, amended 2026-10-01): the console reads a **new route group `/v1/post-analytics/*`** over a **new table** `dashboard_serving_prod.posts_with_deleted` plus the existing event tables (`impressions`, `reactions`, `comments`). The dashboard's `/v1/content/*` routes, the `posts` table and its jobs are not changed.

| Call | Status | Backend | Rules |
| --- | --- | --- | --- |
| dashboard GET /v1/post-analytics/overview/kpis | missing | proposed: the 7 metrics + previous period, `coverage_start`; posts from `posts_with_deleted`, activity from the event tables by data point date | R1, R5, R6, R7, R8, R15 |
| dashboard GET /v1/post-analytics/overview/timeseries | missing | proposed: all 7 metrics per interval (`day\|week\|month`, ISO Monday weeks, UTC days); distinct metrics computed per interval | R1, R9 |
| dashboard GET /v1/post-analytics/overview/top-posts | missing | proposed: 10 posts ranked by `sort` (one of the 6 metrics, default reach), descending, over activity inside the range; any post age, deleted posts included | R1, R5, R10 |
| dashboard GET /v1/post-analytics/insights | missing | proposed: 0–3 typed insights with evidence; the console renders the wording | R12 |
| dashboard GET /v1/post-analytics/content/by-type | missing | proposed: one row per content type, ordered by `sort` descending; a post counts in each of its types; 7 lifetime metrics, publish-date cohort | R2, R5, R14 |
| dashboard GET /v1/post-analytics/content/by-destination | missing | proposed: one row per community (group destination), ordered by `sort` descending, paged by `limit`/`offset` | R2, R3, R14 |
| dashboard GET /v1/post-analytics/content/creators | missing | proposed: top 10 creators by `sort` descending (default published posts) with all metrics and the creator role bucket | R2, R4, R14 |
| dashboard GET /v1/post-analytics/content/posts | missing | proposed: cohort posts with lifetime metrics; `ids` from core search, `sort`, `limit`, `offset` | R2, R14 |
| dashboard GET /v1/post-analytics/posts/{id} | missing | proposed: one post's selected-period and lifetime totals | R11 |
| dashboard GET /v1/post-analytics/export | missing | proposed: streamed CSV; `mode=all|selected`, `widgets` — each chosen widget of the sub-tab | R13 |
| GET /api/v2/search/posts | exists | core keyword search → post public ids sent as `ids` — governance/api/routes.json | R14 |
| GET /api/v3/posts/list | exists | core hydration: title, text, media thumbnail, creator — governance/api/routes.json | R10, R14 |
| GET /api/v3/users/list | exists | core hydration of creator names and avatars — governance/api/routes.json | R14 |
| GET /api/v3/communities | exists | core: group destination names for the filter and table — governance/api/routes.json; src/api/destinations.ts | R3 |
| GET /admin/v1/admin | exists | the session check the console already makes; R8 reads `networkSetting.moduleEntitlement` from it, so the page adds no call — src/api/auth/types.ts:79; src/lib/entitlement.ts:53-66 | R8 |

Data (new, dashboard `infra/`): `dashboard_serving_prod.posts_with_deleted` has the columns of `posts` — same post-type allowlist (no `com.*`), `content_types`/`kind_count` rollup, creator role and tag ids, `community_id` — plus `is_brand` (from `convo_analytics.users`, read in the same join as the role and fixed at load time — social-plus-bigquery conversational_analytics/sync_users.sql:111), `is_deleted` and `deleted_at`; a hard-deleted post's row is removed (the change log's `DELETE` rows), so it and its events count nowhere — amended 2026-10-02, see sketch.md §7. It is loaded **incrementally by change time**: each daily run reads change rows from `append_only_<region>_eko_messaging.posts` newer than its per-region watermark minus a 2-day overlap (`datastream_metadata.source_timestamp`, the pattern of social-plus-bigquery conversational_analytics/sync_posts_last_90d.sql), upserts the latest version of each post, and sets `is_deleted` on a soft or hard delete whatever the post's age; the watermark moves only after the write. A one-off backfill loads from 2025-01-01. Watermark rows use their own keys in `sp-intel.events.sync_watermark`.
Table name `posts_with_deleted` (user, 2026-10-01): it says how it differs from `posts`, so the two are not mixed up. Jobs (approved, user 2026-10-01): **2 new**, both in `social-plus-dashboard/infra/queries/`, scheduled from `infra/main.go`:
- `posts_with_deleted` load (`scheduled/posts_with_deleted.sql`) — daily at 05:00 UTC, one scheduled query for us, eu and sg with a watermark per region, after `content_creator_dims` (02:30): the incremental load above.
- `posts_with_deleted` backfill (`backfill/posts_with_deleted_full_backfill.sql`) — once, by hand, before go-live: every post since 2025-01-01, deleted ones included, from the raw change log.
No reconcile job: the load flags deletions itself. Reused unchanged: `content_creator_dims`, `content_impressions`, `content_reactions`, `content_comments`.
Size: the same filters as `posts`, so about 2.3M rows and 1 GB (the 2.1M rows of `posts` plus about 10% deleted posts, BigQuery 2026-10-01). A daily run reads about two days of changes; the backfill scans the raw log once (US about 612 GB).

Errors (dashboard server/internal/shared/httpx/http.go, middleware/auth.go):
| Response | Meaning | Console |
| --- | --- | --- |
| 400 `start_date, end_date required` / bad date | malformed request | content fallback; a bug (R16 always sends a range) |
| 400 `X-SP-Region header required` | missing region header | content fallback; a bug |
| 401 invalid or missing bearer | token revoked or expired | redirect to login (ST13) |
| 403 `community not accessible` | a community outside the admin's scope was requested | content fallback; R17 keeps the filter inside scope |
| 503 `backend` / `auth verifier error` | BigQuery or core verify failed | content fallback per widget (ST10) |
| 504 `timeout` (60 s) | query too slow | content fallback per widget (ST10) |

Sorting: every list route takes `sort` (the selected metric) and orders by it descending, then by id, so a tie is stable; the console refetches on every metric change and never sorts rows itself. content/posts and content/by-destination page by `limit` (10) and `offset`; top posts and top creators are a fixed 10.

Core work: none. Destination kinds beyond group and an engagement-availability history stay out of scope (sketch §7).
Dashboard work (owner: this squad, built in parallel with the console UI; user, 2026-10-01): the new table, its incremental load job and backfill; the `/v1/post-analytics/*` route group; the console origin in `CORS_ALLOWED_ORIGINS`; impressions counted as distinct `impression_id` with `content_type = 'post'` (R6). Nothing existing changes: `/v1/content/*`, `dashboard_serving_prod.posts`, `content_posts.sql`, `content_posts_reconcile.sql` and the dashboard UI stay as they are. Shared, not changed: the 100-slot BigQuery reservation, the Go service deploy and its middleware.
Console work (owner: this squad): a `dashboardClient` with Bearer token and region header; `api-exempt` on each call. The console builds against the response shapes above while the endpoints land, so the two tracks run in parallel.
Version impact: additive — a new route group and a new table; no existing route, table or job changes — Architect, amended 2026-10-01 (sketch §7).

## 6 Test cases
### S-R1-1 Overview counts activity on an older post
Given a post published 20 Aug got 50 impressions on 5 Sep When the admin picks 1–30 Sep on the Overview Then Total impressions includes those 50 And the post can rank in Top performing posts
### S-R1-2 Overview ignores activity outside the range
Given a post published 5 Sep got 30 impressions on 2 Oct When the admin picks 1–30 Sep Then those 30 impressions are not counted
### S-R2-1 Content Performance uses publish date
Given post A published 20 Aug, post B published 5 Sep When the admin picks 1–15 Sep on Content Performance Then All posts lists B and not A
### S-R2-2 Content Performance metrics are lifetime
Given post B published 5 Sep got 10 reactions on 2 Oct When the admin picks 1–15 Sep on Content Performance Then B shows the 2 Oct reactions in its lifetime metrics
### S-R3-1 Group destination filters to its community
Given posts in community X and community Y When the admin picks destination X Then every widget counts only X's posts
### S-R3-2 User-feed posts count under All destinations only
Given a network with community posts and user-feed posts When the admin keeps "All destinations" Then totals include the user-feed posts And Performance by destination has no row for them
### S-R3-3 The analytics destination menu lists communities only
Given the Analytics destination picker is open Then it lists group destinations only And Homepage, Product detail and "Not available yet" are not in it
### S-R4-1 Creator role buckets
Given creators holding global-admin, moderator, a custom role, and no role When the admin filters by each role Then global-admin is Admin, moderator is Moderator, the custom role and no role are User
### S-R4-2 Brand user is its own bucket
Given a brand user who also holds moderator posted When the admin filters by Brand user Then the posts are included And filtering by Moderator leaves them out
### S-R4-3 Community moderator is User
Given a creator moderates a community but holds no network moderator role When the admin filters by Moderator Then that creator's posts are excluded
### S-R5-1 A multi-image post counts once
Given a post with 5 images When the admin reads Posts published and by content type Then it counts 1 post, type Photo
### S-R5-2 A post with two types counts in both
Given a post with 2 images and 1 video When the admin reads by content type Then it counts once under Photo and once under Video And Posts published counts it once And its row shows both chips
### S-R5-3 Poll keeps its type
Given a poll with images When the admin reads by content type Then it counts under Poll, not Photo
### S-R5-4 A soft-deleted post still counts in its month
Given a post published in January and soft-deleted in February When the admin filters January Then it counts in Posts published And it can rank in Top performing posts And it is listed in Content Performance
### S-R5-5 A late deletion is still flagged
Given a post published in January and soft-deleted in May When the next daily load runs Then the post's row carries `is_deleted` And it still counts in January
### S-R5-6 A hard-deleted post and its activity are left out
Given a post published in January with 40 impressions and 3 comments, hard-deleted in February When the admin filters January Then Posts published, Total impressions and Total comments leave it out And it is not in Top posts, Content performance or the export
### S-R5-7 A late hard delete takes effect
Given a post counted in January When it is hard-deleted in May and the next daily load runs Then its row is removed from `posts_with_deleted` And January no longer counts it or its activity
### S-R6-1 Engagement rate formula
Given 40 viewers, 8 of them reacted or commented When the admin reads Engagement rate Then it shows 20.0%
### S-R6-4 Engagement rate ignores per-post settings
Given the network has comments and reactions When the admin reads Engagement rate Then reach from every post in scope is the denominator
### S-R6-2 Engaged users counts people once
Given one user left 5 reactions and 2 comments on two posts When the admin reads Engaged users Then that user counts 1
### S-R6-3 Impressions count each view event once
Given a view event is stored twice with the same id When the admin reads Total impressions Then it counts 1
### S-R6-5 A post approved the following month counts then
Given a post created on 28 Sep in a group that requires approval And approved on 2 Oct When the admin views 1–31 Oct Then Posts published includes it And 1–30 Sep does not
### S-R6-6 Pending and declined posts do not count
Given a post still pending review and a post declined When the admin views the period they were created in Then Posts published counts neither
### S-R6-7 Replies do not count
Given a post with 2 comments and 1 reply to one of them When the admin views the period Then Comments reads 2
### S-R7-1 Previous period comparison
Given a custom range 8–14 Sep; 1–7 Sep had 100 posts and 8–14 Sep had 110 When the admin reads Posts published Then the card shows "+10% vs. 1 Sep – 7 Sep" in green
### S-R7-3 Preset label
Given the preset Last 7 days When the admin reads a card Then the delta reads "vs. last 7 days"
### S-R7-2 No baseline
Given the previous period has no data When the admin reads a card Then it shows the value and "No baseline to compare"
### S-R8-1 No view events
Given the network sent no view events in the range When the admin reads the metrics Then Reach, Impressions and Engagement rate read N/A, not 0
### S-R8-2 Comments not entitled
Given module comment is locked under enforce mode When the admin reads the comments card Then it reads "Unlock comments" and N/A with a lock icon And its tooltip reads "Unlock comments to boost engagement"
### S-R8-3 Both engagement modules locked
Given modules comment and reaction are both locked When the admin reads Engaged users and Engagement rate Then both read N/A
### S-R8-4 Zero is real
Given comments are entitled and nobody commented When the admin reads Total comments Then it shows 0
### S-R8-5 Range before coverage
Given the range ends before 2025-01-01 When the admin opens the Overview Then every metric reads N/A
### S-R9-1 Interval follows range length
Given ranges of 30, 31, 90 and 91 days When the admin opens the chart Then points are daily, weekly, weekly and monthly
### S-R9-2 Default metric and switch
Given the Overview opens When the admin changes the metric to Reach Then the chart redraws for Reach; Posts published was the default
### S-R9-4 Weeks start on Monday
Given a 60-day range starting Tuesday 1 Sep When the admin reads the chart Then the first point covers Mon 31 Aug – Sun 6 Sep
### S-R9-3 Points are not cumulative
Given 10 posts on day 1 and 5 on day 2 When the admin reads the chart Then day 2 shows 5
### S-R10-1 Top 10 by reach
Given 30 posts had activity in the range When the Overview opens Then Top performing posts lists 10, ordered by reach
### S-R10-2 Metric change refetches
Given the top list is shown When the admin picks Comments Then the list is requested with sort=comments And shows the 10 posts with the most comments, highest first
### S-R10-3 Media-only post
Given a top post has images and no text When the list renders Then its post cell reads "No caption added."
### S-R11-1 Post performance shows both views
Given a post published in August When the admin opens it from a September range Then Selected period shows September; Lifetime shows since publication
### S-R11-2 Open from Top content
Given the Top content insight is shown When the admin selects "This post" Then the post performance sheet opens for that post
### S-R12-1 No filler insights
Given no insight passes eligibility When the Overview opens Then the Key insights section is not shown
### S-R12-2 Insight dropped when the scope decides it
Given every post in scope is a Video post (Content mix needs 2 or more types) When the Overview computes insights Then Content mix is not shown
### S-R12-3 Only eligible cards
Given only Content mix is eligible When the Overview opens Then Key insights shows one card
### S-R13-1 Overview export holds every qualifying post
Given 45 posts had activity in the range When the admin exports Top performing posts with "Selected filters and period" Then the posts file has 45 rows, not 10 And the time-series file has all 7 metrics
### S-R13-2 Selected mode uses the filters in force
Given destination X and role Admin are set When the admin exports with "Selected filters and period" Then every row is inside that scope
### S-R13-4 All available data
Given filters are set When the admin exports with "All available data" Then every widget of the sub-tab covers the last 90 days ending yesterday without filters
### S-R13-3 Export failure
Given the export request fails When the admin exports Then an error toast shows and the page is unchanged
### S-R14-1 Destination table pages
Given 14 communities have posts in the range When the admin reads Performance by destination Then 10 rows and "1-10 of 14 items" And next requests the remaining 4
### S-R14-2 Top creators by another metric
Given the admin picks Comments When the table reloads Then it shows the 10 creators with the most comments, highest first
### S-R14-4 All posts refetches on sort
Given 30 posts in scope When the admin picks Comments on All posts Then the request carries the sort And page 1 shows the 10 posts with the most comments
### S-R14-3 All posts search
Given posts titled "Summer drop" and "Winter" When the admin searches "summer" Then only "Summer drop" is listed
### S-R15-1 Ranges end at the last loaded day
Given the data was last loaded for 30 Sep When the admin opens Analytics on 1 Oct Then the range ends 30 Sep
### S-R16-2 Default range
Given today is 1 Oct When the admin opens the Analytics tab Then the range is 24 Sep – 30 Sep
### S-R16-3 Clearing the date
Given a custom range is set When the admin clears the date chip Then the range returns to Last 7 days ending yesterday
### S-R16-4 Clear on the default range
Given Last 7 days is active When the admin clicks the date chip's × Then the range stays Last 7 days ending yesterday
### S-R16-1 No today
Given today is 1 Oct When the admin opens the date picker Then there is no Today preset and 1 Oct is disabled
### S-R17-1 Community-scoped admin
Given an admin is assigned communities X and Y only When the admin opens Analytics Then "All destinations" is not offered And the destination filter starts on X And every number covers X only, until the admin selects Y
### S-R17-2 Dashboard permission alone does not open Posts
Given an admin holds VIEW_DASHBOARD only When the admin opens /components/posts directly Then the access-denied page shows And Posts is not in the sidebar
### S-R17-3 The post grant opens Posts
Given an admin holds VIEW_POST_AND_COMMENT_MANAGEMENT When the admin opens Posts Then both the Content and Analytics tabs are shown
### S-R18-1 Filters carry over
Given date 1–30 Sep, destination X and role Admin are set on the Overview When the admin switches to Content Performance Then the same three filters are set and the date label reads "Filter by creation date"
### S-R18-2 Content type stays on Content performance
Given content type Video is set on Content performance When the admin switches to the Overview Then the Overview has no content type filter and counts every type And its date header reads "Filter by activity date"
Gaps found: what does "Today" show when data is one day behind → R16 changed (no Today preset, user 2026-10-01). Insight thresholds are not set → R12 test values wait for the Open item.

## 7 Instrumentation
| Event | Properties | Owner | Slice |
| --- | --- | --- | --- |
none — the frame asks for no events (Notion "Posts — Analytics", A1–A4 read 2026-09-28)

## Open
TBC items wait for the final Figma or the PM. Each carries a proposed default so slices SL-00 to SL-05 can start; the default is replaced when the answer lands, and every file that repeats it is swept.
- **Resolved 2026-10-06.** Insight thresholds (R12): the proposed defaults are accepted and fixed in the dashboard — at least 10 posts, a change of 10% or more, a share gap of 10 points or more.
- ~~Export menu~~ — decided: Figma 1548:177712, two modes and 4 widgets per sub-tab (user, 2026-10-02) → R13
- ~~Chart week start and timezone~~ — decided: as the dashboard, Monday weeks, UTC days, no on-screen label (user, 2026-10-01) → R9
- ~~"Data last refreshed" display~~ — decided: not shown; final Figma draws none (2026-10-02) → R15
- **TBC — final Figma.** Widget error copy (ST9, ST10). Proposed default: the DS default of WidgetFallback status="error" with Retry. Needed by SL-01 (copy only).
- ~~The 8 Notion-vs-Figma conflicts~~ — superseded: Figma is final and wins over Notion (user, 2026-10-02); every rule above is swept to it, with the 10 decisions D1–D10 in the Figma inventory https://claude.ai/artifact/8e7yLv1XsYUYHWdog9eRAg
- **TBC — Design.** Copy Figma still marks as draft or wrong; the strings in handoff.md ship until it lands: "Engaged user" vs "Engaged users", "represents" → "represent", the Content performance table subtitles that say "generated inside the selected period" while the tab filters by creation date, "(postType)" in the Top content sentence, the Top posts subtitle now drawn as "Ranked the selected metric…" (typo; "Ranked by" ships). The key-metric and sheet tooltips are final (Figma 1944:133489, 2026-10-02). Needed by SL-01, SL-04, SL-06.
- **TBC — Design.** A cell-level N/A (comment #101) and comment #118 "ordering". Proposed default: "N/A" in muted text. Needed by SL-04. (Custom is back in the content type filter: final Figma 1382:110730, 2026-10-02.)
- ~~Counting soft-deleted posts~~ — decided: count them, kept with `is_deleted` in a new table read by a new route group; the dashboard is unchanged (user, 2026-10-01) → R5, §5
- ~~Post performance container~~ — decided: right drawer (Design, 2026-10-01)
- ~~The dashboard API checks no console permission~~ — decided: accept for MVP, the console gate is the only one (user, 2026-10-01) → R17
