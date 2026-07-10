# Clarifications for PM & Design — PDT-3418: Video & Live Streaming (Tap-to-Reveal Controls)

_Compiled from phase 1.1–1.4 analysis of PDT-3562 (UC1) / PDT-3563 (UC2) / PDT-3564 (UC3)_
_Ground truth: Jira AC (**synced 2026-07-06 17:07** — UC2 rewritten) + PRD + Figma (11 screens) + platform table (Prisa, comment 68264)_
_Updated: 2026-07-06 · per-story analysis: `qa/PDT-3418/PDT-356{2,3,4}-*-analysis.md`_
_English version of `PDT-3418-clarifications-for-pm-design.md`_

---

## 🔄 Changelog — update 2026-07-06 (Jira 17:02–17:07)

PM (Ghita) **rewrote UC2's ACs** + added a Platforms section to every story → **cleared 7 clarifications** (mostly High):

| Was | Result |
|---|---|
| CONF-01 resume target | ✅ **RESOLVED** — resume goes to current live moment (Figma "resume-to-live-edge" was correct) |
| CONF-02 rolling buffer | ✅ **MOOT** — resume goes to live, not the paused position |
| CONF-03 LIVE badge | ✅ **RESOLVED** — out of scope (separate enhancement) |
| CONF-04 web-desktop tap | ✅ **RESOLVED** — no behavior change on desktop |
| CONF-05 desktop scope | ✅ **RESOLVED** — no behavior change, UI-only (button size) |
| AMB-01 return-to-live CTA | ✅ **MOOT** — resume goes to live anyway |
| AMB-02 chat sync | ✅ **RESOLVED** — chat runs in real time always (in AC + platform table) |
| GAP-01 behind-live indicator | ⤵️ **DOWNGRADED** → became a "pause indicator" (the ▶ button is likely it) = AMB-09 (low) |

