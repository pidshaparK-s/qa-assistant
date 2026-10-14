# Posts Analytics — delivery log

Spec: docs/solution/posts-analytics/spec.md · Status when Delivery started: 06 Solution Ready 2026-10-02
Gates (user, 2026-10-02): "implement until finished and compare with figma by yourself … i will check after done every task" — the plan and demo stops are waived; every slice still passes the CI gates and a numeric + live Figma comparison before it is marked done, and the user reviews at the end.
Tracks (user, 2026-10-02): the two repos are built in parallel — `social-plus-dashboard` takes each slice's `dashboard:` half, this repo the `console:` half against the spec §5 shapes until the endpoint lands.

## Slices
| Slice | Status | Since | Note |
| --- | --- | --- | --- |
| SL-00 | done | 2026-10-02 | dashboard PR AmityCo/social-plus-dashboard#257 (SL-00 + the dashboard halves of SL-02…SL-07), gates green; ETL pre-aggregation deferred for discussion |
| SL-01 | done | 2026-10-02 | console track; lead live check 2026-10-02 in demo mode at 1460 wide: default, Locked ×2 with engaged N/A, 4 roles + destination chips with +1 and Clear all — match 1247:5639 and 1531:163476 apart from the differences logged |
| SL-02 | done | 2026-10-02 | lead live check: area chart `type="monotone"` since 81332a7 (natural overshot below zero) (Figma Chart / Area Chart "Basic", gradient), colours, sticky band — match 1247:5639 |
| SL-03 | done | 2026-10-02 | lead live check: chips per type, "No caption added.", pinned action + gradient; sheet measured 768 wide, cards 229×100 — match 1837:87272, 1538:33610 |
| SL-04 | done | 2026-10-02 | lead live check: by content type with chips + MetricBar, sticky 3-filter row; fixed Export clipping at the 1280 floor (filters `min-w-0`, shrink to 194 there, 200 at the Figma width) |
| SL-05 | done | 2026-10-02 | lead live check: Top creators role badges + brand badge, All posts search + metric Select — match 1394:130286 |
| SL-06 | done | 2026-10-02 | lead live check: Momentum / Top content ("This post" link) / Content mix in one bordered row — match 1247:5639; thresholds = spec Open defaults (PM TBC) |
| SL-07 | done | 2026-10-02 | lead live check: popover both modes, 4 Overview widgets checked, "4 of 4 selected" — match 1548:177712; dashboard now exposes Content-Disposition / X-Export-Truncated (PR #257, 2992230) |

## SL-00 Dashboard: the post analytics table and the KPI route
Frames read: — (backend)
Plan: branch `feat/post-analytics` off dashboard origin/main (which has d499364 comments/reactions analytics: `contentfilter`, `user_role_dims`, `serving.etl_watermarks`, `comments_visible_v`); package `server/internal/feature/postanalytics`, ungated beside `content`; `posts_with_deleted` in `infra/pkg/bigquery/serving.go`; scheduled load + backfill SQL; per-region schedule in `infra/main.go` · lead, 2026-10-02 (plan stop waived)
Gates: —
Questions logged (defaults taken by the lead, for the user's review):
- Watermark: `serving.etl_watermarks` job `posts_with_deleted`, not `sp-intel.events.sync_watermark` (cross-repo IAM; that table's heartbeat check fails stale rows) — spec §5 wording to amend
- Load cost: the append-only tables are clustered on `_id` and not partitioned, so a timestamp filter scans the whole table (~1.16 TB US/day). Two-pass load: ids + timestamps first, then the full rows by `_id`
- "No view events" (R8): the network never sent impressions → N/A; zero in range → 0, as `/v1/content` does
- Comments include replies and exclude pending (`comments_visible_v`); reactions count on posts only
- Backfill loads every post regardless of age, so activity on pre-2025 posts still counts on the Overview (R1)
- `content_creator_dims` and `content_posts_reconcile.sql` were replaced by #256 (`user_role_dims`, `content_reconcile.sql`); spec §5 names the old files — wording to amend
- Prod CORS: the prod console-next hostname is needed; non-prod already allows console-next staging and :5175
Built (dashboard track, 2026-10-02): branch `feat/post-analytics`, 8 local commits a02093a…870796a — SL-00, SL-02…SL-07 routes under `/v1/post-analytics/*`; go build/vet/test, `make test-integration` (14 tests), governance checks green; infra `TestStackFilesSatisfyRequiredConfig` fails on origin/main too
Review (independent, prod measured 2026-10-02): routes correct against R1–R17; to fix before the PR — US nightly load ~0.7–1.8 TB (→ single pass over `APPENDS()`, measured ~1.6 GB/day), backfill must seed the watermark, data-driven watermark with a fail-loud >6-day guard, `posts/{id}` lifetime 7.57 GB per open, unbounded has-views probe, 365-day routes ~7 GB each (impressions floor) → pre-aggregate; prod needs main's d499364 infra applied first
Commit: pushed — PR #257 (head 644d8d6): single APPENDS nightly load (US ≈ 35 GB/night, EU 1.7, SG 2.9 billed), backfill seeds a data-driven watermark, bounded has-views probe (KPIs 30d 1.33 → 1.15 GB), posts/{id} 0.24 GB on a recent post; 365-day routes (~6.4–7.2 GB) and old-post Lifetime (6.8 GB) wait for new derived tables. Earlier: cost/watermark fixes paused by the user 2026-10-02 ("complete all slices first; this fix will discuss again once everything done") — the slices run on the existing routes; the fix plan and measurements are in https://claude.ai/artifact/9MrJiAWUbHHjABo3BGhRge (exact counts only, user 2026-10-02)

## SL-01 Analytics tab, filters and key metrics
Frames read: 1247:5639 (Overview, final) · 1378:50839 (sticky filter section) · 1378:33190 (multi-select filter, chips row 1378:33206, menu 1453:45181) · 1531:163476 (metric card states, trend colours 1531:163455) · 1432:87588 (date picker) · node JSON at file version 2405661657054361399, inventory artifact read 2026-10-02
Anatomy walk (Figma number → the class that produces it; app measured live at 1024 main width, so cards read 232 not 272):
- header: breadcrumb "Posts" — PageBreadcrumb — Figma 64 high · app shell h-14 = 56 (shared chrome, not closed)
- heading: title 24/32 w700 · description 14/20 #525252 — PageHeader `pt-6 mb-4` = pad 24 / 16 ✓
- page tabs: Content · Analytics · Settings, 36 high — TabsList line ✓; Figma adds pad-top 12 on the band (heading→tabs 28), app 16 — shared with the Content tab, not closed
- sub-tabs: Overview | Content performance — TabsList default, pad 3 `p-[3px]`, r10 `rounded-lg`, #E5E5E5 `bg-muted`, active r8 white shadow — Figma 237×36, app 239.3×36 (DS `gap-1` 4px; Figma 0) — `px-6 pt-4 pb-1` gives tabs→sub-tabs 16 ✓ and, with the band's pt-3, sub-tabs→filters 16 ✓
- filter band 1378:50839: pad 12/24/16/24 → `pt-3 px-6 pb-4`; 64 high ✓ (live 64), 112 with chips ✓ (live 112); rest #F9FAFB `bg-background-subdue`; stuck #FFFFFF `bg-background` + 0 2 4 -2 / 0 4 6 -1 rgba(0,0,0,.1) = `shadow-md` ✓; `sticky top-0` in AppLayout's scrolling `<main>` (stuck at y 56 live)
- filter row: Destinations 200×36 `w-[200px]` ✓ · Creator roles 200×36 ✓ · gap 8 `gap-2` ✓ · date trigger 245×36 `w-[245px]` ✓, range 14/20 w500 #0A0A0A `font-medium text-foreground` · Export 114×36 pad 8/12 `has-[>svg]:px-3` (live 115.9, glyph width)
- chips row 1378:33206: 32 high, groups bottom-aligned `items-end`, group gap 16 `gap-4`, label→chip 8 `gap-2`, label 14/20 #525252 `tone="muted"`; RemovableChip r6 pad 4/6/4/8 #F3F4F6/#D1D5DB/#4B5563 unchanged; Clear all ghost pill 83×32 pad 8/10 12/16 w500 `size="sm" has-[>svg]:px-2.5`
- multi-select menu 1453:45181: 200 wide `w-[200px]`, rows 32 r6 pad 6/8 (CommandItem) with Checkbox 16 #3B41EC; Clear all row 40 `h-10` under `border-t`, 14/20 w500 #0A0A0A, only when filled
- container: pad 16/24/24/24 → `pt-4 px-6 pb-6`, section gap 24 `gap-6` — filters→"Key metrics" 32 ✓ (live 325−293)
- Key metrics: heading 16/16 w600 `size="base" semibold leading-4` ✓, gap 16 `gap-4` ✓, grid 4 col gap 16 `grid-cols-4 gap-4` ✓
- metric card 1531:163476: 116 `h-[116px]` ✓ · r10 `rounded-lg` ✓ · border #E5E5E5 · 0 1 2 0 rgba(0,0,0,.05) `shadow-xs` ✓ · pad 20 `p-5` · gap 8 `gap-2` · label 14/20 w500 #0A0A0A · info 16 #525252 · value 24/32 w700 `size="2xl" bold leading-8` · trend 12/16, gap 4 `gap-1`; up #16A34A `text-success`, down #DC2626 `text-destructive`, flat #171717 `text-primary`, comparison #525252 `tone="muted"`; locked label + N/A #A3A3A3 `text-ring`, lock 16 in place of info, no trend row; loading bars #F5F5F5 r8 167×16 (inside an 8/8 pad) and 120×16
Plan (stops waived, lead defaults): new `src/api/dashboardClient.ts` (not client.ts — it carries @requirement REQ-CC-111), `src/api/postAnalytics.ts` (keys, `kpis` options with keepPreviousData, R8 resolver), fixtures + demo route; StatCard reshaped (DEC-071); MultiSelectFilter + StickyFilterSection + ActiveFilterChips (DEC-069); AnalyticsDateFilter on DateRangePicker; PostsPage split into shell + PostsContentView + PostsAnalyticsView; route search view/aTab/range/aFrom/aTo/aTargetId/aTargetLabel/roles; sitePermissions accepts either grant
Gates (2026-10-02): typecheck ✓ · lint ✓ (0 errors) · test ✓ 223 files / 2045 tests · typecheck:governance ✓ · governance:ci ✓ "Governance OK — 115 requirements" (REQ-CC-119, REQ-CC-152 a–c re-audited verified after the sitePermissions row change) · i18n:gate ✓ 0 strings · api:check ✓ · qa:copy-check ✓ · lint:comments ✓ · lint:ds ✓ · ds:check ✓ · ds:build ✓ no drift after commit · build ✓
Live check (agent, demo mode, Chrome): default, 4 roles with +1 chip, Brand user only (N/A + "No baseline to compare"), `lock=comment` (Unlock comments card + tooltip), custom 8–14 Sep ("vs. 1 Sep – 7 Sep 2026"), date popover (4 presets, after yesterday disabled), stuck band — match the frames apart from the differences below
Figma differences left:
- header — 64 — 56 (AppLayout shell, every page)
- heading → page tabs — 28 — 16 (shared with Content)
- sub-tabs track — 237 — 239.3 (DS TabsList `gap-1`, DEC-037 rhythm)
- date popover month — opens on the range's month in Figma's example — opens on today's month (DS DateRangePicker)
Questions logged (defaults taken, for the user's review):
- Export renders disabled until SL-07 (holds its 114px in the row)
- Settings tab kept, disabled with "Coming soon" — outside this feature
- S-R17-1 mismatch: a community-scoped admin is clamped to the FIRST assigned community (existing useDestinationScope), not "every number covers X and Y" — the dashboard API takes `communities`, so all-assigned would need the console to send every id
- `useDestinationScope` now takes the accepted grants, so a VIEW_DASHBOARD-only analyst is not mistaken for a scoped admin
- analyst-only admins: the `/components/posts` prefix also opens `/components/posts/create` and `/edit` by URL (RouteGuard matches by prefix); core still refuses the write
- `role_bucket` and `communities` are sent comma-separated, as the dashboard track serves them; spec §5 says "repeatable" — wording to amend
- `engagement_rate` is read as a percentage (4.3 → "4.3%"), not a ratio
- the date chip's ✕ shows only off the default range; clearing returns to Last 7 days (R16); "Showing all time" never shows
- Clear all resets destination and creator roles, not the date (annotation: "the dropdown filters are back to their default state")
- destination and analytics filters use their own URL keys (`aTargetId`, `aFrom`/`aTo`, `range`, `roles`), so the Content tab's filters are untouched
- key-metrics error: one content fallback for the section (spec ST37), not seven per-card errors (handoff row); copy is the DS default (spec Open)
- no `touchesContent` on the kpis query: it renders no core content
- #A3A3A3 locked text reuses the existing `text-ring` token; no new token minted
- lock icon colour #525252 assumed (the frame's icon carries no fill)
- demo: `moduleEntitlement` added to the demo network (`shadow`, so console-next opens); `/demo?lock=comment,reaction` locks modules; Brand user alone answers "no view events", a range before Feb 2025 has no baseline
Commit: 37dd281 (feat/posts-analytics, local, not pushed)

## SL-02 Performance over time
Frames read: `_Chart / Card` I1247:5639;1180:52440;1276:44713 (Overview, final) · 1412:76749 (chart states: empty 1412:76731, no results 1513:112191, loading 1513:112210) · 1568:177793 (chart colour variables) · 1432:60216 (metric menu) · node JSON at file version 2405705461857381674 (newer than the handoff's 2405661657054361399)
Anatomy walk (Figma number → the class that produces it):
- card: 1136×402, r10 `rounded-lg`, border #E5E5E5 `border`, 0 1 2 0 rgba(0,0,0,.05) `shadow-xs` — new WidgetCard `surface="chart"`
- header: pad 24 `px-6 pt-6`, bottom border inside the frame → `border-b pb-[23px]` so the band is 90 ✓ (live 90); title 16/16 w600 `size="base" semibold leading-4`, gap 6 `gap-1.5`, description 14/20 #525252 `tone="muted"`; Select 200×36 `w-[200px]`, bottom-aligned with the text (y 30) `items-end`
- content: pad 24 `p-6` → plot block 1088×264 `h-[264px]`: chart wrapper pad 32/0/32/32 → AreaChart `margin.top 32`, YAxis `width={32}`, XAxis `height={32}` `tickMargin={12}`; plot 1056×200 ✓
- axes: ticks 12/12 #525252 (recharts text, `fontSize: 12`, muted via ChartContainer), x "31 Aug" `d MMM`, 5 y ticks; horizontal grid only #E5E5E5 `CartesianGrid vertical={false}`
- series: stroke 1px in the metric colour `strokeWidth={1}`; fill layer opacity 0.4, gradient colour→white 0 → stops 0.4 / 0 ✓ (live rgb(59,65,236)/0.4, /0); hover dot 8 white with 2px metric stroke `activeDot r 4 strokeWidth 2`
- tooltip 1247:5639 Charts / Tooltip: date 12/16 w500 "1 Sep 2026" `d MMM yyyy`; item name 12/12 #525252, value 12/12 w500, no swatch `hideIndicator`
- colours (DEC-063, chart-7..17 added to globals.css `:root`, HSL round-tripped): Posts published chart-7 #3B41EC · Reach chart-15 #F568F0 · Impressions chart-9 #3769EC · Comments chart-13 #F66005 · Reactions chart-11 #45A5ED · Engaged users chart-14 #F7C506 · Engagement rate chart-16 #27265E — `METRIC_CHART_COLOR`; built CSS carries `--color-chart-7:hsl(var(--chart-7))`
- loading 1513:112210: LoaderCircle 32 centred in the 312 content `Spinner size="8"` in `h-[264px] items-center`
- empty 1412:76731 / no results 1513:112191: 40×40 #E5E5E5 r10 medallion with FolderOpen / SearchX, title 18/28 w500, description 14/22.75 — `EmptyState media="icon" size="md"` (live title 18px)
Plan (stops waived, lead defaults): `timeseries` query options in `src/api/postAnalytics.ts` (key = region + filters, no metric); `toChartPoints`; `intervalFor` / `bucketStart` / `bucketsFor` in `src/lib/analyticsRange.ts` for the fixture and demo; `PerformanceOverTime` in `src/components/posts-analytics/`; new composite WidgetCard (registry.meta, specimen, usage doc); timeseries fixture and demo route
Gates (2026-10-02): typecheck ✓ · lint ✓ exit 0, 0 errors (182 pre-existing warnings, none in new files) · test ✓ 224 files / 2052 tests · typecheck:governance ✓ · governance:ci ✓ "Governance OK — 115 requirements" · i18n:gate ✓ 0 strings · api:check ✓ 335 calls · qa:copy-check ✓ · lint:comments ✓ · lint:ds ✓ · ds:check ✓ · ds:build ✓ no drift after commit · build ✓
Tests: S-R9-1 and S-R9-4 in `src/lib/analyticsRange.test.ts` (the dashboard computes the interval; its own timeseries_test.go covers the route), S-R9-3 in `src/api/postAnalytics.test.ts`, S-R9-2 plus ST40, ST42, ST43 in `PostsAnalytics.test.tsx`
Live check (agent, demo mode, Chrome, 1220 wide): default Posts published in #3B41EC, ticks 0/3/6/9/12; 1 Jul – 29 Aug steps weekly, 9 points from Mon 29 Jun; Admin only → "No results found"; header 90, Select 200×36, plot 264; hover: tooltip "27 Sep 2026 · Posts published 8", no swatch, dot white with a brand stroke (fixed after review: the dot read `var(--background)`, an HSL triplet, and drew black)
Figma differences left:
- card height — 402 — 404 (Card's 1px border sits outside the box; Figma strokes inside)
- tooltip — r8, 200 wide — r10, content width (DS ChartTooltipContent)
- metric menu — 240 wide — trigger width 200 (DS SelectContent)
Questions logged (defaults taken, for the user's review):
- SL-01 drift fixed: the dashboard serves the KPI block as `metrics`, not `kpis` (kpis.go `KPIsResponse`); renamed in postAnalytics.ts, fixtures and tests
- wire shapes follow social-plus-dashboard feat/post-analytics `timeseries.go` (34dd6f0): `{range, interval, tz, has_view_events, points[{bucket, posts_published, reach|null, impressions|null, comments, reactions, engaged_users, engagement_rate|null}]}`; `engagement_rate` already ×100
- the console never sends the interval; the dashboard derives it from the range (≤30 day, ≤90 week, else month)
- "No data available" vs "No results found": empty when no point has any activity (the dashboard zero-fills); "No results found" when a destination or creator role is set, which includes a community-scoped admin's forced destination
- a metric whose series is all null (Reach etc. without view events) reads "No data available" rather than a flat line
- tooltip date for a weekly point is the bucket's Monday ("31 Aug 2026"); monthly reads "Sep 2026"; ticks follow ("31 Aug", "Sep 2026")
- the chart offers all 7 metrics even when comments or reactions are locked (R9 names 7); locked metrics plot their zeros
- the metric is view state (resets on reload), not a URL key
- Figma file moved to version 2405705461857381674 during delivery; 1452:105407 (Top posts full view) no longer resolves — SL-03 reads the 1247:5639 instance
Commit: 1010f97 (feat/posts-analytics, local, not pushed)

## SL-03 Top performing posts and post performance
Frames read: Top Post Tables I1247:5639;1180:52440;1938:91512 (in the Overview 1247:5639; the full view 1452:105407 returns null at file version 2405705461857381674) · title tooltip I1247:5639;1180:52440;1938:102330 · row action tooltip 1833:102509 · Engagement rate head tooltip 1761:128449 · metric menu 1432:87017 · sheet SheetOverlay / Performance I1837:87272;1238:34490 · Lifetime 1394:129120 · sheet card states 1538:33610 · node JSON at 2405705461857381674
Anatomy walk (Figma number → the class that produces it):
- card: 1136 wide, r8 `rounded-md`, border #E5E5E5, no shadow — WidgetCard `surface="table"` (live 8px, shadow none)
- widget header: pad 24/24/20/24, divider inside → `pt-6 px-6 pb-[19px] border-b` = 86 ✓ (live 86); title "Top posts" 16/16 w600 + info 16 gap 6 `gap-1.5`, tooltip dark 12/16 "Ranked by activity generated during the selected date range."; description 14/20 #525252; Select 200×36 centred (y 27) `items-center` ✓ (live 27)
- head row 40 `h-10`: cells pad 8/16 `px-4`, 14/20 w500 #525252; widths # 40 · Post 360 · Content type 200 · Creator 240 · Destination 180 · Reach/Impressions/Comments/Reactions 130 · Engaged users 140 · Engagement rate 180 · Created date 140 · action 64 → `w-[N] min-w-[N]` on a `table-fixed` table (live 40/360/200/240/180/130×4/140/180/140/64, total 2064 ✓); only Engagement rate has an info icon 12 `size-3`, tooltip = the metric definition (1761:128449)
- rows 76 `h-[76px]`, pad 8/16, bottom divider: # 14/20 w500; post title 14/20 w500 one line `truncate` + body 14/20 #525252 two lines `line-clamp-2`; media-only "No caption added." 14/20 w400 #A3A3A3 `text-ring`
- content type: Color Chip 24 r99 pad 4/6/4/8, gap 6 between chips `gap-1.5` — Text grey, Photo blue #EFF6FF/#BFDBFE/#2563EB, Video violet #EBECFD/#3B41EC@50%/#3B41EC (live rgb(235,236,253)/rgb(59,65,236)) — Chip `color`
- creator: Avatar 40 #EBECFD initial #3B41EC `UserAvatar size="md"`, gap 8, name 14/20 w500, user id 14/20 #525252
- created: "17 Aug 2026" w500 / "17:43" #525252 on two lines — `formatDateParts`
- action: 64 pinned right, white, 24px fade — new `TableCell pinned="right"` (DEC-073, sticky live); outline 32×32 r8 BarChartBig 16 `Button variant="outline" size="icon-sm"` (live 32), Tooltip "View performance" dark 12/16 (1833:102509)
- sheet 1837:87272: 768 wide `!max-w-[768px]` (live 768) over a 50% black overlay (Drawer); sticky header 51, pad 14/20, × 16 at 70% + "Performance" 18/28 w600 — PostHeader `h-[51px]` (live 51); context row 48 "Post in" 14/20 w400 + destination w500 link — PostHeader `h-12` + CellLink; body pad 20 gap 16 `p-5 gap-4`: avatar 40 + PostByline + "Created 12 Sep 2026, 16:30", then PostContent (RichText clamps at 3 lines with See more); Separator
- performance block pad 20 gap 16: Tabs 194×36 pad 3 r10 #E5E5E5 (live 194×36) · Date Picker 245×36 "31 Aug 2026 - 30 Sep 2026" with × — AnalyticsDateFilter `readOnly` + `onClear` (DEC-067; live 245×36, the calendar never opens) · Lifetime: "Since published" 14/20 #525252 in its place
- cards 1538:33610: 229×100, 3 per row, gap 20 `grid-cols-3 gap-5`, pad 20, gap 8; icon 16 + label 14/20 w500 gap 4 + info 16; value 24/32 w700; no trend row — StatCard `icon` `className="h-[100px]"` (live 229×100); icons Users, Eye, MessageCircleReply, ThumbsUp, User, TrendingUp; labels are the metric names ("Reach", not "Total reach")
Plan (stops waived, lead defaults): `topPosts` (key = region + filters + sort, refetch per pick, `touchesContent('post')`) and `postPerformance` query options; `resolveTopPosts` joins `post_public_id` to core `GET /api/v3/posts/list` via `hydratePostsPage` (author, community), creators the envelope lacks from `GET /api/v3/users/list` by internal id; TopPostsTable and PostPerformanceSheet in `src/components/posts-analytics/`; the sheet opens through the URL key `aPost` with `usePostPerformanceSheet().open(postId)` for SL-06; MetricTip moved out of the page so the table and sheet share it; DS: `pinned` on TableHead/TableCell (DEC-073), DateRangePicker `readOnly` (DEC-067)
Gates (2026-10-02): typecheck ✓ · lint ✓ exit 0, 0 errors, no warnings in changed files · test ✓ 224 files / 2058 tests · typecheck:governance ✓ · governance:ci ✓ "Governance OK — 115 requirements" · i18n:gate ✓ 0 strings · api:check ✓ 335 calls (posts/list and users/list already in routes.json) · qa:copy-check ✓ · lint:comments ✓ · lint:ds ✓ (and `--staged` ✓) · ds:check ✓ · ds:build ✓ no drift after commit · build ✓
Tests (`PostsAnalytics.test.tsx`): S-R10-1, S-R10-2, S-R10-3, S-R1-1, S-R11-1, plus the row action setting `aPost`. S-R1-1 is checked on the console side only (the request is the range, an older post renders); counting activity on older posts is the dashboard's (top-posts SQL ranks on in-range events whatever the post's age)
Live check (agent, demo mode, Chrome): /components/posts?region=sg&view=analytics — 10 rows by Reach; Comments re-ranks after a second request; row 4 Photo + Video chips; row 6 "No caption added."; View performance on row 4 opens the sheet (Skincare Lab, Priya Nair, Selected period 3,020 reach); × on the chip → Lifetime · Since published, 8,629 reach; the chip never opens a calendar; `/demo?lock=comment` → Comments cell N/A and the sheet's Comments card Locked (greyed, lock icon)
Figma differences left:
- table row — 76 — 77 (the 1px divider sits outside the cell; Figma strokes inside)
- post body hashtags — link colour — plain muted text
- sheet header title — a ghost button — plain text (nothing to click in Figma's behaviour)
- metric menu — 240 wide — trigger width 200 (DS SelectContent)
Questions logged (defaults taken, for the user's review):
- shapes reconciled with social-plus-dashboard feat/post-analytics (posts.go, model.go; confirmed by the coordinator 2026-10-02): top-posts `{range, sort, has_view_events, items[Post + Activity]}`, posts/{id} `{post, range, has_view_events, selected_period, lifetime}`; `post_id` and `user_id` are internal ids, `post_public_id` is what core's posts/list takes; all wire→UI mapping is in `src/api/postAnalytics.ts`
- the Figma file moved after the handoff: Content type is 200 wide in 1247:5639 (handoff says 130); "No caption added." is w400 (handoff says w500); followed the node data
- a post core no longer serves (deleted, or a refused lookup) keeps its rank and numbers; the post cell reads "Post content is not available." (new copy, not in Figma), the creator falls back to users/list, the destination to "—"
- a post on a user feed or other content reads "—" as its destination (R3 names only group destinations)
- table cells: comments or reactions read "N/A" in #A3A3A3 when that module is locked, as do null view metrics; the sheet uses R8's Locked card (label keeps the metric name, per 1538:33610)
- chips for types Figma does not draw: Clip violet Clapperboard, Poll grey ListChecks, Live stream red Radio
- empty Top posts uses EmptyState `empty-readonly` default copy (no Figma copy); filtered-empty uses the chart's "No results found" copy
- the ranking metric is view state (resets on reload) and survives filter and date changes
- the sheet mirrors the page range; its chip cannot pick another range (no rule for it), × switches to Lifetime; Selected period comes back from the tab
- the sheet's card tooltips reuse the key-metric definitions (Figma's sheet copy is a "[content type (plural)]" template)
- an analyst with only VIEW_DASHBOARD: if core refuses posts/list, the rows stay unhydrated; S-R17-2 now asserts the Content feed (v5/search) is not called, since Top posts reads posts/list
- the demo media-only post has no file, so the sheet draws PostContent's Deleted tile for it
- `src/components/posts-analytics/` is outside lint-ds's ENFORCED_DIRS and USAGE_DIRS, so CI's full `lint:ds` does not check it; only the pre-commit `--staged` scan does (it caught a `leading-none` on a raw div in SL-02). Adding the dir is a lint-ds change, left to the lead
- demo: two posts the feeds do not list (`demoAnalyticsPosts`: p-8298 photo + video, p-8299 media-only); Admin alone or a range before 2025 has no top posts
Commit: 69c4772 (feat/posts-analytics, local, not pushed)

## SL-04 Content performance: by content type and by destination
Frames read: Content performance final 1394:130286 (by type `Top by content Tables` 6;1180:52440;1795:234730, by destination 6;1180:52440;1457:233895 with its footer 27140:75756) · performance tables section 1534:199450 (older copy, not followed) · single-select filter 1382:110730 · table states 1378:66318 (skeleton 1531:146302, empty 1531:156734, no results 1531:161852) · node JSON refetched at file version 2405713691583384658 (unchanged since the lead's 10:45 re-diff)
Anatomy walk (Figma number → the class that produces it):
- filter row 1394:130277: Destinations · Content types · Creator roles, each 200×36 gap 8 — DestinationFilter · `Combobox searchable={false}` `w-[200px]` · MultiSelectFilter; placeholder "All content types" 14/20 w400 #525252 → Combobox unset trigger now `font-normal text-muted-foreground` (DEC-068); menu 200 wide, rows 32 pad 6/8 r6, check on the selected row, no search row; filled trigger swaps the chevron for ✕ (ComboboxClear); chip "Content type: Photo" in the chip row
- date header "Filter by creation date" (1807:82476) — AnalyticsDateFilter `basis="creation"` (SL-01)
- card: 1136 wide, r8, border #E5E5E5, no shadow — WidgetCard `surface="table"`; header 86 pad 24/24/20/24, title 16/16 w600 + info 16, description 14/20 #525252, Select 200×36 at y 27 — as SL-03 (live 86)
- head row 40 `h-10`, cells pad 8/16 `px-4`, 14/20 w500 #525252, one line `whitespace-nowrap` ("Published posts" is 100 wide in a 120 column: Figma lets it run into the right pad); widths # 40 · type / destination 140 · Published posts 120 · Reach 120 · Impressions 130 · Comments 120 · Reactions 120 · Engaged users 140 · Engagement rate 206 = 1136 (live 1136); only Engagement rate has the 12px info icon with the metric definition
- rows 40 `h-10` (live 41: the 1px divider sits outside the cell, as in SL-03), # and numbers 14/20 w500 #0A0A0A; type cell one Chip per row (Photo blue, Text grey, Video violet, File orange, Audio yellow, Custom grey; Poll grey ListChecks as SL-03); destination name 14/20 w500 `truncate`
- engagement rate: Progress 111×8 r9999, fill #3B41EC over a #3B41EC + white 80% track → MetricBar `bg-brand` on `bg-brand/20` (built CSS carries the color-mix 20%), length = value ÷ column max (top row 100% live), value 14/20 w500 right-aligned `ml-auto` (Figma #000000, app foreground #0A0A0A)
- by-destination footer 76, pad 20/24: "1-10 of 10 items" 14/20 #525252 left, ‹ 42×36 and › 36×36 ghost right — TablePagination `className="border-t px-6 py-5"` (live 77 with the border); no first or page-size control
- skeleton 1531:146302: rows 32 `h-8`, one #F5F5F5 r8 16-high bar per cell — `SkeletonRows` (5 rows)
- empty / no results: the head row stays, then Empty pad 40 `py-10`: 40×40 #E5E5E5 r10 FolderOpen / SearchX, 18/28 w500, 14/22.75 #525252 — `TableEmpty` → EmptyState `media="icon" size="md"` with the chart's copy (same strings in 1378:66318)
Plan (stops waived, lead defaults): `postAnalytics.ts` gains `contentType` → `post_type`, `byType` / `byDestination` query options (key = region + filters + sort [+ offset], keepPreviousData, every pick refetches), `resolveByDestination` naming communities through core `GET /api/v3/communities/list` (existing `getCommunities`, public ids, partial results); `resolvePostRows` generalises the Top posts join for All posts; shared cells (`cells.tsx`: chips, metric value, creator, MetricSelect, skeleton, empty) used by TopPostsTable too; ContentGroupTable for both tables; ContentPerformance holds sort and page (`usePagedSort`: a filter change returns to page 1, the metric stays); URL key `aType`; cohort fixtures (posts dated into the requested range) and demo routes for content/*
Gates (2026-10-02): typecheck ✓ · lint ✓ exit 0, 0 errors, no warnings in changed files · test ✓ 2068 tests · typecheck:governance ✓ · governance:ci ✓ "Governance OK — 115 requirements" · i18n:gate ✓ 0 strings · api:check ✓ 335 calls (communities/list and posts/list already in routes.json; content/* is the dashboard host, `api-exempt`) · qa:copy-check ✓ · lint:comments ✓ · lint:ds ✓ · ds:check ✓ · ds:build ✓ no drift after commit · build ✓
Tests (`PostsAnalytics.test.tsx`, SL-04 block): S-R2-1, S-R2-2, S-R5-2, S-R5-3, S-R14-1, S-R18-1, S-R18-2, plus metric pick → sort and page 1, bar relative to the column max, filtered empty under the head row. S-R2-1 / S-R2-2 / S-R5-2 / S-R5-3 are console-side: the request carries the creation range and the rows render as served; the cohort, lifetime window and per-type counting are the dashboard's (content.go `buildGroupSQL`, content_test.go)
Live check (agent, demo mode, Chrome, main 1100 wide): /components/posts?region=sg&view=analytics&aTab=content — by type Text 53 · Photo 6 · Video 4 · Audio · File · Poll with chips and bars; by destination 10 rows "1-10 of 14 items", › → "11-14 of 14 items" with 4 rows named from core; head 40, bar 111×8, table 1136
Figma differences left:
- by-type head "Post type" — Figma 1394:130286 — "Content type" (handoff widths table and copy; every other surface says content type)
- by-type Published posts column — 122 (card 1138, 2px over its 1136 container) — 120, as by destination
- rows — 40 — 41 (divider outside the cell, as SL-03)
- by-destination footer — no top stroke, r14 bottom corners — `border-t` (the last row drops its divider) under the card's r8
- metric menu — 240 wide — trigger width 200 (DS SelectContent, as SL-02/03)
- filter row — fits the 1136 content of Figma's 1184 frame — at the pinned 1280 viewport main is 1016 and the row needs 991 of its 968, so Export runs ~25px past the right edge on Content performance only (live: Export right 1273 in a 1272 viewport); shell width is the lead's call, the 200/245/114 widths stay Figma-exact
Questions logged (defaults taken, for the user's review):
- `community_id` is the post's target id, i.e. the community's public id (posts_with_deleted.sql: `IF(target_type = 'community', target_id, NULL)`; the dashboard UI resolves it with communities/list `type=public`); the SL-03 fixture's internal-looking value was aligned to it
- a community core no longer serves keeps its row and reads its id as the name
- the content tables' title tooltips have no Figma copy; they read "Posts published in the selected date range, with metrics from publication to the latest data day." (R2) — TBC with Design
- the three ranked tables keep Figma's subtitle ("…generated inside the selected period, whenever the post was published"), already in spec Open as contradicting the creation-date cohort
- content type persists in the URL (`aType`) when switching to the Overview, so it returns on Content performance; the Overview neither shows nor sends it (S-R18-2)
- the content type chip's ✕ and Clear all clear it; Clear all on the Overview leaves it
- metric and page are view state per table (reset on reload); a filter or date change returns by destination to page 1 and keeps the metric
- by-type skeleton draws 5 rows (the state frame's count); by destination keeps the same 5 while loading
- the Combobox unset-trigger tone change applies app-wide (DEC-068, matching SelectTrigger's placeholder since 54e03f1)
- demo: the cohort is every demo post core serves, dated into the requested range; a handful of text posts carry Photo, Video, File, Audio or Poll types so each row has posts; Priya is a brand user, Kai a moderator, Tomás an admin
Commit: 32ef515 (feat/posts-analytics, local, not pushed); follow-up in the SL-05 fix commit: the by-type fixture keeps only the filtered type's row, as content.go does (`WHERE t = @post_type`), and a locked-comments test for the content tables

## SL-05 Content performance: top creators and all posts
Frames read: Top by Creator Tables 86;1180:52440;1426:15995 (in 1394:130286; pinned column 27102:40803) · All posts full view 1938:103859 (header 27038:118573, footer 27038:117540, media-only row) · All posts in the page 6;1180:52440;1938:106773 · table states 1378:66318 · node JSON at 2405713691583384658
Anatomy walk (Figma number → the class that produces it):
- Top creators card: WidgetCard `surface="table"`, header 86 as SL-04, Select "Published posts" 200×36; the table runs 1330 inside 1136 and scrolls sideways (live 1330)
- creators head 40, 14/20 w500 #525252 `whitespace-nowrap`; widths # 40 · Creator 240 · Creator role 140 · Published posts, Reach, Impressions, Comments, Reactions 130 · Average Engagement Rate / Post 260 with a 12px info icon
- # and Creator pinned left, white, no gradient (the final frame hides it) — `pinned="left"`, Creator `left-10` (DEC-068; live: both stay at x 281 / 321 after a 400px scroll)
- creator rows 56 `h-14` (live 57, divider outside the cell): Avatar 40 #EBECFD initial #3B41EC, gap 8, name 14/20 w500 + BadgeCheck 16 #CA8A04 gap 4 on brand users (`size-4 text-warning`, the PostByline brand convention), user id 14/20 #525252 — CreatorCell
- role: Badge pad 2/8 r8 #E5E5E5 text 12/16 w600 #171717 — `Badge variant="secondary"` (User, Brand user, Moderator, Admin); average engagement rate "22.4%" 14/20 w500, no bar
- All posts header 86: title "All posts" with no info icon, description 14/20 #525252; action group gap 8: InputGroup 240×36 pad 4/12 r8 with Search 16 and "Search content" — SearchField `w-[240px]` (live 240×36); Select "Reach" 200×36
- All posts table: no # column; Post 360 · Content type 200 · Creator 240 · Destination 180 · metrics 130 · Engaged users 140 · Engagement rate 180 · Created date 140 · action 64 pinned right with the 24px fade — the SL-03 row, now `PostTableRow withRank={false}` (live row 2024 wide, 76 high + divider); media-only "No caption added." 14/20 w400 #A3A3A3
- footer 76 pad 20/24 (no stroke; the last row drops its divider → `border-t`): "1-10 of N items" left; « 36 · ‹ 42 · "10/page" Select 100×36 · › 36 gap 4 — TablePagination with `onFirst` and the page-size select `className="border-t px-6 py-5"` (live 77; the DS select is 102 wide)
- loading: 10 rows of 76 with a bar per cell (SL-03's skeleton); empty / no results under the head row as SL-04
Plan (stops waived, lead defaults): `creators` and `allPosts` query options (SL-04 commit); `resolveCreators` hydrates users through core `GET /api/v3/users/list` by internal id (name, public id, avatar via the files sidecar); `fetchAllPosts` runs core `GET /api/v2/search/posts` (`searchPostsV2` + the Content tab's `parseSearchInput`, now exported) and sends the hits as `ids`, then joins rows through `resolvePostRows`; TopCreatorsTable and AllPostsTable; keyword debounced 500 ms (`useDebouncedValue`); page resets on a new keyword, size, sort or filter
Gates (2026-10-02): typecheck ✓ · lint ✓ exit 0, 0 errors (one `no-unsafe-optional-chaining` in the new test fixed) · test ✓ 2074 tests · typecheck:governance ✓ · governance:ci ✓ "Governance OK — 115 requirements" · i18n:gate ✓ 0 strings · api:check ✓ 335 calls (search/posts v2 and users/list already in routes.json) · qa:copy-check ✓ · lint:comments ✓ · lint:ds ✓ · ds:check ✓ · ds:build ✓ no drift · build ✓
Tests (`PostsAnalytics.test.tsx`, SL-05 block): S-R14-2, S-R14-3, S-R14-4, plus creators by published posts with role badges and the brand check, a keyword with no hits sending `ids=` (empty, so the dashboard answers no match) and "No results found", an All posts row opening the sheet
Live check (agent, demo mode, Chrome): /components/posts?region=sg&view=analytics&aTab=content — Top creators 8 rows (the demo has 8 authors) by Published posts: User, Moderator, Brand user (gold check beside Priya Nair), Admin badges; sideways scroll keeps # and Creator; All posts 10 rows, "1-10 of 63 items"; "summer" → "Summer Glow Challenge — Week 1" and "Inside the Luma Beauty shade lab" (core search hits), "1-2 of 2 items"
Figma differences left:
- creator rows — 56 — 57 (divider outside the cell)
- page-size select — 100 — 102 (DS TablePagination)
- All posts footer « control — 36×36 pad 10 — DS PaginationFirst 36×36
- metric menu — 240 wide — trigger width 200 (DS SelectContent)
Questions logged (defaults taken, for the user's review):
- core search sends at most 100 hits as `ids` (`SEARCH_ID_LIMIT`; the dashboard takes up to 1000); posts past the first 100 hits are not reachable by keyword
- search runs `matchingOnlyParentPost` with no deleted flag, so a deleted post (R5 counts it) is not found by keyword; it still lists without a keyword
- the search input is too short to send (one character, a bare "#") → the whole cohort, as on the Content tab
- the keyword is view state, not a URL key (the Content tab keeps `q` in the URL; Analytics keeps none of its table state there)
- page sizes 10, 20 and 50 behind "10/page" (the spec says 10 per page; Figma draws the control)
- "Average Engagement Rate / Post" head tip follows Figma tooltip 1987:281853 (found 2026-10-05): "Formula: Σ Engagement Rate of qualifying Posts ÷ Number of qualifying Posts"; the column reads N/A when the dashboard has no view events
- Top creators title tip reuses the content tables' tip (SL-04)
- ST18 (core search throttled → inline Alert) is in neither slice's state list; a refused search shows the table's content fallback — deferred
- error state (ST62) is the shared WidgetFallback with Retry; it has no demo trigger and no `it` of its own
- `ids=` (empty) survives axios serialisation (checked with `axios.getUri`), so a keyword with no hits reaches the dashboard as "no match"
- a creator core no longer serves reads "Unknown creator" with no user id line; the internal id is never shown
Commit: 891a066 (feat/posts-analytics, local, not pushed)

## SL-06 Key insights
Frames read: `Group Key Insights` I1247:5639;1180:52440;1824:50580 (Overview, final) · states 1538:30978 (filled, partial 1871:91417, loading 1538:30950, "All non available → Hide Key insights") · spec 1545:214347 (show 3 cards / show 1 card 1807:82414) · node JSON at file version 2405721293669184998 (11:20 UTC, newer than 2405713691583384658)
Anatomy walk (Figma number → the class that produces it; live at main 976 wide, so cards read 325 not 378):
- heading: Lightbulb 16 stroke #0A0A0A + gap 4 + "Key insights" 16/16 w600 — `Text as="h2" size="base" semibold leading-4 flex gap-1`, `size-4` (live 16 high ✓)
- heading → box 16 `gap-4` ✓ (live 357−341); section → Key metrics 24 `gap-6` ✓ (live 475→499)
- box: 1136×118, r10, stroke #E5E5E5 inside, no shadow, white items — InsightGroup `rounded-lg border bg-card` (live 118 ✓: 116 content + the 1px border Figma strokes inside), cards `grid-cols-3` thirds, vertical separators #E5E5E5 `divide-x`
- card 1531:163544: pad 20 `p-5`, badge→sentence 16 `gap-4`; badge 20 high pad 2/8 r8 #171717, 12px icon, gap 4, 12/16 w600 #FAFAFA — default `Badge` unchanged (live rgb(23,23,23) / rgb(250,250,250) 12px 600, icon 12 ✓); icons TrendingUp · Star · PieChart
- sentence: 14/20 w400 #0A0A0A, values w600, two lines — `Text as="p" line-clamp-2` + `Trans` with a semibold `Text` (live 14px/20px, 600 ✓); "This post" #2563EB w500 — `Button variant="link" h-auto p-0` (live rgb(37,99,235) 500, 57×20)
- loading 1538:30950: badge bar 90×20 r8, lines 260×16 and 140×16 gap 8, #F5F5F5 — `InsightCard status="loading"` ×3 on `Skeleton` (frame wins over the handoff row's WidgetFallback kpi, contract 3)
- refresh: BusyOverlay over the box; error: WidgetFallback status="error" with Retry under the heading (ST27)
Plan (stops waived, lead defaults): `fetchInsights` / `resolveInsights` / `postAnalyticsQueries.insights` in `src/api/postAnalytics.ts` (key = region + Overview filters, keepPreviousData, `touchesContent('community')`); the community-name join shared with by destination (`communityNames`); InsightGroup + InsightCard composite (DEC-070: registry.meta, specimen, usage doc, figma-sync.yaml); KeyInsights in `src/components/posts-analytics/`; `insightsFixture` + demo route
Gates (2026-10-02): typecheck ✓ · lint ✓ exit 0, 0 errors (182 pre-existing warnings, none in changed files) · test ✓ 224 files / 2082 tests · typecheck:governance ✓ · governance:ci ✓ "Governance OK — 115 requirements" · i18n:gate ✓ 0 strings · api:check ✓ 335 calls (insights is the dashboard host, `api-exempt`) · qa:copy-check ✓ · lint:comments ✓ · lint:ds ✓ · ds:check ✓ · ds:build ✓ no drift after commit · build ✓
Tests (`PostsAnalytics.test.tsx`, SL-06 block): S-R12-1, S-R12-2, S-R12-3, S-R11-2, plus the three cards above Key metrics with the Overview filters and a core-named destination, ST22 skeletons, ST27 fallback. S-R12-2 is console-side (the console renders only what the dashboard serves); the eligibility rules and thresholds are the dashboard's (insights.go `selectInsights`, insights_test.go)
Live check (agent, demo mode, Chrome): /components/posts?region=sg&view=analytics — Momentum "increased 12.5%", Top content "This post … Skincare Lab", Content mix "Video … 18.2% … 41.6%"; section 150, box 118, badge 97×20; "This post" → sheet for p-8298 (Priya Nair, Selected period 3,020 reach); `&roles=brand` → one Content mix card 325 of 976; `&roles=admin` → no section, Key metrics directly under the filters
Figma differences left:
- card height — 118 (sentence frames 20 + 2 + 20) — 116 + border (one flowing 40px paragraph; the 2px is Figma splitting the sentence into frames)
- badge width — 95 — 97 (Figtree glyph width)
- single card — no border (1807:82414, 1871:91426) — the same bordered box, a third wide
- loading / Example instances — pad-left 16 — 20, as the final 1247:5639
Questions logged (defaults taken, for the user's review):
- wire shape from social-plus-dashboard feat/post-analytics `insights.go` (29cb938): `{range, insights[{type, momentum|top_content|content_mix}]}`; `delta_pct` is absolute (direction carries the sign); `content_type` is a code; thresholds are the spec Open defaults (10 posts, 10%, 10 points) in the dashboard
- a top post on a user feed (null `community_id`) reads "This post generated the most engagement in a user feed." — no Figma copy, TBC with Design
- the "(postType)" variant of the Top content sentence (spec Open) is not shown; "represents" ships as Figma draws it
- shares and deltas read up to one decimal ("12.5%", "20%")
- Trans tag for "This post" is `<post>`: `<link>` is a void HTML tag to i18next's parser and rendered an empty button
- the Key insights section is not shown on Content performance (R12 is the Overview's)
Commit: aa806c6 (feat/posts-analytics, local, not pushed)

## SL-07 Export
Frames read: Export 1548:177712 (all mode 1873:22697, selected mode 1673:61282, trigger 1673:63768) · node JSON at file version 2405721293669184998
Anatomy walk (Figma number → the class that produces it):
- trigger: outline 114×36 pad 8/12 r8, FileOutput 16 · "Export" 14/20 w500 · ChevronDown 16, gap 8 — `Button variant="outline" has-[>svg]:px-3` (live 116×36, glyph width as SL-01); busy swaps FileOutput for `Spinner` and disables it
- popover: 250 wide, r8, border #E5E5E5, 4 below the trigger, right edges aligned — `PopoverContent align="end" sideOffset 4 className="w-[250px] p-0"` (live 250; at a 1220 window Radix shifts it left to stay on screen)
- radio group: pad 12 `p-3`, rows 8 apart `gap-2`; radio 16 + 12 `gap-3`; label 14/14 w500 in a 16 row — `Label` in `flex h-4 items-center`; description 14/20 #525252, 6 under the label `gap-1.5`, wraps to 3 lines in 198 (live 196×60) — RadioGroup + RadioGroupItem, brand dot
- checklist (selected only): pad 0/4/4/4 `px-1 pt-0 pb-1`, rows 32 r6 pad 6/16 gap 8 `CommandItem px-4` (live 240×32), Checkbox 16 r4 #3B41EC; "Export all" then the sub-tab's 4 widgets, all ticked
- footer 48 with the top stroke inside → `Separator` + `h-[47px] px-2.5`; "{n} of 4 selected" 14/20 left (selected only); Export CSV pill 84×32 pad 8/10 12/16 w500 #3B41EC `Button size="sm" ml-auto` (live 83×32, 12px, rgb(59,65,236))
- heights: all 178 → live 180, selected 342 → live 344 (DS border outside the box, as SL-02)
Plan (stops waived, lead defaults): `EXPORT_WIDGETS` (export.go `Widgets`), `exportParams`, `exportRange`, `exportFilename`, `fetchExport` (blob) in `src/api/postAnalytics.ts`; `downloadBlob` lifted into `src/lib/download.ts` (UsageDashboard now uses it); ExportMenu in `src/components/posts-analytics/`, keyed by sub-tab so the checklist resets on a switch; demo route returns a small CSV naming the request
Gates (2026-10-02): typecheck ✓ · lint ✓ exit 0, 0 errors (warnings pre-existing; none in changed lines) · test ✓ 224 files / 2089 tests · typecheck:governance ✓ · governance:ci ✓ "Governance OK — 115 requirements" · i18n:gate ✓ 0 strings · api:check ✓ 335 calls (export is the dashboard host, `api-exempt`) · qa:copy-check ✓ · lint:comments ✓ · lint:ds ✓ · ds:check ✓ · ds:build ✓ no drift · build ✓
Tests (`PostsAnalytics.test.tsx`, SL-07 block): S-R13-1, S-R13-2, S-R13-3, S-R13-4, ST72 (default mode, 4 of 4, Export all toggles, none ticked disables Export CSV), ST74 spinner, the truncated info toast. S-R13-1 / S-R13-2 / S-R13-4 are console-side: the request's `mode`, `sub_tab`, `widgets`, range and filters are present or absent; the rows in the file (every active post, all 7 metrics, the 90-day window) are the dashboard's (export.go, export_test.go)
Live check (agent, demo mode, Chrome): /components/posts?region=sg&view=analytics → Export → All available data, no checklist, 180 high; Selected filters and period → 5 ticked rows, "4 of 4 selected", 344 high; Export CSV → popover closes, `post-analytics-overview-2026-09-25_2026-10-01.csv` whose rows read mode selected, the 4 Overview widgets and the range
Figma differences left:
- popover height — 178 / 342 — 180 / 344 (border outside the box)
- checklist rows — 242 — 240 (same 1px border inside the box)
- popover shadow — 0 1 2 -1 + 0 1 3 0 (shadow-sm) — DS PopoverContent shadow-md, as MultiSelectFilter
- trigger while open — 60% opacity in Figma — the DS outline button keeps full opacity
Questions logged (defaults taken, for the user's review):
- dashboard track: CORS sends no `Access-Control-Expose-Headers`, so the browser hides `X-Export-Truncated` and `Content-Disposition` from the console. The console reads `x-export-truncated` anyway (works once the dashboard adds `Expose-Headers: X-Export-Truncated, Content-Disposition`) and names the file itself the way export.go does, `post-analytics-<sub_tab>-<from>_<to>.csv`; "All available data" names the last 90 days ending yesterday in UTC
- error toast copy "The export failed. Try again." and truncated copy "The file was cut at 100,000 rows per table." — TBC with Design (no Figma copy)
- with no widget ticked Export CSV is disabled; "Export all" reads indeterminate when some are ticked and ticks all from there
- mode and ticks are view state: they persist while the page is open on that sub-tab and reset on a sub-tab switch or reload
- the popover closes on Export CSV; the trigger shows the spinner until the file is saved
- widget names in the checklist are the widget titles ("Top posts", not "Top performing posts")
- the export is a plain request, not a query: nothing caches or refetches it
Commit: 8f56120 (feat/posts-analytics, local, not pushed)

## Figma moved during Delivery
- 2026-10-02 10:45 UTC (version 2405713691583384658), re-diffed by the lead against 07:47: the full-view tables 1452:105407 / 1452:112240 were replaced by 1938:102355 / 1938:103859; a final "Key MetricsTooltips" section 1944:133489 (reactions tooltip gains a full stop — fixed in posts.json; the tooltip copy is no longer draft); sheet cards take the same tooltips; multi-type rows draw a chip per type; annotation "Media only post" → "Media-only post"; new annotation "Key insights Library Doc" on the insights group (its link is not in the REST data — read as Notion Appendix A, the insight library the spec already cites); the Top posts subtitle is now drawn "Ranked the selected metric…" (typo, "Ranked by" ships; spec Open)
- lead fixes 2026-10-02: chart curve `natural`; `src/components/posts-analytics` added to lint:ds ENFORCED_DIRS (0 violations)
- 2026-10-02 11:20 UTC (version 2405721293669184998): SL-06 / SL-07 frames read at this version; the earlier slices' frames were not re-diffed

## Final gates (lead, 2026-10-02, branch feat/posts-analytics)
typecheck ✓ · lint ✓ · test ✓ 2089 · typecheck:governance ✓ · governance:ci ✓ 115 requirements · i18n:gate ✓ 0 strings · api:check ✓ 335 calls · qa:copy-check ✓ · lint:comments ✓ · lint:ds ✓ 460 files · ds:check ✓ · ds:build no drift · build ✓

## Spec amended in Delivery
- 2026-10-02 R5: hard-deleted posts and their activity are excluded everywhere; soft-deleted posts still count (user: "exclude hard deleted and its activity too"; Figma tooltip names soft deletes only). Swept spec R5, R6, §5, S-R5-4…S-R5-7, slices SL-00, sketch §7 (Loops back to 02: 1). Dashboard change on PR #257: the hard-deleted row is removed rather than flagged (user, 2026-10-02: "why need is_hard_delete? not just exclude it?").

## Interaction audit 2026-10-02
Scope (user, 2026-10-02): "recheck every thing that click able or open able compare with figma or text, image, video etc rendering align with the figma". Frames refetched at file lastModified 2026-10-02 12:43Z (two independent checkers + the lead's own pass); 1833:102509 and 1944:133489 no longer resolve. Live in demo mode on :5176 at a 1220 viewport (main 976; Figma frames are main 1184 — widths compared relative). Result: **80 rows — 29 match · 43 fixed · 8 left · 0 held** (the user decided the held items 2026-10-02, see "User decisions" below).

| Area | Element | Figma | Result |
| --- | --- | --- | --- |
| Tabs | Content / Analytics line tabs 36 high, hover/active/focus | 1247:5639 | match (DS Tabs states) |
| Tabs | Sub-tab track 237 | 1247:5639 | left — 239.3, DS TabsList `gap-1` (DEC-037 rhythm) |
| Tabs | App header 64, toggle 28×28 at x16 #0A0A0A, separator 1×15 #E5E5E5 at x52, breadcrumb at x68 | 1247:5639 header 1103:32783 | fixed (user, 2026-10-02 "follow figma") — was 56, toggle x18 #525252, no separator, breadcrumb x58; app-wide AppLayout |
| Tabs | Heading → page tabs 28 | 1247:5639 | fixed (user, 2026-10-02) — was 16; PostsPage, both Content and Analytics |
| Tabs | Page tabs Content · Analytics, no Settings | 1247:5639 | fixed (user, 2026-10-02) — disabled Settings tab removed (Posts spec ST2 amended) |
| Filters | Triggers 200×36, placeholder 14/20 w400 #525252 | 1378:33190 | match |
| Filters | Chevron #525252 solid (Destination, Content type) | 1382:110730 | fixed — was `opacity-50` |
| Filters | Chevron points up while a menu is open (all three) | 1378:33190, 1382:110730 | fixed |
| Filters | Destination search narrows the placeholder group too, so "No destinations found" can show | 1382:110730 | fixed (placeholder group kept, spec R3) |
| Filters | Destination menu lists Group only, no "Not available yet" kinds | 1382:110730 | fixed (user, 2026-10-02; spec R3, S-R3-3 amended) — DestinationFilter `showUnavailableKinds={false}` on Analytics only; Posts Content and Comments & Replies unchanged |
| Filters | Destination "Searching..." — one centred 12/16 #525252 line, 24 above/below, no heading | 1382:110730 | fixed |
| Filters | Destination filled text colour | 1378:33190 #0A0A0A · 1382:110730 #525252 | left — Figma disagrees with itself; kept #0A0A0A, shared with Comments & Replies |
| Filters | Content type options Text, Photo, Video, File, Audio, Custom | 1382:110730 | fixed — Custom added (spec R5 amended) |
| Filters | Content type filled trigger 14/20 w400; no ring while open; selected check #3B41EC | 1382:110730 | fixed (DS Combobox) |
| Filters | Menu opens with the first row highlighted | 1382:110730 none | left — cmdk keyboard cursor (DS Command) |
| Filters | Creator roles menu 200, rows 32 pad 6/8, Checkbox 16 brand, Clear all row 40 | 1453:45181 | match |
| Filters | "Select creator roles (n)" + ×, × clears | 1378:33190 | match |
| Filters | Chip 24 r6 #F3F4F6/#D1D5DB, label 14/20 #525252, +N chip + tooltip, truncation tooltip, Clear all 83×32 | 1378:33206 | match |
| Filters | Chip × 16 at 70% | 1217:26520 | fixed (DS RemovableChip, was 12 at 100%) |
| Filters | `roles=brand&roles=admin` keeps both | — | fixed (`parseSearch` collects a repeated key) |
| Filters | Sticky band 64/112, stuck white + shadow | 1378:50839 | match |
| Date | Trigger 245×36, range 14/20 w500 | 1432:87588 | match |
| Date | × on every range incl. the default (a no-op there), side padding 12, × 16 at 70% | 1333:103619 | fixed (user, 2026-10-02; spec R16 amended) — was hidden on Last 7 days, padding 10, × 60%; × opacity is the DS DateRangePicker, app-wide |
| Date | Header "Filter by activity date" / "Filter by creation date" 44 high | 1432:87588, 1807:82476 | match |
| Date | Presets 152×32 r6 | 1432:87588 | fixed — were Button pills |
| Date | Calendar draws the month's own week count (5 for a 5-week month) | 1432:87588 | fixed — `fixedWeeks` dropped (popover 396, Figma 399) |
| Date | Future days 50% #525252, today #F5F5F5 | 1432:87588 | match |
| Date | Day header 21 high | 1432:87588 | left — 16, DS Calendar |
| Date | Cancel / Apply pills 36, Apply #3B41EC | 1432:87588 | match (Apply text #FFF vs #FAFAFA, DS Button) |
| Date | Card comparison follows the range | 1531:163476 | match |
| Export | Trigger, both modes, checklist all/partial/none, CSV busy/disabled, toasts | 1548:177712 | match (SL-07) |
| Export | Popover shadow-sm | 1548:177712 | left — DS PopoverContent shadow-md, app-wide |
| Insights | Bordered row, badges, bold values, "{destination}" bold | 1247:5639 | match — style 4 is SemiBold 600 in 1247:5639, 1538:30978 and 1545:214347 |
| Insights | Line 2 starts "compared with…", "in {destination}.", "but drives…" | 1247:5639 | fixed (`<br/>` in the copy) |
| Insights | Badge 95 wide | 1531:163544 | fixed — Badge padding now counts its 1px border (DS) |
| Insights | "This post" → sheet | 1247:5639 | match |
| Metrics | Info tooltip copy and side | 1944:133489 | match |
| Metrics | Tooltip #171717 pill, #FAFAFA text, r8, pad 6/12 | DS Tooltip 122:10 | fixed (DS, app-wide) |
| Metrics | Tooltip max width 344 | 1531:163476 | left — max-w-sm 384; the DS set defines no width |
| Metrics | Locked: label/value #A3A3A3, lock #0A0A0A, "View …" row | 1531:163476 | fixed (lock was #525252); "View …" is text, as UnlockReactionsStat (no URL in Figma) |
| Metrics | N/A, delta colours, two loading bars, no icon while loading | 1531:163476 | match |
| Chart | Metric menu 240, brand check on the pick | 1432:60216 | fixed 2026-10-06 (was wrongly "no check") |
| Chart | Whole-number ticks for counts | 1247:5639 | fixed (`allowDecimals` only for the rate) |
| Chart | Tick colour #525252 | 1247:5639 | fixed — DS chart selector missed recharts 3.8 `tick-value` |
| Chart | Grid inset 12 / 13, #E5E5E5 at 80%, labels right edge 30, x labels 12 below | 1247:5639 | fixed |
| Chart | A week that starts before the range labels the range's first day | — | fixed |
| Chart | Tooltip 200 wide r8, #E5E5E5 border, shadow-md, 12 right of the dot | 1247:5639 | fixed (DS ChartTooltipContent r10/shadow-xl → r8/shadow-md); it still follows the pointer's height — left |
| Chart | Empty / no results / loading | 1412:76749 | match; no-results breaks after "filters" — fixed |
| Tables | Metric menus 240, no check | 1468:374295, 1534:199465, 1698:253254 | fixed (DS SelectItem `indicator`) |
| Tables | "Published posts" in the content tables' heads and menus | 1394:130286 | fixed (chart and key metrics keep "Posts published") |
| Tables | Descriptions: Top posts, by type, by destination "Ranked by the selected performance metric during the selected period."; Top creators "Ranked by people with the highest…" | 1938:102355, 1394:130286 | fixed |
| Tables | "Post type" head; "Avg. engagement rate / post" head (info icon kept) | 1394:130286 | fixed |
| Tables | Title info icon only on Top posts | 1394:130286 Tooltip=false | fixed — removed from by type, by destination, Top creators |
| Tables | Body hashtags in #2563EB | 1247:5639 | fixed (network hashtags only; 1938:102355 draws them white, a Figma glitch) |
| Tables | Title w500 1 line, body #525252 2 lines, "No caption added." #A3A3A3 | 1938:102355 | match |
| Tables | Rows hug content: media-only 56, captioned 76 | 1938:103859 | fixed (was fixed 76) |
| Tables | Chip per type incl. multi-type; File border #FED7AA; icon chips pad right 6 | DS Color Chip 25031:94332 | fixed (token + DS Chip) |
| Tables | Avatar image vs initial; brand badge on Top creators only | 1938:102355, 1394:130286 | match (Top posts draws no badge) |
| Tables | Pinned columns, 24px fade on the action column; Top creators no fade | 1394:130286 | match (1452:107752 shows a fade; the final page frame wins) |
| Tables | Row action tooltip "View performance" to the left; Top posts title tip to the right | 17103:818, 17103:821 | fixed |
| Tables | ER head tooltip, MetricBar 111×8 | 1761:128449, 1432:83271 | match |
| Tables | Pagination by destination ‹ ›, All posts « ‹ 10/page ›; search debounce; no-results | 1457:241015, 1938:103859 | match; page-size 102 vs 100 left (Posts tab frame #316 draws 102) |
| Tables | Empty / no results: head row kept, 40 box, 18/28 + 14/22.75, 40 around a 120/138 block | 1378:66318 | fixed — Top posts used the generic illustration and dropped the head |
| Tables | Skeleton, error | 1531:146302 | match |
| Tables | Row 40/76 with the divider inside | 1394:130286 | left — 41/77, DS TableRow `border-b` |
| Tables | Role badge 42 / 74 | 1394:130286 | fixed (Badge padding; 41/74 live, glyph) |
| Tables | By type / by destination 2px sideways scroll | 1394:130286 | fixed (last column 204 so 1134 fits inside the card border) |
| Sheet | ×, overlay click, Esc close; Esc on an open preview closes the preview only | 1837:87272 | match; × at 70% fixed |
| Sheet | Panel shadow 0 4 6 -4 + 0 10 15 -3 | 1837:87272 | fixed (DS Drawer right/left `shadow-lg`) |
| Sheet | Overlay extra white 20% layer | 1837:87272 | left — DS overlay black 50% |
| Sheet | Sticky header 51; "Post in" + destination → community page | 1837:87272 | match |
| Sheet | Byline "{brand} ✓ ({publisher})" — 14px #CA8A04 check, 16/16 #525252 name in parentheses | 1247:5671 | fixed — follows PostFeedCard: check on a "Post as" post or a brand author, publisher from `publisherName` |
| Sheet | Avatar 40 initial | 1247:5671 | match (initial even for a brand post, as drawn) |
| Sheet | Attachments 112×112 r6 gap 8, preview opens over the sheet | 1247:5671 | fixed in the demo (PostContent already rendered them; the fixture had no media) |
| Sheet | Title 16/24 w600, body 16/24, hashtags #2563EB, See more 14/20 #2563EB after 3 lines, See less | 1247:5671 | match (demo caption now long with hashtags); RichText box 97.5 vs 96 left (existing renderer) |
| Sheet | Selected period / Lifetime, range chip ×, "Since published" | 1394:129120 | match |
| Sheet | Card icons #0A0A0A, #A3A3A3 when locked; lock #525252 | 1538:33610 | fixed (were #525252) |
| Sheet | Loading card keeps the info icon, one 167 bar | 1538:33610 | fixed |
| Sheet | Long content scrolls under the sticky header | 1837:87272 | match |
| Demo | Brand "Post as" post with 5 photos + a video, long caption with 3 hashtags; Photo, Video, File, Audio, Clip, Custom, Live stream, Poll posts; 10 creators, 4 with avatar images; unknown `aTargetId` empties the chart, insights and Top posts | — | fixed (fixtures) |

Decisions (lead defaults, for the user's review):
- Byline brand check: `post.publisherId` (a "Post as" post) or `author.isBrand`, as PostFeedCard and TopicPoolCard draw it; the analytics role bucket is not used
- "Published posts" is the content tables' wording; the chart menu and Key metrics keep "Posts published" (1247:5639)
- The All posts N/A cell shows with `/demo?lock=comment` rather than a fixture null
- Tooltip colour change is app-wide (DS Tooltip 122:10 draws #171717/#FAFAFA; the ledger had noted the drift); the arrow stays the pill colour (Figma #262626 seam question stays open)
- Badge padding, Chip padding/orange border, SelectItem `indicator`, Combobox trigger, Drawer shadow, chart tooltip and DateRangePicker presets/weeks are DS changes logged in figma-sync.yaml
Gates (2026-10-02, after the audit fixes): typecheck ✓ · lint ✓ 0 errors · test ✓ 224 files / 2096 tests · typecheck:governance ✓ · governance:ci ✓ 115 requirements · i18n:gate ✓ 0 strings · api:check ✓ 335 calls · qa:copy-check ✓ · lint:comments ✓ · lint:ds ✓ 460 files · ds:check ✓ · ds:build ✓ no drift · build ✓ · solution:check ✓
Commit: f34b524 (code + DS) and the docs commit after it

### User decisions 2026-10-02 ("follow figma")
Measured live in demo mode on :5176 against the node JSON (file lastModified 2026-10-02 12:43Z), before → after:
- App header (AppLayout, every page): height 56 → 64; toggle x18 → x16, 28×28, icon #525252 → #0A0A0A; separator none → 1×15 #E5E5E5 at x52; breadcrumb x58 → x68. Toggle and breadcrumb sit 0.5 above Figma (the 1px bottom border is inside the 64). In-page sticky bands stick inside `<main>`, below the header, so no offset moved; only DynamicUiPage's `calc(100vh-3.5rem)` → `4rem`. Checked: Posts Content and Analytics, Content performance (sticky filter band at 64 on scroll), Comments & Replies, Usage, Create post (two-crumb breadcrumb).
- Posts heading → page tabs: 16 → 28 (PageHeader `mb-7` on PostsPage).
- Settings tab: removed; tabs read Content, Analytics. Its two copy keys went with it; nothing else linked to it.
- Date chip ×: shown on Last 7 days too, on Overview and Content performance; clicking it there leaves the range and URL unchanged. Trigger padding 10 → 12 a side, × opacity 0.6 → 0.7 (DS PickerClearButton, every date picker). The icon sits 13 from the outer edge where Figma has 12: the CSS border sits outside the 12 padding, as on the other DS triggers.
- Destination menu (Analytics only): Destination (disabled kinds) + Group → Group. Comments & Replies still shows Destination, Source, Group and "Not available yet".
Commit: e95638b (code + DS) and the docs commit after it
Spec amended: R3, R16, S-R3-3 (sketch §7, Loops back to 02: 3); Posts spec ST2 and handoff ST2 (Posts sketch §7, Loops back to 02: 10).

## Re-audit 2026-10-06
Read-only re-audit of every annotation, tooltip, state frame and menu against file version 2406790434509761126 (98 rows: 79 match, 17 differ, 2 partial). Fixed:
- Chart and Top posts metric menus check the pick in brand (1432:60216, 1432:87017); the content-table menus stay unchecked (1468:374295). DS `SelectItem indicator="brand"`.
- Metric menus are disabled while their table loads or has no rows (1531:146302, 1531:156734, 1531:161852).
- Filter chips cap at 120 wide and truncate (chip component max width).
- The Engagement rate tooltip is one paragraph (1247:5706, 1761:128449).
- The post performance sheet's range is its own picker, changing only the sheet (annotation I1538:31773; spec R11 amended).
Not changed:
- Left-pinned # and Post columns from the generic "Sticky Column + Scrolling" state (1393:72590): the final page frame 1247:5639 pins only the right action column, and the final page frame wins (as for the fade, row 348).
- Chart state frames drawn without the metric Select (1412:76749): shared with Comments with another description, read as a template artefact; the Select stays.

