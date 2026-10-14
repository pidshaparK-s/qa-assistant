# Posts (admin-console/post-content) — Day 0 intake (QA)

Date: 2026-09-21 (replayed 2026-10-04) · Mode: **no-frame replay @ Figma as of today** — the frame is in Notion and was not available; no PRD either, so the only inputs are Figma + console today.
**Caveat:** Figma file `M6cjjCbL4R4OUSSCabpFI8` was last modified 2026-10-02, after the replay date. Some frames may already carry decisions the room made after 09-21 (e.g. `🆕` markers on "Decline post" 314:59775 and "Less than 15-min … mid-process" in 382:90630). Treat any Figma value below as possibly post-dated.
Inputs:
- Figma `⤷ View post` 157:1297 (sections 162:12390 Published · 207:39499 Scheduled · 259:43274 Requires approval · 207:38276 Deleted · 207:38959 Featured · 314:63978 cross-component nav)
- Figma `⤷ Create & Edit post` 157:1296 (207:36368 Create · 357:85187 Edit published · 382:90630 Edit scheduled / 15-min cutoff)
- Figma `💠 Key page components` 129:866 (515:19021 list · 523:24371 Creation · 529:29990 Edit scheduled · 529:29987 Editing · 791:25432 Upgrade required)
- Figma `🌏 Generic cases: All` 484:8020 (538:118744 Page States · 570:125148 destination filter · 588:62661 date filter · 625:25259 sorting · 538:118240 pagination · sticky 539:25577 · sticky 1873:8793)
- console today: classic posts on `main` @ `24ce6dab` (2026-09-20, last commit before the replay date; HEAD of `main` folds console-next in and was not used) — `src/pages/posts/{PostsAndComments,CreatePost,feedFilter}.tsx`, `src/components/post/{PostActionsMenu,PostAuthoring,FeedAndAccountFields}.tsx`, `src/api/posts.ts`, `src/config/adminPermissions.ts`, `src/i18n/locales/en/posts.json`
- `src/config/sitePermissions.ts` (origin/next) · S-CAT (origin/next `.claude/skills/solution/reference/goldfish.md`) · knowledge `testability-catalogue.md` (no entry has feature = posts)

Verdict: **NOT READY — 6 must-before-03 unknowns** (no frame: rank, events and appetite are frame fields nobody has given QA; scope vs classic parity and three platform-truth questions change the shape)

Source tags: `frame §n` · `PRD §n` · `Figma <node>` · `console <path>` · `core <file:line>` · `knowledge <file#id>` · `derived` (inferred — PM confirms) · `UNKNOWN`

## 1 QA frame card

| # | Need | Value | Source | QA uses it for |
|---|---|---|---|---|
| 1 | Capabilities, ranked | C1 An admin creates a post in a publishing destination, now or scheduled, as Myself or a Brand · C2 An admin finds posts by status tab (Published / Featured / Scheduled / Requires approval / Deleted), search, destination, creator and date · C3 An admin edits a published post with an optional reason, and reads its change history · C4 An admin edits, reschedules or cancels a scheduled post · C5 An admin approves or declines a pending post · C6 An admin features a post in its destination (replacing the current one) or removes the feature · C7 An admin deletes a post · C8 An admin clears a post's flags · C9 An admin copies a post's link and ID · C10 An admin opens a post's comments and reactions from the post. **Rank: none** | list: Figma 157:1297, 157:1296 · rank: `UNKNOWN` | traceability; test depth by rank |
| 2 | Actors → system roles | Content admin → console admin role with `VIEW_POST_AND_COMMENT_MANAGEMENT` (page) plus, per action, `EDIT_POST_AND_COMMENT` (edit), `CAN_MANAGE_FEATURED_POST` / `CAN_MANAGE_GLOBAL_PINNED_POST` (feature), `MODERATE_POST_AND_COMMENT`, `MANAGE_POST_AND_COMMENT`, `CAN_USE_BRAND_USERS` (post as Brand). Post author (end user) → no console account (sees results in the app). Which permission gates create, schedule, delete, approve/decline: not gated in classic beyond page view | console `src/config/sitePermissions.ts` · console `src/config/adminPermissions.ts` · console `PostActionsMenu.tsx:203-298` · `FeedAndAccountFields.tsx:82-86` · gating of create/delete/review: `derived` | which roles to test with |
| 3 | Platform coverage | console (this feature). App side (UIKit) observes the effects: featured post on top of the destination, edit not marked as edited, owner not notified, deleted post not visible | `derived` from Figma 357:85187 note ("On the UI Kit side, the post won't be marked as edited…") and 382:90268 feature copy | configurations; cross-product cases |
| 4 | Boundaries (what is out) | Figma draws none of: poll posts, live-stream posts, product tagging, post tags / hashtag limits, pin to community, community-featured vs global-featured split, hide/unhide, flag post, content-quality filter, mark-as-checked, the classic Comments top tab. Classic has all of them. Analytics tab has its own Figma page (1012:32193) → assumed a separate feature | `derived` (Figma absence vs console `CreatePost.tsx`, `PostActionsMenu.tsx`, `feedFilter.ts`) — absence is not a decision | out-of-scope up front |
| 5 | Constraints (entitlement, quota, legal) | Module not entitled → "Upgrade required" page · Brand not entitled → Brand option disabled + "Unlock brand profile to boost engagement" tooltip · max 100 scheduled posts in pending status · max 10 media per post · title ≤150, body ≤50,000, alt text ≤100, reason ≤250 chars · network blocklist (words in title, links in body) · one featured post per destination · change history keeps the 10 most recent console changes + the original | Figma 791:25432 · 749:138952 · 207:36368 toasts ("max scheduled: 100 pending status") · 523:24371 · 357:85187 | negative cases |
| 6 | Measurement / events | — | `UNKNOWN` | instrumentation cases |
| 7 | Names (internal · customer-facing) | Page "Posts"; tabs **Published** (classic: "Posted"), Featured, Scheduled, Requires approval, Deleted; "publishing destination" (classic: feed / community / target), "All destinations" (renamed from "All publishing destinations", sticky 1873:8793); "Feature post to publishing destination" (classic: Feature globally / Feature in community / Pin); "Post as: Myself · Brand"; scheduled badges Pending · Failed · Rescheduled; Declined sub-tab under Requires approval | Figma 515:19021, 162:12390, 259:43274, 207:39499 · console `posts.json` subTabs | exact copy in expected |
| 8 | Complexity · appetite | — | `UNKNOWN` | QA time reservation, depth |

