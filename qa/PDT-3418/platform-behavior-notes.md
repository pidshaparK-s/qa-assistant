# Platform / form-factor behaviour differences — PDT-3418

> **Read this before writing test cases.** For the ACs below the behaviour is **not uniform across
> platforms**, so a single cross-platform "expected" is WRONG. Write a **separate expected per platform**.
> These are standing facts (not clarifications to close). Recorded 2026-07-08.

Interpretation used here: **"Web UIKit" = web on desktop**; **"web on mobile" behaves like the mobile app**.
(If "Web UIKit" means something else in your setup, correct this note.)

---

## 📖 Glossary — canonical terms for PDT-3418 (extend as new ones appear)

Use these exact terms in ACs, analysis, and test cases. When PM/Design use a looser synonym, map it back here.

| Term (canonical) | Means | Synonyms / PM wording | Behaves like / scope |
|---|---|---|---|
| **Live LS** (LS on state `Live`) | A livestream whose Room status = `live` — actively broadcasting | "live stream", "livestream on Live", "Live" | Separate player component; **no ±10s skip** (UC3 AC-06); mobile-web cannot pause it |
| **Recorded LS** | A livestream **after it ended** → recording / VOD | "recorded livestream", "recorded LS" | Uses the **video** component → behaves like video (**has** ±10s skip) |
| **Video** | A video post (VOD) | — | Has ±10s skip |
| **±10s skip** | The **−10s / +10s** skip buttons (UC3) | PM's **"back and forward seeking"** / **"control indicators"** (UC1 AC-04, UC2 AC-01) | **Same two buttons.** Present on video / recorded; **absent on Live**. No separate seek control exists in this epic |
| **scrub / scroll** | Dragging the playback position manually along the timeline | web "scroll to renew position", "seek bar", "scrubber" | A **different gesture** from the discrete ±10s skip — do NOT conflate |
| **OS native media control** | The system-level transport control OUTSIDE our app UI (lock screen / notification shade / Bluetooth / car head-unit) | "media control" (Fidriyanto 68234), "native control" | **Not our in-app UI at all.** On Android it can FF/rewind a **Live** stream — declared a **bug** (AMB-05, FU-4), independent of AC-06 (which only governs in-app buttons) |
| **tap-to-reveal** | First tap reveals controls, playback continues | — | **Mobile** only — see PV-1 |
| **1-Step Pause** | First tap pauses directly | — | **Desktop** / Web UIKit — see PV-1 |

> ⚠️ **Root of CONF-08:** PM wrote "back and forward seeking" (UC1/UC2) for the **same** buttons UC3 calls "±10s skip". Canonical term = **"±10s skip"**; treat "back and forward seeking" as a synonym. On a **Live** stream these buttons do **not** appear.
>
> ⚠️ **Three distinct "seek-like" surfaces — do not conflate:** (1) **±10s skip** — our in-app button · (2) **scrub/scroll** — dragging the in-app progress bar · (3) **OS native media control** — the system's own transport UI, outside our app entirely. A Live stream has none of (1), but Android's (3) can still seek it today — that gap is FU-4's bug, not an AC-06 gap.

---

## PV-1 · First tap on a playing player — reveal-controls vs 1-Step Pause

The whole point of UC1 is "tap reveals controls instead of toggling pause" — but that change applies to
**mobile only**. On **desktop** the current 1-step tap-to-pause is kept.

| Form factor | Platforms | First tap on a **playing** player | How you pause |
|---|---|---|---|
| **Mobile** | UIKit iOS, UIKit Android, **web on mobile** | Reveals the controls overlay; **playback CONTINUES** (no pause on first tap) | 2 steps: reveal controls → tap the central pause button |
| **Desktop** | **Web UIKit (desktop)** | **1-Step Pause** — tap toggles pause/play **directly** | 1 step: tap = pause |

**Why:** consistent with `platforms.not_supported: "Desktop — no behaviour change; only a small UI design
change (button size)"` and the platform table (comment 68264: web-desktop can pause ✅, web-mobile ❌).

### ACs affected → split the expected
- **UC1 AC-01** (tap → controls appear, playback continues) — holds for **mobile**; on **desktop** the tap **pauses** instead. → see `PDT-3562…json` → AC-01 `platform_variance`.
- **UC1 AC-04** (pause via central button) — on mobile you must first reveal controls (2-step); on desktop the tap already paused (1-step). The **path into the paused state differs**.
- **UC2 pause entry** (pause a live stream) — same cascade: mobile = reveal-then-tap; desktop = direct tap. (Also: **mobile web cannot pause a Live stream at all** — platform table 68264.)

### Test-case guidance
- Author **per-platform expected** for every tap/pause interaction AC; never one shared "expected".
- Minimum matrix per tap AC: `{iOS, Android, web-mobile}` (reveal-controls path) **vs** `{web-desktop}` (1-step pause path).
- When Layer 3 / phase-3-2 turns these ACs into test conditions, carry this split through to each condition.

---

## Related variances already captured elsewhere (cross-ref)
- **'Live' LS uses a separate player component** from video/recorded LS on web/iOS/Android → test as 2 paths (ledger **GAP-04**, UC1 AC-01 `OI-UC1-02`).
- **Resume-to-live tolerance:** lands a few seconds behind live due to buffering — expected, don't assert exact-live (ledger **CONF-07**).
- **Rapid-tap on web** currently debounces; must change to **accumulate** to meet UC3 AC-07 (ledger **GAP-07**).
- **Android native-control seek on Live** = bug (ledger **AMB-05**, FOLLOWUPS **FU-4**).
