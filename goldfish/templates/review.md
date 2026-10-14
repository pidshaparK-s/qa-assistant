# <Feature> — Solution review (QA) · <sketch | detail §n>

Date: <YYYY-MM-DD> · Input: <path @ sha | branch> · Status of the artefact: <02 | 03 | 04 | 05> · Core @ <sha>
Replay: blind | NOT blind — <why> (findings touching amended text marked †)
Not re-checked here (solution:check does it): flow with no rule · rule with no test case · n/a state with no reason · empty permission cell · unknown id

## Findings

| # | Ref | Lens | Finding | Proposed fix | Route | Blocks |
| --- | --- | --- | --- | --- | --- | --- |
| QF1 | R6 | numbers | "at least 15 minutes" — inclusive? measured from when? | `R6 … ≥ 15 min from Save, server clock` | PR comment → Eng | 05 |

Route: `PR comment → Eng|Design` · `chat → PM` ([product]) · `chat → Architect` (platform truth) · `huddle` (two roles disagree) · `QA decides`
Blocks: `03` · `05` · `—` (low — batched in one closing comment, not asked one by one)

## Testability flags
- TF1 <rule/state> — why it is hard to verify — what makes it testable (test hook · env setting · data) — route — knowledge ref

## Effort drivers (no numbers unless the team asks)
- roles × configurations to cover · time-based rules · cross-product checks · env setup that needs a person

## Held for Detailing (sketch mode only)
- <detail seen early, not asked now>

## QA decided (not asked)
- <item> — becomes a QA case / assumption

## Summary
Findings: <n> (to room <n> · QA decides <n>) · Blocking before 03/05: <ids>
