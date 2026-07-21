# Platform Behavior Registry

**Cross-epic** — not scoped to one story. **Read this before writing AC / scenarios / test cases**
for any feature area listed below; do not assume uniform behaviour across iOS / Android / web-desktop / mobile-web just because PM says "same as before".

> PM does not spec platform-by-platform differences. QA discovers these (via code-check, manual testing, or
> resolving a PM ambiguity) and maintains this registry going forward. An entry here is a **standing fact**,
> not an open question — cite it, don't re-litigate it, unless you have evidence it changed.

**Adding a new entry:** confirmed a platform behaves differently on a feature you're working on? Add it here
(`qa/_shared/platform-behavior-registry.json`), even if it's not this epic's focus — the next epic that touches
this feature area inherits it for free. Only add STANDING divergences (interaction model / OS capability /
SDK support) — not in-flight bugs being fixed for one epic (those belong in that epic's own notes; they go
stale the moment they're fixed).

Gate: `checks/platform_registry_integrity.py` (structural — dup ids, phantom epic refs, non-divergent entries).

---

## Video / Live player — tap interaction model

### PB-001 — First tap on a PLAYING player: mobile reveals controls without pausing (2-step to pause); web-desktop pauses directly on first tap (1-step).

**Divergence type:** `interaction-steps` · **Status:** `confirmed`

| Platform | Behaviour |
|---|---|
| **iOS** | 2-step: tap reveals the controls overlay (playback continues); tap the center button to pause |
| **Android** | 2-step: same as iOS |
| **Web (desktop)** | 1-step: tap pauses directly, no intermediate reveal |
| **Web (mobile)** | 2-step: behaves like the mobile app, not like web-desktop |

**Evidence:** PM platform table (comment 68264) + code-verified 2026-07-08 against Amity-Social-Cloud-UIKit-Web + AmityUIKitIOS (see qa/PDT-3418/_epic/platform-behavior-notes.md PV-1)  
**PM position:** PM described this as 'no behaviour change, only a small UI design change (button size)' — did not flag the interaction-step difference; QA-maintained  
**First confirmed:** PDT-3418 (2026-07-08)  ·  **Also seen in:** —

---

## Live player — pause control availability

### PB-002 — mobile-web cannot pause a Live stream at all; iOS, Android, and web-desktop all can.

**Divergence type:** `not-supported` · **Status:** `confirmed`

| Platform | Behaviour |
|---|---|
| **iOS** | 2-step pause available (reveal then tap) |
| **Android** | 2-step pause available (reveal then tap) |
| **Web (desktop)** | 1-step pause available |
| **Web (mobile)** | No pause control is shown — cannot pause a Live stream |

**Evidence:** PM platform table (comment 68264); confirmed in PDT-3418 manual test pass (MC-B11 / EC-UC2-013..015)  
**PM position:** Not called out by PM — surfaced by QA while writing per-platform test cases  
**First confirmed:** PDT-3418 (2026-07-08)  ·  **Also seen in:** —

---

## Live player — network-drop reconnect indicator

### PB-003 — The 'Reconnecting' indicator is driven by a DIFFERENT signal per platform, so it appears at different times: iOS ties it to the device's own network monitor (shows even while the viewer has the stream paused); web ties it to the broadcaster/SDK room status (generally does NOT show for a plain viewer-side pause, only when the broadcaster itself drops).

**Divergence type:** `timing` · **Status:** `confirmed`

| Platform | Behaviour |
|---|---|
| **iOS** | Full-screen scrim + spinner, driven by NWPathMonitor (device network) — shows while paused too, since it's about the viewer's own connectivity |
| **Android** | Not yet code-verified — assume parity with iOS until checked (OS-level network monitor pattern is typical) |
| **Web (desktop)** | LivestreamOverlay Reconnecting spinner, gated on SDK room.status==='waitingReconnect' (broadcaster-side) — generally NOT shown for a viewer-side pause |
| **Web (mobile)** | Same mechanism as web-desktop (shared web player) |

**Evidence:** Code-verified 2026-07-08: LiveStreamViewerView.swift:244-272 + NetworkMonitor.swift:11-28 (iOS) vs LivestreamOverlay.tsx:57-66 + LivestreamPlayer.tsx:128 (web) — see qa/PDT-3418/_epic/platform-behavior-notes.md  
**PM position:** Not specced by PM at this level of detail — QA had to read source to resolve UC2 E-04 / AC-08  
**First confirmed:** PDT-3418 (2026-07-08)  ·  **Also seen in:** —

---
