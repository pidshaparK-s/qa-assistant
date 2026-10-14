# post-content — replay scorecard (2026-10-04)

Compares the blind replay outputs (`day0.md`, `review-sketch-replay.md`, `review-detail-replay.md`)
with what was actually found after Solution Ready: test-factory `qa/admin-console/post-content/clarifications.json`
(24, all post-06) and `BUGS-TO-RAISE.md` #1–34 (found while automating). Scored by hand by the
orchestrating session, which wrote neither replay.

## Caveat — not fully blind
- Posts was solutioned **and delivered in one PR** (#272, `2213f6c7`). No pre-delivery draft of
  sketch/spec exists in git: the replay read status-06 text with five Delivery amendments. Findings
  that touch amended text are marked † and not scored as hits.
- Day 0 used Figma as of 2026-10-02 (no version history via `figma:explore`).
- So this replay tests **whether the lenses find the right things**, not timing. Timing needs Shadow.

## Clarifications (24) → did the replay raise it before build?

| CL | Topic | Replay | Verdict |
|---|---|---|---|
| 01 | Featured tab with no destination | QF28 (fan-out bound/order) | partial |
| 02 | Pending post actions | QF5 (no Pending row in R2) | **hit** |
| 03 | Scheduled card actions | QF5 (no Scheduled row) | **hit** |
| 04 | Post as locked on edit | — | miss |
| 05 | Create starts in filtered group | — | miss |
| 06 | Mention only group members | — | miss |
| 07 | Alt text 100 cap | QF4 (150/50,000/100 caps in no rule) | **hit** |
| 08 | Media reorder rule | — | miss |
| 09 | 12 rules no flow reaches | out of scope by design (solution:check) | n/a |
| 10 | Deleted tab actions | QF5 (Deleted row vs SL-06) | **hit** |
| 11 | No deep link → copy label | QF35 (clipboard content) | partial |
| 12 | Scheduled forward date filter | — | miss |
| 13 | Edit reason field | QF17 (reason on scheduled edit) | partial |
| 14 | Non-group destinations | QF24† / SQF4† | contaminated |
| 15 | Reschedule minimum time | QF10 · Day0 Q8 | **hit** (twice) |
| 16 | Scheduled footer total | QF29 · SQF3 | **hit** |
| 17 | Edit not marked edited in app | QF19 · Day0 TF10 | **hit** |
| 18 | "Deleted by" for AI moderation | Day0 TF6 (testability only) | partial |
| 19 | 10-item limit for audio/files | QF23 | **hit** |
| 20 | Scheduled limit unreachable on staging | Day0 TF2 · QF14 | **hit** |
| 21 | Post as tooltip text | — | miss |
| 22 | No results → Clear filters | — | miss |
| 23 | Manage on a comment | — | miss |
| 24 | R35 Scheduled exception | † | contaminated |

**10 hit · 5 partial · 7 miss · 2 contaminated · 1 n/a.** Misses are mostly "keep today's behaviour?"
(04, 05, 06, 12, 22) — the review has no lens that diffs Figma against console today.

## Bugs (34) → which were spec-level, and did the replay see them?
Most bugs are build defects no spec review can catch (copy, formatting, attachments, ⌘⇧X …).
The ones whose root is an undecided or wrong rule:

| Bug | Root | Replay | Verdict |
|---|---|---|---|
| #3 conflict shows "Access restricted" | conflict / no-permission / self-approve all 403 | QF15† | contaminated, but found |
| #5 VIEW-only can approve | §4 ✓ means "shown", not "succeeds" | QF32 | **hit** |
| #14 DONE schedule stays listed | core returns DONE to the list | QF11 | **hit** |
| #15 cancel a published schedule = success | core delete checks no status | QF13 · Day0 Q10 | **hit** |
| #6 delete an already-deleted post succeeds | same family | QF13 | partial |
| #29 / #30 1-hour messages, edit in last hour | R6/R15 clock & edge | QF9 · QF10 · QF26 | **hit** |
| #33 composer schedules escape the limit | core limit by postType | QF14 | partial |
| #12 Pending/Declined share empty copy | empty copy per tab | QF30 | partial |
| #17 mention needs MANAGE_COMMUNITY_USER | hidden permission dependency | — | miss |

## Cost
- Detail review: 41 to the room on a 486-line spec — too many for a live room. After the new
  noise cut (only blocks-05 or changes a P1–P2 case goes individually), estimate ~15–20.
- Day 0 from Figma alone: 6 before-03 questions; 3 of them (Q3 featured placement, Q4 declined
  listable, Q5 reschedule support) are exactly the core gaps the Solution later had to handle
  (SQF1/2, TF10 missing PUT alias).

## What to change next
1. Add a **"today" lens**: Figma says `Follow existing` or the rule is silent → diff against console
   today and write the behaviour as a rule candidate (would have caught CL-04/05/06/12/22).
2. Add a **permission-dependency lens**: an action that calls another module's API (mention → member
   search) needs that module's permission in §4 (bug #17).
3. Shadow the next real feature — timing can only be measured live.
