# Layer 2 · STEP 4 — Scope Boundary & Gap Analysis (phase-2-6)

_Skill: `phase-2-6-scope-and-gap-analysis` · Reuses: Relationship Map + User Need (L1 phase-1-1/1-2) · Input: 4 units, 41 ACs, 15 BRs, resolved clarifications, code-verified behavior_
_Purpose: the LAST gate before sprint — lock what's in/out/assumed/constrained/open so no scope creep mid-sprint._

> **Status: QA-prepared draft — NOT yet signed off.** Sign-off (PM + Dev lead + QA) is a team action; placeholders below. Nothing here invents a decision the team hasn't made — resolved items cite their clarification id; genuinely-open items are listed as Open Gaps with an owner.

---

## Technique 1 — User Need → AC coverage map (reuse L1 1-2)

Every User Need from Layer 1's three-layer analysis, traced to the AC(s) that cover it. A need with no AC = gap.

| User Need (from L1) | Unit | Covered by | Status |
|---|---|---|---|
| Tap the player without accidentally pausing; reach controls when wanted | UC1a/UC1b | AC-01, AC-02, AC-03 + defaults | ✅ |
| Pause deliberately, resume from where I meant to (video) | UC1a | AC-04, AC-05 | ✅ |
| Pause a live stream without losing the chat | UC2 | AC-01, AC-07 (chat) + BR-14 | ✅ |
| On resume, rejoin what's happening live now (not stale footage) | UC2 | AC-02 + BR-13 | ✅ |
| Know the stream ended even if I was paused | UC2 | AC-03 + BR-12 | ✅ |
| Skip ±10s to rewatch/jump without scrubbing | UC3 | AC-01, AC-02 | ✅ |
| Skip repeatedly (rapid) and land predictably | UC3 | AC-07, AC-08 | ✅ |
| Not be left staring at a frozen frame on interruption | UC2 | AC-08 + BR-15 (code-verified) | ✅ |

**No orphan User Need** — every need maps to ≥1 AC. No coverage gap.

---

## Technique 2 — Error-state check (every happy path has a failure answer?)

| Happy path | "What if it fails / interrupts?" | Answer |
|---|---|---|
| Tap to reveal / pause | media buffering/stalled on tap | ✅ AC-10 (UC1) — icon reflects real state |
| Resume live | network drops while paused | ✅ AC-08 (UC2) — "Reconnecting", stays paused, resume→live (code-verified) |
| Pause live | host ends stream during pause | ✅ AC-03 (UC2) — ended wins (BR-12) |
| Skip ±10s | skip while buffering | ✅ AC-10 mobile (resolved) / ⚠️ AC-11 web (FU-3, low) |
| Any playing state | app backgrounded | ✅ AC-11 (UC1) — OS default (Option 1, code-grounded) |

**No happy-path AC without a failure answer.** One web sub-case (FU-3) is a low open gap, tracked below.

---

## Technique 3 — Silent-actor check (reuse L1 1-1 Relationship Map)

| Actor / object | Has AC coverage? | Decision |
|---|---|---|
| Community member (viewer) | ✅ primary actor, all ACs | in scope |
| Live chat (real-time sub) | ✅ BR-14, UC2 AC-01/02/07 | in scope |
| Room state machine (live→ended/recorded) | ✅ UC2 AC-03, BR-12 | in scope |
| System auto-dismiss timer | ✅ UC1 AC-03/08, BR-03 | in scope |
| **Host / broadcaster** | ❌ no AC | **out of scope** — viewer-POV feature; host unaffected by viewer pause (documented, not a gap) |
| **OS native media control** | ❌ no AC | **out of scope as a bug** — Android live-scrub = FU-4, filed separately |
| Concurrent viewers | ❌ no AC | **out of scope** — player state is per-viewer/independent (no shared state to spec) |

All silent actors explicitly classified — none left ambiguous.

---

## SCOPE BOUNDARY — PDT-3418 (Video & live streaming — tap/pause/skip)

**Sprint:** _[TBD]_ · **Agreed by:** _[PM — pending] · [Dev lead — pending] · [QA — Pidshapar]_ · **Date:** 2026-07-09 (draft)

### ✓ IN SCOPE
- **UC1a** — Tap-to-reveal on **video / recorded LS** (all platforms): tap reveals (mobile) / 1-step pause (desktop, BR-09); tap-outside dismiss; 1s auto-dismiss + reset-on-interaction; pause→play-icon+seek persist; resume from exact position.
- **UC1b** — Tap-to-reveal on **'Live'** (separate component): same reveal/dismiss/pause model, **no seek controls** (BR-01).
- **UC2** — Live **pause/resume** on **iOS / Android / web-desktop**: pause indicator = ▶ overlay (BR-07); chat stays live (BR-14); resume → current live edge within buffering tolerance (BR-13); ended/recorded wins over pause (BR-12).
- **UC3** — **10s skip** on video/recorded (nice-to-have, **confirmed in-release** per AMB-04): ±10s (BR-04); boundary clamp + preserve-state (BR-05); rapid accumulate, icon shows ±10 (BR-08); no skip on Live (BR-01).
- **Desktop** — UI-only change (button size); no behaviour change.
- **Known dev deltas (in-scope work, not yet built)** — web auto-dismiss 3s→1s (BR-03); web rapid-tap debounce→accumulate (BR-08); web-Live reveal-controls overlay = net-new. _(From STEP 2 code read — these are build tasks, not open decisions.)_

