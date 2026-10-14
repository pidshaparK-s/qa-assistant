# Snapshot — read-only

These files are a **read-only copy** of console-next `docs/solution/posts-analytics/`, taken for QA review before the Solution is final.
Do not edit them here; send changes to the Solution room or as review comments on the PR.

| | |
|---|---|
| PR | https://github.com/AmityCo/social-plus-console/pull/358 (open, base `next`, author kazekunz) |
| Branch | `solution/posts-analytics` |
| Commit | `4fe1362449f96e2b0f917770e012292ac51f0184` — head of `solution/posts-analytics` (PR #358, which now also carries the implementation merged from #368). Spec line reads "QA — pending" |
| Status in spec | 06 Solution Ready 2026-10-02 · all four confirmations signed "Chanatip"; QA's is not accepted by QA (pidshapar, 2026-10-06) |
| Taken | 2026-10-08, with delivery.md (previous: 9eb5d71, 99eb9b7, 9b09094) |

Refresh (from the social-plus-console checkout):
```bash
git fetch origin solution/posts-analytics
for f in sketch spec handoff slices delivery; do git show FETCH_HEAD:docs/solution/posts-analytics/$f.md > ../qa-assistant/products/admin-console/posts-analytics/solution/$f.md; done
git rev-parse FETCH_HEAD   # update the Commit row above
```
After the PR merges into `next`, QA work moves to social-plus-test-factory: `pnpm solution:import admin-console/post-analytics`.
