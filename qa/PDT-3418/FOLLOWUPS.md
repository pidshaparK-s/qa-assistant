# FOLLOWUPS — PDT-3418 (Video & live streaming)

> Deferred / side-effect actions surfaced by `qa-clarifications-review` on **2026-07-08**.
> These are **low-severity or non-blocking** — they do **not** gate Layer 2. (CONF-08 and AMB-11, the last open items, were **resolved 2026-07-08** — see `clarifications.json`.)
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

| FU | From | Owner | Action | Blocking? |
|----|------|-------|--------|-----------|
| FU-1 | CONF-06 | PM / BA | Remove the stale "(confirm… assume 3s)" comment from the PRD — auto-dismiss is confirmed **1 second**. Doc hygiene only. | No (low) |
| FU-2 | AMB-06 | Design | Provide the **concrete hit-target size** of the central pause/play button (dp/px), so the pause-vs-dismiss edge (AC-02) is testable. "Same size, refer from figma" is not a spec. | No (low) |
| FU-3 | GAP-08 | Engineering (Web) | Confirm what the **±10s skip button does on a video / recorded LS while it is buffering on web** (a **Live** stream has no ±10s skip). Mobile = seek-and-rebuffer is clear; the web answer only described a "Reconnecting" UI + manual **scrub/scroll** — a *different gesture* from tapping the ±10s skip. | No (low) |
| FU-4 | AMB-05 | Engineering (Android) / QA | **File a bug**: on Android, the **OS native media control** (lock screen / notification — outside our app UI) can fast-forward/rewind a **Live** stream — declared NOT acceptable. AC-06 only governs the in-app **±10s skip** buttons, so this is a separate defect, not an AC gap. | No (bug, separate) |
| FU-5 | CONF-08, AMB-11 | **PM** | **Update the Jira AC text** to match the decisions of 2026-07-08, or the next sync re-introduces the conflicts: **(a)** UC1 AC-04 + UC2 AC-01 — seek controls are video/recorded **only**; remove "back and forward seeking" from the **LIVE** pause overlay. **(b)** UC3 AC-03 — skip-back to 0:00 **preserves prior state** (playing→continue from 0:00, paused→stay paused), NOT "the video is in a paused state". Our story JSONs already reflect these; Jira does not yet. | ⚠️ sync-integrity |

---

## FU-1 — PRD says "assume 3s", AC says 1s
- **Source:** CONF-06 (low, resolved)
- **What's settled:** Auto-dismiss timeout = **1 second**, final (Jira AC-03 + PM).
- **Action:** Edit the PRD (`products/PDT-3418/prd/Video & live streaming.html`) to drop the leftover "(confirm… assume 3s)" note so no reader expects 3s.

## FU-2 — Central button hit-target size
- **Source:** AMB-06 (low, followup)
- **What's missing:** A concrete tap-target dimension. PM answer was "I think it same size, refer from figma".
- **Action:** Design to state the hit-target size (or point to the exact Figma layer with measured bounds). Needed to write a reliable pause-vs-dismiss boundary test for UC1 AC-02.

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
