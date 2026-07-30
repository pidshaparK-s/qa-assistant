---
name: proposal-preimplementation-gap-checks
description: "Open proposal (not yet implemented) — 4 skill/process additions to catch audience-timing, cutover-data, and precedent-consistency gaps before dev implements, based on PDT-3421/3420 bugs"
metadata: 
  node_type: memory
  type: project
  originSessionId: 89d10506-d925-446d-95ab-05cca43c5cef
---

Proposed on 2026-07-21, status: **awaiting user decision** — user said "keep as proposal, decide in a new session" (not yet implemented, no files edited).

## The ask
User wants to systematize catching classes of bugs found during PDT-3421 (Notification Tray) + PDT-3420 (Push) manual testing — BEFORE developers implement, not after via as-built source review.

## Retro — 4 things that slipped through, mapped to existing `.claude/skills/phase-1-4-edge-and-error-ac` mental models
- **BUG-F/G** (new user sees old-event flood / new user sees nothing for a public event) — an "audience timing" gap: existing Model 2 (Timing) checklist only covers concurrent-session state changes, not "actor joined before/after a broadcast trigger" or "zero-state actor eligible for 'all users' claims."
- **TR-CL-26** (should pre-release events show in the enriched tray at all) — a "cutover boundary" gap: existing Model 4 (Data Integrity) mentions migration in prose but has no checklist item for "does data created before this feature/release deserve the new behavior."
- **TR-CL-05 timezone reversal** (PM said event-tz, dev pushed back post-implementation: should follow existing viewer-local precedent) — no mental model covers "does this contradict how the same concept already works elsewhere in the app" — a "precedent consistency" gap.
- **TR-CL-13→26** (I resolved a clarification via as-built/source-review, but the discovered behavior actually contradicted the original question's premise, and I silently marked it `resolved` instead of flagging the mismatch) — a process gap in the `qa-clarifications-review` skill, not a mental-model gap.

## 4 proposed additions (none implemented yet)
1. **Extend Model 2 (Timing) checklist** in `phase-1-4-edge-and-error-ac/SKILL.md`: for any AC claiming "all users / network-wide," explicitly ask — does a user who joined/signed-up AFTER the trigger see something different than one who joined before? Does a zero-prior-action user qualify for "all users"?
2. **Extend Model 4 (Data Integrity) checklist**, same file: does data created BEFORE this feature/release deserve the new behavior fully, partially, or should it be excluded (cutover boundary)?
3. **New "Precedent Consistency" check** (new Model 5, or folded into phase-1-3 happy-path enrichment): before locking a PM answer into an AC, check whether the same concept already has established behavior elsewhere in the product — if so, does the new answer match or contradict it?
4. **Gate rule addition to `qa-clarifications-review/SKILL.md` Step 1**: when a clarification is resolved via `resolved-by-code`/as-built (not an explicit human decision), compare the discovered behavior against the ORIGINAL question's premise/expectation. If it contradicts, do NOT silently mark `resolved` — downgrade to `still-ambiguous` or open a new linked clarification for explicit PM confirmation.

## Acknowledged limit
Items 1-3 catch things QA/BA can find by reading AC more deeply. The actual BUG-F/G root cause (Neo4j User-node lazy-creation) is an implementation/architecture detail no amount of AC-reading would surface — that needs a NEW pre-sprint step: a short structured "audience computation probe" handed directly to engineering for any AC using "all/every/entire network" language (e.g., "does audience computation depend on any lazily-created state? is there a time-bound relative to account/join time? what happens for a zero-state actor?"). No existing phase does this pre-emptively today (closest is phase-2-6 scope/gap, but not this specific).

## Options discussed, not yet chosen
- (a) Edit the SKILL.md files now (phase-1-4 + qa-clarifications-review)
- (b) Retrofit the new checklists against PDT-3421/3420 retroactively first, to prove they'd have caught these, before touching the shared skill files
- (c) Just keep as a proposal, discuss further in a new session ← **user picked this for now**

## How to apply
When this comes up again (same session or new): don't re-litigate the retro — it's above. Ask directly which of (a)/(b)/(c) to do, or whether the user has a different direction after thinking about it. Relates to [[team-manual-testcase-convention]] and the PDT-3421 bug docs (BUG-F, BUG-G, TR-CL-26) in `qa/PDT-3421/`.
