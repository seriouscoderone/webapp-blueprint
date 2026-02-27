# Fix Cycle Reference

## Overview

After `wait-for-results.py` exits 0, read `final_test_results/results.json` and fix each FAILED scenario **one at a time, sequentially**. Do not attempt parallel fixes — failures often share a root cause, and parallel edits risk merge conflicts.

---

## Step 1: Read and Prioritize Failures

```bash
python3 scripts/summarize-results.py --build-token $BUILD_TOKEN
```

This prints PASSED/FAILED/UNTESTED counts per app, lists FAILED scenario titles, and exits 1 if any failures exist.

To read the raw results:
```
blackbox/builds/{build_token}/final_test_results/results.json
```

For each FAILED scenario, the test agent has filled in:
- `steps_to_reproduce` — ordered list of browser actions taken
- `error_detail` — raw assertion output, stack trace, or browser console errors
- `last_run` — ISO-8601 timestamp
- `build_id` — the build_token

---

## Step 2: Fix Each Failure Sequentially

For each FAILED scenario, in order:

### 2a. Read context
1. Read `steps_to_reproduce` and `error_detail` from `results.json`
2. Re-read the full BDD scenario from its `.feature.md` file — the Given/When/Then steps define the exact expected behavior
3. Read the relevant page spec (`spec/apps/{app}/pages/{page}.md`) and API contracts (`spec/apps/{app}/api-contracts.md`) for the affected surface

### 2b. Write a reproducing test
Write a **unit or integration test** that:
- Exercises the specific code path that fails
- Fails before your fix (red)
- Passes after your fix (green)

Do not skip this step. The reproducing test prevents regression.

### 2c. Fix the code
Fix the implementation until:
- Your new test passes
- Existing tests still pass
- The fix is minimal (avoid scope creep)

### 2d. Commit
```bash
git add <affected files>
git commit -m "fix: {Scenario Title} — {one-line description of root cause}"
```

Example:
```bash
git commit -m "fix: User can view order history — empty state shown when no orders exist"
```

---

## Step 3: After All Fixes

Once all FAILED scenarios have been addressed (or after hitting the stopping condition):

1. Verify your new tests all pass: `npm test` (or equivalent)
2. Trigger a new deployment (new SHA → new build_token → new manifest.json)
3. The test agent runs again against the fixed build

---

## Stopping Condition

Track consecutive failures per scenario across build cycles. If the **same scenario fails 3 consecutive build cycles**:

1. Stop the automated fix loop
2. Write a note in `blackbox/builds/{token}/spec-gaps.md` describing the scenario and what you attempted
3. Surface it to the human as a blocking issue requiring review
4. Do not continue iterating — you may be fighting a spec ambiguity or an environmental issue

---

## What If UNTESTED Scenarios Appear?

A scenario in `final_test_results/results.json` with `status: "UNTESTED"` means the test agent did not process it. This should not happen in a complete run — if it does, it indicates the test agent crashed or timed out mid-run. Re-trigger the test cycle (new manifest.json with the same build_token or a new one).
