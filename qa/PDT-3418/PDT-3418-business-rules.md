# Layer 2 · STEP 3 — Business Rule Extraction (phase-2-3)

_Skill: `phase-2-3-business-rule-extraction` · Engine: "Why" from `phase-1-1` · Input: 41 ACs across UC1a/UC1b/UC2/UC3 (STEP 2) + code-verified behavior_
_Method: for each AC ask "why must it be this way, and is that true across contexts?" → cross-context answer = BR. Classify (permission/constraint/computation/state), assign br_id, consolidate across units._

> **Scope tag:** `epic` = true across all of PDT-3418 · `media-type` = differs video/recorded vs Live · `platform` = differs by platform/form-factor.
> **Δ code-delta** = the current implementation differs from this rule (dev work to close — from the code-verified notes, not a spec ambiguity).

---

## Section 1 — Business Rules, by type

### Permission / Scope

| BR | Statement | Type | Scope | From AC |
|---|---|---|---|---|
| **BR-01** | Seek / skip (±10s) controls exist **only** on a video or recorded live stream — **never** on an active Live stream. | Permission/Scope | media-type | UC1a AC-04, UC1b AC-07, UC3 AC-01/02/06 |
| **BR-02** | Pause / resume of an **active Live** stream is **not available on mobile web** (offered on iOS, Android, web-desktop only). | Permission/Scope | platform | UC2 AC-05 (default) |

### Constraint / Limit

| BR | Statement | Type | Scope | From AC |
|---|---|---|---|---|
| **BR-03** | The controls overlay auto-dismisses after **1 second** of no interaction **while playing**; the countdown **restarts on every control interaction** (volume, scrubber). | Constraint | epic **Δ** | UC1a/UC1b AC-03 |
| **BR-04** | Each skip action moves playback by **exactly 10 seconds**. | Constraint | media-type | UC3 AC-01/02/07 |
| **BR-05** | Skip **clamps at content boundaries** — playback never goes below **0:00** or past the **final frame**, and never loops, even mid-burst during rapid taps. | Constraint | media-type | UC3 AC-03/04/08 |
| **BR-06** | The controls behaviour is **identical across all in-scope surfaces** (global/user/community/event-discussion feeds, media gallery, fullscreen) — surface-invariant. _(Surface-invariant ≠ platform-invariant — see BR-09.)_ | Constraint | epic | UC1a/UC1b AC-06 |

### Computation / Display

| BR | Statement | Type | Scope | From AC |
|---|---|---|---|---|
| **BR-07** | The **pause indicator IS the central play (▶) button overlay** itself — not a separate badge or banner. | Computation/Display | media-type (Live) | UC2 AC-01 |
| **BR-08** | Rapid skip taps **accumulate** (each tap adds ±10s to the seek target), but the skip **icon always shows the per-tap value (+10 / −10)**, never the accumulated total. | Computation/Display | media-type **Δ** | UC3 AC-07 |
| **BR-09** | The **first-tap interaction model is platform-dependent**: on **mobile** (iOS/Android/web-mobile) the first tap **reveals controls without toggling playback**; on **desktop** (Web UIKit) the first tap is a direct **1-step pause/play**. | Computation/Display | platform | UC1a/UC1b AC-01 (PV-1) |

### State / Lifecycle