### ✗ OUT OF SCOPE (this release)
- LIVE badge change while paused — separate enhancement (OI-UC2-02).
- Return-to-live CTA — moot; resume already returns to live (OI-UC2-01).
- Double-tap-to-pause gesture — descoped, central button only (AMB-03).
- Accumulated-total skip icon (e.g. "+30") — future; icon stays ±10 (GAP-07).
- **Live pause/resume on mobile-web** — platform boundary, not supported (BR-02).
- Explicit foreground-reset on app-background (Option 2) — OS default adopted instead (AC-11 decision).
- Android OS-native-control seek on Live — this is a **bug to fix (FU-4)**, not a feature in this scope.

### ~ ASSUMPTIONS (owner must confirm)
| Assumption | Risk if wrong | Owner |
|---|---|---|
| Recorded LS resume = exact position, same as video (AC-05 says "a video"; recorded shares the video component) | AC-05 scope wrong for recorded LS; extra test path | Eng |
| "A few seconds behind live" buffering tolerance (BR-13) is acceptable to product as the resume target | If product wants tighter, it's a live-streaming physics limit — can't be met | PM (low — CONF-07 already accepted "expected") |

### ! CONSTRAINTS (cannot change)
- 'Live' LS uses a **separate player component** from video/recorded on every platform (GAP-04) → build + test twice, per platform.
- Live-stream **buffering** means resume-to-live lands a few seconds behind live (CONF-07) — exact-live is not achievable.
- **mobile-web cannot pause a Live stream** in the current architecture (BR-02).
- Backward seek during Live is limited to a rolling buffer window (Fidriyanto 68317) — largely moot given resume-to-live.
- Platforms: UIKit iOS / Android / React Native / Flutter / WebUIKit; desktop UI-only.

### ? OPEN GAPS (must have owner + due before sprint day 1)
| Gap | Owner | Due | Severity |
|---|---|---|---|
| **FU-2** — concrete hit-target size of the central pause/play button (needed for a deterministic pause-vs-dismiss boundary test, UC1 AC-02) | Design | before UC1 dev | Medium (test determinism) |
| **FU-3** — exact behaviour of the ±10s button mid-buffer on **web** (mobile resolved) | Web Eng | before UC3 dev | Low |

_Everything else that was open is now closed:_ the 17 original clarifications (resolved/ac-change/followup), CONF-08 + AMB-11 (decided), and the 2 STEP-2 pendings (resolved from source code). FU-1 (PRD cleanup) and FU-5 (Jira align) are doc-hygiene, not scope gaps.

---

## Schema 1 linkage (what this step feeds into STEP 6)

- **`open_questions[]`** ← the 2 Open Gaps above (FU-2, FU-3), each with owner.
- **`clarifications_needed[]`** per AC ← the 2 assumptions (recorded-LS-resume, buffering-tolerance) until confirmed.
- **`ac.source: "QA"`** ← the 20 QA-authored ACs from STEP 2 (things in scope that PM's original AC didn't state — default states, error cases).
- **No BLOCKED flows** for Schema 2 — no AC depends on an unclosed gap that would force a `status: BLOCKED` placeholder. (FU-2/FU-3 refine test precision, they don't block a flow's shape.)

---

## Pre-sprint checklist (skill's own)

- ✅ Every User Need has ≥1 covering AC (Technique 1)
- ✅ Every happy-path AC has a failure answer (Technique 2) — 1 low web gap (FU-3) tracked
- ✅ Every silent actor classified in/out (Technique 3)
- ✅ Every assumption has owner + risk
- ✅ Every open gap has an owner (due = "before sprint day 1"; dates TBD with team)
- ✅ Every out-of-scope item documented with reason
- ⬜ **PM + Dev lead + QA sign-off** — pending (team action)
- ✅ No Schema-2 flow sourced from an unclosed gap

---

## STEP 4 exit — ready for STEP 5 (Prioritization, `phase-2-5`)

**Yes.** Scope is fully partitioned; coverage/error/silent-actor checks pass; only 2 low/medium Open Gaps remain (FU-2, FU-3), both with owners and neither blocking authoring. The sole remaining pre-sprint item is human sign-off. STEP 5 can proceed to MoSCoW + QA-effort scoring on this locked scope.
