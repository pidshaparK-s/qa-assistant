# Sign-off package — PDT-3418 (Video & live streaming)

**Epic:** PDT-3418 · **Stories:** PDT-3562 (UC1, split QA-internal into UC1a/UC1b), PDT-3563 (UC2), PDT-3564 (UC3)
**Prepared:** 2026-07-09 · **Status:** L1 → L2 → L3 complete, all gates green · **NOT yet signed off**
**Reviewers:** PM · Dev lead · QA lead

---

## What we're asking

1. **Approve 3 open decisions** (below) — these are the only judgment calls not yet locked. Everything else is settled (7 decisions confirmed / code-resolved).
2. **Acknowledge 5 follow-ups** (FU-1…FU-5) — non-blocking, owned, tracked. One (FU-5) is a **sync-integrity** action for PM; one (FU-3) blocks exactly 1 of 105 test conditions.

Approving the 3 decisions closes the scope-boundary sign-off (`PDT-3418-scope-boundary.md`) and unblocks sprint commit.

---

## ① Decisions to sign off

| # | Type | Decision | Owner | Approve = |
|---|---|---|---|---|
| **DEC-06** | priority | MoSCoW: **UC1a Must · UC1b Must · UC2 Should · UC3 Could** (sprint order 1,1,2,3) | **PM** | commit this order to the sprint |
| **DEC-07** | scope | **LIVE badge / viewer-count live-update = OUT of scope** (a separate enhancement) | **PM** (QA proposed) | we do not build/test live-updating badge in this feature |
| **DEC-10** | policy | **L3 automation context** — platforms iOS/Android/RN/Flutter/Web (desktop = 1-step); stability MIXED (mobile video/recorded stable · web overlay changing · **web-Live net-new**); Live tests are flaky (SDK+broadcast+network) → mock-heavy, assert "≈ live within tolerance" | **QA lead** | the 105-TC automation plan (98 automate-family) stands on these assumptions |

**Impact if a decision changes:**
- **DEC-06** — promoting UC2 → Must enlarges the critical path (UC2 is the hardest unit, highest QA effort 20/21). Descoping UC3 is the clean lever — it removes real effort (timing-sensitive rapid-tap, boundary matrix), not "free" work despite the "nice-to-have" label.
- **DEC-07** — pulling badge live-update *into* scope adds new ACs + TCs to UC2 (badge behaviour during pause/resume) and enlarges the hardest unit.
- **DEC-10** — if Live env is actually CI-stable, or web-Live is already validated, several `Automate (with mock)` / `when stable` verdicts become plain `Automate` (cheaper). If it's flakier than assumed, more shift to Manual/real-device.

Full text + rationale + source refs: [`decisions.json`](decisions.json) (DEC-06, DEC-07, DEC-10).
Autonomous runs HALT on these until settled — `python3 checks/decision_ledger.py qa/PDT-3418 --autonomous`.

---

## ② What was built (L1 → L2 → L3)

| Layer | Output | Numbers | Key artifacts |
|---|---|---|---|
| **L1** BA Requirement Analysis | enriched AC · clarification register · platform notes | 19 clarifications processed · **0 still-ambiguous** (2 → follow-ups) | [clarifications.json](clarifications.json) · [platform-behavior-notes.md](platform-behavior-notes.md) · [FOLLOWUPS.md](FOLLOWUPS.md) |
| **L2** QA Story Authoring | Schema 1 (spec) → Schema 2 (flows) | **40 ACs** · **15 BRs** (32 instances) · **41 flows** · UC1 split UC1a/UC1b | [story-shape](PDT-3418-story-shape.md) · [business-rules](PDT-3418-business-rules.md) · [scope-boundary](PDT-3418-scope-boundary.md) · Schema 1/2 ×4 |
| **L3** Test Design | test conditions + automation judgment | **105 TCs** · automate-family **98** · partial 3 · manual 4 · **BR+AC coverage 100%** | [test-design-overview](PDT-3418-test-design-overview.md) · 4× `*-test-design.md` |

**Traceability (verifiable end-to-end):** `epic → story → uc → br/ac → flow → TC`.

**Gate suite — all green** (stdlib, `exit 0/1`, run before commit):

| Gate | Layer | Guards |
|---|---|---|
| `ac_coverage.py` | L1 | analysis covers every AC + STALE detection |
| `schema1_integrity.py` | L2 | no dangling/dead br_id, no dup id |
| `schema_trace.py` | L2 | Schema 1↔2 coverage, no phantom ac/br, actors declared |
| `decision_ledger.py` | L2 | judgment logged; open human decision = HALT (autonomous) |
| `br_tc_coverage.py` | L3 | every BR + AC has a test condition |

Split note: **UC1a/UC1b is a QA-INTERNAL split** of the single Jira ticket PDT-3562 (by player component: video/recorded vs 'Live'). **No new Jira ticket** — PDT-3562 stays one ticket.

---

## ③ Follow-ups (non-blocking, owned)

| FU | Owner | Action | Blocking? |
|---|---|---|---|
| **FU-1** | PM / BA | Remove stale "(assume 3s)" note from PRD — auto-dismiss is 1s | No (doc hygiene) |
| **FU-2** | Design | Provide concrete hit-target size of central pause/play button (makes UC1 AC-02 boundary testable) | No (low) |
| **FU-3** | Eng (Web) | Confirm what the **±10s skip** button does on video/recorded **while buffering on web** | ⚠️ blocks **1 TC** (UC3-07b) only |
| **FU-4** | Eng (Android) / QA | File bug: OS-native media control can FF/rewind a **Live** stream (separate from in-app; not an AC gap). Fix → **cross-platform parity re-check** | No (separate defect) |
| **FU-5** | **PM** | **Align Jira AC text** to the 2026-07-08 decisions (seek on video/recorded only; UC3 skip-back preserves prior state) — else next sync re-introduces the conflicts | ⚠️ **sync-integrity** |

**Standing platform fact (carry into every test case):** first tap on a playing player = **mobile: reveal controls (no pause)** vs **desktop Web UIKit: 1-Step Pause**. Author a separate expected per platform. Not a closeable item.

---

## ④ Verify it yourself

```
python3 checks/ac_coverage.py       qa/PDT-3418
python3 checks/schema1_integrity.py qa/PDT-3418
python3 checks/schema_trace.py      qa/PDT-3418
python3 checks/decision_ledger.py   qa/PDT-3418
python3 checks/br_tc_coverage.py    qa/PDT-3418
```
All exit 0 as of 2026-07-09.

---

## ⑤ Sign-off

| Role | Name | Approves DEC-06 / 07 / 10 | Date | Notes |
|---|---|---|---|---|
| PM | | ☐ 06 ☐ 07 | | |
| Dev lead | | ☐ (feasibility) | | |
| QA lead | | ☐ 10 | | |

_Once all three sign, update `PDT-3418-scope-boundary.md` status to "signed off" and re-bless the ledger (`decisions.json`: set DEC-06/07/10 status → `confirmed`)._
