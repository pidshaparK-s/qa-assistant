# Layer 2 · STEP 1 — Story Shape (INVEST check)

_Skill: `phase-2-1-user-story-invest` · Input: Layer 1 output (enriched AC + clean Clarification Register, all 3 UCs)_
_Scope: epic-wide (PDT-3418) — INVEST checked together since UC2/UC3 reference UC1's mechanism directly_

> **Reading this table:** ✅ pass · ⚠️ pass-with-note (real finding, not a blocker) · 🔀 split candidate (a decision, not auto-applied)

---

## UC1 — PDT-3562: Tap to Reveal Controls

> "As a community member watching a video or live stream, I want tapping the player surface to reveal controls rather than toggle pause, so that I don't accidentally interrupt playback during normal viewing."

| Letter | Verdict | Reasoning |
|---|---|---|
| **I** ndependent | ✅ | Doesn't wait on UC2 or UC3. (AC-04's mention of skip controls "remaining visible" is a coexistence note, not a build-order dependency — it's vacuously true if UC3 doesn't exist yet.) |
| **N** egotiable | ✅ | One cohesive mechanism (reveal/dismiss/pause/resume) — not a kitchen-sink of unrelated asks. AC-06 (cross-surface) is the one genuinely cuttable margin. |
| **V** aluable | ✅ | Directly fixes the reported accidental-pause bug (XM/Ulta). Clear actor + clear pain removed. |
| **E** stimable | ✅ | Was NOT estimable before Layer 1 (overlay-after-pause, timer-reset, platform split were all open). Now concrete: GAP-02/03/04, CONF-08, PV-1 all resolved. |
| **S** mall | 🔀 **split candidate** | 6 ACs × 5 platforms × **2 render-paths** (video/recorded component vs 'Live' component — GAP-04: genuinely different implementation per platform) × 2 form-factor behaviors (PV-1: mobile reveal vs desktop 1-step). This is real surface area, not a feeling — GAP-04 already documents the component split as a fact, not a QA opinion. See split option below. |
| **T** estable | ✅ | Best-specified of the three stories — every AC has exact Given/When/Then, platform variance, and render-path split spelled out. |

### 🔀 Split — DECIDED 2026-07-08: yes, split by mechanism
The fault line is **which player component implements it**, not which platform (each platform still needs both halves). Confirmed by the user — proceed with UC1a/UC1b for Layer 2 authoring.

| | Scope | ACs carried |
|---|---|---|
| **UC1a — Tap-to-reveal (video / recorded LS)** | Video component path | AC-01, AC-02, AC-03, AC-04 (video/recorded branch — seek controls visible), AC-05, AC-06 (scoped: video/recorded surfaces) |
| **UC1b — Tap-to-reveal ('Live' livestream)** | Separate live-player component path | AC-01, AC-02, AC-03 (same content as UC1a — behavior is identical, only the underlying component differs), AC-04 (Live branch — NO seek controls), AC-06 (scoped: Live surfaces) |

- **AC-05 excluded from UC1b** — video-only resume-from-exact-position; live resume is UC2's domain (current-live-moment, CONF-07).
- **AC-01/02/03 have identical Given/When/Then in both** — the split isn't about different behavior, it's about a different underlying component needing its own implementation + test pass per platform (GAP-04). Only AC-04's seek-visibility bullet actually differs in content.