## 2 Rule candidates (from Figma copy + console today — NOT rules; the room decides)
- RC1 Title is optional; at most 150 characters (counter 0/150 → 150 allowed) — Figma 523:24371 · console `PostAuthoring.tsx:42` — [product]
- RC2 Body at most 50,000 characters; a post needs body text **or** at least one attachment — Figma 523:24371 · console `CreatePost.tsx:369-372` (Figma marks no field required) — [product]
- RC3 At most 10 media per post ("at a time" in copy = per post in console) — Figma 621:102823 · console `PostAuthoring.tsx:101` — [product]
- RC4 Each photo takes alt text of at most 100 characters — Figma 207:36368 — [product]
- RC5 Mentions are available only when the destination is a group, and only after a destination is chosen — Figma 207:36368 — [product]
- RC6 Post as Brand needs the brand entitlement and `CAN_USE_BRAND_USERS`; otherwise Brand is disabled with a tooltip — Figma 749:138952 · console `FeedAndAccountFields.tsx:82-86` — [system]
- RC7 A scheduled time must be in the future and at least 1 hour from now — Figma 207:36368 error copy · console `CreatePost.tsx:68` — [product]; which clock, and is exactly 60 min allowed? (QA decided below)
- RC8 At most 100 scheduled posts may be pending; the 101st fails on submit — Figma 207:36368 — [system]; counted per what? (Q7)
- RC9 A scheduled post can be edited or rescheduled only while at least 15 minutes remain before its scheduled time; a save that crosses the cutoff mid-edit fails — Figma 382:90630, 207:39499 — [product]
- RC10 A scheduled post can be cancelled until it publishes; cancel cannot be undone — Figma 207:39499 ("Not Published/Failed yet? → YES") — [product]
- RC11 At its scheduled time a pending post publishes and moves to Published; or it shows Failed with a reason — Figma 207:39499 — [system]
- RC12 One featured post per destination; featuring another asks to replace, and the replaced post stays published but unfeatured; also available at create — Figma 314:57576, 207:36368 — [product]
- RC13 Removing the feature keeps the post published — Figma 571:52117 — [product]
- RC14 Editing a published post logs the change with an optional reason; the app does not mark the post edited and does not notify its owner; Save is enabled only when something changed — Figma 357:85187 — [product]
- RC15 Change history shows the 10 most recent console changes plus the original — Figma 357:85187 — [system]
- RC16 Create / edit fail when the title has a blocked word or the body has a blocked link; the admin stays on the form — Figma 207:36368, 357:85187 — [system]
- RC17 Create / edit fail when the destination is deleted mid-process; edit fails when the post is deleted while editing — Figma 207:36368, 357:85187 — [system]
- RC18 Delete cannot be undone; the post disappears for users but stays in the console's Deleted tab with "Deleted by" (an admin or AI); deleting an already-deleted post reports "Post is already deleted." — Figma 314:57577, 207:38276, 737:133320 — [product]
- RC19 Clear flags resets the flag count to zero, cannot be undone, takes an optional reason (≤250) and is logged; AI moderation results stay visible — Figma 314:57572 — [product]
- RC20 Approve moves a pending post to Published with "Approved by"; Decline keeps it unpublished and lists it under Declined — Figma 613:95651, 843:21725 — [product]; **classic says declined posts are permanently deleted** (console `posts.json:250`) (Q4)
- RC21 A review on a post another admin already reviewed fails with "Post has been reviewed." — Figma 804:43590 — [system]
- RC22 Leaving create or edit with unsaved changes asks to discard — Figma 1703:315878 — [product]
- RC23 Scheduled tab filters and sorts by scheduled date (next 7 / 14 / 21 / 30 days, custom); other tabs by creation date (today, last 7 / 14 / 21 / 30 days); default all time; 20 per page — Figma 588:62832, 588:62661, 625:25259, 538:118240 — [product]

