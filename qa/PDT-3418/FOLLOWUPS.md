# FOLLOWUPS — PDT-3418 (Video & live streaming)

> Deferred / side-effect actions surfaced by `qa-clarifications-review` on **2026-07-08**.
> These are **low-severity or non-blocking** — they do **not** gate Layer 2. (CONF-08 and AMB-11, the last open items, were **resolved 2026-07-08** — see `clarifications.json`.)
> **Dispositions recorded 2026-07-09** (team sign-off): FU-1 ignored · FU-2 resolved (64×64) · FU-3 open (blocks 1 TC) · FU-4 bug → release · FU-5 repo-authoritative (ledger DEC-11).
> Source of each item = the clarification `id` in `qa/PDT-3418/clarifications.json`.

---

## 📌 Standing note — platform behaviour differs (carry into EVERY test case)

Tap-interaction behaviour is **not uniform across platforms** → full detail in **[`platform-behavior-notes.md`](platform-behavior-notes.md)**.
The big one — **first tap on a playing player:**
- **Mobile** (iOS app, Android app, **web-on-mobile**): tap = **reveal controls, playback continues** (UC1 AC-01).
- **Desktop** (Web UIKit): **1-Step Pause** — tap = **pause directly**; tap-to-reveal not applied.

➡️ When writing test cases for tap/pause ACs (UC1 AC-01 / AC-04, UC2 pause entry), author a **separate expected per platform**.
This is a **standing fact**, not a closeable action (do not tick it off). Also encoded on UC1 AC-01 `platform_variance` in the story JSON.

---

| FU | From | Owner | Action | Status (2026-07-09) |
|----|------|-------|--------|---------------------|
| FU-1 | CONF-06 | PM / BA | Remove the stale "(assume 3s)" PRD comment — auto-dismiss is **1s**. | **Ignored** — team: not worth the edit (1s already authoritative in the AC/JSON) |
| FU-2 | AMB-06 | Design → answered | Central pause/play button hit-target size. | ✅ **Resolved** — **64×64px** (Figma); dev's call on impl (may use native) |
| FU-3 | GAP-08 | Engineering (Web) | What the **±10s skip button does on video / recorded while buffering on web** (a **Live** stream has no ±10s skip). Mobile = seek-and-rebuffer clear; web answer only described a "Reconnecting" UI + manual **scrub/scroll** — a *different gesture*. | ⏳ **Open** — follow-up · blocks 1 TC (UC3-07b) |
| FU-4 | AMB-05 | Engineering (Android) / QA | Android **OS-native media control** (lock screen / notification) can FF/rewind a **Live** stream — NOT acceptable. Separate defect, not an AC gap. | 🐞 **Bug** — verify in the release (cross-platform parity) |
| FU-5 | CONF-08, AMB-11 | ~~PM~~ → QA (repo) | Align Jira AC text to the 2026-07-08 decisions. **PM declined this round.** | **Repo authoritative** — corrections held in-repo; don't re-sync-clobber (ledger **DEC-11**) |

---

## FU-1 — PRD says "assume 3s", AC says 1s
- **Source:** CONF-06 (low, resolved)
- **What's settled:** Auto-dismiss timeout = **1 second**, final (Jira AC-03 + PM).
- **Action:** Edit the PRD (`products/PDT-3418/prd/Video & live streaming.html`) to drop the leftover "(confirm… assume 3s)" note so no reader expects 3s.
- **Disposition (2026-07-09):** **Ignored** — team decided the PRD edit isn't worth it; the 1s value is authoritative in the AC / story JSON regardless of the stale PRD note.

## FU-2 — Central button hit-target size
- **Source:** AMB-06 (low, followup)
- **What's missing:** A concrete tap-target dimension. PM answer was "I think it same size, refer from figma".
- **Action:** Design to state the hit-target size (or point to the exact Figma layer with measured bounds). Needed to write a reliable pause-vs-dismiss boundary test for UC1 AC-02.
- **Resolved (2026-07-09):** hit-target = **64×64px** (Figma: width 64 / height 64). Final implementation is the **developer's decision** — may use the platform-native control. The pause-vs-dismiss boundary test (UC1a / UC1b AC-02) targets the rendered **64×64** area; assert against the *actual rendered* target since the impl may be native.

## FU-3 — ±10s skip while buffering (video / recorded, web)
- **Source:** GAP-08 (low, followup) · **Scope:** video / recorded LS only — a **Live** stream has no ±10s skip (UC3 AC-06)
- **What's settled:** Mobile = **seek-and-rebuffer** at the target position (Prisa 68329).
- **What's open:** the web answer (Chayanit 68304) described a "Reconnecting" UI + manual **scrub/scroll** (dragging to a position — a *different gesture* from tapping the **±10s skip** button). What the **±10s skip** button itself does mid-buffer on web is not stated.
- **Action:** Web dev to confirm the **±10s skip** behaviour during buffering so UC3 AC-01/02 have a deterministic web expectation.

## FU-4 — Android native-control seek on live is a bug
- **Source:** AMB-05 (medium, resolved — scope answered; bug is the side-effect)
- **Still valid — confirmed 2026-07-08.** This is about the **OS native media control** (lock screen / notification — a system-level surface outside our app), not the in-app **±10s skip** button (FU-3's scope) and not manual **scrub/scroll**. All three are distinct — see the glossary in `platform-behavior-notes.md`.
- **What's settled:** UC3 AC-06 covers **only** the in-app **±10s skip** buttons. Android's OS-native media control allowing FF/rewind on a **Live** stream (Fidriyanto 68234; platform table 68264: Android ✅, iOS/web ❌) is **NOT acceptable**.
- **Action:** File a defect against Android for native-control seek on Live streams (ref platform table, comment 68264). Track separately from PDT-3564 AC coverage — not yet filed as of this writing.
- **Verification once fixed — cross-platform parity check:** confirm ALL platforms converge to the SAME `state = Live` behaviour, not just that Android is patched. Current known state per the platform table (68264): iOS ❌ / Android ✅-bug / web-desktop ❌ / web-mobile ❌ for native-control seek on Live. Target: **all ❌**. Re-verify iOS and web still block it too (don't assume they're untouched by a future player/SDK upgrade) — this is a general principle for any `state = Live` behaviour, not just this bug: whenever a platform table shows one platform diverging, re-test all platforms together when the fix ships, not just the one that was broken.
- **Disposition (2026-07-09):** confirmed a real bug — fold the fix **and** the cross-platform parity re-check into **release testing** for this release (QA verifies during release; tracked as a defect, not a PDT-3564 AC gap).

## FU-5 — Jira AC text vs repo (PM declined)
- **Source:** CONF-08, AMB-11 · **Owner:** was PM
- **Disposition (2026-07-09):** **PM declined** to update the Jira wording this round. QA holds the corrections **in this repo** as the authoritative source (ledger **DEC-11**). The Jira↔repo divergence is intentional — a future Jira sync (`qa-story-diff`) must treat UC1a/UC1b AC-04 (seek on video/recorded only) and UC3 AC-03 (skip-back preserves prior state) as **intentionally divergent, not stale**, and must not clobber them.