**How this is tracked (no fake Jira key invented):** Jira still has **one** ticket, PDT-3562 — splitting it into two tickets is a PM/team action I can't perform (no Jira-write access here) and haven't assumed. For Layer 2 authoring, `story_id` stays **PDT-3562**; **UC1a** / **UC1b** become two `uc_id` values under it — the schema already supports this level (`story_id → uc_id`, per `00-schema-process-guide.md`'s own example: one story, multiple UCs). If the team later formalizes this as two real Jira tickets, re-key at that point.

---

## UC2 — PDT-3563: Live Stream Pause State

> "As a community member watching a live stream, I want to pause and resume the stream, so that I can step away and always rejoin at what is happening live."

| Letter | Verdict | Reasoning |
|---|---|---|
| **I** ndependent | ⚠️ **dependent on UC1** | UC2's pause button + overlay dismiss (AC-01) is the SAME mechanism UC1 AC-04 defines — UC2 doesn't redefine it. Already flagged in the L1 analysis header ("Depends on UC1 — pause/play must exist first"). **Fix per the skill = sequence explicitly, not merge:** UC2 dev/test cannot meaningfully start before UC1's overlay/pause-button contract is locked. |
| **N** egotiable | ✅ | AC-03 (stream-ends-while-paused) is a real but cuttable edge case; AC-01/AC-02 are the essential core. |
| **V** aluable | ✅ | Matches modern livestream UX (YouTube/Twitch-style "always rejoin live"). Clear actor + clear pain. |
| **E** stimable | ✅ | CONF-07 (resume-to-live is a confirmed behavior CHANGE, with buffering tolerance), GAP-05/06, AMB-09, CONF-08 all resolved — concrete now. |
| **S** mall | ✅ | 3 ACs, single mechanism, no render-path split like UC1. Appropriately scoped. |
| **T** estable | ✅ | Indicator verified against Figma, ended-always-wins is unambiguous, buffering tolerance is spec'd for resume assertions. |

---

## UC3 — PDT-3564: 10-Second Skip Back/Forward (Nice-to-Have)

> "As a community member watching a video, I want to skip backward or forward 10 seconds so that I can quickly rewatch or jump ahead without scrubbing."

| Letter | Verdict | Reasoning |
|---|---|---|
| **I** ndependent | ⚠️ **dependent on UC1** | Precondition is literally "the controls overlay is visible" — that overlay is UC1's. Already flagged in the L1 analysis ("Dependency: needs the controls overlay from UC1"). Same fix: sequence after UC1, don't merge. |
| **N** egotiable | ✅ | Most negotiable of the three — tagged "nice-to-have" at the whole-story level (AMB-04: in scope now, but descopable if timeline slips). Within the story, AC-07/AC-08 (rapid-tap accumulate) are a further-cuttable "nice-to-have inside a nice-to-have." |
| **V** aluable | ✅ | Standard, expected video-player UX (skip without imprecise scrubbing). |
| **E** stimable | ✅ | GAP-07 (accumulate, web must change from debounce), AMB-11 (preserve-state at 0:00), AMB-08 (exact-10 clamp) all resolved. |
| **S** mall | ✅ (optional further split) | 8 ACs, one mechanism (discrete ±10s skip), video/recorded-only — no render-path split like UC1. Appropriately small as-is. *Optional, lower-priority* split: basic skip (AC-01/02/03/04/05/06) vs rapid-tap accumulate (AC-07/08) as a fast-follow — not recommended unless capacity is tight, since slicing an already-optional story further adds coordination overhead for little gain. |
| **T** estable | ✅ | Deterministic accumulate math, exact-10 clamp, preserve-state at 0:00 all defined; Live-exclusion and the native-control bug are scoped out separately (FU-4). |

---

## Epic-level findings (cross-story)

1. **Build order: UC1 → {UC2, UC3}.** Both UC2 and UC3 consume UC1's controls-overlay/pause-button mechanism. This must be explicit in the sprint plan and in Schema 1's story sequencing — not left implicit. Neither dependency requires a merge (per the skill's own guidance: "แก้: merge หรือ sequence ให้ชัด" — sequencing is the correct fix when the story is otherwise clean).
2. **UC1 is the one real split candidate**, and it's evidence-backed (GAP-04), not a guess. UC2 and UC3 are each correctly scoped as single stories.
3. **No role-out-of-scope trap** — all 3 use the same actor ("community member") with genuine, distinct value per story; none is a permission-boundary disguised as a story.
4. **All three "So that" clauses pass the removal test** — each carries real business/UX rationale (UC2's is load-bearing: it's the reason AC-02 changed to resume-to-live at all). No rewrite needed.

---

## STEP 1 exit — ready for STEP 2

**Decided shape going into STEP 2 (4 units, under 3 Jira keys):**

| Unit | Jira key (`story_id`) | `uc_id` |
|---|---|---|
| UC1a — Tap-to-reveal (video/recorded) | PDT-3562 | UC1a |
| UC1b — Tap-to-reveal (Live) | PDT-3562 | UC1b |
| UC2 — Live Stream Pause State | PDT-3563 | UC2 |
| UC3 — 10-Second Skip | PDT-3564 | UC3 |

Build order for sprint planning: **{UC1a, UC1b} → {UC2, UC3}** (UC2/UC3 both consume UC1's overlay/pause-button contract — Finding 1 above).

No blocker for `phase-2-2` (AC authoring, STEP 2) to start on this 4-unit shape.