| BR | Statement | Type | Scope | From AC |
|---|---|---|---|---|
| **BR-10** | Play/pause state changes **only** through an explicit user pause/play action (BR-09), or a terminal room state (BR-12). **No implicit operation** — revealing controls, skipping, overlay auto-dismiss, or a network stall — ever toggles play/pause. | State | epic | UC1 AC-01/02, UC3 AC-03/05/08, UC2 AC-08 |
| **BR-11** | Overlay persistence follows playback state: **while playing** it auto-dismisses (BR-03); **while paused** it **persists** and dismisses only on a tap **outside** the play button — and the media **stays paused** after that dismiss. | State | epic | UC1a/UC1b AC-04, UC2 AC-01 |
| **BR-12** | A **terminal room state (ended/recorded) always takes priority** over the viewer's local paused state — the player moves to ended/recorded regardless of pause and regardless of recording-processing readiness (shows "Livestream ended"; there is **no intermediate 'processing' state**). | State | media-type (Live) | UC2 AC-03 |
| **BR-13** | **Resume target depends on media type**: a **video/recorded** stream resumes from the **exact paused position**; an **active Live** stream resumes at the **current live edge** (landing within normal buffering tolerance — a few seconds behind live is **expected**, not a defect). | State | media-type | UC1a AC-05, UC2 AC-02 |
| **BR-14** | The **live chat is independent of video playback state** — it keeps receiving/displaying messages in real time while the video is paused, and messages are **never replayed or skipped** on resume. | State | media-type (Live) | UC2 AC-01/02 |
| **BR-15** | The viewer is **never left on a frozen frame with no feedback** — any interruption surfaces an explicit state (a "Reconnecting" indicator on network loss with **automatic** retry, or the ended state on stream end). | State | epic | UC2 AC-03/AC-08 (code-verified) |

**Total: 15 BRs** — Permission 2 · Constraint 4 · Computation 3 · State 6.

---

## Section 2 — Cross-unit consolidation (the point of this step)

BRs that appear in **more than one** unit — extracted once, referenced everywhere, so dev implements + QA tests them a single time:

| BR | UC1a | UC1b | UC2 | UC3 | Consolidation note |
|---|:--:|:--:|:--:|:--:|---|
| **BR-01** seek video-only | ✅ | ✅ | ✅ | ✅ | The single most cross-cutting rule — it's why UC1's AC-04 split into UC1a (seek visible) / UC1b (no seek), why UC2's Live overlay has no seek, and why UC3 excludes Live. **One rule, four touch-points.** Was the root of CONF-08. |
| **BR-09** platform interaction model | ✅ | ✅ | ✅ | ✅ | Mobile reveal vs desktop 1-step — governs the first tap everywhere, and how the paused state is *entered* in every unit (= PV-1). |
| **BR-10** state changes only via explicit action | ✅ | ✅ | ✅ | ✅ | Unifies "tap doesn't pause" (UC1), "skip doesn't change state" (UC3), "network stall doesn't change state" (UC2). |
| **BR-11** overlay playing-dismiss / paused-persist | ✅ | ✅ | ✅ | — | Same overlay lifecycle in UC1 and UC2's pause overlay. |
| **BR-03** 1s auto-dismiss + reset | ✅ | ✅ | (◑) | — | UC1's timer; UC2's pause overlay inherits the persist-half via BR-11. |
| **BR-06** surface-invariance | ✅ | ✅ | — | — | |
| **BR-13** resume target by media type | ✅ | — | ✅ | — | The paired rule: UC1a owns the video-exact half, UC2 owns the live-edge half — **do not** let UC1b author a conflicting live-resume (UC1b defers to UC2). |

BRs local to a single unit: **BR-02** (UC2), **BR-04/BR-05/BR-08** (UC3), **BR-07/BR-12/BR-14/BR-15** (UC2).

**No duplicate/conflicting BRs found** — the earlier CONF-08 (seek-on-live) contradiction is now expressed as the single BR-01 rather than two clashing AC clauses, which is exactly what consolidation is meant to prevent.

---

## Section 3 — AC → BR traceability matrix (feeds Schema 1's `ac.br_ids[]`)

Rather than re-paste 41 ACs, this matrix IS the linkage — each row becomes an AC's `br_ids[]` in STEP 6.

