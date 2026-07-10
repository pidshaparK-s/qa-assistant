# Layer 2 · STEP 5 — Prioritization + QA Effort (phase-2-5)

_Skill: `phase-2-5-prioritization` · Input: 4 units, 41 ACs, 15 BRs, scope boundary, code-verified deltas, dependency order (STEP1)_
_Reminder (skill): BA+QA does NOT prioritize FOR the PM — we recommend, flag Must-inflation, and expose QA effort the PM/dev can't see. Final MoSCoW = PM's call._

---

## Section 1 — MoSCoW (recommended; PM owns final)

| Unit | MoSCoW | Why | AC-coverage expectation |
|---|---|---|---|
| **UC1a** Tap-to-reveal (video/recorded) | **Must** | The epic's reason to exist — stops tap from toggling pause (the XM/Ulta bug). No product without it. | full — all 4 scenario types |
| **UC1b** Tap-to-reveal (Live) | **Must** | The same bug hits Live; and web-Live is net-new. The fix is incomplete if Live still tap-pauses. | full — all 4 types |
| **UC2** Live pause/resume | **Should** | High value, but there IS a workaround: pausing a Live still works via UC1's button; only the *resume-to-live* upgrade is missing (today's resume-from-pause is degraded-but-functional). | core ACs first; race/network edges can follow |
| **UC3** 10-Second skip | **Could** | Explicit nice-to-have (AMB-04: in-release but descopable). Cutting it hurts a little, not a lot. | happy path enough if squeezed |
| _Out-of-scope set_ | **Won't (this release)** | LIVE badge, return-to-live CTA, double-tap, accumulated skip icon, mobile-web Live pause, Option-2 backgrounding — all documented in scope-boundary with reasons. | documented "not this release" |

**Must-ratio check:** 2 of 4 units = **~50% Must** → healthy (skill flags >60%). ⚠️ **If PM promotes UC2 to Must** (marquee "pause live" capability), Must rises to ~75% — defensible for a cohesive 3-part feature, but note UC2 is also the **highest QA effort** (below), so a Must-UC2 meaningfully enlarges the critical path.

---

## Section 2 — Impact vs Effort (Must + Should)

```
                 Low Effort                 High Effort
             ┌──────────────────────┬──────────────────────────┐
High Impact  │  (none pure)         │  UC1a · UC1b · UC2        │
             │                      │  → Major Projects         │
             ├──────────────────────┼──────────────────────────┤
Low Impact   │  (none)              │  UC3 (Could)              │
             │                      │  → high-ish effort, lower │
             │                      │    impact → descope lever │
             └──────────────────────┴──────────────────────────┘
```

- **No pure Quick Wins** — everything is multi-platform × (video + Live component), so nothing is genuinely low-effort. UC1a is the closest to "do first" (highest impact, unblocks the rest).
- **Sprint order (respects the STEP1 dependency UC1 → {UC2, UC3}):**
  1. **UC1a + UC1b** — foundation + the core fix (UC2/UC3 both consume UC1's overlay/pause mechanism).
  2. **UC2** — needs UC1's pause button in place.
  3. **UC3** — Could; needs UC1's overlay; first to drop if the sprint tightens.

---

## Section 3 — QA Effort Score (7 criteria × 1–3; 7–10 Low · 11–15 Med · 16–21 High)

| Criteria | UC1a | UC1b | UC2 | UC3 |
|---|:--:|:--:|:--:|:--:|
| # of AC (1-3 / 4-7 / 8+) | 3 (11) | 3 (10) | 3 (8) | 3 (12) |
| Hardest AC type | 3 error | 3 error | 3 error/edge | 3 edge |
| # BR related | 3 (~7) | 3 (~6) | 3 (~9) | 3 (~7) |
| BR reuse across units | 3 | 3 | 3 | 2 |
| Dependency / integration | 2 internal ×5 platforms | 2 internal, separate Live comp | 2 internal, **behaviour-change** | 2 internal, web-change |
| Environment complexity | 3 device+bg+multi-plat | 3 **live broadcast** setup | 3 **live + network-drop + race + chat-sync** | 3 boundary videos + rapid-tap timing |
| Regression risk | 3 shared overlay/BR-10 | 3 shared BR | 3 **behaviour change** on existing resume | 2 mostly standalone |
| **TOTAL** | **20 High** | **20 High** | **20 High** | **18 High** |

**This whole epic is High QA effort across the board** — the dominant multipliers are **5 platforms × the video/Live component split × live-stream test infra**. That's the headline for the PM.

### ⚠️ Where the PM will underestimate (say these out loud)
- **UC2 is the hardest, not UC1.** "Just add a pause button" hides that resume-to-live is a **behaviour CHANGE re-implemented on every platform** (CONF-07), plus the **hardest test environment in the epic** (need a live broadcast + simulate network drop + host-ends-during-pause race + long-pause + chat/video re-sync). If any unit slips, expect it here.
- **UC1b ≠ "same as UC1a".** Web-Live has **no reveal-controls overlay today** (code-verified) — it's net-new build + a separate component to test per platform, not a copy of UC1a.
- **UC3 "nice-to-have" ≠ cheap.** It scored **18 (High)**: 12 ACs, timing-sensitive rapid-tap accumulation, boundary matrix, web debounce→accumulate change. **This is the real descope lever** — cutting UC3 removes genuine QA effort, not a token amount. Cutting UC2 does not (it's core behaviour).
- **3 known dev deltas add rework/verify cycles** on web specifically: auto-dismiss 3s→1s (BR-03), debounce→accumulate (BR-08), web-Live overlay net-new (BR-01/11). Web will lag the other platforms.

### Effort-reduction levers to offer PM (skill's "give a choice" pattern)
1. **Drop UC3** → biggest QA saving, lowest user pain (it's Could).
2. **Defer UC2's edge ACs** (long-pause tolerance AC-06, chat re-sync AC-07) to a fast-follow → keeps UC2 core, trims the hardest env cases.
3. **Stage web behind mobile** → mobile is closer to spec today; web carries all 3 deltas.

---

## STEP 5 exit — ready for STEP 6 (emit Schema 1)

MoSCoW recommended (Must: UC1a/UC1b · Should: UC2 · Could: UC3 · Won't: documented set), sprint order set (UC1→UC2→UC3), QA effort scored (all High; UC2 hardest; UC3 the descope lever). These `moscow` + `qa_effort` values drop into each Schema-1 file's prioritization block at STEP 6.
