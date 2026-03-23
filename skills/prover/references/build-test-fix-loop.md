# Phase 3 — Build-Test-Fix Loop

This reference covers the deterministic test execution loop. The LLM never participates in test execution — it only reads results and fixes application source code.

---

## Command Sequence

Each cycle runs these three commands in order:

### Step 1: Compile Features

```bash
npx bddgen
```

This compiles `.feature` files into `.spec.ts` files that Playwright can execute. Must succeed before running tests.

If `bddgen` fails:
- Check for syntax errors in `.feature` files (but do NOT modify them — they are immutable)
- Check for missing step definitions
- Check for import errors in step files
- Fix infrastructure issues only — never modify `.feature` content

### Step 2: Run Tests

```bash
npx playwright test --reporter=json 2>&1 | tee test-results/raw-output.txt
```

Or, if using the config's built-in JSON reporter:

```bash
npx playwright test
```

The JSON reporter configured in `playwright.config.ts` writes to `test-results/results.json` automatically.

**Key flags:**
- Do NOT add `--retries` — failures must be real
- Do NOT add `--workers` — config already sets `workers: 1`
- Do NOT add `--reporter` if already configured in `playwright.config.ts`

### Step 3: Parse Results

```bash
python3 {SKILL_DIR}/scripts/parse-playwright-results.py \
  --results-file test-results/results.json \
  --meta-file .prover-meta.json \
  --cycle {N} \
  --app {APP_NAME} \
  --project-dir {project_root}
```

Exit codes:
- **0** — All scenarios passed
- **1** — Some scenarios failed
- **2** — File error (missing results file, parse error)

---

## Reading Playwright JSON Output

The JSON reporter produces a nested structure:

```
config
└── projects[]
    └── suites[]
        └── suites[]          (nested: file → describe → test)
            └── specs[]
                └── tests[]
                    └── results[]
                        ├── status: "passed" | "failed" | "timedOut" | "skipped"
                        ├── duration: number (ms)
                        ├── error?: { message, stack }
                        └── attachments[]
                            └── { name: "trace", path: "..." }
```

### Mapping to Scenarios

- Each Gherkin `Scenario:` becomes one `spec` in the JSON
- The spec's `title` matches the scenario title
- `Scenario Outline:` with `Examples:` produces multiple specs (one per example row)
- The `suites` hierarchy corresponds to: File → Feature → Scenario

### Status Mapping

| Playwright Status | Prover Status |
|-------------------|---------------|
| `passed` | `PASSED` |
| `failed` | `FAILED` |
| `timedOut` | `ERROR` |
| `skipped` | `NOT_RUN` |

---

## Interpreting Failures

When a scenario fails, extract:

1. **Failing step** — The error stack trace points to the step definition that failed
2. **Error message** — The assertion or runtime error message
3. **Trace file** — If `trace: 'retain-on-failure'` is set, a trace zip exists in `test-results/`
4. **Screenshot** — If `screenshot: 'only-on-failure'` is set, a PNG exists in `test-results/`

### Reading a Failure

```json
{
  "status": "failed",
  "error": {
    "message": "expect(locator).toBeVisible()\n\nLocator: getByRole('table', { name: /orders/i })\nExpected: visible\nReceived: hidden",
    "stack": "Error: expect(locator).toBeVisible()...\n    at tests/steps/portal/order-management.steps.ts:42:5"
  },
  "attachments": [
    { "name": "screenshot", "path": "test-results/.../test-failed-1.png" },
    { "name": "trace", "path": "test-results/.../trace.zip" }
  ]
}
```

From this, the agent knows:
- The orders table is not rendering (hidden instead of visible)
- The step file and line number where the assertion failed
- A screenshot and trace to inspect the actual page state

### Viewing Traces

To examine a trace:

```bash
npx playwright show-trace test-results/.../trace.zip
```

Or read the screenshot to understand the visual state.

---

## Fix Protocol

### What to Fix

**ONLY application source code.** This means:

- Frontend components (React, Vue, Svelte, etc.)
- Backend API routes and handlers
- Database migrations or seed scripts
- Configuration files (env, routing, etc.)
- CSS/styling issues

