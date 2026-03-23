# Spec Sync — Post-Fix Feedback Loop

After completing the build-test-fix loop (or after each cycle), review the fixes made and sync any spec gaps back to the spec files. This ensures the spec accurately reflects the application as built.

---

## When to Run

- **After each fix cycle** — Once fixes are committed, before the next test run
- **After all tests pass** — Final review to ensure spec matches reality
- **After exhaustion** — Review exhausted scenarios for spec issues

---

## Process

### 1. Review Fix History

Examine the git log since the loop started:

```bash
git log --oneline --since="$(date -v-1d)" -- .
```

Or review the `.prover-meta.json` history entries, which capture the error and fix description for each cycle.

### 2. Identify Spec Gaps

For each fix commit, ask:

- **Missing behavior?** — Did the fix implement something the spec did not describe? If so, the spec should be updated.
- **Wrong assumption?** — Did the spec assume an API shape, UI pattern, or flow that turned out to be incorrect?
- **Missing edge case?** — Did the fix handle an edge case (empty state, error state, boundary condition) not covered in the spec?
- **Missing entity/field?** — Did the fix require a data model change not reflected in `domain-refinement.md`?

### 3. Update Spec Files

Update the appropriate spec files to reflect what was actually built:

| Gap Type | Update Target |
|----------|---------------|
| Missing UI element | `spec/apps/{app}/pages/{page}.md` |
| Wrong API shape | `spec/apps/{app}/api-contracts.md` |
| Missing state transition | `spec/apps/{app}/state-interaction.md` or `spec/suite/state-interaction.md` |
| Missing entity/field | `spec/apps/{app}/domain-refinement.md` |
| Missing permission | `spec/apps/{app}/role-refinement.md` |
| Wrong navigation flow | `spec/suite/navigation-shell.md` |

### 4. Feature File Policy

**Do NOT modify `.feature` files during the build-test-fix loop.** Feature files are immutable during Phase 3.

If a fix reveals that a `.feature` scenario is:
- **Incorrectly specified** — Flag it for human review
- **Missing a scenario** — Flag it for human review
- **Over-specified** — Flag it for human review

Create a section in `.prover-meta.json` or a separate `spec-sync-notes.md` to track these flags:

```markdown
## Feature File Review Needed

### order-management.feature.md
- Scenario "Filter by date range" assumes a date picker component but the app uses inline date inputs
- Missing scenario for bulk order export

### user-management.feature.md
- Scenario "Deactivate user" does not account for the confirmation modal
```

### 5. Post-Loop Feature Updates

After the loop is complete (all passed or exhausted) and the agent is no longer in Phase 3, `.feature` files may be updated by running the spec pipeline again:

1. Update the relevant spec files (pages, API contracts, etc.)
2. Re-run `webapp-blueprint` Step 9 (BDD Features) for affected apps
3. Re-run `webapp-architect` for any impacted steps
4. Re-convert `.feature.md` to `.feature`
5. Re-run the prover from Phase 1 if harness changes are needed, or from Phase 3 if only app code changes

---

## Commit Convention

Spec sync commits use a distinct prefix:

```
spec-sync: {file} — {description}
```

Examples:
```
spec-sync: api-contracts.md — add missing PATCH /orders/:id/status endpoint
spec-sync: orders-page.md — add empty state description for no orders
spec-sync: domain-refinement.md — add archived_at field to Order entity
```

---

## Avoiding Spec Drift

The goal of spec sync is to prevent **spec drift** — the spec saying one thing while the app does another. Every fix commit is a signal that the spec might be incomplete.

Rules:
1. **Every fix commit should trigger a spec review** — even if no spec change is needed
2. **Spec changes are committed separately from code fixes** — separate concerns
3. **Spec changes should be minimal and targeted** — only update what the fix revealed
4. **Never weaken the spec to match a bug** — if the app is wrong, fix the app; if the spec was wrong, fix the spec