## 3 States the inputs show (S-CAT walk, draft)
Generic Page States (538:118744) covers every Posts surface: §3 empty per tab, §4 filtered-to-nothing, §5 pagination, §6 network fallback, §7 API-error fallback, §8 error toast after submit, §9 access denied (direct URL), §10 revoked mid-session, §11 upgrade required (791:25432), §17 no console account. §16 offline is n/a (S-CAT).

| Surface (Figma node) | Drawn | Not drawn — ask or apply standing look |
| --- | --- | --- |
| Posts list, 5 tabs (515:19021, 162:12390 …) | §3 (incl. Pending/Declined variants), §4, §5, §6, §7, §9, §10 (as toast "Access restricted…"), §11, §14 (conflict toasts per action) | §1 skeleton, §2 busy overlay, §12 feature off, §15 rate limit → standing look. §10 drawn as a toast, S-CAT says 403 state → follow Figma (newer, same team) |
| Create post page (523:24371, 207:36368) | §8 (blocked word/link, destination deleted), §11 brand not entitled (disabled + tooltip), §13 scheduled limit (as submit toast), schedule field errors, discard dialog, mention search loading / no results | §13 drawn as a submit-time toast, S-CAT says disabled + tooltip → follow Figma (count is server-side). Media upload failure / file-type / size errors: "Check media guidelines … follow existing" → classic dialog. §1, §6, §7 for the destination and creator pickers → standing look |
| Edit published post (529:29987, 357:85187) + Review changes / Change history dialogs | §8 (blocked word/link, destination deleted), §14 deleted while editing, history list | Change history empty (never edited) → standing §3. Editing a post whose type the form can't show (poll, live stream — classic hides Edit) → depends on Q1 |
| Edit scheduled / Reschedule (529:29990, 314:58127, 382:90630) | 15-min cutoff footer, cutoff crossed mid-edit, reschedule success/fail toasts | Reschedule date-picker validation (min offset) not drawn → Q8 |
| Scheduled card states (207:39499) | Pending, Rescheduled, Failed + "[Fail reason message]", Once published → Published | Failed reasons are a placeholder → Q9. Actions on a Failed post → Q10 |
| Confirm dialogs: delete, clear flags, feature/replace, remove feature, decline, cancel scheduled, discard | each dialog + success and failure toast | §15 rate limit → standing look |
| Post detail / comments / reactions sheets (314:63978) | cross-component navigation, reactions sheet | owned by Comments & Reactions features — out of this feature's cases beyond "opens" |

