# Posts Analytics — backlog slices

Every slice is vertical: a `dashboard:` half in `social-plus-dashboard` and a `console:` half in this repo, one PR per repo, built in parallel by this squad and demoed together. The solution — sketch, spec, handoff and these slices — lives only here, in `social-plus-console/docs/solution/posts-analytics/`; Delivery reads it from here for both halves, and the dashboard PR links back to the slice. The console builds against the spec §5 shapes until the endpoint lands.

## SL-00 Dashboard: the post analytics table and the KPI route
spec: §5 data, row overview/kpis · R4, R5, R6, R8, R15, R17 · S-R5-4, S-R5-5, S-R5-6, S-R5-7, S-R6-3
depends on: —
dashboard: new table `posts_with_deleted` with `is_brand` and `is_deleted` (soft deletes); hard-deleted posts are removed, so they and their activity count nowhere; its incremental load by change time and the backfill from 2025-01-01; route group `/v1/post-analytics/*` with `overview/kpis` (7 metrics, previous period, `role_bucket` with admin, moderator, brand and user, `post_type`); impressions as distinct `impression_id` with `content_type = 'post'`; the console origin in `CORS_ALLOWED_ORIGINS`. Nothing existing changes
console: — (SL-01 reads it)
demo: a post published in January and soft-deleted in February is in `posts_with_deleted` with `is_deleted` and counts; a hard-deleted one counts nowhere, nor do its views, comments or reactions in `GET /v1/post-analytics/overview/kpis` for January; the dashboard's Content page and `/v1/content/*` answer exactly as before.

## SL-01 Analytics tab, filters and key metrics
spec: F1 steps 1–3, 5, Alt 5a–5c · R1, R3, R4, R6, R7, R8, R15, R16, R17 · ST1–ST20, ST29–ST38 · S-R1-2, S-R3-1, S-R3-2, S-R3-3, S-R4-1, S-R4-2, S-R4-3, S-R5-1, S-R6-1, S-R6-2, S-R6-4, S-R7-1, S-R7-2, S-R7-3, S-R8-1, S-R8-2, S-R8-3, S-R8-4, S-R8-5, S-R15-1, S-R16-1, S-R16-2, S-R16-3, S-R16-4, S-R17-1, S-R17-2, S-R17-3 · handoff DEC-069, DEC-071
depends on: SL-00
dashboard: — (uses SL-00)
console: `dashboardClient` (Bearer token, region header, `api-exempt`); Analytics tab enabled behind either permission; Overview / Content performance sub-tabs; sticky filter bar with destination, multi-select creator role (4 buckets) and chips, date picker "Filter by activity date" defaulting to Last 7 days; the 7 StatCards with tooltips, delta ("vs. last 7 days" or the previous dates), N/A and Locked ("Unlock comments")
demo: an admin with either permission opens Posts › Analytics on the last 7 days ending yesterday, switches destination and creator role (a brand moderator counts under Brand user only), and reads the 7 key metrics with their deltas, "No baseline to compare", N/A for a network without view events, and "Unlock comments" or "Unlock reactions" cards where those are unbought; an admin with neither permission gets the access-denied page.

## SL-02 Performance over time
spec: F1 step 6, Alt 6a · R1, R9 · ST39–ST46 · S-R9-1, S-R9-2, S-R9-3, S-R9-4 · §5 row overview/timeseries
depends on: SL-01
dashboard: `/v1/post-analytics/overview/timeseries`
console: Performance over time area chart with the metric Select, one chart token per metric (chart-7 to chart-16, DEC-063)
demo: the chart draws Posts published by default in its own colour, switches to any of the 7 metrics, steps daily, weekly or monthly as the range crosses 30 and 90 days, and shows "No data available" for an empty scope.

## SL-03 Top performing posts and post performance
spec: F1 steps 7–8, F2 step 7 · R1, R10, R11 · ST47–ST54, ST64–ST71 · S-R1-1, S-R10-1, S-R10-2, S-R10-3, S-R11-1 · §5 rows overview/top-posts, posts/{id}
depends on: SL-01
dashboard: `/v1/post-analytics/overview/top-posts`; `/v1/post-analytics/posts/{id}`
console: Top performing posts table with core hydration, the metric Select refetching the top 10 by that metric, the action column pinned right; the post performance sheet with iconed StatCards (DEC-071)
demo: the top 10 posts by reach include a post published before the range that was active inside it, reload as the top 10 by comments, show "No caption added." for a media-only post and both chips for a video + photo post, and open a right sheet that toggles Selected period and Lifetime · Since published.

## SL-04 Content performance: by content type and by destination
spec: F2 steps 1–4, Alt 2a · R2, R3, R5, R14, R18 · ST2, ST55–ST63 · S-R2-1, S-R2-2, S-R5-2, S-R5-3, S-R14-1, S-R18-1, S-R18-2 · §5 rows content/by-type, content/by-destination · handoff DEC-072
depends on: SL-01
dashboard: `/v1/post-analytics/content/by-type` (a post counts in each of its types); `/v1/post-analytics/content/by-destination` (paged); every route takes `sort`, descending
console: Content performance sub-tab; single-select content type filter; date header "Filter by creation date"; by content type and by destination tables at Published posts, refetched on every metric change, with MetricBar
demo: Content performance keeps the Overview's date, destination and creator role with the label "Filter by creation date", adds the content type filter, and lists content types (a video + photo post in both rows, Poll on its own) and group destinations 10 per page, with lifetime metrics for posts published in the range.

## SL-05 Content Performance: top creators and all posts
spec: F2 steps 5–6 · R4, R14 · ST55–ST63 · S-R14-2, S-R14-3, S-R14-4 · §5 rows content/creators, content/posts, search/posts, posts/list, users/list
depends on: SL-04
dashboard: `/v1/post-analytics/content/creators`; `/v1/post-analytics/content/posts`, both with `sort`
console: Top creators table with role badges; All posts table with core search and « ‹ 10/page › paging
demo: Top creators lists 10 creators by published posts with their creator role and reloads as the top 10 by comments, and All posts finds "summer" through core search, reloads sorted by comments and pages 10 at a time.

## SL-06 Key insights
spec: F1 step 4, Alt 4a · R7, R12 · ST21–ST28 · S-R12-1, S-R12-2, S-R12-3, S-R11-2 · §5 row insights · handoff DEC-070
depends on: SL-01, SL-03, SL-04 · thresholds: the spec defaults, accepted 2026-10-06 (R12)
dashboard: `/v1/post-analytics/insights`
console: Key insights section with InsightCard (Momentum, Top content, Content mix), only eligible cards, section hidden when none, "This post" opening the sheet
demo: up to 3 cards show Momentum, Top content and Content mix, an insight the scope decides is dropped, "This post" opens the post's sheet, and the section disappears when none is eligible.

## SL-07 Export
spec: F3, Alt 3a · R13 · ST72–ST75 · S-R13-1, S-R13-2, S-R13-3, S-R13-4 · §5 row export
depends on: SL-02, SL-03, SL-05, SL-06
dashboard: `/v1/post-analytics/export` with `mode` and `widgets`
console: Export popover — "All available data" (last 90 days, no filters) or "Selected filters and period" with the widget checklist — and Export CSV
demo: "Selected filters and period" with all 4 Overview widgets downloads the time series with all 7 metrics and every post active in the range, not only the top 10, inside the filters in force; "All available data" covers the last 90 days without filters; a failed export shows an error toast and leaves the page as it was.

Release scope (2026-10-06, QA review): this release ships Key insights (SL-06) and the SL-03 post performance sheet that "This post" opens.
