# Spec Sync Reference

## Overview

The build/test/fix cycle often reveals gaps in the spec: edge cases not covered by BDD scenarios, API shapes that differ from `api-contracts.md`, seed records that were missing, UI states not described in page specs. **Spec Sync** closes this loop — it keeps the spec as living truth rather than letting it drift from the implementation.

---

## When to Run

| Situation | Recommendation |
|-----------|---------------|
| First green cycle (all PASSED) | **Recommended** — establish baseline |
| Cycle with 2+ fix commits | **Recommended** — fixes likely extended the spec |
| Cycle with 0 fix commits | Optional |
| Every cycle | Overkill for stable suites |

---

## Step 1: Review the Fix Commits

```bash
git log {pre_build_sha}..HEAD --oneline
```

Where `{pre_build_sha}` is the SHA before you started the current build cycle (recorded in the previous `manifest.json`, or tracked manually).

Read each commit diff. For each change, ask:
- Does this code path correspond to a BDD scenario? If not → propose new scenario
- Does this API response shape match `api-contracts.md`? If not → propose spec update
- Were seed records added that aren't in `seed-data.md`? If so → propose seed update
- Are UI states handled in code but absent from page specs? If so → note for spec maintainer

---

## Step 2: Write spec-gaps.md

Create a report at:
```
blackbox/builds/{build_token}/spec-gaps.md
```

Format:
```markdown
# Spec Gaps — Build {build_token}

## New BDD Scenarios Needed
- `spec/apps/{app}/features/{feature}.feature.md`: Add scenario for {description}

## API Contract Divergences
- `spec/apps/{app}/api-contracts.md`: `GET /orders` response includes `meta.total` field not documented

## Seed Data Additions
- `spec/apps/{app}/seed-data.md`: Needs at least 1 cancelled order record for "order history empty state" scenario

## Page Spec Gaps
- `spec/apps/{app}/pages/order-detail.md`: Error state for 404 not described
```

---

## Step 3: Apply Updates (Optional)

With user confirmation (or autonomously in full-auto mode), apply the proposed changes to `./spec/`:

1. Edit the relevant spec files
2. If BDD features were updated, regenerate the suite template:
   ```bash
   python3 scripts/generate-blackbox-template.py --suite {suite_name}
   ```
3. Commit the spec updates:
   ```bash
   git commit -m "spec: sync gaps from build cycle {build_token}"
   ```

---

## Step 4: Start the Next Cycle

With spec gaps applied (or noted), trigger a new build cycle:
1. New code changes (if needed)
2. New deployment → new build_token
3. New `manifest.json` → test agent runs again
4. The updated suite template ensures any new BDD scenarios are included in the next test run
