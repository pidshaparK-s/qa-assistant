# <Feature> — Day 0 intake (QA)

Date: <YYYY-MM-DD> · Mode: frame | no-frame (PRD + Figma) | replay @<sha>
Inputs: <frame link | PRD link/section | Figma pages (node ids) | console today: src path>
Verdict: NO FRAME — <n> frame gaps (+ READY/NOT READY on the rest) | READY | DERIVED — <n> fields need PM confirm at 03 | NOT READY — <n> must-before-03 unknowns

Source tags: `frame §n` · `PRD §n` · `Figma <node>` · `console <path>` · `core <file:line>` · `knowledge <file#id>` · `derived` (inferred — PM confirms) · `UNKNOWN`

## 1 QA frame card

| # | Need | Value | Source | QA uses it for |
|---|---|---|---|---|
| 1 | Capabilities, ranked | C1 A <role> <verb> … | | traceability; test depth by rank |
| 2 | Actors → system roles | <person> → <role> \| no account | | which roles to test with |
| 3 | Platform coverage | console / uikit-web / ios / android … | | configurations |
| 4 | Boundaries (what is out) | | | out-of-scope up front |
| 5 | Constraints (entitlement, quota, legal) | | | negative cases |
| 6 | Measurement / events | | | instrumentation cases |
| 7 | Names (internal · customer-facing) | | | exact copy in expected |
| 8 | Complexity · appetite | | | QA time reservation, depth |

## 2 Rule candidates (from PRD AC — NOT rules; the room decides)
- RC1 <statement> — PRD §x — likely [product|system]

## 3 States the inputs show (S-CAT walk, draft)
| Surface (Figma node) | Drawn | Not drawn — ask or apply standing look |
| --- | --- | --- |

## 4 Early testability flags
- TF1 <what> — why hard — what would make it testable — knowledge ref

## 5 Questions for the ticket chat (each passes the 4 criteria)
### Frame gaps (one note to PM, not asked one by one)
- <rank · appetite · events …>
### Must answer before 03
- Q1 → <PM|Architect|Design>: <one-decision question> — changes: <field/rule>
### Can wait for Detailing
- Q2 → …

## 6 QA decided (did not ask)
- <assumption or case note> — why it failed the criteria
