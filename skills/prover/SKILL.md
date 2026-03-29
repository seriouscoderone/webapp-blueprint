---
name: webapp-prover
description: Deterministic BDD testing and build-test-fix cycle for webapp-blueprint suites. Converts BDD features to executable Playwright tests, runs them deterministically, and orchestrates code fixes for failures. No LLM in the test execution path.
---

# Webapp Prover — Deterministic BDD Test & Fix Cycle

## Overview

This skill implements a **deterministic build-test-fix loop** for applications specified by `webapp-blueprint` and `webapp-architect`. Tests compile from Gherkin `.feature` files and run via `npx playwright test` — **no LLM is involved in test execution**. The LLM is only used for two things: (1) writing step definitions, and (2) fixing application code when tests fail.

**Three phases:**

| Phase | Name | Purpose | LLM Role |
|-------|------|---------|----------|
| 1 | Test Harness Generation | Scaffold all test infrastructure | Code generation |
| 2 | Step Definition Implementation | Fill in step definition bodies | Code generation |
| 3 | Build-Test-Fix Loop | Run tests, fix failures, repeat | Fix app code only |

**Core principle:** Tests are deterministic. Once Phase 2 completes, test code is immutable. Only application source code changes during the fix loop.

---

## Prerequisites

Before running this skill, verify:

1. **`.architect-meta.json` exists** — webapp-architect completed Steps 10-17
2. **`.feature.md` files exist** under `spec/apps/{app}/features/`
3. **`spec/apps/{app}/pages/*.md` exist** — page pattern specs (needed for page objects)
4. **`spec/apps/{app}/api-contracts.md` exists** — API contract definitions (needed for API helpers)

### Environment checks

Run these checks before proceeding — if any fail, stop and tell the user what to install:

```bash
# Node.js (required — cannot be installed by the agent)
node --version    # must be v18+

# Python 3 (required for parse-playwright-results.py)
python3 --version
```

If Node.js is missing, tell the user:

> **Node.js v18+ is required.** Install it from https://nodejs.org or via your package manager (`brew install node`, `nvm install 18`, etc.) and re-run this skill.

The agent handles all npm package installation (`playwright-bdd`, `@playwright/test`, browser binaries) — the user only needs Node.js itself.

### Spec prerequisites

If `.architect-meta.json` is missing or spec files don't exist, tell the user:

> Run `webapp-blueprint` (Steps 1-9) and `webapp-architect` (Steps 10-17) first.

### Test data dictionary (recommended)

Check for `spec/apps/{app}/test-data-dictionary.json`. This file maps BDD placeholder tokens (e.g., `{ADMIN_USER}`) to canonical seed values (e.g., `"Emily Worthington"`). It is produced by the architect in Step 17.

If the dictionary is missing, warn the user:

> **Warning:** No test-data-dictionary.json found. Feature files may contain placeholder tokens that cannot be resolved. Run webapp-architect Step 17 to generate the dictionary, or be prepared to manually map entity names during Phase 2.

The prover works without the dictionary (placeholder tokens become literal strings) but test failures from name mismatches are likely.

---

## Phase 1 — Test Harness Generation

Follow `{SKILL_DIR}/references/harness-generation.md` for the full guide.

This phase generates all test scaffolding from the spec. No manual coding — the agent reads spec files and produces the entire test infrastructure.

### Steps

1. **Convert `.feature.md` to `.feature`** — Strip markdown wrappers, extract pure Gherkin. If `feature-md-to-gherkin.py` is available in the project's installed skills, use it. Otherwise, perform the conversion manually following the rules in `{SKILL_DIR}/references/harness-generation.md`.
2. **Generate `playwright.config.ts`** with `defineBddConfig()` from `playwright-bdd`
3. **Generate base fixtures** (`tests/fixtures/base.fixture.ts`)
4. **Generate step definition skeletons** (`tests/steps/`) — empty TODO bodies with correct `Given`/`When`/`Then` bindings
5. **Generate page objects** (`tests/page-objects/`) from page pattern specs (Step 11)
6. **Generate API helpers** (`tests/api-helpers/`) from `api-contracts.md` (Step 13)

### Output Structure

```
tests/
├── playwright.config.ts
├── fixtures/
│   └── base.fixture.ts
├── features/{app}/
│   └── *.feature          (converted from .feature.md)
├── steps/
│   ├── common/
│   │   ├── auth.steps.ts
│   │   └── navigation.steps.ts
│   └── {app}/
│       └── {feature}.steps.ts
├── page-objects/{app}/
│   └── {page}.page.ts
└── api-helpers/
    └── {app}.api.ts
```

### Completion Check

Phase 1 is complete when:
- All `.feature.md` files have corresponding `.feature` files
- `playwright.config.ts` exists and imports `defineBddConfig`
- At least one step definition skeleton exists per feature
- Page objects exist for all pages referenced in features
- `npm install` succeeds with playwright-bdd dependencies

---

## Phase 2 — Step Definition Implementation

Follow `{SKILL_DIR}/references/step-implementation.md` for the full guide.

