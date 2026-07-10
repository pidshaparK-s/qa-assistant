# Sign-off package — PDT-3418 (Video & live streaming)

**Epic:** PDT-3418 · **Stories:** PDT-3562 (UC1, split QA-internal into UC1a/UC1b), PDT-3563 (UC2), PDT-3564 (UC3)
**Prepared:** 2026-07-09 · **Status:** L1 → L2 → L3 complete, all gates green · **✅ SIGNED OFF 2026-07-09**
**Reviewers:** PM · Dev lead · QA lead

---

## Outcome — signed off 2026-07-09

1. **3 decisions APPROVED** — DEC-06 (priority · PM), DEC-07 (badge scope · PM), DEC-10 (automation context · QA lead) → all `confirmed` in the ledger. All 11 decisions now settled; `decision_ledger.py --autonomous` exits 0.
2. **5 follow-ups dispositioned** — FU-1 ignored · FU-2 resolved (**64×64px**) · FU-3 open (blocks 1 TC) · FU-4 confirmed bug → verify in release · FU-5 PM declined → **this repo is authoritative** (ledger DEC-11).

Scope-boundary is now **signed off**; sprint commit is unblocked.

---

## ① Decisions — approved 2026-07-09

| # | Type | Decision | Owner | Approve = |
|---|---|---|---|---|
| **DEC-06** | priority | MoSCoW: **UC1a Must · UC1b Must · UC2 Should · UC3 Could** (sprint order 1,1,2,3) | **PM** | commit this order to the sprint |
| **DEC-07** | scope | **LIVE badge / viewer-count live-update = OUT of scope** (a separate enhancement) | **PM** (QA proposed) | we do not build/test live-updating badge in this feature |
| **DEC-10** | policy | **L3 automation context** — platforms iOS/Android/RN/Flutter/Web (desktop = 1-step); stability MIXED (mobile video/recorded stable · web overlay changing · **web-Live net-new**); Live tests are flaky (SDK+broadcast+network) → mock-heavy, assert "≈ live within tolerance" | **QA lead** | the 105-TC automation plan (98 automate-family) stands on these assumptions |

**Impact if a decision changes:**
- **DEC-06** — promoting UC2 → Must enlarges the critical path (UC2 is the hardest unit, highest QA effort 20/21). Descoping UC3 is the clean lever — it removes real effort (timing-sensitive rapid-tap, boundary matrix), not "free" work despite the "nice-to-have" label.
- **DEC-07** — pulling badge live-update *into* scope adds new ACs + TCs to UC2 (badge behaviour during pause/resume) and enlarges the hardest unit.
- **DEC-10** — if Live env is actually CI-stable, or web-Live is already validated, several `Automate (with mock)` / `when stable` verdicts become plain `Automate` (cheaper). If it's flakier than assumed, more shift to Manual/real-device.

Full text + rationale + source refs: [`decisions.json`](decisions.json). **All three approved 2026-07-09 → status `confirmed`.** The ledger now has 0 open decisions — `decision_ledger.py qa/PDT-3418 --autonomous` exits 0.

---

## ② What was built (L1 → L2 → L3)

| Layer | Output | Numbers | Key artifacts |
|---|---|---|---|
| **L1** BA Requirement Analysis | enriched AC · clarification register · platform notes | 19 clarifications processed · **0 still-ambiguous** (2 → follow-ups) | [clarifications.json](clarifications.json) · [platform-behavior-notes.md](platform-behavior-notes.md) · [FOLLOWUPS.md](FOLLOWUPS.md) |
| **L2** QA Story Authoring | Schema 1 (spec) → Schema 2 (flows) | **40 ACs** · **15 BRs** (32 instances) · **41 flows** · UC1 split UC1a/UC1b | [story-shape](PDT-3418-story-shape.md) · [business-rules](PDT-3418-business-rules.md) · [scope-boundary](PDT-3418-scope-boundary.md) · Schema 1/2 ×4 |
| **L3** Test Design | test conditions + automation judgment | **105 TCs** · automate-family **99** · partial 2 · manual 4 · **BR+AC coverage 100%** | [test-design-overview](PDT-3418-test-design-overview.md) · 4× `*-test-design.md` |

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

| FU | Owner | Action | Status (2026-07-09) |
|---|---|---|---|
| **FU-1** | PM / BA | Remove stale "(assume 3s)" note from PRD — auto-dismiss is 1s | **Ignored** (not worth the edit) |
| **FU-2** | Design → answered | Central pause/play button hit-target | ✅ **Resolved — 64×64px** (Figma); dev's call, may use native |
| **FU-3** | Eng (Web) | What the **±10s skip** button does on video/recorded **while buffering on web** | ⏳ **Open** — blocks 1 TC (UC3-07b) |
| **FU-4** | Eng (Android) / QA | OS-native control can FF/rewind a **Live** stream (separate defect, not an AC gap) | 🐞 **Bug** — verify in release (parity check) |
| **FU-5** | ~~PM~~ → QA (repo) | Align Jira AC text to the decisions. **PM declined.** | **Repo authoritative** (ledger DEC-11) |

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
| PM | | ☑ 06 ☑ 07 | 2026-07-09 | approved |
| Dev lead | | ☑ feasibility | 2026-07-09 | approved |
| QA lead | Pidshapar | ☑ 10 | 2026-07-09 | approved |

_Done 2026-07-09: scope-boundary status → "signed off"; ledger re-blessed (DEC-06/07/10 → `confirmed`); **DEC-11** added — this repo is authoritative for the CONF-08/AMB-11 corrections since PM declined FU-5._