### What NEVER to Fix

- `.feature` files — IMMUTABLE
- Step definition files — IMMUTABLE after Phase 2
- Page object files — IMMUTABLE after Phase 1
- Playwright configuration — IMMUTABLE after Phase 1
- Test fixtures — IMMUTABLE after Phase 1

### Fix Process

1. **Read the failure** — Understand what the test expected vs. what happened
2. **Identify root cause** — Is it a missing component? Wrong API response? Missing route? CSS issue?
3. **Fix the app code** — Make the minimal change to make the test pass
4. **Commit the fix** — Use the commit convention below
5. **Re-run the loop** — Go back to Step 1 (npx bddgen)

### Sequential Fixing

Fix **one failure at a time**. Do not attempt to fix multiple unrelated failures in a single commit.

Why:
- Easier to bisect if a fix introduces regressions
- Each fix can be reviewed independently
- Clearer commit history

If multiple failures share the same root cause (e.g., a missing component used by 5 scenarios), fix the root cause in one commit.

---

## Commit Conventions

```
fix: {Scenario Title} — {short description}
```

Examples:
```
fix: View order list — render orders table component
fix: Create new order — add POST /api/orders endpoint
fix: Filter by status — connect status dropdown to query params
fix: Login as admin — set correct RBAC permissions for admin role
```

---

## Exhaustion Detection

A scenario is **exhausted** when it has failed **3 consecutive times**. This means the agent has tried 3 different fixes and none worked.

When a scenario is exhausted:
1. Mark it as `"exhausted": true` in `.prover-meta.json`
2. Skip it in subsequent cycles
3. Continue fixing other failures

The `parse-playwright-results.py` script handles exhaustion tracking automatically via the `consecutive_failures` counter.

---

## Stopping Conditions

### 1. All Passed (Exit: Success)

```
parse-playwright-results.py exits 0
.prover-meta.json status → "passed"
```

### 2. All Remaining Failures Exhausted (Exit: Partial)

Every non-passing scenario has `exhausted: true`. No more fixes to attempt.

```
.prover-meta.json status → "partial"
```

### 3. Max Cycles Reached (Exit: Timeout)

`current_cycle >= max_cycles` (default: 10).

```
.prover-meta.json status → "failed"
```

---

## .prover-meta.json Update Protocol

After each cycle:

1. **Run `parse-playwright-results.py`** — It updates the meta file automatically
2. **Verify the update** — Read `.prover-meta.json` to confirm:
   - `current_cycle` incremented
   - Each scenario has a new `history` entry
   - `summary` counts are correct
   - `status` field reflects current state

### Initial Creation

If `.prover-meta.json` does not exist, the first cycle creates it. The parse script initializes the structure from the test results and the app name.

### Manual Override

If the agent needs to reset the loop (e.g., after a major refactor):
- Delete `.prover-meta.json`
- The next cycle starts fresh

---

## Full Cycle Example

```
Cycle 1:
  npx bddgen                          → compiles 15 features
  npx playwright test                  → 20 pass, 5 fail
  parse-playwright-results.py          → exit 1
  Fix: "View order list" — add orders table component
  git commit -m "fix: View order list — add orders table component"

Cycle 2:
  npx bddgen                          → compiles 15 features
  npx playwright test                  → 23 pass, 2 fail
  parse-playwright-results.py          → exit 1
  Fix: "Create new order" — add POST /api/orders route
  git commit -m "fix: Create new order — add POST /api/orders route"

Cycle 3:
  npx bddgen                          → compiles 15 features
  npx playwright test                  → 24 pass, 1 fail
  parse-playwright-results.py          → exit 1
  Fix: "Delete order" — add confirmation dialog handler
  git commit -m "fix: Delete order — add confirmation dialog handler"

Cycle 4:
  npx bddgen                          → compiles 15 features
  npx playwright test                  → 25 pass, 0 fail
  parse-playwright-results.py          → exit 0
  .prover-meta.json status → "passed"
  DONE
```