**🆕 2 new items:** CONF-07 (resume-to-live is a behavior change), AMB-10 (user_story doesn't match the new ACs)

**Current status:** 22 original → **7 cleared** · **15 carried forward** (14 unchanged + GAP-01 downgraded) · **+2 new** = **17 items still open** (High: 5 · Medium: 6 · Low: 6)

---

## How to read this document

3 categories, ordered by priority. Every item is written as **observation → consequence → question**, tagged with: priority · ask→who · story/AC · source. ✅ resolved items are shown compactly with their resolution; open items are shown in full.

---

## A. Conflicts

### ✅ RESOLVED (2026-07-06)
- **CONF-01 · UC2 AC-02 · resume target** — ✅ AC-02 rewritten: resume goes to the **current live moment** (not the paused position). Figma `LS-mobile-05-resume-to-live-edge` is now correct.
- **CONF-02 · UC2 AC-02 · rolling buffer** — ✅ **moot** — resume goes to live, not the paused position, so the buffer-boundary problem disappears.
- **CONF-03 · UC2 AC-01 · LIVE badge while paused** — ✅ Ghita: updating the LIVE badge = separate enhancement, **out of scope** for this release.
- **CONF-04 · UC2 · web-desktop tap-to-resume** — ✅ Ghita: **no behavior changes on Desktop** (out of scope).
- **CONF-05 · UC1 AC-06 · desktop scope** — ✅ Jira: Desktop "no behaviour change; only a small UI design change (button size)".

### 🔴 CONF-07 · OI-UC2-07 · Resume-to-live is a behavior change from current (NEW)
- **Priority:** Medium–High · **Ask:** Engineering / PM · **Story:** UC2 (PDT-3563) AC-02 · **Source:** AC-02 (rewritten) ↔ platform table (Prisa, 68264)
- **Observation:** The new AC-02 requires resume to go to the current live moment. But Prisa's platform table confirms **current behavior on all platforms = resume-from-paused-position** (iOS ✅, Android ✅, web-desktop ✅).
- **Consequence:** AC-02 is therefore a **change to existing behavior**, not a spec of what exists — dev must implement it anew on every platform, and QA must test the new behavior (not the current one). If misread as "existing," nobody implements it.
- **Question:** Confirm resume-to-live-moment is the intended new behavior on all platforms (replacing today's resume-from-pause)? Any platform exceptions or migration concerns?

### 🟡 CONF-06 · UC1-Q1 · Auto-dismiss timeout: 1s (Jira) vs "assume 3s" (PRD)
- **Priority:** Low · **Ask:** Engineering / PM · **Story:** UC1 (PDT-3562) AC-03 · **Source:** Jira ↔ PRD
- **Observation:** Jira AC-03 = "1 second" (resolved), but the PRD still carries a leftover "*(assume 3s)*" comment.
- **Consequence:** Docs out of sync — anyone reading the PRD assumes 3s.
- **Question:** Confirm 1s is final and update the PRD to match?

---

## B. Unclear / Gaps

### 🔴 GAP-02 · UC1-Q2 · Does the controls overlay stay or disappear after tapping pause?
- **Priority:** High · **Ask:** Engineering · **Story:** UC1 AC-04 · **Source:** Jira AC (unspecified)
- **Observation:** AC-04 says pause + icon change but doesn't state whether the overlay stays or auto-dismisses.
- **Consequence:** If it disappears immediately → the user must tap again to reach play → an extra step; devs may differ.
- **Question:** When paused, does the overlay stay visible? Does the 1s timer keep running or stop?

### 🔴 GAP-03 · UC1-Q3 · Does the auto-dismiss timer reset when the user interacts?
- **Priority:** High · **Ask:** Engineering · **Story:** UC1 AC-03 · **Source:** Jira AC (unspecified)
- **Observation:** AC-03 auto-dismisses after "no action for 1s"; doesn't say whether interacting (e.g. volume) resets the timer.
- **Consequence:** If it doesn't reset → the overlay may vanish while the user is still using it.
- **Question:** Should the 1s timer reset when the user interacts with the overlay?

### 🔴 GAP-04 · UC1-Q6 · 'Live' live stream uses a different component — separate coverage?
- **Priority:** High · **Ask:** Engineering / Design · **Story:** UC1 AC-01/AC-06 · **Source:** Jira comment (Chayanit, 2026-07-03)
- **Observation:** On web, video + recorded LS use the same component but **'Live' LS uses a different one**. _(The new UC3 precondition confirms recorded LS is in the video family.)_
- **Consequence:** Tap-to-reveal verified on video/recorded LS doesn't automatically cover Live LS → the core fix may not take effect on Live.
- **Question:** Confirm tap-to-reveal must work identically across video / recorded LS / 'Live' LS? If so, Live must be implemented + tested separately.

### 🔴 GAP-05 · UC2 · Pause collides with stream end — which state wins?
- **Priority:** High · **Ask:** PM / Engineering · **Story:** UC2 AC-01/AC-03 · **Source:** phase 1.4 Timing
- **Observation:** No AC covers tapping pause at the exact instant the host ends the stream (race).
- **Consequence:** The player may land in an inconsistent state (paused mixed with ended).
- **Question:** If pause and stream-end happen simultaneously, which wins — ended/recorded or paused?

### 🟠 GAP-06 · UC2 · Recording not ready when the stream ends while paused
- **Priority:** Medium · **Ask:** Engineering · **Story:** UC2 AC-03 · **Source:** phase 1.4 Data-integrity
- **Observation:** AC-03 = ended/recorded state but doesn't cover the recording still processing.
- **Consequence:** The viewer may see a frozen frame/error while waiting.
- **Question:** If the stream ends while paused but the recording isn't ready, show a "processing" state?

### 🟠 GAP-07 · UC3-Q2 · Rapid repeated skip — accumulate or debounce?
- **Priority:** Medium · **Ask:** Engineering · **Story:** UC3 AC-01/AC-02 · **Source:** phase 1.4 Timing
- **Observation:** No behavior specified for rapid skip taps.
- **Consequence:** The final position is unpredictable (−30s or −10s?).
- **Question:** Rapid skip → accumulate or debounce to a single −10s?

### 🟡 GAP-08 · UC3-Q3 · Skip while buffering
- **Priority:** Low · **Ask:** Engineering · **Story:** UC3 AC-01/AC-02 · **Source:** phase 1.4 Environment
- **Observation:** No behavior specified for skip while buffering.
- **Consequence:** May stick on loading / land at the wrong position.
- **Question:** Skip while buffering → queue or seek-and-rebuffer?

---

## C. Ambiguous

### ✅ RESOLVED (2026-07-06)
- **AMB-01 · UC2 · return-to-live CTA** — ✅ **moot** — resume goes to live anyway; there is no lingering "behind live" state to return from.
- **AMB-02 · UC2 · chat sync during pause** — ✅ AC-01/02 state chat runs in real time + platform table confirms all platforms.

### 🟠 AMB-03 · UC1-Q4 · Has the double-tap gesture been descoped?
- **Priority:** Medium · **Ask:** PM / Design · **Story:** UC1 · **Source:** PRD (A1)
- **Observation:** PRD = pause bound to "central button **or double-tap** — Design to recommend", but the AC uses only the central button.
- **Consequence:** If double-tap must still be supported → many more tests + must disambiguate from single-tap.
- **Question:** Has double-tap been descoped (central button only)?

### 🟠 AMB-04 · UC3-Q1 · Is the nice-to-have (UC3) in this release, or descoped?
- **Priority:** Medium · **Ask:** PM · **Story:** UC3 · **Source:** PRD + PDT-3564 note
- **Observation:** UC3 = "Nice to have… can be descoped if it impacts delivery timeline".
- **Consequence:** Affects sprint planning + QA effort.
- **Question:** Is UC3 in this release or descoped?

### 🟡 AMB-05 · UC3-Q4 · Native OS scrub on live vs AC-06 (in-app)
- **Priority:** Low–Medium · **Ask:** PM · **Story:** UC3 AC-06 · **Source:** Jira comment (Fidriyanto/Android) + platform table
- **Observation:** AC-06 = in-app skip not shown on live. But Android can scrub live via the **OS native media control** (iOS/web ❌ per Prisa's table).
- **Consequence:** No direct conflict (native ≠ in-app), but without a scope statement, someone may think seeking on live is fully blocked.
- **Question:** Confirm AC-06 covers only in-app buttons? Is native scrub on live (Android) acceptable?

### 🟡 AMB-06 · UC1-Q7 · Hit-target size of the central pause button
- **Priority:** Low · **Ask:** Design · **Story:** UC1 AC-02 · **Source:** phase 1.4 Boundary
- **Observation:** AC-02 separates "tap outside the button" (dismiss) from tapping it — but doesn't define the hit-target.
- **Consequence:** A tap near the edge resolves as button/surface non-deterministically → pause vs dismiss is ambiguous.
- **Question:** What is the central button's hit-target size?

### 🟡 AMB-07 · UC2-Q8 · Figma `LS-mobile-02/03/05` look identical
- **Priority:** Low · **Ask:** Design · **Story:** UC2 / UC1 · **Source:** Figma
- **Observation:** The 3 screens look identical in the PNG export.
- **Consequence:** Annotations/interactions may have been lost in export → QA misreads the flow.
- **Question:** How do the 3 screens differ in state? Share the Figma link / annotated frames.

### 🟡 AMB-08 · UC3-Q5 · Boundary "less than 10s" vs "exactly 10s"
- **Priority:** Low · **Ask:** Engineering · **Story:** UC3 AC-03/AC-04 · **Source:** phase 1.4 Boundary
- **Observation:** ACs cover "less than 10s" / "within 10s" — not the exact-10s value.
- **Consequence:** Off-by-one at the boundary.
- **Question:** Position = exactly 10s → clamp (0:00/final) or skip normally?

### 🟡 AMB-09 · OI-UC2-08 · Pause indicator visual = the ▶ button overlay? (NEW, ← GAP-01 downgraded)
- **Priority:** Low · **Ask:** Design · **Story:** UC2 AC-01 · **Source:** AC-01 (rewritten) ↔ Figma `LS-mobile-04`
- **Observation:** The new AC-01 = "a visual indicator communicating the stream is paused" (dropped "behind live edge"). Figma `LS-mobile-04` shows a central ▶ button.
- **Consequence:** Unclear whether the pause indicator is the ▶ button overlay or a distinct element (but much lower risk than before, since ▶ already conveys "paused").
- **Question:** Confirm the pause indicator = the central play-button overlay (LS-mobile-04), or is a distinct element needed?

### 🟡 AMB-10 · OI-UC2-09 · `user_story` still says "behind the live edge" — doesn't match the new ACs (NEW)
- **Priority:** Low · **Ask:** PM · **Story:** UC2 · **Source:** Jira user_story ↔ AC (rewritten)
- **Observation:** The new ACs dropped the "behind live edge" concept (just pause + resume-to-live), but the Jira `user_story` still reads "know when I'm paused **and behind the live edge**".
- **Consequence:** Docs inconsistent — anyone reading the user_story will misread the intent vs the ACs.
- **Question:** Update UC2's `user_story` to match the new ACs (pause + resume-to-live, drop "behind live edge")?

---

## D. Recommendations & additions

1. **UC1 core (AC-01/02/03) can be greenlit now** — main bug (XM/Ulta), timeout resolved (1s), desktop resolved. No need to wait for UC2.
2. **UC2 is much more ready** — no longer needs a design pass for a behind-live indicator (concept dropped). Focus on **CONF-07** — confirm with Eng that resume-to-live is a behavior change to be implemented anew on every platform.
3. **Add the missing ACs:** VOD/recorded-LS "end while paused" (UC2 AC-03 covers live-end); controls-after-pause (GAP-02) and timer-reset (GAP-03) should become ACs once decided; a cross-platform behavior matrix (Prisa's table is a good start).
4. **PM should update UC2's `user_story`** (AMB-10) + record every answer in the Decision Log (still empty).
5. **Fill the PRD/Figma links on the Jira epic** (blank) + request the real Figma link (AMB-07).
6. **Test-platform matrix** — base it on Prisa's table (68264); must cover iOS/Android/web-mobile/web-desktop since current behavior differs (especially resume, which is about to change).

---

## E. Readiness verdict — why it is (still) not fully ready for developers

### Per-story summary (after the 2026-07-06 update)

| Story | Was | Now | Reason | Blocking |
|---|---|---|---|---|
| **UC1 (PDT-3562)** | 🟡 Partial | 🟡 **Partial** | core ready, desktop resolved | GAP-02, GAP-03, GAP-04 |
| **UC2 (PDT-3563)** | 🔴 Not ready | 🟡 **much improved** | resume/chat/badge/desktop resolved | CONF-07, GAP-05, (AMB-09) |
| **UC3 (PDT-3564)** | 🟢 Cond. ready | 🟢 **Cond. ready** | design complete, recorded LS clarified | AMB-04 (descope), GAP-07 |

### Remaining systemic reasons (down from 5 → 3)

1. **Behavior change not yet confirmed** — resume-to-live (CONF-07) changes behavior on every platform; dev/QA must be aware before starting.
2. **Engineering details undefined** — overlay-after-pause (GAP-02), timer-reset (GAP-03), pause-races-end (GAP-05), Live component coverage (GAP-04).
3. **Scope decisions pending** — UC3 descope (AMB-04), double-tap (AMB-03).

_(Gone from before: missing design ✅, resume conflict ✅, cross-platform not unified ✅ — all cleared by this update.)_

### What can start right now

- ✅ **UC1 core (AC-01/02/03)** — ready to implement.
- ✅ **UC2** — design/planning can start (concept is now clear); once CONF-07 is confirmed → start dev.
- 🎯 **Sequence:** UC1 core → rest of UC1 (answer GAP-02/03) → UC2 (confirm CONF-07) → UC3 (if not descoped).

---

_Sources: per-story `qa/PDT-3418/PDT-3562-uc1-analysis.md`, `PDT-3563-uc2-analysis.md`, `PDT-3564-uc3-analysis.md` · stored stories `products/PDT-3418/stories/*.json` (synced 2026-07-06) · prior by-mechanism `output/backup/PDT-3418-*.md`_