| Unit · AC | br_ids |
|---|---|
| **UC1a** AC-01 (tap reveals) | BR-09, BR-10 |
| UC1a AC-02 (tap outside dismiss) | BR-10, BR-11 |
| UC1a AC-03 (auto-dismiss 1s + reset) | BR-03, BR-11 |
| UC1a AC-04 (pause: icon+seek persist) | BR-01, BR-11 |
| UC1a AC-05 (resume exact position) | BR-13 |
| UC1a AC-06 (cross-surface) | BR-06 |
| UC1a AC-07 (default baseline) | — (UI default, no BR) |
| UC1a AC-08 (timer resets on interaction) | BR-03 |
| UC1a AC-09 (pause vs timer race) | BR-10, BR-11 |
| UC1a AC-10 (tap during buffering) | BR-15 |
| UC1a AC-11 (app backgrounded) | BR-10 |
| **UC1b** AC-01/02/03 (tap reveal/dismiss/auto-dismiss, Live) | BR-09, BR-10, BR-03, BR-11 |
| UC1b AC-04 (cross-surface) → *AC-09 in doc* | BR-06 |
| UC1b AC-07 (pause: **no** seek, Live) | BR-01, BR-11 |
| UC1b AC-05/06/08/10/11 (default/reset/race/buffer/bg) | BR-03, BR-10, BR-11, BR-15 |
| **UC2** AC-01 (pause indicator + chat + dismiss) | BR-07, BR-11, BR-14, BR-01 (no-seek) |
| UC2 AC-02 (resume → live edge) | BR-13, BR-14 |
| UC2 AC-03 (ended wins) | BR-12, BR-15 |
| UC2 AC-04 (default at live edge) | — (UI default) |
| UC2 AC-05 (mobile-web no pause) | BR-02 |
| UC2 AC-06 (long-pause resume tolerance) | BR-13 |
| UC2 AC-07 (chat/video re-sync) | BR-14 |
| UC2 AC-08 (network drop while paused) | BR-10, BR-15 |
| **UC3** AC-01/02 (skip ±10s) | BR-04, BR-10 |
| UC3 AC-03 (boundary 0:00, preserve state) | BR-05, BR-10 |
| UC3 AC-04 (boundary final frame, end) | BR-05, BR-12 |
| UC3 AC-05 (skip while paused) | BR-10 |
| UC3 AC-06 (live: no skip) | BR-01 |
| UC3 AC-07 (rapid accumulate) | BR-04, BR-08 |
| UC3 AC-08 (rapid near boundary) | BR-05 |
| UC3 AC-09/10/11 (default/buffer mobile/web) | BR-15 |

---

## ⚠️ Deltas — where current code ≠ BR (dev work, carried from STEP 2 code read)

| BR | Rule | Current code | Action |
|---|---|---|---|
| **BR-03** | auto-dismiss = 1s (all platforms) | **web = 3s** (`VideoPlayerControls.tsx:60-70`); iOS = 1s | web change 3s→1s |
| **BR-08** | rapid taps accumulate | **web currently debounces** to a single ±10s (Chayanit 68304) | web change debounce→accumulate |
| **BR-01 / BR-11** | tap-to-reveal + persist overlay on Live (web) | **web LIVE path has no reveal-controls overlay** (bare Plyr) | net-new dev for UC1b on web |

These are **not** BR ambiguities — the rules are decided. They're implementation gaps flagged for STEP 5 (effort) + dev handoff.

---

## STEP 3 exit — ready for STEP 4 (Scope gate, `phase-2-6`)

**Yes.** 15 BRs extracted, all classified, cross-unit consolidation mapped, every AC linked (2 UI-default ACs correctly carry no BR). No duplicate or conflicting rules. The `br_ids[]` per AC above is ready to drop into Schema 1 at STEP 6.

Checklist (skill's own): ✅ each BR is a statement not a scenario · ✅ subjects precise (media-type vs platform vs state kept distinct) · ✅ scope tagged on every BR · ✅ no two BRs state the same thing · ✅ shared logic points to one BR (BR-01/09/10 consolidated) · ✅ UI-only items (default states) correctly excluded from BRs.
