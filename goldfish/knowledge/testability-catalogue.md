# Testability catalogue (QA-owned)

Things that are hard or impossible to verify on our environments, and what makes them testable.
Feeds the testability flags at Day 0 and in Solution review (status 02), so the room hears about
them while a test hook or an env setting is still cheap to ask for.

An entry earns its place only with a **source** (a code path, a blocker entry, a ticket) and a
**date**. `feature:` names the feature it was learned on — Replay mode skips entries learned on the
feature being replayed.

| id | Area | Hard to test because | What makes it testable | Source | Learned · feature |
|---|---|---|---|---|---|
| TC-ENTITLEMENT-GATE | console-next access | `CONSOLE_NEXT_REQUIRES_ENTITLEMENT` closes the whole app to a network whose `moduleEntitlement.mode` is off/absent | e2e uses an entitlement stub; a rule that depends on "not entitled" needs a network in that state, named in the case | console `CLAUDE.md` § development-phase access gate · `src/lib/entitlement.ts` | 2026-09-20 · all |
| TC-SHARED-SESSION | auth | console and console-next share one session on staging (cookie belongs to the API host) | separate browser profile per console; a "two admins" case needs two profiles | console `CLAUDE.md` § access gate | 2026-09-20 · all |
| TC-ADMIN-ROLE-PERMANENT | permissions | the platform serves no DELETE for admin roles, so a role a test creates is permanent | ask for a standing custom role per needed permission set, once; never create per test | console `qa/BLOCKERS.md` 2026-09-04 | 2026-09-04 · content-widget |
| TC-PERMISSION-REVOKED | permissions | revoking mid-session needs editing a role other admins share; console re-checks only on full load | standing custom role (above); rule must say *when* the revocation takes effect (next call? next load?) | console `qa/BUGS-TO-RAISE.md` #30 | 2026-09-11 · roles |
| TC-OFFLINE-MUTATION | network | mutations use TanStack default `networkMode`; offline save is not reported | rule must state the offline result; S-CAT §16 says console is online-only — a rule claiming otherwise needs a case | console `qa/BUGS-TO-RAISE.md` #31 | 2026-09-11 · all |
| TC-AI-MODERATION | moderation | AI-moderation credentials not provisioned on staging | a rule whose actor is AI moderation needs seeded data or the credentials; otherwise manual / blocked | console `qa/BUGS-TO-RAISE.md` #1 | 2026-08-16 · moderation |
| TC-WEBHOOK | integrations | webhook disabled on staging | env change by platform, or case is manual on another env | console `qa/BUGS-TO-RAISE.md` #16 | 2026-08-16 · events |
| TC-RTMP | livestream | no RTMP publisher in the harness | livestream state cases manual until QA infra exists | console `qa/BUGS-TO-RAISE.md` #11 | 2026-08-16 · livestream |
| TC-COMMUNITY-NO-RESTORE | groups | core soft-deletes a community and serves no restore, so a delete case consumes a group and the Deleted list only grows on shared staging | per-run group factory, run-tagged names; never delete a shared fixture group | core `src/services/v3/community.service.js` (`isDeleted` query, no restore action) @62e15bbb8 | 2026-10-05 · group-list-content |
| TC-NETWORK-SETTING | env | network-level settings (e.g. `membershipAcceptance`) are shared by everyone on staging | a rule that depends on a network setting names the setting; the case names the network that has it | console `qa/BLOCKERS.md` 2026-08-17 | 2026-08-17 · communities |

## Generic lenses (no source needed — they are questions, not facts)

- **Time** — a rule with a time window or cutoff: can QA move the clock or must the case wait? Inclusive or exclusive edge, which clock (server or browser)?
- **Limits** — a quota or max count: can it be lowered on staging, or must the case fill it for real?
- **Cross-product** — a console action whose result shows in the app (UIKit/SDK): who verifies the app side, on which build?
- **Async** — a result that arrives later (notification, index, scheduled job): how long to wait, what is the observable signal?
- **Third party** — a result decided outside our system (AI, payment, store): seeded data or a stub?
