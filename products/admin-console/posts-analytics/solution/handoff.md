# Posts Analytics — design handoff

Status: capture of 2026-10-02 against the final Figma · disposable · TBC rows wait for Design (spec.md Open)
Format: Figma ⤷ Analytics under Posts (1012:32193) and Generic ⤷ Analytics (1378:32648), read at file version 2405661657054361399 (2026-10-02 07:47 UTC), re-diffed at 2405713691583384658 (10:45 UTC): tooltip copy final, sheet cards take the same tooltips, multi-type rows draw a chip per type · HTML prototype: none
Figma is final (user, 2026-10-02) and wins over the frame. Full inventory — every component, label, annotation, state, column width and colour, with the frame each was read from: https://claude.ai/artifact/8e7yLv1XsYUYHWdog9eRAg. Build each slice side by side with the Figma frame; styles must match it.

## State → component
| State | Component | Enforces | Note |
| --- | --- | --- | --- |
| ST1 | Tabs: TabsList variant="line" (Content, Analytics) + TabsList variant="default" (Overview, Content performance); filter bar sticky | R17, R18 | page tab bar, then the segmented sub-tab switcher; filter section sticks under the 64px header (heights 64 / 112 / 144 with chip rows, padding 12/24/16/24, white, shadow) — usage/ui/tabs.md; Figma 1247:5639, 1378:50839 |
| ST2 | Tabs: TabsList variant="default"; Combobox for the single-select content type | R2, R5, R18 | Content performance selected; the filter offers Text, Photo, Video, File, Audio and Custom — Figma 1394:130286, 1382:110730 |
| ST3 | new: MultiSelectFilter; RemovableChip for active chips | R3, R4, R5 | creator role is multi-select; chip row with at most 3 chips per filter, a "+N" chip (own ×, tooltip lists the rest one per line), truncated chips show the full label in a tooltip, "Clear all" resets every filter; a filled trigger swaps its chevron for × — DEC-069, Figma 1378:33190, 1456:101022 |
| ST4 | WidgetFallback status="loading" per widget | — | each widget sets its own `variant` (kpi, chart, table) — usage/composite/widget-fallback.md |
| ST5 | BusyOverlay | — | wraps each widget on a filter change; never stacked with a skeleton — usage/composite/BusyOverlay.md |
| ST6 | skip | — | each widget owns its empty state — agreed Chanatip (Design), 2026-10-01 |
| ST7 | skip | — | each widget owns its filtered-empty state — agreed Chanatip (Design), 2026-10-01 |
| ST8 | skip | — | paging belongs to the two paged tables (ST61) — agreed Chanatip (Design), 2026-10-01 |
| ST9 | WidgetFallback status="error" | — | per-widget retry; the filter bar stays usable |
| ST10 | WidgetFallback status="error" | — | same as ST9 |
| ST11 | skip | — | nothing is submitted on this page; export errors are ST73 — agreed Chanatip (Design), 2026-10-01 |
| ST12 | EmptyState case="forbidden" size="page" | R17 | direct URL without either permission; the tab itself is hidden |
| ST13 | skip | R17 | a 401 sends the admin to login through the shared client; no screen to draw — agreed Chanatip (Design), 2026-10-01 |
| ST14 | skip | — | n/a in spec — agreed Chanatip (Design), 2026-10-01 |
| ST15 | skip | — | n/a in spec — agreed Chanatip (Design), 2026-10-01 |
| ST16 | skip | — | n/a in spec — agreed Chanatip (Design), 2026-10-01 |
| ST17 | skip | — | n/a in spec — agreed Chanatip (Design), 2026-10-01 |
| ST18 | Alert | R14 | inline notice under the All posts search when core's search is throttled |
| ST19 | skip | — | offline n/a — agreed Chanatip (Design), 2026-10-01 |
| ST20 | EmptyState case="forbidden" size="page" | R17 | existing access-required behaviour of RouteGuard |
| ST21 | new: InsightCard | R11, R12 | dark badge with icon (Momentum TrendingUp, Top content Star, Content mix PieChart) + one sentence with bold values, max 2 lines; the three sit in one bordered box split by separators; "This post" is a link (#2563EB, w500) that opens the sheet — DEC-070, Figma 1538:30978 |
| ST22 | WidgetFallback status="loading" variant="kpi" ×3 | R12 | #F5F5F5 bars, r8 |
| ST23 | BusyOverlay | — | |
| ST24 | section not rendered | R12 | "All non available → Hide Key insights" — Figma 1538:30978 |
| ST25 | skip | R12 | same as ST24 — agreed Chanatip (Design), 2026-10-01 |
| ST26 | skip | R12 | at most 3 cards — agreed Chanatip (Design), 2026-10-01 |
| ST27 | WidgetFallback status="error" | — | |
| ST28 | skip | — | covered by the page surface — agreed Chanatip (Design), 2026-10-01 |
| ST29 | StatCard + DS change: `delta` | R6, R7 | "+10% vs. last 7 days" or "+10% vs. 18 Sep – 25 Sep 2025"; up #16A34A, down #DC2626, no change #171717 (DS success / destructive / foreground); card 272×116, r10, pad 20, gap 8; value 24/32 w700; label 14/20 w500 + info icon — DEC-071, Figma 1531:163476 |
| ST30 | StatCard + DS change: `delta` empty text | R7 | "No baseline to compare" — DEC-071 |
| ST31 | StatCard value="N/A" | R8 | value stays #0A0A0A, info icon stays — Figma 1531:163476 |
| ST32 | StatCard + DS change: `locked` with tooltip | R8 | label "Unlock <comments\|reactions>", N/A, both #A3A3A3; lock icon replaces the info icon; no delta; tooltip "Unlock <comments\|reactions> to boost engagement" + "View <comments\|reactions>" link with ArrowUpRight; same treatment as UnlockReactionsStat (src/components/comments-and-replies/UnlockTooltip.tsx) — DEC-071, Figma 1531:163476 |
| ST33 | StatCard status="loading" | — | |
| ST34 | BusyOverlay | — | |
| ST35 | skip | R8 | a card always shows a value — agreed Chanatip (Design), 2026-10-01 |
| ST36 | skip | — | 7 fixed cards — agreed Chanatip (Design), 2026-10-01 |
| ST37 | StatCard status="error" with onRetry | — | |
| ST38 | skip | — | covered by the page surface — agreed Chanatip (Design), 2026-10-01 |
| ST39 | ChartContainer (area) + ChartTooltip/ChartTooltipContent inside WidgetFallback variant="chart"; Select for the metric | R9 | area fill in the metric's chart token (DEC-063), no legend, tooltip with date + metric name + value and no swatch; card r10, header pad 24 with bottom border, Select 200×36 — Figma 1247:5639, 1432:60216 |
| ST40 | Spinner (LoaderCircle, 32px) in the plot area | — | Figma 1513:112210 |
| ST41 | BusyOverlay | — | |
| ST42 | WidgetFallback status="empty" (EmptyState case="empty-readonly") | R9 | copy chart-empty |
| ST43 | EmptyState case="no-results" | R9 | copy chart-no-results |
| ST44 | skip | — | one series — agreed Chanatip (Design), 2026-10-01 |
| ST45 | WidgetFallback status="error" | — | |
| ST46 | skip | — | covered by the page surface — agreed Chanatip (Design), 2026-10-01 |
| ST47 | DataTable + Select (rank by; each pick refetches) | R10 | widths # 40, Post 360, Content type 130, Creator 240, Destination 180, metrics 130 (Engaged users 140, Engagement rate 180), Created date 140, action 64 pinned right with a 24px gradient; row 76; post = title w500 1 line + body #525252 2 lines; content type is Chip (one per type); creator Avatar 40 + name + id; date and time on two lines; action Button variant="outline" size="icon" BarChartBig with Tooltip "View performance"; only the Engagement rate head has an info icon; heads not sortable — Figma 1452:105407, 1833:102509, 1761:128449 |
| ST48 | DataTable loading skeleton | — | |
| ST49 | BusyOverlay | — | |
| ST50 | EmptyState case="empty-readonly" | R10 | |
| ST51 | EmptyState case="no-results" | R10 | |
| ST52 | skip | R10 | fixed top 10 — agreed Chanatip (Design), 2026-10-01 |
| ST53 | WidgetFallback status="error" | — | |
| ST54 | skip | — | covered by the page surface — agreed Chanatip (Design), 2026-10-01 |
| ST55 | DataTable + Select (rank by; each pick refetches, back to page 1); engagement-rate column uses new: MetricBar | R14 | widget header pad 24/24/20/24, title 16/16 w600 + info icon, description 14/20 #525252; by type rows 40 high, MetricBar 111×8 in #3B41EC relative to the column max; Top creators rows 56, # and Creator pinned left, role as Badge variant="secondary", avg engagement rate as text; All posts action pinned right — DEC-072, Figma 1394:130286, 1452:107752, 1452:112240 |
| ST56 | SearchField | R14 | "Search content" — Figma 1378:66318 |
| ST57 | DataTable loading skeleton | — | |
| ST58 | BusyOverlay | — | |
| ST59 | EmptyState case="empty-readonly" | R14 | FolderOpen in a 40×40 #E5E5E5 r10 box; title 18/28 w500; description 14/22.75 #525252 — Figma 1378:66318 |
| ST60 | EmptyState case="no-results" | R14 | SearchX, same box and type — Figma 1378:66318 |
| ST61 | TablePagination via DataTable | R14 | by destination: "1-10 of N items" + ‹ ›; All posts: "1-10 of N items" + « ‹ "10/page" › — Figma 1457:241015, 1452:112240 |
| ST62 | WidgetFallback status="error" | — | |
| ST63 | skip | — | covered by the page surface — agreed Chanatip (Design), 2026-10-01 |
| ST64 | Drawer direction="right" (768 wide) + existing post renderer + StatCard ×6 with `icon`; Tabs for Selected period / Lifetime | R11 | sticky header "Performance" with ×; "Post in" + destination link; byline with created date; content only, "See more" after 3 lines, no moderation log, no footer; cards 229×100 in 3×2 with icons Users, Eye, MessageCircleReply, ThumbsUp, User, TrendingUp; range chip with clear × on the right — Figma 1837:87272, 1538:33610 |
| ST65 | the same Drawer, Lifetime selected | R11 | "Since published" |
| ST66 | StatCard status="loading" ×6 | — | |
| ST67 | skip | — | opens once per post — agreed Chanatip (Design), 2026-10-01 |
| ST68 | StatCard value="N/A" | R8 | |
| ST69 | skip | — | one post, no filters — agreed Chanatip (Design), 2026-10-01 |
| ST70 | EmptyState case="error" size="md" with onRetry | — | |
| ST71 | skip | — | covered by the page surface — agreed Chanatip (Design), 2026-10-01 |
| ST72 | Popover + RadioGroup + Checkbox + Button | R13 | 250 wide, right-aligned to Export; "All available data" (default, 178 high, no count) or "Selected filters and period" (342 high) with "Export all" + 4 widget checkboxes all ticked and "<n> of 4 selected"; Export CSV pill 84×32 #3B41EC 12/16 w500 — Figma 1548:177712 |
| ST73 | `toast()` from components/ui/sonner, error | R13 | copy TBD |
| ST74 | Button with Spinner | R13 | |
| ST75 | skip | — | n/a — agreed Chanatip (Design), 2026-10-01 |

Filters reused from the Posts page (domain components, not DS-registered): DestinationFilter (src/components/comments-and-replies/DestinationFilter.tsx) with `showUnavailableKinds={false}`, groups only, for R3; CommentsDateFilter's DateRangePicker with `withActions`, a clear × on every range (1333:103619), `title` ("Filter by activity date" / "Filter by creation date") and `disabledDates={{ after: yesterday }}` for R16, presets Last 7 days, Last 2 weeks, Last 3 weeks, Last 30 days, default Last 7 days. Popover 410×399, preset rail 160, calendar 248×293, Cancel and Apply as pills — Figma 1432:87588, 1548:177057. Content type chips use Chip: Photo blue (Image icon), Text grey (Text), Video violet (Video), File orange (Paperclip), Audio yellow (Mic), Custom grey (Sparkles) — Figma 1394:130286. Font Figtree throughout; hidden layers in Figma (toast, keyboard hints, table-head checkbox, sort arrows, Status column) are not built.

## Copy
| Key | Text | Source |
| --- | --- | --- |
| tab.analytics | "Analytics" | Figma 1247:5639 |
| subtab.overview | "Overview" | Figma 1247:5639 |
| subtab.contentPerformance | "Content performance" | Figma 1247:5639 |
| filter.destination.all | "All destinations" | Figma 1247:5639 |
| filter.creatorRole.all | "All creator roles" | Figma 1247:5639 |
| filter.contentType.all | "All content types" | Figma 1394:130286 |
| filter.creatorRole.options | "User" / "Brand user" / "Moderator" / "Admin" | Figma comment #88, 1452:107752 |
| filter.chips.destination | "Destination:" | Figma 1382:110730 |
| filter.date.title.overview | "Filter by activity date" | Figma 1432:87588 |
| filter.date.title.content | "Filter by creation date" | Figma 1807:82476 |
| filter.date.presets | "Last 7 days" / "Last 2 weeks" / "Last 3 weeks" / "Last 30 days" | Figma 1432:87588 |
| filter.export | "Export" | Figma 1247:5639 |
| filter.clearAll | "Clear all" | Figma 1456:101034 |
| insights.title | "Key insights" | Figma 1247:5639 |
| insights.momentum | "Momentum" · "Post engagement {increased/decreased} {delta}% compared with the previous period." | Figma 1247:5639 |
| insights.topContent | "Top content" · "This post generated the most engagement in {destination}." | Figma 1247:5639 |
| insights.contentMix | "Content mix" · "{Type} posts represents {share%} of posts but drives {share%} of engagement." | Figma 1247:5639 — "represents" TBC (spec Open) |
| metrics.title | "Key metrics" | Figma 1247:5639 |
| metrics.postsPublished | "Posts published" | Figma 1247:5711 |
| metrics.reach | "Total reach" | Figma 1247:5712 |
| metrics.impressions | "Total impressions" | Figma 1247:5713 |
| metrics.comments | "Total comments" | Figma 1415:147282 |
| metrics.reactions | "Total reactions" | Figma 1415:147283 |
| metrics.engagedUsers | "Engaged user" | Figma 1415:147285; "Engaged users" elsewhere — TBC (spec Open) |
| metrics.engagementRate | "Engagement rate" | Figma 1415:147286 |
| metrics.tip.postsPublished | "Number of posts published during the selected period, including posts that were later soft deleted." | Figma 1247:5708 — final (Figma 1944:133489) |
| metrics.tip.reach | "Number of unique people who viewed at least one post during the selected period, regardless of when the post was published." | Figma 1247:5709 — final (Figma 1944:133489) |
| metrics.tip.impressions | "Total number of times posts were viewed during the selected period. Repeat views by the same person are counted." | Figma 1247:5710 — final (Figma 1944:133489) |
| metrics.tip.comments | "Total number of comments taken on posts during the selected period, regardless of post creation date." | Figma 1415:147287 |
| metrics.tip.reactions | "Total number of reactions taken on posts during the selected period, regardless of post creation date." | Figma 1944:133489 — final |
| metrics.tip.engagedUsers | "Number of unique people who reacted to or commented on a post during the selected period." | Figma 1415:147305 — final (Figma 1944:133489) |
| metrics.tip.engagementRate | "Engaged users ÷ People reached* × 100" / "*People reached on posts where comments or reactions are enabled." | Figma 1415:147311 — final (Figma 1944:133489) |
| metrics.noBaseline | "No baseline to compare" | Figma 1531:163476 |
| metrics.lockedLabel | "Unlock comments" / "Unlock reactions" | Figma 1531:163476 |
| metrics.vsPreset | "vs. last 7 days" (the preset name) | Figma 1531:163476 |
| metrics.vsRange | "vs. {from} – {to}" | Figma 1531:162374 |
| metrics.unlock.comments | "Unlock comments to boost engagement" / "View comments" | Figma 1451:95513 |
| metrics.unlock.reactions | "Unlock reactions to boost engagement" / "View reactions" | Figma 1412:81479 |
| chart.title | "Performance over time" | Figma 1247:5639 |
| chart.description | "Daily totals for the selected metric, by the date the activity happened." | Figma 1247:5639 |
| chart-empty | "No data available" / "Data activity is unavailable for the selected scope." | Figma 1412:76731 |
| chart-no-results | "No results found" / "Try adjusting the search keywords, filters⏎or date range to get results." (break after "filters") | Figma 1513:112191, 1412:76749 |
| topPosts.title | "Top posts" | Figma 1247:5639, renamed 2026-10-02 07:47 UTC |
| topPosts.description | "Ranked by the selected performance metric during the selected period." | Figma 1247:5639, 1938:102355 (final 12:43Z) |
| topPosts.tooltip | "Ranked by activity generated during the selected date range." | Figma 1247:5639 |
| topPosts.view | "View performance" | Figma 1833:102509 |
| post.noCaption | "No caption added." | Figma 1452:112240 (14/20 w500 #A3A3A3) |
| contentType.* | "Text" / "Photo" / "Video" / "File" / "Audio" / "Custom" | Figma 1394:130286 |
| creatorRole.* | "User" / "Brand user" / "Moderator" / "Admin" | Figma 1452:107752 |
| byType.title | "Performance by content type" | Figma 1394:130286 |
| byType.description | "Ranked by the selected performance metric during the selected period." | Figma 1394:130286 (final 12:43Z) |
| byType.column | "Post type" | Figma 1394:130286 |
| contentTables.publishedPosts | "Published posts" (content tables' heads and menus; chart and Key metrics keep "Posts published") | Figma 1394:130286, 1468:374295 |
| tables.metric.publishedPosts | "Published posts" | Figma 1394:130286 |
| byDestination.title | "Performance by destination" | Figma 1457:241015 |
| byDestination.description | same as byType.description | Figma 1457:241015 |
| creators.title | "Top creators" | Figma 1452:107752 |
| creators.description | "Ranked by people with the highest selected performance metric for posts in the selected period." | Figma 1394:130286 |
| creators.role | "Creator role" | Figma 1452:107752 |
| creators.avgEr | "Avg. engagement rate / post" | Figma 1394:130286 |
| creators.avgTip | "Formula: Σ Engagement Rate of qualifying Posts ÷ Number of qualifying Posts" | Figma 1987:281853 |
| allPosts.title | "All posts" | Figma 1378:66318 |
| allPosts.description | "Individual post performance. Metrics are lifetime for every post in the cohort." | Figma 1378:66318 |
| allPosts.search | "Search content" | Figma 1378:66318 |
| postPerformance.period | "Selected period" | Figma 1394:129120 |
| postPerformance.title | "Performance" | Figma 1837:87272 |
| postPerformance.postIn | "Post in" | Figma 1837:87272 |
| postPerformance.lifetime | "Lifetime" / "Since published" | Figma 1394:129120 |
| export.all | "All available data" / "Includes all data recorded in this console within the last 90 days." | Figma 1548:177712 |
| export.selected | "Selected filters and period" | Figma 1548:177712 |
| export.exportAll | "Export all" | Figma 1548:177712 |
| export.count | "{n} of {total} selected" | Figma 1548:177712 |
| export.submit | "Export CSV" | Figma 1548:177712 |
| export.error | TBD | — |
| widget.error | TBD | not drawn |

## Design detail (final Figma, 2026-10-02)
Read from the node JSON and Dev Mode annotations; the inventory artifact linked above has the renders and the node coverage list.

Type (Figtree)
| Element | Size / line | Weight | Colour |
| --- | --- | --- | --- |
| Widget title | 16/16 | 600 | #0A0A0A |
| Widget description | 14/20 | 400 | #525252 |
| Table head | 14/20 | 500 | #525252 |
| Table number, destination, creator name | 14/20 | 500 | #0A0A0A |
| Post body, user id, time | 14/20 | 400 | #525252 |
| Metric value | 24/32 | 700 | #0A0A0A |
| Metric label | 14/20 | 500 | #0A0A0A |
| Delta | 12/16 | 400 | R7 colours |
| Badge (insight type, creator role) | 12/16 | 600 | #FAFAFA on #171717 / #171717 on #E5E5E5 |
| Insight sentence | 14/20 | 400, values 600 | #0A0A0A |
| Removable chip | 14/20 | 400 | #4B5563 on #F3F4F6, border #D1D5DB, r6, pad 4/6/4/8 |
| Empty-state title / description | 18/28 / 14/22.75 | 500 / 400 | #0A0A0A / #525252 |

Surfaces: cards r10, border 1px #E5E5E5, drop shadow; table cells pad 8/16 with a bottom border; Select, date trigger and Export button 36 high, r8, pad 8/12 (Selects 200 wide, date trigger 245); content-type chip r99, pad 4/6/4/8, 24 high.

Column widths
| Table | Columns (px) | Row |
| --- | --- | --- |
| Top performing posts | # 40 · Post 360 · Content type 130 · Creator 240 · Destination 180 · Reach, Impressions, Comments, Reactions 130 · Engaged users 140 · Engagement rate 180 · Created date 140 · action 64 (pinned right, 24px gradient) | 76 |
| By content type | # 40 · Content type 140 · Published posts 122 · Reach 120 · Impressions 130 · Comments 120 · Reactions 120 · Engaged users 140 · Engagement rate 206 (MetricBar) | 40 |
| By destination | as by content type, Destination in place of Content type | 40 |
| Top creators | # 40 and Creator 240 (pinned left) · Creator role 140 · Published posts, Reach, Impressions, Comments, Reactions 130 · Average Engagement Rate / Post 260 | 56 |
| All posts | Post 360 · Content type 130 · Creator 240 · Destination 180 · Reach, Impressions, Comments, Reactions 130 · Engaged users 140 · Engagement rate 180 · Created date 140 · action 64 (pinned right) | 76 |

Annotations, verbatim
- Chart content 1276:44713: "Chart x-axis granularity based on selected period: 7 days → daily points / up to 30 days → daily points / >30 days, up to 90 days → weekly / >90 days → monthly"
- Chart tooltip item: "show the selected metric"
- Metric menus: "Show default metric: Posts published" (chart, 1432:60216) · "Reach" (Top performing posts 1432:87017, All posts 1698:253254) · "Published posts" (by content type, by destination, Top creators 1468:374295, 1534:199465)
- Date picker 1432:87588, 1807:82476: "default: Last 7 days" · Generic 1548:176790: "Date filter labels should adapt to each component's context."
- Top posts avatar: "Show user's image if added"
- By content type 1432:83271 and by destination rows: "Height -> Hug content / Re-rank the order once sorting or filter changed"
- All posts search: "search keywords follow existing" · media-only row: "Media only post"
- Key insights heading 1871:91421: "Key insights: Max 3 card / If there isn't enough data to display on all 3 cards -> show eligible insight cards / Max 2 lines" · example: "View Post analytics"
- Metric card 1531:162374 trend row: "{starting date - ending date}" · state sheet: "add icon for each metric" (sheet only, comment #119)
- Sheet header: "Sticky at the top" · sheet content: "Post content only / follow existing text limits behavior / no moderation log / truncated using See more when exceeding the 3rd line (similar to the current one.)" · See more: "Allow expand / collapse"
- Removable chip 1378:33206: "each filter group: show a maximum of 3 visible chips per filter. each chip has a maximum width. If the label exceeds that width, truncate the label with an ellipsis (…). if > than 3 options are selected, group the remaining selections into a +N overflow chip."
- Clear all: "clear all values -> the dropdown filters are back to their default state." · multi-select menu item: "Back to the default state/selection"
- Sticky filter section 1378:50839: "Sticky at the top"
- Export 1548:177712: radio "default selected" · description "all data from last 90 days" · menu item "default select all widgets export"

Not built: layers hidden in every Figma frame — toast ("Topic added", "Undo", "No internet connection."), keyboard hints on Export and tooltips, the table-head checkbox, sort arrows on heads, a "Status" column, the sheet footer, admin activity log and schedule status. The green "Existing behavior" box is a designer marker.

## New components and patterns
Confirmed by Design (Chanatip), 2026-10-01; updated to the final Figma 2026-10-02.
- MultiSelectFilter — multi-select filter with "Select <things> (n)" trigger, checkbox list and active chips with Clear all; Combobox is single-select only — Figma 1378:33190 — DEC-069 → /figma-ds-sync
- InsightCard — type label with icon over one sentence whose values are bold; reused 3 times — Figma 1531:163544 — DEC-070 → /figma-ds-sync
- StatCard `delta`, `locked` and `icon` props — delta line ("+10% vs. <range>" or "No baseline to compare"), a locked state with lock icon and tooltip, and a leading metric icon used only in the post performance sheet; a DS change, not a className override — Figma 1531:163476, 1538:33610 — DEC-071 → /figma-ds-sync
- Chart tokens chart-7 to chart-17 — the Figma chart ramp (chart-7 #3B41EC, chart-8 #B1B3F7, chart-9 #3769EC, chart-10 #AFC3F7, chart-11 #45A5ED, chart-12 #B5DBF8, chart-13 #f66005, chart-14 #F7C506, chart-15 #F568F0, chart-16 #27265E, chart-17 #828282); globals.css has only chart-1 to chart-5 — Figma 1568:177793 — DEC-063 → /figma-ds-sync
- MetricBar — inline proportion bar (111×8, r9999, #3B41EC on a light track, length relative to the column max) with a percentage, for the engagement-rate column — Figma 1432:83271 — DEC-072 → /figma-ds-sync

## Skipped — agreed, not dropped
- ST6, ST7, ST8 page-level empty and paging — each widget owns them — agreed Chanatip (Design), 2026-10-01
- ST11, ST75 nothing submitted besides export — agreed Chanatip (Design), 2026-10-01
- ST13 denied mid-session — 401 → login, no screen — agreed Chanatip (Design), 2026-10-01
- ST14–ST17, ST19 n/a states — agreed Chanatip (Design), 2026-10-01
- ST25, ST26, ST35, ST36, ST44, ST52, ST67, ST69 — nothing extra to draw — agreed Chanatip (Design), 2026-10-01
- ST28, ST38, ST46, ST54, ST63, ST71 — covered by the page surface — agreed Chanatip (Design), 2026-10-01