## 4 Early testability flags
- TF1 **Time** — scheduled publish needs ≥1 h of real waiting; the 15-min cutoff needs a post placed exactly around it — ask Eng at 02 for a staging override of the minimum offset (or a "publish now" test hook), and confirm the cutoff uses the server clock — lens: Time
- TF2 **Limit 100 pending scheduled posts** — on shared staging the case must create 100 real scheduled posts, and other runs share the count — ask for a lower limit on a dedicated test network, or a network reserved for the case — knowledge `testability-catalogue.md#TC-NETWORK-SETTING`, lens: Limits
- TF3 **Scheduled post Failed** — no known way to make a publish fail on purpose — needs the failure reasons (Q9) and one we can trigger (e.g. delete the destination before publish) — lens: Async
- TF4 **Requires approval** — needs a destination with post review on and a pending post written by a user (SDK/API as end user, not the console) — seed via API; name the network/community setting in the case — `#TC-NETWORK-SETTING`
- TF5 **Blocklist** — blocked words/links are a network setting shared on staging — the case names the network and a blocklisted word/link it owns — `#TC-NETWORK-SETTING`
- TF6 **AI moderation** ("Deleted by AI", AI flags kept after clear flags) — credentials not on staging — seeded data or manual — `#TC-AI-MODERATION`
- TF7 **Entitlement** — Upgrade-required page and Brand-not-entitled need networks in those states — entitlement stub / named network — `#TC-ENTITLEMENT-GATE`
- TF8 **Concurrency** (deleted while editing, reviewed by another admin, destination deleted mid-create) — second admin needs a second browser profile, or the test deletes via API between steps — `#TC-SHARED-SESSION`
- TF9 **Permissions** — one standing custom role per permission set (edit-only, feature-only, view-only, no brand); never create roles per test; revoked mid-session needs the shared-role caveat — `#TC-ADMIN-ROLE-PERMANENT`, `#TC-PERMISSION-REVOKED`
- TF10 **Cross-product** — "not marked edited", "owner not notified", "featured on top", "deleted not visible to users" are app-side — who verifies on which UIKit build; notification absence is an Async negative (how long to wait) — lens: Cross-product, Async

## 5 Questions for the ticket chat (each passes the 4 criteria)
### Must answer before 03
- Q1 → PM: Is the scope exactly what Figma draws (classic-only post types and actions — poll, live stream, product tags, post tags, pin, hide/unhide, flag, content-quality filter, mark-as-checked — are dropped), or must every classic capability survive? — changes: capabilities, boundaries (field 4)
- Q2 → PM: Rank C1–C10. — changes: field 1 (what gets cut first at 03, test depth). *(fails criterion 1 strictly — rank changes depth, not a rule — kept because the skill requires rank and the frame would carry it)*
- Q3 → Architect: Is Figma's one "featured post" per destination the existing placements (global pin for Home page, community announcement for groups) or a new placement? — changes: RC12/RC13 limit (classic: global capped by network `maxGlobalPinnedPost`, community at 1; Figma: 1 with replace), API surface
- Q4 → Architect: Does core keep a declined post listable (Figma: Declined tab), when classic says declined posts are permanently deleted? — changes: RC20, the Declined state, a tab. *(check core first at 02 — core was not in the replay inputs)*
- Q5 → Architect: Does core support editing and rescheduling a scheduled post? Classic calls `/admin/v1/posts/schedule` for create, list and delete only — changes: C4 scope (core work or cut). *(check core first, as Q4)*
- Q6 → PM: Does the frame ask for any events on this feature? — changes: field 6; instrumentation is built in Detailing or never

### Can wait for Detailing
- Q7 → Architect: The 100-pending-scheduled-post limit is counted per network, per destination or per admin? — changes: RC8 expected + TF2 data plan
- Q8 → PM: When rescheduling, must the new time be ≥1 h from now (like create) or only ≥15 min? — changes: RC9/RC7 boundary cases
- Q9 → Architect: What reasons make a scheduled post Failed (Figma "[Fail reason message]")? — changes: RC11 expected copy + TF3
- Q10 → PM: What can an admin do with a Failed scheduled post — edit and retry, cancel, or nothing? — changes: Failed-card actions + permissions

## 6 QA decided (did not ask)
- "Up to 10 media at a time" = 10 per post — classic `PostAuthoring.tsx:101` answers it (criterion 2)
- A post needs body text or at least one attachment — classic `CreatePost.tsx:369`; case written both ways (criterion 2)
- 15-min cutoff and 1-h minimum are inclusive ("at least"), server clock — boundary cases at exactly 15:00 / 60:00 and one minute inside; confirm when §3 is drafted (copy answers it; criterion 2)
- Scheduled-limit and revoked-mid-session looks follow Figma (submit toast; access toast), not the S-CAT standing look — Figma draws them (criterion 2)
- Requires approval menu = Clear flags + Copy post ID (no Edit, unlike classic) — Figma 857:23308 decides the drawn menu (criterion 2)
- Create / schedule / delete / approve / decline are gated as in classic (page permission only in the UI; core decides) — permissions matrix is filled by the room at 04; QA reviews it there (criterion 2 — classic + core answer it)
- Blocklist applies to both title and body for both words and links unless core says otherwise — Figma shows one example each; core answers it (criterion 2)
- Audio / files mixed with photos / videos in one post — core answers it; check at 04 (criterion 2)
- Change-history cap: case with 11 edits checks that the oldest console edit drops and the original stays (no question)
- Appetite (field 8) not asked — does not change a rule, state, permission or expected (criterion 1); QA reserves time by surface count: 7 surfaces, 23 RCs → large
- Analytics tab, comments, reactions and their sheets are other features (own Figma pages) — tested here only as "opens"