The agent reads page specs, state-interaction, api-contracts and fills in the TODO bodies in step definition files. This is a coding task — the agent writes Playwright automation code.

### Key Rules

- **Locator hierarchy:** `page.getByRole()` > `page.getByText()` > `page.getByTestId()` > `page.locator()`
- **Assertions:** Use `expect()` from `@playwright/test`
- **Given steps** set up preconditions (prefer API-based setup over UI)
- **When steps** perform user actions (click, fill, navigate)
- **Then steps** assert outcomes (visibility, text content, counts)

### Completion Check

Phase 2 is complete when:
- No step definition file contains TODO placeholders
- `npx bddgen` compiles without errors
- All step bindings resolve to implemented functions

---

## Phase 3 — Build-Test-Fix Loop

Follow `{SKILL_DIR}/references/build-test-fix-loop.md` for the full guide.

This is the deterministic loop. The LLM never touches test execution — it only reads results and fixes application code.

```
┌─────────────────────────────────────────────────┐
│  1. npx bddgen                                  │
│     └─ Compile .feature → .spec.ts              │
│                                                  │
│  2. npx playwright test --reporter=json          │
│     └─ Run tests deterministically               │
│                                                  │
│  3. python3 {SKILL_DIR}/scripts/                 │
│        parse-playwright-results.py               │
│     └─ Parse JSON → per-scenario status          │
│                                                  │
│  4. IF all pass → update .prover-meta.json → DONE│
│     IF failures:                                 │
│       a. Read failure messages + trace paths     │
│       b. Fix app code (NOT test code,            │
│          NOT .feature files)                     │
│       c. Commit fix → go to step 1               │
│     IF same scenario fails 3× → mark exhausted   │
│     IF all remaining failures exhausted → STOP   │
│                                                  │
│  5. Update .prover-meta.json with results        │
└─────────────────────────────────────────────────┘
```

### Immutability Rules

These are **absolute** during Phase 3:

- `.feature` files are **IMMUTABLE** — never modify Gherkin
- Step definitions are **IMMUTABLE** after Phase 2 — never modify test code
- Only **application source code** is modified by the fix agent
- The fix agent **NEVER** modifies test files

### When to Stop

1. **All scenarios pass** — success
2. **All remaining failures are exhausted** (3 consecutive failures each) — partial success
3. **Max cycles reached** (default: 10) — timeout

---

## Prover Metadata

Tracks per-scenario status across cycles. Written to `.prover-meta.json` at the project root.

```json
{
  "version": "1.0",
  "skill": "webapp-prover",
  "app": "admin-portal",
  "status": "in_progress|passed|partial|failed",
  "current_cycle": 3,
  "max_cycles": 10,
  "base_url": "http://localhost:3000",
  "summary": {
    "total": 25,
    "passed": 22,
    "failed": 2,
    "exhausted": 1,
    "not_run": 0
  },
  "features": {
    "Order Management": {
      "source": "spec/apps/portal/features/order-management.feature.md",
      "scenarios": {
        "View order list": {
          "status": "PASSED",
          "history": [
            {"cycle": 1, "status": "FAILED", "error": "...", "fix": "..."},
            {"cycle": 2, "status": "PASSED"}
          ],
          "consecutive_failures": 0,
          "exhausted": false
        }
      }
    }
  }
}
```

### Status Values

| Status | Meaning |
|--------|---------|
| `PASSED` | Scenario passed in the latest cycle |
| `FAILED` | Scenario failed in the latest cycle |
| `ERROR` | Scenario timed out or had infrastructure error |
| `EXHAUSTED` | Failed 3 consecutive times — skipped |
| `NOT_RUN` | Not yet executed |

---

## Spec Sync

After all tests pass (or after each cycle), optionally review fixes and sync gaps back to spec. See `{SKILL_DIR}/references/spec-sync.md`.

This is a feedback loop: if fixing app code revealed that the spec was missing behaviors or had incorrect assumptions, update the spec to reflect reality. Do **not** modify `.feature` files during the loop — flag them for human review instead.

---

## Script Reference

| Script | Location | Purpose |
|--------|----------|---------|
| `parse-playwright-results.py` | `{SKILL_DIR}/scripts/` | Parse Playwright JSON output, update `.prover-meta.json` |

### Parse Results Usage

```bash
python3 {SKILL_DIR}/scripts/parse-playwright-results.py \
  --results-file test-results/results.json \
  --meta-file .prover-meta.json \
  --cycle N \
  --app APP \
  --project-dir {project_root}
```

---

## Quick Start

```
1. Verify prerequisites (spec complete, architect done)
2. Phase 1: Generate test harness
     → npm install playwright-bdd @playwright/test
     → Convert features, generate config, fixtures, skeletons, page objects, API helpers
3. Phase 2: Implement step definitions
     → Fill in all TODO bodies with Playwright automation code
4. Phase 3: Run the loop
     → npx bddgen && npx playwright test --reporter=json
     → Parse results → fix app code → commit → repeat
5. Done when all pass or exhausted
```
